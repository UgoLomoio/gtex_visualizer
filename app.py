"""
*************************************************************************************************************
*                                                                                                           *
*   GTex data visualizer developed by Ugo Lomoio at Magna Graecia University of Catanzaro                   *
*                                                                                                           *
*                           Dash App with Server Side callbacks                                             *
*                                                                                                           *
*************************************************************************************************************
"""

from dash import html, dcc, Dash, dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import numpy as np 
import pandas as pd 
from make_plots import *
import scipy.stats as stats

all_tissues = ['All', 'Adipose_Subcutaneous', 'Adipose_Visceral_Omentum', 'Adrenal_Gland',
 'Artery_Aorta', 'Artery_Coronary', 'Artery_Tibial', 'Bladder',
 'Brain_Amygdala', 'Brain_Anterior_cingulate_cortex_BA24',
 'Brain_Caudate_basal_ganglia', 'Brain_Cerebellar_Hemisphere',
 'Brain_Cerebellum', 'Brain_Cortex', 'Brain_Frontal_Cortex_BA9',
 'Brain_Hippocampus', 'Brain_Hypothalamus',
 'Brain_Nucleus_accumbens_basal_ganglia', 'Brain_Putamen_basal_ganglia',
 'Brain_Spinal_cord_cervical_c-1', 'Brain_Substantia_nigra',
 'Breast_Mammary_Tissue', 'Cells_Cultured_fibroblasts',
 'Cells_EBV-transformed_lymphocytes', 'Cervix_Ectocervix',
 'Cervix_Endocervix', 'Colon_Sigmoid', 'Colon_Transverse',
 'Esophagus_Gastroesophageal_Junction', 'Esophagus_Mucosa',
 'Esophagus_Muscularis', 'Fallopian_Tube', 'Heart_Atrial_Appendage',
 'Heart_Left_Ventricle', 'Kidney_Cortex', 'Kidney_Medulla', 'Liver', 'Lung',
 'Minor_Salivary_Gland', 'Muscle_Skeletal', 'Nerve_Tibial', 'Ovary',
 'Pancreas', 'Pituitary', 'Prostate', 'Skin_Not_Sun_Exposed_Suprapubic',
 'Skin_Sun_Exposed_Lower_leg', 'Small_Intestine_Terminal_Ileum', 'Spleen',
 'Stomach', 'Testis', 'Thyroid', 'Uterus', 'Vagina', 'Whole_Blood']

with open('all_genes_dict.txt', 'r') as f:
    data = f.readline()
    all_genes_dict = dict(eval(str(data)))

all_filters = ["No filters", "Divide by Gender", "Divide by Age", "Divide by Gender and Age"]

max_n_clicks = 0

def empty_figure(title = "Fill Dropdown menus and press the Update Plot Button", color = "white"):

    fig = go.FigureWidget()
    fig.update_layout(template="plotly_dark", title=title, title_font_color=color)
    return fig

def get_gencode_id_from_gene_name(gene_name):

    gencode_id = all_genes_dict[gene_name]
    return gencode_id 

fig_prec_violin = empty_figure()
fig_prec_pie = empty_figure()
prec_gene = None
prec_tissue = None
prec_filter = None
prec_table = pd.DataFrame(columns = ["", "f_value", "p_value"])
prec_table_title = "Anova and Kruskal analysis results only when Update Plots button is clicked"

app = Dash(__name__)          #create the dash app fist 
server = app.server

