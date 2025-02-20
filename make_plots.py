"""
*************************************************************************************************************
*                                                                                                           *
*   GTex data visualizer developed by Ugo Lomoio at Magna Graecia University of Catanzaro                   *
*                                                                                                           *
*                                                                                                           *
*************************************************************************************************************
"""

import plotly.graph_objects as go
import requests
from plotly.subplots import make_subplots
import networkx as nx 
import pandas as pd 
import numpy as np 
from pandas import json_normalize
import random 
"""
GTex API requests https://www.gtexportal.org/home/api-docs/
"""
# template = plotly_dark
template = "plotly_white"
line_color = "black"
#line_color = "white"

all_ages = ["20-29", "30-39", "40-49", "50-59", "60-69", "70-79"]
all_genders = ["male", "female"]

colors = ['aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure',
                'beige', 'bisque', 'blanchedalmond', 'blue',
                'blueviolet', 'brown', 'burlywood', 'cadetblue',
                'chartreuse', 'chocolate', 'coral', 'cornflowerblue',
                'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan',
                'darkgoldenrod', 'darkgray', 'darkgrey', 'darkgreen',
                'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange',
                'darkorchid', 'darkred', 'darksalmon', 'darkseagreen',
                'darkslateblue', 'darkslategray', 'darkslategrey',
                'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue',
                'dimgray', 'dimgrey', 'dodgerblue', 'firebrick',
                'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro',
                'ghostwhite', 'gold', 'goldenrod', 'gray', 'grey', 'green',
                'greenyellow', 'honeydew', 'hotpink', 'indianred', 'indigo',
                'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen',
                'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan',
                'lightgoldenrodyellow', 'lightgray', 'lightgrey',
                'lightgreen', 'lightpink', 'lightsalmon', 'lightseagreen',
                'lightskyblue', 'lightslategray', 'lightslategrey',
                'lightsteelblue', 'lightyellow', 'lime', 'limegreen',
                'linen', 'magenta', 'maroon', 'mediumaquamarine',
                'mediumblue', 'mediumorchid', 'mediumpurple',
                'mediumseagreen', 'mediumslateblue', 'mediumspringgreen',
                'mediumturquoise', 'mediumvioletred', 'midnightblue',
                'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'navy',
                'oldlace', 'olive', 'olivedrab', 'orange', 'orangered',
                'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise',
                'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink',
                'plum', 'powderblue', 'purple', 'red', 'rosybrown',
                'royalblue', 'saddlebrown', 'salmon', 'sandybrown',
                'seagreen', 'seashell', 'sienna', 'silver', 'skyblue',
                'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen',
                'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise',
                'violet', 'wheat', 'white', 'whitesmoke', 'yellow',
                'yellowgreen']

