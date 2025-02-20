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
import networkx as nx 
from make_plots import *
import methods
import scipy.stats as stats

config = {
        'responsive': True, 
        'displayModeBar': True,
        'toImageButtonOptions': {
            'format': 'png', # one of png, svg, jpeg, webp
            #'height': 1080,
            #'width': 1920,
            'scale': 6 # Multiply title/legend/axis/canvas sizes by this factor
        }
    }

all_methods = ["None", "with_labels", "betweenness_centrality", "closeness_centrality", "degree_centrality", "eigenvector_centrality", "community_louvain", "community_leiden", "spectral_clustering"] # "community_girvan_newmann"
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

#template = "plotly_dark"
template = "plotly_white"

with open('all_genes_dict.txt', 'r') as f:
    data = f.readline()
    all_genes_dict = dict(eval(str(data)))

with open("ENSG_to_ENSP.txt", "r") as f:
    ensembl_gene_protein_mapping = dict(eval(f.read()))

all_filters = ["No filters", "Group by Gender", "Group by Age", "Group by Gender and Age"]
all_ages = ["20-29", "30-39", "40-49", "50-59", "60-69", "70-79"]
all_genders = ["male", "female"]
max_n_clicks = 0
bg = "white" #'rgb(17, 17, 17)'
txt_color = "black"

def empty_figure(title = "Fill Dropdown menus and press the Update Plot Button", color = "black"):

    fig = go.Figure()
    fig.update_layout(template=template, title=title, title_font_color=color)
    return fig

def get_current_y_range(x_range, y_all):
    
    y = y_all[int(x_range[0]):int(x_range[1])] #FIX X RANGE 
    temp = max(max(y))
    temp_min = -0.1
    return [temp_min, temp+0.1]#FIX

def get_gencode_id_from_gene_name(gene_name):

    gencode_id = all_genes_dict[gene_name]
    return gencode_id 

fig_prec_violin = empty_figure()
fig_prec_pie = empty_figure()
fig_prec_ppi = empty_figure()
prec_gene = None
prec_tissue = None
prec_filter = None
prec_method = None 
prec_href = ""
prec_href_gene = ""
prec_table = pd.DataFrame(columns = ["", "f_value", "p_value"])
prec_table_title = "Anova, Kruskal and Shapiro analysis results only when Update Plots button is clicked" 
prec_xrange = [0, len(all_tissues)]
max_download_n_clicks = 0
max_download_data_n_clicks = 0
max_about_n_clicks = 0
curr_violin = fig_prec_violin 
curr_G = None 
curr_data = None
curr_fvalue_shapiro = "None"
curr_pvalue_shapiro = "None"

app = Dash(__name__)          #create the dash app fist 
server = app.server
app.title = "GTexVisualizer "