app_dash_layout_args = [
            
        html.H1("GTex gene data visualization",  
                    style={'backgroundColor':'rgb(17, 17, 17)', 'color': 'orange'}
        ),

        html.Div(
                
                    children = [
                        html.Label("Select a gene: ", style={'backgroundColor':'rgb(17, 17, 17)', 'color': 'white'}),
                        dcc.Dropdown(list(all_genes_dict.keys()), list(all_genes_dict.keys())[0], id='genes_dd', style={'color': 'black', 'border': '3px solid #ff7300'})
                    ],
                    style={'width': '100%', 'display': 'inline-block'}
        ),

        html.Div(
                
                    children = [
                        html.Label("Select a tissue:", style={'backgroundColor':'rgb(17, 17, 17)', 'color': 'white'}),
                        dcc.Dropdown(all_tissues, all_tissues[0], id='tissues_dd', style={'color': 'black', 'border': '3px solid #ff7300'})
                    ],
                    style={'width': '100%', 'display': 'inline-block'}
        ),
    
        html.Div(
                
                    children = [
                        html.Label("Select a filter:", style={'backgroundColor':'rgb(17, 17, 17)', 'color': 'white'}),
                        dcc.Dropdown(all_filters, all_filters[0], id='filters_dd', style={'color': 'black', 'border': '3px solid #ff7300'})
                    ],
                    style={'width': '100%', 'display': 'inline-block'}
        ),

        dcc.Loading(id = "loading-violin", style={"position": "absolute", "left": "0px", "top": "350px", 
                    'backgroundColor':'rgb(17, 17, 17)', 'color': 'white', 'width': "800px", 'height': '1000px'}, type="default",  
                    
                    children=
                    [
                            html.Div(
                                dcc.Graph( 
                                        id="fig-violin",
                                        figure=empty_figure(),
                                        animate=False,
                                        style={"position": "absolute", "left": "0px", "top": "350px", 
                                               'backgroundColor':'rgb(17, 17, 17)', 'color': 'white', 'width': "800px", 'height': '1000px'},
                                        config = {'responsive': True, 'displayModeBar': True}
                                )
                            )
                    ]      
        ),
                  
        dcc.Loading(
                    id = "loading-pie",   
                    children=[html.Div(
                        dcc.Graph( 
                                    id="fig-pie",
                                    figure=empty_figure(),
                                    animate=False,
                                    style={"position": "absolute", "left": "1000px", "top": "350px", 
                                    'backgroundColor':'rgb(17, 17, 17)', 'color': 'white', 'width': "800px", 'height': '1000px'},
                                    config = {'responsive': True, 'displayModeBar': True}
                        )

                    )],
                    style={"position": "absolute", "left": "1000px", "top": "350px", 
                                    'backgroundColor':'rgb(17, 17, 17)', 'color': 'white', 'width': "800px", 'height': '1000px'},
                    type="default"
        ),
    
        html.Button(
                    "Update Plots",
                    id = "plot-button",  
                    n_clicks=0,
                    style={"position": "absolute", "left": "850px", "top": "280px", 'cursor': 'pointer', 'border': '0px', 
                           'border-radius': '3px', 'background-color': 'rgb(31, 24, 252)', 'color': 'white', 'font-size': '12px',
                           'font-family': 'Open Sans', 'width': "100px", 'height': '40px', 'border': '3px solid #ff7300'}
        ),
        
        html.Div(
            [
                html.Label(prec_table_title, id="table_title"),
                dash_table.DataTable(data = [{"": "Anova", "f_value": "", "p_value": "None"}, {"": "Kruskal", "f_value": "None", "p_value": "None"}],
                                     columns = [{"name": name, "id": name} for name in prec_table.columns], id='anova_table', style_header={'backgroundColor': 'rgb(30, 30, 30)','color': 'white'},
                                     style_data={'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white'})
            ],  
            style={"position": "absolute", "right": "200px", "top": "1400px", 
                                            'backgroundColor':'rgb(17, 17, 17)', 'color': 'white', 'width': '400px', 'height': '200px'}
        ),

]
app.layout = html.Div(
        app_dash_layout_args,
        style = {'border': '0px', 'backgroundColor':'rgb(17, 17, 17)', 'background-size': '100%', 'position': 'fixed',
                'width': '100%', 'height': '100%', 'overflowX': 'scroll'}
)
    