all_tissues = ['Adipose_Subcutaneous', 'Adipose_Visceral_Omentum', 'Adrenal_Gland',
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


def request_api_subject_from_age(age):
     
    #age range, for example 60-69
    if age < 20:
        raise Exception("No GTex data for age < 20")
    elif age > 69:
        raise Exception("No GTex data for age > 69")
    elif age >= 20 and age <= 29:
        age = "20-29"
    elif age >= 30 and age <= 39:
        age = "30-39"
    elif age >= 40 and age <= 49:
        age = "40-49"
    elif age >= 50 and age <= 59:
        age = "50-59"
    elif age >= 60 and age <= 69:
        age = "60-69"
    
    results = requests.get("https://gtexportal.org/api/v2/dataset/sample?format=json&datasetId=gtex_v10&ageBracket={}&pageSize=5000".format(age)).json()
    dataframe = json_normalize(results["subject"]) 
    return dataframe

def request_api_subject_from_gender(gender):
    
    if gender == "M":
        gender = "male"
    else: #elif gender == "F"
        gender = "female"
        
    results = requests.get("https://gtexportal.org/api/v2/dataset/sample?format=json&datasetId=gtex_v10&sex={}&pageSize=5000".format(gender)).json()
    dataframe = json_normalize(results["subject"]) 
    return dataframe

def request_api_gene_expression(gene):
    
    #print("https://gtexportal.org/api/v2/expression/geneExpression?datasetId=gtex_v10&gencodeId={}&format=json".format(gene))
    results =  requests.get("https://gtexportal.org/api/v2/expression/geneExpression?datasetId=gtex_v10&gencodeId={}&format=json".format(gene)).json()
    dataframe = pd.DataFrame(results["data"])
    return dataframe

def request_api_subject_from_gender_and_age(gender, age):
    if gender == "M":
        gender = "male"
    else: #elif gender == "F"
        gender = "female"
    df_wanted_age = request_api_subject_from_age(age)
    df = df_wanted_age.loc[df_wanted_age["sex"] == gender]
    df.set_index("subjectId", inplace=True)
    return df

def request_api_gene_expression_with_gender(gene):
    
    #print("https://gtexportal.org/api/v2/expression/geneExpression?datasetId=gtex_v10&gencodeId={}&attributeSubset=sex&format=json".format(gene))
    results =  requests.get("https://gtexportal.org/api/v2/expression/geneExpression?datasetId=gtex_v10&gencodeId={}&attributeSubset=sex&format=json".format(gene)).json()
    dataframe = pd.DataFrame(results["data"])
    return dataframe

def request_api_gene_expression_with_age(gene):
    
    #print("https://gtexportal.org/api/v2/expression/geneExpression?datasetId=gtex_v10&gencodeId={}&attributeSubset=ageBracket&format=json".format(gene))
    results =  requests.get("https://gtexportal.org/api/v2/expression/geneExpression?datasetId=gtex_v10&gencodeId={}&attributeSubset=ageBracket&format=json".format(gene)).json()
    dataframe = pd.DataFrame(results["data"])
    return dataframe

"""
Violin plots
"""

def plot_by_gene_and_gender_and_tissue(gencode_id, gene_name, tissue):

    df = request_api_gene_expression_with_gender(gencode_id)
    fig = go.Figure()
    genders = ["male", "female"]
    data = {gender: [float(elem) for elem in list(df["data"][df['tissueSiteDetailId'] == tissue][df['subsetGroup'] == gender].values[0])] for gender in genders}
    colors = ["cyan", "pink"]
    for i, (gender, data_tissue_gender) in enumerate(data.items()):
         fig.add_trace(go.Violin(x0 = tissue, y=data_tissue_gender, points='outliers', name = gender, box_visible=True,  line_color=line_color, fillcolor = colors[i], meanline_visible=True, opacity=0.8))
    
    fig.update_xaxes(type='category')
    fig.update_layout(violinmode='group', hovermode='x unified', template=template,  yaxis_title="TPM", title= "Violin plot of Gene {} and Tissue {} grouped by gender".format(gene_name, tissue), title_font_size=24, autosize=False,
    width=1500, height=800, legend=dict(font=dict(size= 24)), title_font_color = line_color)
    fig.update_yaxes(title = dict(font=dict(size= 24)))
    fig.update_xaxes(title = dict(font=dict(size= 24)))
    return fig, pd.DataFrame.from_dict(data, orient='index')

def plot_by_gene_and_gender(gencode_id, gene_name):
    
    df = request_api_gene_expression_with_gender(gencode_id)
    print(df)
    fig = go.Figure()
    genders = ["male", "female"]
    tissues = np.unique(list(df["tissueSiteDetailId"]))
    data = {tissue: {gender: [float(elem) for elem in list(df["data"][df['tissueSiteDetailId'] == tissue][df['subsetGroup'] == gender].values[0])] for gender in genders} for tissue in tissues}
    print(data)
    colors = ["cyan", "pink"]
    for i, (tissue, data_tissue) in enumerate(data.items()):
        for j, (gender, data_tissue_gender) in enumerate(data_tissue.items()):
            if i == 0:
                fig.add_trace(go.Violin(x0 = tissue, y=data_tissue_gender, points='outliers', legendgroup=gender, scalegroup=gender, name=gender, box_visible=True,  line_color=line_color, fillcolor = colors[j], meanline_visible=True, opacity=0.8))
            else:
                fig.add_trace(go.Violin(x0 = tissue, y=data_tissue_gender, points='outliers', legendgroup=gender, scalegroup=gender, showlegend=False, box_visible=True,  line_color=line_color, fillcolor = colors[j], meanline_visible=True, opacity=0.8))
    
    fig.update_xaxes(type='category')
    fig.update_layout(violinmode='group', hovermode='x unified', template=template, yaxis_title="TPM", title= "Violin plot of Gene {} grouped by Gender".format(gene_name), title_font_size=24, autosize=False, width=1500, height=800, xaxis=dict(rangeslider=dict(
                     visible=True)), title_font_color = line_color)

    fig.update_yaxes(autorange = True,fixedrange = False, title = dict(font=dict(size= 24)))
    return fig, pd.DataFrame.from_dict(data, orient='index')


def plot_by_gene_and_tissue_and_age(gencode_id, gene_name, tissue):
    
    df = request_api_gene_expression_with_age(gencode_id)
    print(df)
    fig = go.Figure()
    tissues = all_tissues
    ages = np.unique(list(df["subsetGroup"]))
    colors = ["red", "green", "blue", "cyan", "yellow", "orange"]
    #data = {tissue: {age: [float(elem) for elem in list(df['data'][df['tissueSiteDetailId'] == tissue][df['subsetGroup'] == age].values[0])] for age in ages} for tissue in tissues}
    data = {age: [float(elem) for elem in list(df["data"][df['tissueSiteDetailId'] == tissue][df['subsetGroup'] == age].values[0])] for age in ages}
    print(data)
    #for i, (tissue, data_tissue) in enumerate(data.items()):
        #for j, (age, data_tissue_age) in enumerate(data_tissue.items()):
    for j, (age, data_tissue_age) in enumerate(data.items()):
        #if i == 0:
        fig.add_trace(go.Violin(x0 = tissue, y=data_tissue_age, points='outliers', legendgroup=age, scalegroup=age, name=age, box_visible=True,  line_color=line_color, fillcolor = colors[j], meanline_visible=True, opacity=0.8))
        #else:
        #    fig.add_trace(go.Violin(x0 = tissue, y=data_tissue_age, points='outliers', legendgroup=age, scalegroup=age, showlegend=False, box_visible=True,  line_color=line_color, fillcolor = colors[j], meanline_visible=True, opacity=0.8))
    
    fig.update_xaxes(type='category', title = dict(font=dict(size= 24)))
    fig.update_layout(violinmode='group', hovermode='x unified', template=template,  yaxis_title="TPM", title= "Violin plot of Gene {}, Tissue {} grouped by age".format(gene_name, tissue), title_font_size=24, autosize=False, width=1500, height=800, xaxis=dict(rangeslider=dict(visible=True)), legend=dict(font=dict(size= 20)), title_font_color = line_color)
                                                                                                                                                                                                                                                                         
    fig.update_yaxes(autorange = True,fixedrange = False, title = dict(font=dict(size= 24)))
    return fig, pd.DataFrame.from_dict(data, orient='index')

def plot_by_gene(gencode_id, gene_name):
    
    selected_colors = []
    df = request_api_gene_expression(gencode_id)
    tissues = all_tissues
    data = {tissue:[float(elem) for elem in list(df["data"][df['tissueSiteDetailId'] == tissue].values[0])] for tissue in tissues}
    fig = go.Figure()
    for i, (tissue, tissue_data) in enumerate(data.items()):
        while(True):
            color = random.sample(colors, 1)[0]
            if color not in selected_colors:
                selected_colors.append(color)
                break
        fig.add_trace(go.Violin(x0 = tissue, y=tissue_data, points='outliers', name = tissue, box_visible=True,  line_color=line_color, fillcolor = color, meanline_visible=True, opacity=0.8))
    
    fig.update_xaxes(type='category')
    fig.update_layout(template=template, hovermode='x unified', yaxis_title="TPM", title= "Violin plot of Gene {}".format(gene_name), title_font_size=24, autosize=False, width=1500, height=800, xaxis=dict(rangeslider=dict(
                     visible=True)), title_font_color = line_color)
    fig.update_yaxes(title = dict(font=dict(size= 24)))
    return fig, pd.DataFrame.from_dict(data, orient='index')

def plot_by_gene_and_tissue(gene, gene_name, tissue):
    
    df = request_api_gene_expression(gene)
    fig = go.Figure()
    data = [float(elem) for elem in list(df["data"][df['tissueSiteDetailId'] == tissue].values[0])]
    fig.add_trace(go.Violin(x0=tissue, y=data, name=tissue, box_visible=True, line_color=line_color, meanline_visible=True, fillcolor='lightseagreen', points="outliers", opacity=0.8))
    fig.update_layout(template=template, hovermode='x unified', yaxis_title="TPM", title= "Violin plot of Gene {} and Tissue {}".format(gene_name, tissue), title_font_size=24, title_font_color = line_color)
    fig.update_yaxes(title = dict(font=dict(size= 20, color = line_color)))
    return fig, pd.DataFrame.from_dict(data)


def plot_by_gene_and_gender_and_tissue_and_age(gencode_id, gene_name, tissue):
    #maybe create the dataframe here, input gender and gene and tissue
    df = request_api_gene_expression_with_gender(gencode_id)
    fig = go.Figure()
    genders = ["male", "female"]
    ages = ["20-29", "30-39", "40-49", "50-59", "60-69", "70-79"]
    data = {gender: {age: [float(elem) for elem in list(df["data"][df['tissueSiteDetailId'] == tissue][df['subsetGroup'] == gender][df['ageBracket'] == age].values[0])] for age in ages} for gender in genders}
    colors = ["cyan", "pink"]
    for i, (gender, data_tissue_gender) in enumerate(data.items()):
         fig.add_trace(go.Violin(x0 = tissue, y=data_tissue_gender, points='outliers', name = gender, box_visible=True,  line_color=line_color, fillcolor = colors[i], meanline_visible=True, opacity=0.8))
    
    fig.update_xaxes(type='category')
    fig.update_layout(violinmode='group', hovermode='x unified', template=template,  yaxis_title="TPM", title= "Violin plot of Gene {} and Tissue {} grouped by gender".format(gene_name, tissue), autosize=False,
    width=1500, height=800, legend=dict(font=dict(size= 24)), title_font_size=24, title_font_color = line_color)
    fig.update_yaxes(title = dict(font=dict(size= 24)))
    fig.update_xaxes(title = dict(font=dict(size= 24)))
    return fig, pd.DataFrame.from_dict(data, orient='index')

def plot_by_gene_tissue_age_and_gender(gencode_id, gene_name, tissue):

    df_gender = request_api_gene_expression_with_gender(gencode_id)
    df_age = request_api_gene_expression_with_age(gencode_id)
    genders = ["male", "female"]
    ages = ["20-29", "30-39", "40-49", "50-59", "60-69", "70-79"]
    data_gender = {gender: [float(elem) for elem in list(df_gender["data"][df_gender['tissueSiteDetailId'] == tissue][df_gender['subsetGroup'] == gender].values[0])] for gender in genders}
    data_age = {age: [float(elem) for elem in list(df_age["data"][df_age['tissueSiteDetailId'] == tissue][df_age['subsetGroup'] == age].values[0])] for age in ages}
    data = {age: {gender: [float(elem1) for elem1 in data_gender[gender] for elem2 in data_age[age] if elem1 == elem2] for gender in genders} for age in ages}
    
    fig = go.Figure()
    idx = 0
    colors = ["blue", "pink", "cyan", "violet", "green", "red", "orange", "purple", "yellow", "brown", "blue", "magenta"]
    for i, (age, data_age) in enumerate(data.items()):
        for j, (gender, data_age_gender) in enumerate(data_age.items()):

            fig.add_trace(go.Violin(x0 = tissue, y=data_age_gender, points='outliers', name=age+" "+gender, box_visible=True,  line_color=line_color, fillcolor = colors[idx], meanline_visible=True, opacity=0.8))
            idx += 1
    fig.update_xaxes(type='category')
    fig.update_layout(violinmode='group', hovermode='x unified', yaxis_title = "TPM", template=template, title= "Violin plot of Gene {}, Tissue {} grouped by Gender and Age".format(gene_name, tissue),  title_font_size=24, autosize=False, width=1500, height=800, xaxis=dict(rangeslider=dict(
                     visible=True)), legend=dict(font=dict(size= 24)), title_font_color = line_color)
    # fig.update_yaxes(autorange = True,fixedrange = False)
    fig.update_yaxes(title = dict(font=dict(size= 24)))
    fig.update_xaxes(title = dict(font=dict(size= 24)))
    return fig, pd.DataFrame.from_dict(data, orient='index')


#api for pie charts
def request_api_gene_expression_with_tissue_and_death(tissue):
  
    deaths = ["Ventilator%20case", "Fast%20death%20-%20violent", "Fast%20death%20-%20natural%20causes", "Intermediate%20death", "Slow%20death"]
    results = {}
    for death in deaths:
        response = requests.get("https://gtexportal.org/api/v2/dataset/sample?datasetId=gtex_v10&tissueSiteDetailId={}&hardyScale={}&format=json&pageSize=2000&sortBy=sampleId&sortDirection=asc".format(tissue, death)).json()
        results[death.replace("%20", " ")] = len(response["data"])
        #print(results)
    return results

def request_api_gene_expression_with_tissue_and_autolysisScore(tissue):
    
    autolysisScore = ["None", "Mild", "Moderate", "Severe"]
    
    results = {}
    for score in autolysisScore:
        response = requests.get("https://gtexportal.org/api/v2/dataset/sample?datasetId=gtex_v10&tissueSiteDetailId={}&autolysisScore={}&format=json&pageSize=2000&sortBy=sampleId&sortDirection=asc".format(tissue, score)).json()
        #print(2, response)
        results[score] = len(response["data"])
    return results


def request_api_gene_expression_all_tissues_and_death():
  
    deaths = ["Ventilator%20case", "Fast%20death%20-%20violent", "Fast%20death%20-%20natural%20causes", "Intermediate%20death", "Slow%20death"]
    results = {}
    for tissue in all_tissues:
        temp = {}
        for death in deaths:
            response = requests.get("https://gtexportal.org/api/v2/dataset/sample?datasetId=gtex_v10&tissueSiteDetailId={}&hardyScale={}&format=json&pageSize=2000&sortBy=sampleId&sortDirection=asc".format(tissue, death)).json()
            temp[death.replace("%20", " ")] = len(response["data"])
        results[tissue] = temp
        
    return results

def request_api_gene_expression_all_tissues_and_autolysisScore():
    
    autolysisScore = ["None", "Mild", "Moderate", "Severe"]
    
    results = {}
    for tissue in all_tissues:
        temp = {}
        for score in autolysisScore:
            response = requests.get("https://gtexportal.org/api/v2/dataset/sample?datasetId=gtex_v10&tissueSiteDetailId={}&autolysisScore={}&format=json&pageSize=2000&sortBy=sampleId&sortDirection=asc".format(tissue, score)).json()
            temp[score] = len(response["data"])
        results[tissue] = temp
    return results
#pie chart

def plot_gene_tissue_data(gene, gene_name, tissue):
    
    df_genders = request_api_gene_expression_with_gender(gene)
    df_ages = request_api_gene_expression_with_age(gene)

    gender_colors = ["cyan", "pink"]
    genders = ["male", "female"]
    age_colors = ["red", "green", "blue", "cyan", "yellow", "orange"]
    ages = ["20-29", "30-39", "40-49", "50-59", "60-69", "70-79"]
    #scores = ["None", "Mild", "Moderate", "Severe"]
    score_colors = ["red", "green", "blue", "cyan", "yellow", "orange"]
    #deaths = ["Ventilator case", "Fast death - violent", "Fast death - natural causes", "Intermediate death", "Slow death"]
    deaths_colors = ["red", "green", "blue", "cyan", "yellow", "orange"]
    
    data_genders = {gender: [float(elem) for elem in list(df_genders["data"][df_genders['tissueSiteDetailId'] == tissue][df_genders['subsetGroup'] == gender].values[0])] for gender in genders} #.values[0]
    data_ages = {age: [float(elem) for elem in list(df_ages["data"][df_ages['tissueSiteDetailId'] == tissue][df_ages['subsetGroup'] == age].values[0])] for age in ages} #.values[0]
    data_score = request_api_gene_expression_with_tissue_and_autolysisScore(tissue)
    data_deaths = request_api_gene_expression_with_tissue_and_death(tissue)
    
    fig = make_subplots(rows=2, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}], [{'type':'domain'}, {'type':'domain'}]], subplot_titles=['Donors gender', 'Donors age', 'Donors autolysis score', 'Donors death'])
    fig.add_trace(go.Pie(labels=list(data_genders.keys()), values=[len(gender_list) for gender_list in data_genders.values()], marker_colors=gender_colors, name="Gender"),
                  1, 1)
    fig.add_trace(go.Pie(labels=list(data_ages.keys()), values=[len(age_list) for age_list in data_ages.values()], marker_colors=age_colors, name="Age"),
                  1, 2)
    fig.add_trace(go.Pie(labels=list(data_score.keys()), values= list(data_score.values()), marker_colors=score_colors, name="Autolysis score"),
                  2, 1)
    fig.add_trace(go.Pie(labels=list(data_deaths.keys()), values= list(data_deaths.values()), marker_colors=deaths_colors, name="Deaths"),
                  2, 2)
    fig.update_traces(hoverinfo='label+percent', textinfo = 'label')
    fig.update_layout(template=template, hovermode='x unified', title= "Pie charts for Gene {} and Tissue {}".format(gene_name, tissue), autosize=False, width=600, height=800, xaxis =  {                                     
                      'showgrid': False}, yaxis = {'showgrid': True}, showlegend=False, title_font_color = line_color)    
    return fig