app_dash_layout_args = [
            
        html.H1("GTexVisualizer: a platform for ageing studies",  
                    style={'backgroundColor': bg, 'color': 'orange'}
        ),

        html.Div(
                
                    children = [
                        html.Label("Select a gene: ", style={'backgroundColor': bg, 'color': txt_color}),
                        dcc.Dropdown(list(all_genes_dict.keys()), list(all_genes_dict.keys())[0], id='genes_dd', multi = True, style={'color': 'black', 'border': '3px solid #ff7300'}),#multi=True
                        html.A("Gene info", id = "ensembl-gene-link", href='', target="_blank",style={"position": "absolute", 'backgroundColor': bg, "left": "150px", "top": "10%", 'color': "blue", 'width': "20%"}),

                    ],
                    style={'width': '100%', 'display': 'inline-block'}
        ),

        html.Div(
                
                    children = [
                        html.Label("Select a tissue: ", style={'backgroundColor': bg, 'color': txt_color}),
                        dcc.Dropdown(all_tissues, all_tissues[0], id='tissues_dd', multi=True, style={'color': 'black', 'border': '3px solid #ff7300'})#multi=True
                    ],
                    style={'width': '100%', 'display': 'inline-block'}
        ),
    
        html.Div(
                
                    children = [
                        html.Label("Plot by: ", style={'backgroundColor': bg, 'color': txt_color}),
                        dcc.Dropdown(all_filters, all_filters[0], id='filters_dd', style={'color': 'black', 'border': '3px solid #ff7300'})
                    ],
                    style={'width': '100%', 'display': 'inline-block'}
        ),
        html.Div(
                [       
                    html.Button(
                                "Download Data",
                                id = "download-data-button",  
                                n_clicks=0,
                                style={"position": "absolute", "left": "40%", "top": "5%", 'cursor': 'pointer', 'border': '0px', 
                                       'border-radius': '3px', 'background-color': 'rgb(31, 24, 252)', 'color': 'white', 'font-size': '12px',
                                       'font-family': 'Open Sans', 'width': "200px", 'height': '40px', 'border': '3px solid #ff7300'}
                    ),
                    dcc.Download(id="download-data"),
                ]
        ),
        html.Div(

             children = [   
                dcc.Loading(id = "loading-violin", style={"position": "absolute", "left": "0px", "top": "25%", 'backgroundColor': bg, 
                                                          'color': txt_color, 'width': "100%", 'height': '50%'}, type="default",  
                    
                            children=
                            [
                                   html.Div(
                                        dcc.Graph( 
                                                id="fig-violin",
                                                figure=empty_figure(),
                                                animate=False,
                                                style={"position": "absolute", "left": "0px", "top": "30%", 
                                                       'backgroundColor': bg, 'color': txt_color, 'width': "100%", 'height': '100%', 'display': 'inline-block'},
                                                config = config
                                        )
                                   ),
                                   html.Div(
                                            dcc.RangeSlider(id='rangeslider-1', min=0,max=len(all_tissues), step=1, value=[0, len(all_tissues)], tooltip={"placement": "bottom", "always_visible": True}),
                                            id = "slider-conteiner-1",
                                            style={"position": "absolute", "left": "0px", "top": "25%", 'backgroundColor': bg, 'color': txt_color, 'width': "100%", 'height': '50px'}
                                   )
                            ]
                )
        ]),
        html.Div([
            
            dcc.Loading(
                                id = "loading-pie",   
                                children=[html.Div(
                                    dcc.Graph( 
                                                id="fig-pie",
                                                figure=empty_figure(),
                                                animate=False,
                                                style={"position": "absolute", "left": "0px", "top": "150%", 'backgroundColor': bg, 'color': txt_color, 'width': "45%", 'height': '45%'}, #
                                                config = config
                                    )

                                )],
                                style={"position": "absolute", 'backgroundColor': bg, "left": "0px", "top": "150%",  'color': txt_color, 'width': "45%", 'height': '45%', 'display': 'inline-block'}, # "left": "1000px", "top": "350px", 
                                type="default"
            ),
        
            dcc.Loading(
                                id = "loading-ppi",   
                                children=[html.Div(
                                    dcc.Graph( 
                                                id="fig-ppi",
                                                figure=empty_figure(),
                                                animate=False,
                                                style={"position": "absolute", "left": "50%", "top": "140%", 'backgroundColor': bg, 'color': txt_color, 'width': "45%", 'height': '45%'}, #
                                                config = config
                                    )

                                )],
                                style={"position": "absolute", 'backgroundColor': bg, "left": "50%", "top": "140%",  'color': txt_color, 'width': "45%", 'height': '45%'}, # "left": "1000px", "top": "350px", 
                                type="default"
            )
            ],
        style={"position": "absolute", 'backgroundColor': bg, "left": "0%", "top": "140%",  'color': txt_color, 'width': "100%", 'height': '45%'},
        ),
        html.A("See this PPI with STRING", id = "ppi-string-link", href='', target="_blank",style={"position": "absolute", 'backgroundColor': 'rgb(17, 17, 17)', "left": "50%", "top": "130%",  'color': 'white', 'width': "45%"}),

        #add save data and save plot for ppi 
        html.Div(
                
                    children = [
                        html.Label("Select a method for graph analysis and visualization: ", style={'backgroundColor': bg, 'color': txt_color}),
                        dcc.Dropdown(all_methods, all_methods[0], id='methods_dd', style={'color': 'black', 'border': '3px solid #ff7300'})
                    ],
                    style={'width': '45%', 'display': 'inline-block', "position": "absolute", "left": "50%", "top": "120%" }
        ),
        html.Button(
                    "Update Plots",
                    id = "plot-button",  
                    n_clicks=0,
                    style={"position": "absolute", "left": "0px", "top": "35%", 'cursor': 'pointer', 'border': '0px', 
                           'border-radius': '3px', 'background-color': 'rgb(31, 24, 252)', 'color': 'white', 'font-size': '12px',
                           'font-family': 'Open Sans', 'width': "200px", 'height': '40px', 'border': '3px solid #ff7300'}
        ),
        html.Div(
                [       
                    html.Button(
                                "Download Plots",#and Data
                                id = "download-plots-button",  
                                n_clicks=0,
                                style={"position": "absolute", "left": "55%", "top": "5%", 'cursor': 'pointer', 'border': '0px', 
                                       'border-radius': '3px', 'background-color': 'rgb(31, 24, 252)', 'color': 'white', 'font-size': '12px',
                                       'font-family': 'Open Sans', 'width': "200px", 'height': '40px', 'border': '3px solid #ff7300'}
                    ),
                    dcc.Download(id="download-plots"),
                    #dcc.Download(id="download-data")
                ]
        ),

        html.Div(
            [
                html.Label(prec_table_title, id="table_title"),
                dash_table.DataTable(data = [{"": "Anova", "f_value": "None", "p_value": "None"}, {"": "Kruskal", "f_value": "None", "p_value": "None"}, {"": "Shapiro", "f_value": "None", "p_value": "None"}],  export_format="csv",
                                     columns = [{"name": name, "id": name} for name in prec_table.columns], id='anova_table', style_header={'backgroundColor': 'rgb(30, 30, 30)','color': 'white'},
                                     style_data={'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white'})
            ],  
            style={"position": "absolute", "left": "0px", "top": "120%", 
                                            'backgroundColor': bg, 'color': txt_color, 'width': '45%', 'height': '5%', 'display': 'inline-block'}
        ),

        html.Div([
            html.Span('Contributors', className='contributors'),
            html.Ul([
                html.Li(['Ugo Lomoio, Magna Graecia University of Catanzaro']),
                html.Li(['Pietro Hiram Guzzi, Magna Graecia University of Catanzaro']),
                html.Li(['Pierangelo Veltri, University of Calabria']),
                html.Li(["Contact us: hguzzi@unicz.it"]),
                html.Li(html.A("User Guide", href="./assets/GTexVisualizer_User_Guide.pdf"))
            ]),
            ],
            className="footer",
            style={"position": "absolute", "left": "0px", "top": "220%", 'width': '100%'}
        )
    ]    