@app.callback(

    Output("fig-violin", "figure"),
    Output("fig-pie", "figure"),
    Output("table_title", "children"),
    Output("anova_table", "data"),

    Input('plot-button', 'n_clicks'), 

    State('filters_dd', 'value'),
    State('genes_dd', 'value'),
    State('tissues_dd', 'value'),

    #prevent_initial_call=True
)
def update_plot(n_clicks, filters, gene_name, tissue):


    global fig_prec_violin 
    global fig_prec_pie
    global prec_table_title
    global prec_table
    global prec_gene 
    global prec_tissue 
    global prec_filter 

    print("Clicked {}, {}, {}".format(gene_name, tissue, filters))
    if gene_name is None:
        gene_name = all_genes_dict.keys()[0]
    if tissue is None:
        tissue = all_tissues[0]
    if filters is None:
        filters = all_filters[0]

    gencode_id = get_gencode_id_from_gene_name(gene_name)
    table_title = "Anova and Kruskal analysis results for: Gene '{}', Tissue '{}' and Filter '{}'".format(gene_name, tissue, filters)
    prec_table_title = table_title
    if gene_name != prec_gene or tissue != prec_tissue or filters != prec_filter:
           
        print("Changed genecode or tissue or filter")

        if tissue == "All":
                  
            print("Creating violin plots")
            if filters == "No filters":

                fig_violin = plot_by_gene(gencode_id, gene_name)
                ys = [fig_violin.data[i]["y"] for i in range(len(fig_violin.data))]
                fvalue_anova, pvalue_anova = stats.f_oneway(ys[0], ys[1], ys[2], ys[3], ys[4], ys[5], ys[6], ys[7], ys[8], ys[9], ys[10],
                                                ys[11], ys[12], ys[13], ys[14], ys[15], ys[16], ys[17], ys[18], ys[19], ys[20],
                                                ys[21], ys[22], ys[23], ys[24], ys[25], ys[26], ys[27], ys[28], ys[29], ys[30],
                                                ys[31], ys[32], ys[33], ys[34], ys[35], ys[36], ys[37], ys[38], ys[39], ys[40],
                                                ys[41], ys[42], ys[43], ys[44], ys[45], ys[46], ys[47], ys[48], ys[49], ys[50],
                                                ys[51], ys[52], ys[53])
                fvalue_kruskal, pvalue_kruskal = stats.kruskal(ys[0], ys[1], ys[2], ys[3], ys[4], ys[5], ys[6], ys[7], ys[8], ys[9], ys[10],
                                                ys[11], ys[12], ys[13], ys[14], ys[15], ys[16], ys[17], ys[18], ys[19], ys[20],
                                                ys[21], ys[22], ys[23], ys[24], ys[25], ys[26], ys[27], ys[28], ys[29], ys[30],
                                                ys[31], ys[32], ys[33], ys[34], ys[35], ys[36], ys[37], ys[38], ys[39], ys[40],
                                                ys[41], ys[42], ys[43], ys[44], ys[45], ys[46], ys[47], ys[48], ys[49], ys[50],
                                                ys[51], ys[52], ys[53])
                df = pd.DataFrame([["Anova", fvalue_anova, pvalue_anova], ["Kruskal", fvalue_kruskal, pvalue_kruskal]], columns = ["", "f_value", "p_value"])
                dict_data = df.to_dict('rows')

            elif filters == "Divide by Gender":
                        
                fig_violin = plot_by_gene_and_gender(gencode_id, gene_name)
                ys = [fig_violin.data[i]["y"] for i in range(len(fig_violin.data))]
                fvalue_anova, pvalue_anova = stats.f_oneway(ys[0], ys[1], ys[2], ys[3], ys[4], ys[5], ys[6], ys[7], ys[8], ys[9], ys[10],
                                                ys[11], ys[12], ys[13], ys[14], ys[15], ys[16], ys[17], ys[18], ys[19], ys[20],
                                                ys[21], ys[22], ys[23], ys[24], ys[25], ys[26], ys[27], ys[28], ys[29], ys[30],
                                                ys[31], ys[32], ys[33], ys[34], ys[35], ys[36], ys[37], ys[38], ys[39], ys[40],
                                                ys[41], ys[42], ys[43], ys[44], ys[45], ys[46], ys[47], ys[48], ys[49], ys[50],
                                                ys[51], ys[52], ys[53], ys[54], ys[55], ys[56], ys[57], ys[58], ys[59], ys[60],
                                                ys[61], ys[62], ys[63], ys[64], ys[65], ys[66], ys[67], ys[68], ys[69], ys[70],
                                                ys[71], ys[72], ys[73], ys[74], ys[75], ys[76], ys[77], ys[78], ys[79], ys[80],
                                                ys[81], ys[82], ys[83], ys[84], ys[85], ys[86], ys[87], ys[88], ys[89], ys[90],
                                                ys[91], ys[92], ys[93], ys[94], ys[95], ys[96], ys[97], ys[98], ys[99], ys[100],
                                                ys[101], ys[102], ys[103], ys[104], ys[105], ys[106], ys[107])
                fvalue_kruskal, pvalue_kruskal = stats.kruskal(ys[0], ys[1], ys[2], ys[3], ys[4], ys[5], ys[6], ys[7], ys[8], ys[9], ys[10],
                                                ys[11], ys[12], ys[13], ys[14], ys[15], ys[16], ys[17], ys[18], ys[19], ys[20],
                                                ys[21], ys[22], ys[23], ys[24], ys[25], ys[26], ys[27], ys[28], ys[29], ys[30],
                                                ys[31], ys[32], ys[33], ys[34], ys[35], ys[36], ys[37], ys[38], ys[39], ys[40],
                                                ys[41], ys[42], ys[43], ys[44], ys[45], ys[46], ys[47], ys[48], ys[49], ys[50],
                                                ys[51], ys[52], ys[53], ys[54], ys[55], ys[56], ys[57], ys[58], ys[59], ys[60],
                                                ys[61], ys[62], ys[63], ys[64], ys[65], ys[66], ys[67], ys[68], ys[69], ys[70],
                                                ys[71], ys[72], ys[73], ys[74], ys[75], ys[76], ys[77], ys[78], ys[79], ys[80],
                                                ys[81], ys[82], ys[83], ys[84], ys[85], ys[86], ys[87], ys[88], ys[89], ys[90],
                                                ys[91], ys[92], ys[93], ys[94], ys[95], ys[96], ys[97], ys[98], ys[99], ys[100],
                                                ys[101], ys[102], ys[103], ys[104], ys[105], ys[106], ys[107])
                df = pd.DataFrame([["Anova", fvalue_anova, pvalue_anova], ["Kruskal", fvalue_kruskal, pvalue_kruskal]], columns = ["", "f_value", "p_value"])
                dict_data = df.to_dict('rows')

            else:

                error = "{} is not a valid filter for tissue = {}".format(filters, tissue)
                fig_violin = empty_figure(error, 'red')
                table_title += "Can't compute" 
                prec_table_title = table_title
                df = pd.DataFrame([["Anova", "None", "None"], ["Kruskal", "None", "None"]], columns = ["", "f_value", "p_value"])
                dict_data = df.to_dict('rows')

            fig_prec_violin = fig_violin
            prec_table = dict_data 

            print("Creating pie plots")
            if gencode_id != prec_gene or tissue != prec_tissue:
                fig_pie = empty_figure(title = "Pie figures not yet implemented with Tissue = 'All'")             #to do fig pie with all tissues
            else:
                fig_pie = fig_prec_pie
                
            if gencode_id != prec_gene:
                print("Changed gencode {} -> {}".format(prec_gene, gencode_id))
                prec_gene = gencode_id 
            if tissue != prec_tissue:
                print("Changed tissue {} -> {}".format(prec_tissue, tissue))
                prec_tissue = tissue 
            if filters != prec_filter:
                print("Changed filter {} -> {}".format(prec_filter, filters))
                prec_filter = filters 

            print("Figures: ", fig_violin, fig_pie)
            fig_prec_pie = fig_pie
            
            return fig_violin, fig_pie, table_title, dict_data
                
        else:
                    
            print("Creating violin plots")
            if filters == "No filters":
                
                fig_violin = plot_by_gene_and_tissue(gencode_id, gene_name, tissue)
                table_title += ", apply a filter if tissue is != All"
                prec_table_title = table_title 
                df = pd.DataFrame([["Anova", "None", "None"], ["Kruskal", "None", "None"]], columns = ["", "f_value", "p_value"])
                dict_data = df.to_dict('rows')            
            
            elif filters == "Divide by Gender":

                fig_violin = plot_by_gene_and_gender_and_tissue(gencode_id, gene_name, tissue)
                ys = [fig_violin.data[i]["y"] for i in range(len(fig_violin.data))]
                fvalue_anova, pvalue_anova = stats.f_oneway(ys[0], ys[1])
                fvalue_kruskal, pvalue_kruskal = stats.kruskal(ys[0], ys[1])
                df = pd.DataFrame([["Anova", fvalue_anova, pvalue_anova], ["Kruskal", fvalue_kruskal, pvalue_kruskal]], columns = ["", "f_value", "p_value"])
                dict_data = df.to_dict('rows')

            elif filters == "Divide by Age":

                fig_violin = plot_by_gene_and_tissue_and_age(gencode_id, gene_name, tissue)
                ys = [fig_violin.data[i]["y"] for i in range(len(fig_violin.data))]
                fvalue_anova, pvalue_anova = stats.f_oneway(ys[0], ys[1], ys[2], ys[3], ys[4])
                fvalue_kruskal, pvalue_kruskal = stats.kruskal(ys[0], ys[1], ys[2], ys[3], ys[4])
                df = pd.DataFrame([["Anova", fvalue_anova, pvalue_anova], ["Kruskal", fvalue_kruskal, pvalue_kruskal]], columns = ["", "f_value", "p_value"])
                dict_data = df.to_dict('rows')
                        
            else: #"Divide by Gender and Age"

                fig_violin = plot_by_gene_tissue_age_and_gender(gencode_id, gene_name, tissue)
                ys = [fig_violin.data[i]["y"] for i in range(len(fig_violin.data))]
                fvalue_anova, pvalue_anova = stats.f_oneway(ys[0], ys[1], ys[2], ys[3], ys[4], ys[5], ys[6], ys[7], ys[8], ys[9])
                fvalue_kruskal, pvalue_kruskal = stats.kruskal(ys[0], ys[1], ys[2], ys[3], ys[4], ys[5], ys[6], ys[7], ys[8], ys[9])
                df = pd.DataFrame([["Anova", fvalue_anova, pvalue_anova], ["Kruskal", fvalue_kruskal, pvalue_kruskal]], columns = ["", "f_value", "p_value"])
                dict_data = df.to_dict('rows')

            print(dict_data)
            fig_prec_violin = fig_violin
            prec_table = dict_data 
            
            if filters != prec_filter:
                print("Changed filter {} -> {}".format(prec_filter, filters))
                prec_filter = filters 

            print("Creating pie plots")
            if gencode_id != prec_gene or tissue != prec_tissue:
                   
                if gencode_id != prec_gene:
                    print("Changed gencode {} -> {}".format(prec_gene, gencode_id))
                    prec_gene = gencode_id 
                if tissue != prec_tissue:
                    print("Changed tissue {} -> {}".format(prec_tissue, tissue))
                    prec_tissue = tissue 
                    
                print(1)
                fig_pie = plot_gene_tissue_data(gencode_id, gene_name, tissue) #problem here
                fig_prec_pie = fig_pie
                print("Returing figures ", fig_violin, fig_pie)
                return fig_violin, fig_pie, table_title, dict_data
                    
            else:
                print(2)
                print("Figures ", fig_violin, fig_prec_pie)
                return fig_violin, fig_prec_pie, table_title, dict_data

    else:

        print("gencode and tissue and filters not changed")
        print("Returing figures")
        return fig_prec_violin, fig_prec_pie, prec_table_title, prec_table

if __name__ == "__main__":

    app.run_server(debug=True, dev_tools_hot_reload=False, threaded = True)