def plot_gene_data(gene, gene_name):
    
    df_genders = request_api_gene_expression_with_gender(gene)
    df_ages = request_api_gene_expression_with_age(gene)

    gender_colors = ["cyan", "pink"]
    genders = ["male", "female"]
    age_colors = ["red", "green", "blue", "cyan", "yellow", "orange"]
    ages = ["20-29", "30-39", "40-49", "50-59", "60-69", "70-79"]
    #scores = ["None", "Mild", "Moderate", "Severe"]
    score_colors = ["red", "green", "blue", "cyan", "yellow", "orange"]
    #deaths = ["Ventilator case", "Fast death - violent", "Fast death - natural causes", "Intermediate death", "Slow death"]
    deaths_colors = ["red", "green", "blue", "cyan", "yellow", "orange"]
    
    data_genders = {gender: [float(elem) for elem in list(df_genders["data"][df_genders['subsetGroup'] == gender].values[0])] for gender in genders} #.values[0]
    data_ages = {age: [float(elem) for elem in list(df_ages["data"][df_ages['subsetGroup'] == age].values[0])] for age in ages} #.values[0]
    data_score = request_api_gene_expression_all_tissues_and_autolysisScore()
    data_deaths = request_api_gene_expression_all_tissues_and_death()
    data_tissues = {tissue: len(list(data_tissue)) for tissue, data_tissue in data_score.items()}


    fig = make_subplots(rows=3, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}], [{'type':'domain'}, {'type':'domain'}], [{'type':'domain'}, {'type':'domain'}]], subplot_titles=['Donors gender', 'Donors age', 'Donors autolysis score', 'Donors death'])
    fig.add_trace(go.Pie(labels=list(data_genders.keys()), values=[len(gender_list) for gender_list in data_genders.values()], marker_colors=gender_colors, name="Gender"),
                  1, 1)
    fig.add_trace(go.Pie(labels=list(data_ages.keys()), values=[len(age_list) for age_list in data_ages.values()], marker_colors=age_colors, name="Age"),
                  1, 2)
    fig.add_trace(go.Pie(labels=list(data_score.keys()), values= list(data_score.values()), marker_colors=score_colors, name="Autolysis score"),
                  2, 1)
    fig.add_trace(go.Pie(labels=list(data_deaths.keys()), values= list(data_deaths.values()), marker_colors=deaths_colors, name="Deaths"),
                  2, 2)
    fig.add_trace(go.Pie(labels=list(data_tissues.keys()), values= list(data_tissues.values()), marker_colors=colors, name="Tissues"),
                  3, 1)
    fig.update_traces(hoverinfo='label+percent', textinfo = 'label')
    fig.update_layout(template=template, hovermode='x unified', title= "Pie charts for Gene {} and all tissues".format(gene_name), autosize=False, width=600, height=800, xaxis =  {                                     
                      'showgrid': False}, yaxis = {'showgrid': True}, showlegend=False, title_font_color = line_color)    
    return fig

