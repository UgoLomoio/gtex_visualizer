"""
*************************************************************************************************************
*                                                                                                           *
*   GTex data visualizer developed by Ugo Lomoio at Magna Graecia University of Catanzaro                   *
*                                                                                                           *
*                           App with Server Side callbacks                                                  *
*                                                                                                           *
*************************************************************************************************************
"""

from dash import html, dcc, Dash 
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import numpy as np 
from make_plots import *


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

all_genes = list(np.loadtxt("all_genes.txt", delimiter = '\t', dtype = '<U41'))

all_filters = ["No filters", "Divide by Gender", "Divide by Age", "Divide by Gender and Age"]

max_n_clicks = 0

def empty_figure(title = "Fill Dropdown menus and press the Update Plot Button"):

    fig = go.FigureWidget()
    fig.update_layout(template="plotly_dark", title=title)
    return fig

fig_prec_violin = empty_figure()
fig_prec_pie = empty_figure()
prec_gene = None
prec_tissue = None
prec_filter = None

app = Dash(__name__)          #create the dash app fist 
server = app.server

app_dash_layout_args = [
            
        html.H1("GTex gene data visualization",  
                    style={'backgroundColor':'rgb(17, 17, 17)', 'color': 'orange'}
                   ),
            
        html.Div(
                
                children = [
                    html.Label("Select a gene:",  
                               style={'backgroundColor':'rgb(17, 17, 17)', 'color': 'white'}),
                    dcc.Dropdown(all_genes, all_genes[0], id='genes_dd',
                                 style={'color': 'black', 'border': '3px solid #ff7300'}
                                )
                ],
                style={'width': '100%', 'display': 'inline-block'}
        ),
            
        html.Div(
                
                children = [
                    html.Label("Select a tissue:", 
                               style={'backgroundColor':'rgb(17, 17, 17)', 'color': 'white'}),
                    dcc.Dropdown(all_tissues, all_tissues[0], id='tissue_dd',  
                                style={'color': 'black', 'border': '3px solid #ff7300'}
                                )
                ],
                style={'width': '100%', 'display': 'inline-block'}
        ),
    
        html.Div(
                
                children = [
                    html.Label("Select a filter:",
                               style={'backgroundColor':'rgb(17, 17, 17)', 'color': 'white'}),
                    dcc.Dropdown(all_filters, all_filters[0], id='filters_dd', 
                                 style={'color': 'black', 'border': '3px solid #ff7300'}
                                )
                ],
                style={'width': '100%', 'display': 'inline-block'}
        ),
    
        dcc.Graph( 
                    id="fig-violin",
                    figure=empty_figure(),
                    animate=False,
                    style={"position": "absolute", "left": "0px", "top": "300px", 
                           'backgroundColor':'rgb(17, 17, 17)', 'color': 'white', 'width': "800px", 'height': '1000px'},
                    config = {'responsive': True, 'displayModeBar': True}

        ),
        dcc.Graph( 
                    id="fig-pie",
                    figure=empty_figure(),
                    animate=False,
                    style={"position": "absolute", "left": "1000px", "top": "300px", 
                           'backgroundColor':'rgb(17, 17, 17)', 'color': 'white', 'width': "800px", 'height': '1000px'},
                    config = {'responsive': True, 'displayModeBar': True}

        ),
    
        html.Button(
                    "Update Plots",
                    id = "plot-button",  
                    n_clicks=0,
                    style={"position": "absolute", "right": "400px", "top": "280px", 'cursor': 'pointer', 'border': '0px', 
                           'border-radius': '3px', 'background-color': 'rgb(31, 24, 252)', 'color': 'white', 'font-size': '12px',
                           'font-family': 'Open Sans', 'width': "100px", 'height': '40px', 'border': '3px solid #ff7300'}
        )
]
app.layout = html.Div(
        app_dash_layout_args,
        style = {'border': '0px', 'backgroundColor':'rgb(17, 17, 17)', 'background-size': '100%', 'position': 'fixed',
                'width': '100%', 'height': '100%', 'overflowX': 'scroll'}
)
    
@app.callback(

    Output("fig-violin", "figure"),
    Output("fig-pie", "figure"),
    
    Input('plot-button', 'n_clicks'), 

    State('filters_dd', 'value'),
    State('genes_dd', 'value'),
    State('tissue_dd', 'value'),

    prevent_initial_call=True
)
def update_plot(n_clicks, filters, gene, tissue):
    #change tissue doesn't work 
    #change gene doesn't work 


    global fig_prec_violin 
    global fig_prec_pie
    global prec_gene 
    global prec_tissue 
    global prec_filter 

    gencode_id, gene_name = gene.split(" ")
    print("Clicked {}, {}, {}".format(gene, tissue, filters))
        
    if gencode_id != prec_gene or tissue != prec_tissue or filters != prec_filter:
            
        print("Changed genecode or tissue or filter")

        if tissue == "All":
              
            print("Creating violin plots")
            if filters == "No filters":

                fig_violin = plot_by_gene(gencode_id, gene_name)

            elif filters == "Divide by Gender":
                    
                fig_violin = plot_by_gene_and_gender(gencode_id, gene_name)

            else:

                error = "{} is not a valid filter for tissue = {}".format(filters, tissue)
                fig_violin = empty_figure(title = error)

            fig_prec_violin = fig_violin

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

            print("Returning figures: ", fig_violin, fig_pie)
            fig_prec_pie = fig_pie
            return fig_violin, fig_pie
            
        else:
                
            print("Creating violin plots")
            if filters == "No filters":

                fig_violin = plot_by_gene_and_tissue(gencode_id, gene_name, tissue)

            elif filters == "Divide by Gender":

                fig_violin = plot_by_gene_and_gender_and_tissue(gencode_id, gene_name, tissue)

            elif filters == "Divide by Age":

                fig_violin = plot_by_gene_and_tissue_and_age(gencode_id, gene_name, tissue)
                    
            else: #"Divide by Gender and Age"

                fig_violin = plot_by_gene_tissue_age_and_gender(gencode_id, gene_name, tissue)

            fig_prec_violin = fig_violin
            
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
                return fig_violin, fig_pie
                
            else:
                print(2)
                print("Returing figures ", fig_violin, fig_prec_pie)
                return fig_violin, fig_prec_pie

    else:

        print("gencode and tissue and filters not changed")
        print("Returing figures")
        return fig_prec_violin, fig_prec_pie

app.run_server(debug=True, dev_tools_hot_reload=False), #threaded = True)