app.layout = html.Div(
        app_dash_layout_args,
        style = {'border': '0px', 'backgroundColor': 'white', 'background-size': '100%', 'position': 'absolute',
                'width': '100%', 'height': '100%', 'margin': '0px'}
)
  
@app.callback(
    Output("download-plots", "data"),
    Input('download-plots-button', 'n_clicks'),
    State('filters_dd', 'value'),
    State('genes_dd', 'value'),
    State('tissues_dd', 'value'),
    prevent_initial_call=True
)
def download_plots(download_n_clicks, filters, gene_names, tissues):

    global max_download_n_clicks
    global curr_violin

    if download_n_clicks > max_download_n_clicks:
        max_download_n_clicks = download_n_clicks
                
        if isinstance(tissues, str):
            if isinstance(gene_names, str):
                curr_violin.write_html("./assets/plots/{}_{}_{}_violin.html".format(gene_names, tissues.replace("[", "").replace("]", "").replace("'", ""), filters.replace(" ", "")))
                send_violin = dcc.send_file("./assets/plots/{}_{}_{}_violin.html".format(gene_names, tissues.replace("[", "").replace("]", "").replace("'", ""), filters.replace(" ", "")))
            else:
                genes_str = ""
                for gene in gene_names:
                    genes_str+=gene
                curr_violin.write_html("./assets/plots/{}_{}_{}_violin.html".format(genes_str, tissues.replace("[", "").replace("]", "").replace("'", ""), filters.replace(" ", "")))
                send_violin = dcc.send_file("./assets/plots/{}_{}_{}_violin.html".format(genes_str, tissues.replace("[", "").replace("]", "").replace("'", ""), filters.replace(" ", "")))
        else:
            tissues_str = ""
            for tissue in tissues:
                tissues_str+=tissue
            if isinstance(gene_names, str):
                curr_violin.write_html("./assets/plots/{}_{}_{}_violin.html".format(gene_names, tissues_str, filters.replace(" ", "")))
                send_violin = dcc.send_file("./assets/plots/{}_{}_{}_violin.html".format(gene_names, tissues_str, filters.replace(" ", "")))
            else:
                genes_str = ""
                for gene in gene_names:
                    genes_str+=gene
                curr_violin.write_html("./assets/plots/{}_{}_{}_violin.html".format(genes_str, tissues_str, filters.replace(" ", "")))
                send_violin = dcc.send_file("./assets/plots/{}_{}_{}_violin.html".format(genes_str, tissues_str, filters.replace(" ", "")))
        #no download pie plots for now, the user can download them as png image
        return send_violin

  
@app.callback(
    Output("download-data", "data"),
    Input('download-data-button', 'n_clicks'),
    State('filters_dd', 'value'),
    State('genes_dd', 'value'),
    State('tissues_dd', 'value'),
    prevent_initial_call=True
)
def download_data(download_n_clicks, filters, gene_names, tissues):

    global max_download_data_n_clicks
   

    if download_n_clicks > max_download_data_n_clicks:
        max_download_data_n_clicks = download_n_clicks
        
        if isinstance(tissues, str):
            if isinstance(gene_names, str):
                with open("./assets/data/{}_{}_{}_data.txt".format(gene_names, tissues.replace("[", "").replace("]", "").replace("'", ""), filters.replace(" ", "")), 'w') as f:
                    f.write(curr_data.to_string())
                send_data = dcc.send_file("./assets/data/{}_{}_{}_data.txt".format(gene_names, tissues.replace("[", "").replace("]", "").replace("'", ""), filters.replace(" ", "")))
            else:
                genes_str = ""
                for gene in gene_names:
                    genes_str+=gene
                with open("./assets/data/{}_{}_{}_data.txt".format(genes_str, tissues.replace("[", "").replace("]", "").replace("'", ""), filters.replace(" ", "")), 'w') as f:
                    f.write(curr_data.to_string())
                send_data = dcc.send_file("./assets/data/{}_{}_{}_data.txt".format(genes_str, tissues.replace("[", "").replace("]", "").replace("'", ""), filters.replace(" ", "")))
        else:
            tissues_str = ""
            for tissue in tissues:
                tissues_str+=tissue
            if isinstance(gene_names, str):
                with open("./assets/data/{}_{}_{}_data.txt".format(gene_names, tissues_str, filters.replace(" ", "")), 'w') as f:
                    f.write(curr_data.to_string())
                send_data = dcc.send_file("./assets/data/{}_{}_{}_data.txt".format(gene_names, tissues_str, filters.replace(" ", "")))
            else:
                genes_str = ""
                for gene in gene_names:
                    genes_str+=gene
                with open("./assets/data/{}_{}_{}_data.txt".format(genes_str, tissues_str, filters.replace(" ", "")), 'w') as f:
                    f.write(curr_data.to_string())
                send_data = dcc.send_file("./assets/data/{}_{}_{}_data.txt".format(genes_str, tissues_str, filters.replace(" ", "")))
        return send_data