#PPI plot

def visualize_network(G, color_by = None, size_by = None, title = None, layout = "spring_layout", size_scale=10, with_labels = False):
    """
      Layouts: [graphviz_layout, pydot_layout, bipartite_layout, circular_layout, kamada_kawai_layout, planar_layout, random_layout, rescale_layout,
                spring_layout, spectral_layout, spiral_layout, multipartite_layout] 
      Size_by: "color_by", None, List or "node_attribute" in G.nodes(data=True)
    """
    if title is None:
        title = "Plotly Networkx visualization"

    if color_by not in set(G.nodes(data=True)[list(G.nodes.keys())[0]].keys()) and color_by is not None:
        raise Exception("Attribute Error: '{}' not found in nodes attributes".format(color_by)) #need to change or remove that raise exception
    else:
        if size_by == "color_by":
            size_by = color_by 
    if layout is not None:
        if layout == "graphviz_layout":
            pos = nx.nx_pydot.graphviz_layout(G)
        elif layout == "pydot_layout":
            pos = nx.nx_pydot.pydot_layout(G)
        elif layout == "bipartite_layout":
            top = nx.bipartite.sets(G)[0]
            pos = nx.bipartite_layout(G, top)
        elif layout == "circular_layout":
            pos = nx.circular_layout(G)
        elif layout == "kamada_kawai_layout":
            pos = nx.kamada_kawai_layout(G)
        elif layout == "planar_layout":
            pos = nx.planar_layout(G)
        elif layout == "random_layout":
            pos = nx.random_layout(G)
        elif layout == "rescale_layout":
            pos = nx.rescale_layout(G)
        elif layout == "spring_layout":
            pos = nx.spring_layout(G)
        elif layout == "spectral_layout":
            pos = nx.spectral_layout(G)
        elif layout == "spiral_layout":
            pos = nx.spiral_layout(G)
        elif layout == "multipartite_layout":
            pos = nx.multipartite_layout(G)
        elif isinstance(layout, dict):
            pos = layout

        nx.set_node_attributes(G, pos, "pos")

    edge_x = []
    edge_y = []
    edge_text = []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
        edge_text.append("Edge {} - {}".format(edge[0], edge[1]))

    edge_trace = go.Scatter(
                                  x=edge_x, y=edge_y,
                                  line=dict(width=1.0, color=line_color), #0.5
                                  hoverinfo='text',
                                  text=edge_text,
                                  mode='lines'
                            )

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)
    
    if color_by == "color": #WITH LABELS OR NONE METHODS
        showscale = False
        marker = dict(
                                  showscale=showscale,
                                  color=[],
                                  size=14
                     )
    else:
        showscale = True
        marker = dict(
                                  showscale=showscale,
                                  #colorscale options
                                  #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                                  #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                                  #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                                  colorscale='Rainbow',
                                  reversescale=False,
                                  color=[],
                                  size=14,
                                  colorbar=dict(
                                    thickness=15,
                                    title=color_by,
                                    xanchor='left',
                                    titleside='right'
                                  )
                     )


    node_trace = go.Scatter(
                               x=node_x, y=node_y,
                               mode= "markers",
                               hoverinfo="name+text",
                               marker = marker,
                               line_width=2
                               
                            )
    if color_by is not None:
        node_color = []
        node_size = []
        for node, attributes in G.nodes(data=True):
            value = attributes[color_by]
            node_color.append(value)
            if isinstance(value, str):
                colors_str = [elem[color_by] for elem in list(dict(G.nodes(data=True)).values())]
                map_size_with_color = {elem: i+1 for i, elem in enumerate(np.unique(colors_str))}
                value = map_size_with_color[value]

            if size_by is not None:
                size = value*size_scale
            else: 
                size = 14
            node_size.append(size)
        node_trace.marker.color = node_color
        if size_by is not None:
            node_trace.marker.size = node_size

    annotations = []
    if with_labels:
        for node in G.nodes(data=True):
            annotations.append(
                dict(
                    x=node[1]["pos"][0],
                    y=node[1]["pos"][1],
                    text=node[0], # node name that will be displayed
                    xanchor='left',
                    xshift=10,
                    font=dict(color=line_color, size=18), #14
                    showarrow=False, arrowhead=1, ax=-10, ay=-10
                )
            )
    
    nodes_text = []
    for node, attributes in G.nodes(data=True):
        node_text = "Node: {}\n\n".format(node)
        for attribute_name, value in dict(attributes).items():
            node_text += "{}: {}\n".format(attribute_name, value)
        nodes_text.append(node_text)
    node_trace.text = nodes_text

    #print(annotations)
    fig = go.Figure(data=[edge_trace, node_trace],
                      layout=go.Layout(
                      title=title,
                      title_font_size=24,
                      title_font_color = line_color,
                      #font = {"color ": line_color},
                      showlegend= False,
                      hovermode='closest',
                      margin=dict(b=20,l=5,r=5,t=40),
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), 
                      template=template,
                      autosize=False, 
                      width=900, 
                      height=800,
                      annotations = annotations
                      ),
    )
    return fig