def single_dd_values_handler(x_range, filters, gene_name, tissue, gencode_id):
    
    global fig_prec_violin 
    global fig_prec_pie
    global fig_prec_ppi
    global prec_table_title
    global prec_table
    global prec_href 
    global prec_gene 
    global prec_tissue 
    global prec_filter 
    global prec_xrange
    global curr_violin
    global curr_fvalue_shapiro
    global curr_pvalue_shapiro
    global curr_data

    table_title = "Anova, Kruskal and Shapiro analysis results for: Gene '{}', Tissue '{}' and Plot by '{}'".format(gene_name, tissue, filters)
    prec_table_title = table_title
    if tissue == "All":
                  
        print("Creating violin plots")
        if filters == "No filters":

            fig_violin, curr_data = plot_by_gene(gencode_id, gene_name)
            hidden1 = False
                
            ys = [fig_violin.data[i]["y"] for i in range(len(fig_violin.data))]
            ys_shapiro = [elem for y in ys for elem in y]
            shapiro_test = stats.shapiro(ys_shapiro)
            fvalue_shapiro = shapiro_test.statistic
            pvalue_shapiro = shapiro_test.pvalue
            curr_fvalue_shapiro = fvalue_shapiro
            curr_pvalue_shapiro = pvalue_shapiro

            y_range = get_current_y_range(x_range, ys)
            x_range_real = [prec_xrange[0]-0.5, prec_xrange[1]+0.5]
            fig_prec_violin.update_layout(xaxis = {'autorange': False, 'range': x_range_real, 'uirevision': True, 'rangeslider': {'autorange': True, 'range': prec_xrange}}, yaxis = {'autorange': False, 'range': y_range})

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
            df = pd.DataFrame([["Anova", fvalue_anova, pvalue_anova], ["Kruskal", fvalue_kruskal, pvalue_kruskal], ["Shapiro", fvalue_shapiro, pvalue_shapiro]], columns = ["", "f_value", "p_value"])
            dict_data = df.to_dict('records')

        elif filters == "Group by Gender":
                        
            fig_violin, curr_data = plot_by_gene_and_gender(gencode_id, gene_name)
            hidden1 = False
                
            ys = [fig_violin.data[i]["y"] for i in range(len(fig_violin.data))]
            y_range = get_current_y_range(x_range, ys)
            x_range_real = [prec_xrange[0]-0.5, prec_xrange[1]+0.5]
            fig_prec_violin.update_layout(xaxis = {'autorange': False, 'range': x_range_real, 'uirevision': True, 'rangeslider': {'autorange': True, 'range': prec_xrange}}, yaxis = {'autorange': False, 'range': y_range})
            ys_shapiro = [elem for y in ys for elem in y]
            shapiro_test = stats.shapiro(ys_shapiro)
            fvalue_shapiro = shapiro_test.statistic
            pvalue_shapiro = shapiro_test.pvalue
            curr_fvalue_shapiro = fvalue_shapiro
            curr_pvalue_shapiro = pvalue_shapiro

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
                
            df = pd.DataFrame([["Anova", fvalue_anova, pvalue_anova], ["Kruskal", fvalue_kruskal, pvalue_kruskal], ["Shapiro", curr_fvalue_shapiro, curr_pvalue_shapiro]], columns = ["", "f_value", "p_value"])
            dict_data = df.to_dict('records')

        else:

            error = "{} is not a valid filter for tissue = {}".format(filters, tissue)
            fig_violin = empty_figure(error, 'red')
            hidden1 = True
            table_title += "Can't compute" 
            prec_table_title = table_title
               
            df = pd.DataFrame([["Anova", "None", "None"], ["Kruskal", "None", "None"], ["Shapiro", "None", "None"]], columns = ["", "f_value", "p_value"])
            dict_data = df.to_dict('records')

        fig_violin.update_layout(xaxis = {'rangeslider': {'visible':False}})
        curr_violin = fig_violin
        fig_prec_violin = fig_violin
        prec_table = dict_data 
           

        print("Creating pie plots")
        #if tissue != prec_tissue:
            #fig_pie = plot_gene_data(gencode_id, gene_name)
        fig_pie = empty_figure("Pie plots not implemented for tissue == All", "red")
        #else:
            #fig_pie = fig_prec_pie
            
        if gene_name != prec_gene:
            print("Changed gene {} -> {}".format(prec_gene, gene_name))
            prec_gene = gene_name 
        if tissue != prec_tissue:
            print("Changed tissue {} -> {}".format(prec_tissue, tissue))
            prec_tissue = tissue 
            if filters != prec_filter:
                print("Changed filter {} -> {}".format(prec_filter, filters))
                prec_filter = filters 

            #print("Returning figures: ", fig_violin, fig_pie)
            fig_prec_pie = fig_pie
            
        return fig_violin, fig_pie, table_title, dict_data, hidden1
                
    else:
                    
        print("Creating violin plots")
        hidden1 = True

        if filters == "No filters":
                
            fig_violin, curr_data = plot_by_gene_and_tissue(gencode_id, gene_name, tissue)
            prec_xrange = [0, 1]
            ys = [fig_violin.data[i]["y"] for i in range(len(fig_violin.data))]
            ys_shapiro = [elem for y in ys for elem in y]
            shapiro_test = stats.shapiro(ys_shapiro)
            fvalue_shapiro = shapiro_test.statistic
            pvalue_shapiro = shapiro_test.pvalue
            curr_fvalue_shapiro = fvalue_shapiro
            curr_pvalue_shapiro = pvalue_shapiro
            df = pd.DataFrame([["Anova", "None", "None"], ["Kruskal", "None", "None"], ["Shapiro", fvalue_shapiro, pvalue_shapiro]], columns = ["", "f_value", "p_value"])
            dict_data = df.to_dict('records')            
            
        elif filters == "Group by Gender":

            fig_violin, curr_data = plot_by_gene_and_gender_and_tissue(gencode_id, gene_name, tissue)
            prec_xrange = [0, 1]
            ys = [fig_violin.data[i]["y"] for i in range(len(fig_violin.data))]
            fvalue_anova, pvalue_anova = stats.f_oneway(ys[0], ys[1])
            fvalue_kruskal, pvalue_kruskal = stats.kruskal(ys[0], ys[1])
            ys_shapiro = [elem for y in ys for elem in y]
            shapiro_test = stats.shapiro(ys_shapiro)
            fvalue_shapiro = shapiro_test.statistic
            pvalue_shapiro = shapiro_test.pvalue
            curr_fvalue_shapiro = fvalue_shapiro
            curr_pvalue_shapiro = pvalue_shapiro
            df = pd.DataFrame([["Anova", fvalue_anova, pvalue_anova], ["Kruskal", fvalue_kruskal, pvalue_kruskal], ["Shapiro", curr_fvalue_shapiro, curr_pvalue_shapiro]], columns = ["", "f_value", "p_value"])
            dict_data = df.to_dict('records')
            
        elif filters == "Group by Age":

            fig_violin, curr_data = plot_by_gene_and_tissue_and_age(gencode_id, gene_name, tissue)
            prec_xrange = [0, 1]
            ys = [fig_violin.data[i]["y"] for i in range(len(fig_violin.data))]
            fvalue_anova, pvalue_anova = stats.f_oneway(ys[0], ys[1], ys[2], ys[3], ys[4])
            fvalue_kruskal, pvalue_kruskal = stats.kruskal(ys[0], ys[1], ys[2], ys[3], ys[4])
            ys_shapiro = [elem for y in ys for elem in y]
            shapiro_test = stats.shapiro(ys_shapiro)
            fvalue_shapiro = shapiro_test.statistic
            pvalue_shapiro = shapiro_test.pvalue
            curr_fvalue_shapiro = fvalue_shapiro
            curr_pvalue_shapiro = pvalue_shapiro
            df = pd.DataFrame([["Anova", fvalue_anova, pvalue_anova], ["Kruskal", fvalue_kruskal, pvalue_kruskal], ["Shapiro", curr_fvalue_shapiro, curr_pvalue_shapiro]], columns = ["", "f_value", "p_value"])
            dict_data = df.to_dict('records')
                        
        else: #"Group by Gender and Age"

            fig_violin, curr_data = plot_by_gene_tissue_age_and_gender(gencode_id, gene_name, tissue)
            prec_xrange = [0, 1]
            ys = [fig_violin.data[i]["y"] for i in range(len(fig_violin.data))]
            fvalue_anova, pvalue_anova = stats.f_oneway(ys[0], ys[1], ys[2], ys[3], ys[4], ys[5], ys[6], ys[7], ys[8], ys[9])
            fvalue_kruskal, pvalue_kruskal = stats.kruskal(ys[0], ys[1], ys[2], ys[3], ys[4], ys[5], ys[6], ys[7], ys[8], ys[9])
            ys_shapiro = [elem for y in ys for elem in y]
            shapiro_test = stats.shapiro(ys_shapiro)
            fvalue_shapiro = shapiro_test.statistic
            pvalue_shapiro = shapiro_test.pvalue
            curr_fvalue_shapiro = fvalue_shapiro
            curr_pvalue_shapiro = pvalue_shapiro
            df = pd.DataFrame([["Anova", fvalue_anova, pvalue_anova], ["Kruskal", fvalue_kruskal, pvalue_kruskal], ["Shapiro", curr_fvalue_shapiro, curr_pvalue_shapiro]], columns = ["", "f_value", "p_value"])
            dict_data = df.to_dict('records')
           
        fig_prec_violin = fig_violin
        curr_violin = fig_violin
        prec_table = dict_data 
        

        if filters != prec_filter:
            print("Changed filter {} -> {}".format(prec_filter, filters))
            prec_filter = filters 

        print("Creating pie plots")
        if gene_name != prec_gene or tissue != prec_tissue:
            print(gencode_id, gene_name, tissue)
            if gene_name != prec_gene:
                print("Changed gene name {} -> {}".format(prec_gene, gene_name))
                prec_gene = gene_name 
            if tissue != prec_tissue:
                print("Changed tissue {} -> {}".format(prec_tissue, tissue))
                prec_tissue = tissue 
            #fig_pie = plot_gene_tissue_data(gencode_id, gene_name, tissue) 
            #fig_prec_pie = fig_pie
            #print("Returing figures ", fig_violin, fig_pie)
                    
        #else:
             
            #print("Returning figures ", fig_violin, fig_prec_pie)

        fig_pie = plot_gene_tissue_data(gencode_id, gene_name, tissue) 
        fig_prec_pie = fig_pie
        return fig_violin, fig_pie, table_title, dict_data, hidden1
           