def request_protein_interactions_network(protein_id, threshold=0.4):
    
    string_api_url = "https://version-11-5.string-db.org/api"
    output_format = "tsv-no-header"
    method = "network"
    request_url = "/".join([string_api_url, output_format, method])
    
    params = {

        "identifiers" : "%0d".join(protein_id), # your protein
        "species" : 9606, # species NCBI identifier 
         #"caller_identity" : "test_for_now" # your app name

    }

    response = requests.post(request_url, data=params)
    edgelist = []
    weights = {}

    if "Error" in response.text:
        return None 
    else:
        for line in response.text.strip().split("\n"):

            l = line.strip().split("\t")

            n1, n2 = l[2], l[3]

            ## filter the interaction according to experimental score
            experimental_score = float(l[10])
            if experimental_score > threshold:

                #print("\t".join([n1, n2, "experimentally confirmed (prob. %.3f)" % experimental_score])) 
                edgelist.append([n1, n2])
                weights[(n1, n2)] = experimental_score
            
            G = nx.from_edgelist(edgelist)
    
            for (n1, n2), weight in weights.items():
                 G[n1][n2]['weight'] = weight
        return G

def get_url_string(protein_name):
    
    string_api_url = "https://version-11-5.string-db.org/api"
    output_format = "tsv-no-header"
    method = "get_link"
    request_url = "/".join([string_api_url, output_format, method])
    
    params = {

        "identifiers" : protein_name, # your protein
        "species" : 9606, # species NCBI identifier for HUMAN proteins
        "caller_identity" : "gtex_visualizer" 

    }

    response = requests.post(request_url, data=params).text    
    return response