def multi_dd_values_handler(x_range, filters, gene_name, tissue, gencode_id):

    global fig_prec_violin 
    global fig_prec_pie
    global fig_prec_ppi
    global prec_table_title
    global prec_table
    global prec_href 
    global prec_gene 
    global prec_tissue 
    global prec_filter 
    global prec_xrange
    global curr_violin
    global curr_fvalue_shapiro
    global curr_pvalue_shapiro
    global curr_data 

    table_title = "Anova, Kruskal and Shapiro analysis results for: Gene '{}', Tissue '{}' and Plot by '{}'".format(gene_name, tissue, filters)
    prec_table_title = table_title

    if filters == "No filters":
        
        if isinstance(gene_name, str):
            
            gene_name = gene_name[0]
            hidden1 = True        
            fig_violin, curr_data = multi_tissues_violin_plot(gencode_id, gene_name, tissue)
            fig_prec_violin = fig_violin 
            prec_xrange = [0, 1]
            ys = [fig_violin.data[i]["y"] for i in range(len(fig_violin.data))]
            ys_shapiro = [elem for y in ys for elem in y]
            shapiro_test = stats.shapiro(ys_shapiro)
            fvalue_shapiro = shapiro_test.statistic
            pvalue_shapiro = shapiro_test.pvalue
            curr_fvalue_shapiro = fvalue_shapiro
            curr_pvalue_shapiro = pvalue_shapiro
            table_title = "Multiple tissues selected, Only Shapiro is supported"
            prec_table_title = table_title 
            df = pd.DataFrame([["Anova", "None", "None"], ["Kruskal", "None", "None"], ["Shapiro", fvalue_shapiro, pvalue_shapiro]], columns = ["", "f_value", "p_value"])
            dict_data = df.to_dict('records')         
            fig_pie = empty_figure("Pie plot doesn't support multiple tissues selection.", "red")
            fig_prec_pie = fig_pie
            curr_violin = fig_violin
            return fig_violin, fig_pie, table_title, dict_data, hidden1
        
        else:

            hidden1 = True
            fig_violin, curr_data = multi_genes_violin_plot(gencode_id, gene_name, tissue)
            fig_prec_violin = fig_violin 
            prec_xrange = [0, 1]
            ys = [fig_violin.data[i]["y"] for i in range(len(fig_violin.data))]
            ys_shapiro = [elem for y in ys for elem in y]
            shapiro_test = stats.shapiro(ys_shapiro)
            fvalue_shapiro = shapiro_test.statistic
            pvalue_shapiro = shapiro_test.pvalue
            curr_fvalue_shapiro = fvalue_shapiro
            curr_pvalue_shapiro = pvalue_shapiro
            table_title = "Multiple tissues and Genes selected, Only Shapiro is supported"
            prec_table_title = table_title 
            df = pd.DataFrame([["Anova", "None", "None"], ["Kruskal", "None", "None"], ["Shapiro", fvalue_shapiro, pvalue_shapiro]], columns = ["", "f_value", "p_value"])
            dict_data = df.to_dict('records')         
            fig_pie = empty_figure("Pie plot doesn't support multiple tissues and genes selection.", "red") 
            fig_prec_pie = fig_pie
            curr_violin = fig_violin
            return fig_violin, fig_pie, table_title, dict_data, hidden1
        
    else:
        return fig_prec_violin, fig_prec_pie, prec_table_title, prec_table, True #to change


@app.callback(

    Output("fig-ppi", "figure"),
    Output("ppi-string-link", "href"),
    Output("ensembl-gene-link", "href"),
    
    Input('methods_dd', 'value'), 
    Input('plot-button', 'n_clicks'), 

    State('genes_dd', 'value')
)
def update_ppi_plot(method, n_clicks, gene_name):
    
    global fig_prec_ppi
    global curr_G 
    global prec_gene 
    global prec_href 
    global prec_method
    global prec_href_gene 

    if gene_name != prec_gene:
        
        #prec_gene = gene_name 
        print("Creating PPI network plot")
        prec_gene = gene_name 
        protein_name = gene_name
        gencode_ids = []
        if isinstance(gene_name, list):
            for gene in gene_name:
                gencode_id = get_gencode_id_from_gene_name(gene)
                gencode_id = gencode_id.split(".")[0]
                gencode_ids.append(gencode_id)
            protein_list = protein_name    
            Gs = []

            for i, protein in enumerate(protein_list):
               
                gencode_id = gencode_ids[i]
                G = request_protein_interactions_network([protein])
        
                if G is None:

                    protein_id = ensembl_gene_protein_mapping[gencode_id]
                    G = request_protein_interactions_network([protein_id])
                
                    if G is not None:
                        Gs.append(G)
                else:
                    Gs.append(G)

            if len(Gs)>=2:
                final_G = nx.compose_all(Gs)
            elif len(Gs) == 1:
                final_G = Gs[0]
            else: 
                final_G = None
        elif isinstance(protein_name,str):
            protein_list = [protein_name]
            gencode_id = get_gencode_id_from_gene_name(gene_name)
            gencode_id = gencode_id.split(".")[0]
            
            final_G = request_protein_interactions_network(protein_list)
        
            if final_G is None:

                protein_id = ensembl_gene_protein_mapping[gencode_id]
                final_G = request_protein_interactions_network([protein_id])

        curr_G = final_G 
        href_gene = "http://www.ensembl.org/Homo_sapiens/Gene/Summary?db=core;g={}".format(gencode_id)
        prec_href_gene = href_gene
        if final_G is not None:#TO DO: check if method  != None 
            node_colors = {node: ("green" if node in protein_list else "blue") for node in final_G.nodes}
            nx.set_node_attributes(final_G, node_colors, "color")
            if isinstance(gene_name, list):
                if len(gene_name) == 1:
                    temp_gene_name = gene_name[0]
                else:
                    temp_gene_name = gene_name

            fig_ppi = visualize_network(final_G, color_by = 'color', size_by = 'color', title = "{} Protein - Protein Interaction Network".format(temp_gene_name), layout = "spring_layout")
                         
            href = get_url_string(gene_name)

        else:
            fig_ppi = empty_figure("Cannot create a PPI. Gene {} doens't transcribe for any protein.".format(gene_name), "red")
            href = ""
           
        fig_prec_ppi = fig_ppi
        prec_href = href
        prec_method = "None"
        return fig_ppi, href, href_gene 

    else: #gene not changed

        if method != prec_method:
            prec_method = method
            prec_title = fig_prec_ppi.layout.title.text.split("with")[0].rstrip()          
            print("Updating ppi plot with method ", method)
            if curr_G is not None:
               
                if method == "with_labels":

                    if len(gene_name) == 1:
                        temp_gene_name = gene_name[0]
                    else:
                        temp_gene_name = gene_name
                    fig_ppi = visualize_network(curr_G, color_by = 'color', size_by = 'color', title = "{} Protein - Protein Interaction Network".format(temp_gene_name), layout = "spring_layout", with_labels = True)
                    fig_prec_ppi = fig_ppi
                    return fig_ppi, prec_href, prec_href_gene
                
                elif method != "None":
                   
                    method_to_call = getattr(methods, method)

                    if method == "spectral_clustering":
                        A = nx.adjacency_matrix(curr_G)
                        output = method_to_call(A, list(curr_G.nodes(data=False).keys()))
                    else:
                        output = method_to_call(curr_G)
        
                    nx.set_node_attributes(curr_G, output, "output")

                    if "centrality" in method:
                        fig_ppi = visualize_network(curr_G, color_by = 'output', size_by = None, title = prec_title + " with method {} ".format(method),layout = "spring_layout", size_scale=100)
                    else:
                        fig_ppi = visualize_network(curr_G, color_by = 'output', size_by = None, title = prec_title + " with method {} ".format(method),layout = "spring_layout")
                    fig_prec_ppi = fig_ppi
                    return fig_ppi, prec_href, prec_href_gene

                else:#method None
                    
                    fig_ppi = visualize_network(curr_G, color_by = 'color', size_by = 'color', title = prec_title + " with method {} ".format(method),layout = "spring_layout")
                    fig_prec_ppi = fig_ppi
                    return fig_ppi, prec_href, prec_href_gene
            
            else:#curr_G None
                
                return fig_prec_ppi, "", prec_href_gene #fig_prec_ppi in this case is an error figure: empty figure with red title containing the error
        
        else: #method not changed
           
            return fig_prec_ppi, prec_href, prec_href_gene