#multi dropdown tissues plot (up to 20 tissues)

def multi_tissues_violin_plot(gene, gene_name, tissues):
   
    df = request_api_gene_expression(gene)
    limit = 20
    fig = go.Figure()
    unique_tissues = np.unique(tissues)
    selected_colors = []
    for tissue in unique_tissues[:limit]:
        if tissue != "All":
            while(True):
                color = random.sample(colors, 1)[0]
                if color not in selected_colors:
                    selected_colors.append(color)
                    break
            data = [float(elem) for elem in list(df[df['tissueSiteDetailId'] == tissue].values[0])]
            fig.add_trace(go.Violin(x0=tissue, y=data, name=tissue, box_visible=True, line_color=line_color, meanline_visible=True, fillcolor=color, points="outliers", opacity=0.8))
    fig.update_layout(template=template, hovermode='x unified', yaxis_title="TPM", title= "Violin plot of Gene {} and First {} Tissues selected".format(gene_name, limit), autosize=False, width=1500, height=800, xaxis=dict(rangeslider=dict(
                     visible=True)))
    return fig, pd.DataFrame.from_dict({tissue: list(df[df['tissueSiteDetailId'] == tissue].values[0]) for tissue in unique_tissues[:limit]}, orient='index')

#multi dropdown genes plots (up to 2 genes and all tissues)