@app.callback(

    Output("fig-violin", "figure"),
    Output("fig-pie", "figure"),
    Output("table_title", "children"),
    Output("anova_table", "data"),
    Output("slider-conteiner-1", "hidden"),

    Input('plot-button', 'n_clicks'), 
    Input("rangeslider-1", "value"),

    State('filters_dd', 'value'),
    State('genes_dd', 'value'),
    State('tissues_dd', 'value')

)
def update_plot(n_clicks, x_range, filters, gene_name, tissue):

    global fig_prec_violin 
    global fig_prec_pie
    global fig_prec_ppi
    global prec_table_title
    global prec_table
    global prec_href 
    global prec_gene 
    global prec_tissue 
    global prec_filter 
    global prec_xrange
    global curr_violin
    global curr_fvalue_shapiro
    global curr_pvalue_shapiro
    global curr_data 

    if isinstance(gene_name, str):
        gene_name = gene_name.replace("[", "").replace("]", "").split(",")

    for gene in gene_name:
        if gene not in list(all_genes_dict.keys()):
            
            error = "Gene {} not in supported genes".format(gene_name)
            error_fig = empty_figure(error, "red")
            curr_violin = error_fig
            fig_prec_violin = error_fig
            fig_prec_pie = error_fig
            return error_fig, error_fig, error, prec_table, False #change prec table with table with Nones
    
    if isinstance(tissue, str):
        tissue = tissue.replace("[", "").replace("]", "").split(",")
    
    for t in tissue:
        if t not in all_tissues:
         
            error = "Tissue {} not in supported tissues".format(tissue)
            error_fig = empty_figure(error, "red")
            curr_violin = error_fig
            fig_prec_violin = error_fig
            fig_prec_pie = error_fig
            return error_fig, error_fig, error, prec_table, False

    if filters not in all_filters:
        error = "Filter {} not in supported filters".format(filters)
        error_fig = empty_figure(error, "red")
        curr_violin = error_fig
        fig_prec_violin = error_fig
        fig_prec_pie = error_fig
        return error_fig, error_fig, error, prec_table, False

    if prec_xrange != x_range:
        prec_xrange = x_range
        if x_range[0] == x_range[1]:
             curr_violin = fig_prec_violin
             return fig_prec_violin, fig_prec_pie, prec_table_title, prec_table, False

        print("Setting x_range ", x_range) 
        if fig_prec_violin is not None:
            if prec_tissue == "All":

                y_all = [fig_prec_violin.data[i]["y"] for i in range(len(fig_prec_violin.data))]
                y_range = get_current_y_range(x_range, y_all)
                print("Setting y_range ", y_range)
                x_range_real = [x_range[0]-0.5, x_range[1]+0.5]
                fig_prec_violin.update_layout(xaxis = {'autorange': False, 'range': x_range_real, 'uirevision': True, 'rangeslider': {'autorange': True, 'range': x_range}}, yaxis = {'autorange': False, 'range': y_range})
                curr_violin = fig_prec_violin
                return fig_prec_violin, fig_prec_pie, prec_table_title, prec_table, False
            
    print("Clicked {}, {}, {}".format(gene_name, tissue, filters))
    if gene_name is None:
        gene_name = all_genes_dict.keys()[0]
    if tissue is None:
        tissue = all_tissues[0]
    if filters is None:
        filters = all_filters[0]

    gencode_id = []
    for gene in gene_name:
        gencode_id.append(get_gencode_id_from_gene_name(gene))
    table_title = "Anova, Kruskal and Shapiro analysis results for: Gene '{}', Tissue '{}' and Filter '{}'".format(gene_name, tissue, filters)
    prec_table_title = table_title
    if gene_name != prec_gene or tissue != prec_tissue or filters != prec_filter:
        print("Changed gene name or tissue or filter")
        if len(tissue) == 1 and len(gene_name) == 1:
            print("Single tissue and gene")
            tissue = tissue[0]
            gene_name = gene_name[0]
            gencode_id = gencode_id[0]
            prec_tissue = tissue
            fig_violin, fig_pie, table_title, dict_data, hidden1 = single_dd_values_handler(x_range, filters, gene_name, tissue, gencode_id)
            return  fig_violin, fig_pie, table_title, dict_data, hidden1 
        else:
            print("List of tissues or list of genes")
            fig_violin, fig_pie, table_title, dict_data, hidden1 = multi_dd_values_handler(x_range, filters, gene_name, tissue, gencode_id)
            return  fig_violin, fig_pie, table_title, dict_data, hidden1 
    else:

        print("gencode and tissue and filters not changed")
        if prec_tissue == "All":
            if prec_filter == "No filters":
                hidden1 = False
            elif prec_filter == "Group by Gender":
                hidden1 = False
            else: 
                hidden1 = True
        else:
            hidden1 = True
        return fig_prec_violin, fig_prec_pie, prec_table_title, prec_table, hidden1

if __name__ == "__main__":

    app.run_server(debug=False, dev_tools_hot_reload=False, threaded = True)

#Fix index and columns of returned dataframes 