def multi_genes_violin_plot(genes, genes_name, tissues):

    dfs = {}
    for gene in genes:
        dfs[gene] = request_api_gene_expression(gene)
    
    limit_total = 40
    unique_tissues = np.unique(tissues)
    unique_genes = np.unique(genes)
    unique_genes_name = np.unique(genes_name)
    if len(unique_genes)*len(unique_tissues) > limit_total:
        if len(unique_genes) > 2:
            limit_g = 2
        if len(unique_tissues) > 20:
            limit_t = 20
    else:
        limit_g = len(unique_genes)
        limit_t = len(unique_tissues)

    fig = go.Figure()

    selected_colors = []
    for i, gene in enumerate(unique_genes[:limit_g]): 
        gene_name = unique_genes_name[i]
        for tissue in unique_tissues[:limit_t]:
            if tissue != "All":
                while(True):
                    color = random.sample(colors, 1)[0]
                    if color not in selected_colors:
                        selected_colors.append(color)
                    break
                data = [float(elem) for elem in list(dfs[gene][dfs[gene]['tissueSiteDetailId'] == tissue].values[0])]
                fig.add_trace(go.Violin(x0=tissue, y=data, name="{}_{}".format(gene_name, tissue), box_visible=True, line_color=line_color, meanline_visible=True, fillcolor=color, points="outliers", opacity=0.8))
    fig.update_layout(violinmode='group', hovermode='x unified', template=template, yaxis_title="TPM", title= "Violin plot of First {} Genes and First {} Tissues selected".format(limit_g, limit_t), autosize=False, width=1500, height=800, xaxis=dict(rangeslider=dict(
                     visible=True)))
    return fig, pd.DataFrame.from_dict({gene: {tissue: list(dfs[gene][dfs[gene]['tissueSiteDetailId'] == tissue].values[0]) for tissue in unique_tissues[:limit_t]} for gene in unique_genes[:limit_g]}, orient='index')
