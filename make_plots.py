"""
*************************************************************************************************************
*                                                                                                           *
*   GTex data visualizer developed by Ugo Lomoio at Magna Graecia University of Catanzaro   *
*                                                                                                           *
*                                                                                                           *
*************************************************************************************************************
"""

import plotly.graph_objects as go
import requests
from plotly.subplots import make_subplots

import pandas as pd 
import numpy as np 
from pandas import json_normalize

"""
GTex API requests https://www.gtexportal.org/home/api-docs/
"""

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
    
    results = requests.get("http://gtexportal.org/rest/v1/dataset/subject?format=json&datasetId=gtex_v8&ageBracket={}&pageSize=5000".format(age)).json()
    dataframe = json_normalize(results["subject"]) 
    return dataframe

def request_api_subject_from_gender(gender):
    
    if gender == "M":
        gender = "male"
    else: #elif gender == "F"
        gender = "female"
        
    results = requests.get("http://gtexportal.org/rest/v1/dataset/subject?format=json&datasetId=gtex_v8&sex={}&pageSize=5000".format(gender)).json()
    dataframe = json_normalize(results["subject"]) 
    return dataframe

def request_api_gene_expression(gene):
    
    results =  requests.get("http://gtexportal.org/rest/v1/expression/geneExpression?datasetId=gtex_v8&gencodeId={}&format=json".format(gene)).json()
    dataframe = pd.DataFrame(results["geneExpression"])
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
    
    results =  requests.get("http://gtexportal.org/rest/v1/expression/geneExpression?datasetId=gtex_v8&gencodeId={}&attributeSubset=sex&format=json".format(gene)).json()
    dataframe = pd.DataFrame(results["geneExpression"])
    return dataframe

def request_api_gene_expression_with_age(gene):
    
    results =  requests.get("http://gtexportal.org/rest/v1/expression/geneExpression?datasetId=gtex_v8&gencodeId={}&attributeSubset=ageBracket&format=json".format(gene)).json()
    dataframe = pd.DataFrame(results["geneExpression"])
    return dataframe

"""
Violin plots
"""

def plot_by_gene_and_gender_and_tissue(gencode_id, gene_name, tissue):

    df = request_api_gene_expression_with_gender(gencode_id)
    fig = go.FigureWidget()
    genders = ["male", "female"]
    data = {gender: [float(elem) for elem in list(df['data'][df['tissueSiteDetailId'] == tissue][df['subsetGroup'] == gender].values[0])] for gender in genders}
    colors = ["cyan", "pink"]
    for i, (gender, data_tissue_gender) in enumerate(data.items()):
         fig.add_trace(go.Violin(x0 = tissue, y=data_tissue_gender, points='outliers', name = gender, box_visible=True,  line_color='white', fillcolor = colors[i], meanline_visible=True, opacity=0.8))
    
    fig.update_xaxes(type='category')
    fig.update_layout(violinmode='group', hovermode='x unified', template="plotly_dark",  yaxis_title="TPM", title= "Violin plot of Gene {} and Tissue {} divided by gender".format(gene_name, tissue))
    return fig

def plot_by_gene_and_gender(gencode_id, gene_name):
    
    df = request_api_gene_expression_with_gender(gencode_id)
    fig = go.FigureWidget()
    genders = ["male", "female"]
    tissues = np.unique(list(df["tissueSiteDetailId"]))
    data = {tissue: {gender: [float(elem) for elem in list(df['data'][df['tissueSiteDetailId'] == tissue][df['subsetGroup'] == gender].values[0])] for gender in genders} for tissue in tissues}
    colors = ["cyan", "pink"]
    for i, (tissue, data_tissue) in enumerate(data.items()):
        for j, (gender, data_tissue_gender) in enumerate(data_tissue.items()):
            if i == 0:
                fig.add_trace(go.Violin(x0 = tissue, y=data_tissue_gender, points='outliers', legendgroup=gender, scalegroup=gender, name=gender, box_visible=True,  line_color='white', fillcolor = colors[j], meanline_visible=True, opacity=0.8))
            else:
                fig.add_trace(go.Violin(x0 = tissue, y=data_tissue_gender, points='outliers', legendgroup=gender, scalegroup=gender, showlegend=False, box_visible=True,  line_color='white', fillcolor = colors[j], meanline_visible=True, opacity=0.8))
    
    fig.update_xaxes(type='category')
    fig.update_layout(violinmode='group', hovermode='x unified', template="plotly_dark", yaxis_title="TPM", title= "Violin plot of Gene {} divided by Gender".format(gene_name), autosize=False, width=1000, height=1500, xaxis=dict(rangeslider=dict(
                     visible=True)))
    fig.update_yaxes(autorange = True,fixedrange = False)
    return fig  


def plot_by_gene_and_tissue_and_age(gencode_id, gene_name, tissue):
    
    df = request_api_gene_expression_with_age(gencode_id)
    fig = go.FigureWidget()
    tissues = np.unique(list(df["tissueSiteDetailId"]))
    ages = np.unique(list(df["subsetGroup"]))
    colors = ["red", "green", "blue", "cyan", "yellow", "orange"]
    #data = {tissue: {age: [float(elem) for elem in list(df['data'][df['tissueSiteDetailId'] == tissue][df['subsetGroup'] == age].values[0])] for age in ages} for tissue in tissues}
    data = {age: [float(elem) for elem in list(df['data'][df['tissueSiteDetailId'] == tissue][df['subsetGroup'] == age].values[0])] for age in ages}
    
    #for i, (tissue, data_tissue) in enumerate(data.items()):
        #for j, (age, data_tissue_age) in enumerate(data_tissue.items()):
    for j, (age, data_tissue_age) in enumerate(data.items()):
        #if i == 0:
        fig.add_trace(go.Violin(x0 = tissue, y=data_tissue_age, points='outliers', legendgroup=age, scalegroup=age, name=age, box_visible=True,  line_color='white', fillcolor = colors[j], meanline_visible=True, opacity=0.8))
        #else:
        #    fig.add_trace(go.Violin(x0 = tissue, y=data_tissue_age, points='outliers', legendgroup=age, scalegroup=age, showlegend=False, box_visible=True,  line_color='white', fillcolor = colors[j], meanline_visible=True, opacity=0.8))
    
    fig.update_xaxes(type='category')
    fig.update_layout(violinmode='group', hovermode='x unified', template="plotly_dark",  yaxis_title="TPM",  title= "Violin plot of Gene {}, Tissue {} divided by age".format(gene_name, tissue), autosize=False, width=1000, height=1500, xaxis=dict(rangeslider=dict(
                     visible=True)))
    fig.update_yaxes(autorange = True,fixedrange = False)
    return fig

def plot_by_gene(gencode_id, gene_name):
    
    
    df = request_api_gene_expression(gencode_id)
    tissues = np.unique(list(df["tissueSiteDetailId"]))
    data = {tissue:[float(elem) for elem in list(df['data'][df['tissueSiteDetailId'] == tissue].values[0])] for tissue in tissues}
    fig = go.FigureWidget()
    for i, (tissue, tissue_data) in enumerate(data.items()):
        fig.add_trace(go.Violin(x0 = tissue, y=tissue_data, points='outliers', name = tissue, box_visible=True,  line_color='white', fillcolor = colors[i], meanline_visible=True, opacity=0.8))
    
    fig.update_xaxes(type='category')
    fig.update_layout(template="plotly_dark", hovermode='x unified', yaxis_title="TPM", title= "Violin plot of Gene {}".format(gene_name), autosize=False, width=1000, height=1500, xaxis=dict(rangeslider=dict(
                     visible=True)))
    return fig

def plot_by_gene_and_tissue(gene, gene_name, tissue):
    
    df = request_api_gene_expression(gene)
    fig = go.FigureWidget()
    data = [float(elem) for elem in list(df['data'][df['tissueSiteDetailId'] == tissue].values[0])]
    fig.add_trace(go.Violin(x0=tissue, y=data, name=tissue, box_visible=True, line_color='white', meanline_visible=True, fillcolor='lightseagreen', points="outliers", opacity=0.8))
    fig.update_layout(template="plotly_dark", hovermode='x unified', yaxis_title="TPM", title= "Violin plot of Gene {} and Tissue {}".format(gene_name, tissue))
    return fig


def plot_by_gene_and_gender_and_tissue_and_age(gencode_id, gene_name, tissue):
    #maybe create the dataframe here, input gender and gene and tissue
    df = request_api_gene_expression_with_gender(gencode_id)
    fig = go.FigureWidget()
    genders = ["male", "female"]
    ages = ["20-29", "30-39", "40-49", "50-59", "60-69"]
    data = {gender: {age: [float(elem) for elem in list(df['data'][df['tissueSiteDetailId'] == tissue][df['subsetGroup'] == gender][df['ageBracket'] == age].values[0])] for age in ages} for gender in genders}
    colors = ["cyan", "pink"]
    for i, (gender, data_tissue_gender) in enumerate(data.items()):
         fig.add_trace(go.Violin(x0 = tissue, y=data_tissue_gender, points='outliers', name = gender, box_visible=True,  line_color='white', fillcolor = colors[i], meanline_visible=True, opacity=0.8))
    
    fig.update_xaxes(type='category')
    fig.update_layout(violinmode='group', hovermode='x unified', template="plotly_dark",  yaxis_title="TPM", title= "Violin plot of Gene {} and Tissue {} divided by gender".format(gene_name, tissue))
    return fig

def plot_by_gene_tissue_age_and_gender(gencode_id, gene_name, tissue):

    df_gender = request_api_gene_expression_with_gender(gencode_id)
    df_age = request_api_gene_expression_with_age(gencode_id)
    genders = ["male", "female"]
    ages = ["20-29", "30-39", "40-49", "50-59", "60-69"]
    data_gender = {gender: [float(elem) for elem in list(df_gender['data'][df_gender['tissueSiteDetailId'] == tissue][df_gender['subsetGroup'] == gender].values[0])] for gender in genders}
    data_age = {age: [float(elem) for elem in list(df_age['data'][df_age['tissueSiteDetailId'] == tissue][df_age['subsetGroup'] == age].values[0])] for age in ages}
    data_age_gender = {age: {gender: [float(elem1) for elem1 in data_gender[gender] for elem2 in data_age[age] if elem1 == elem2] for gender in genders} for age in ages}
    
    fig = go.FigureWidget()
    idx = 0
    colors = ["blue", "pink", "cyan", "violet", "green", "red", "orange", "purple", "yellow", "brown"]
    for i, (age, data_age) in enumerate(data_age_gender.items()):
        for j, (gender, data_age_gender) in enumerate(data_age.items()):
            fig.add_trace(go.Violin(x0 = tissue, y=data_age_gender, points='outliers', name=age+" "+gender, box_visible=True,  line_color='white', fillcolor = colors[idx], meanline_visible=True, opacity=0.8))
            idx += 1
    fig.update_xaxes(type='category')
    fig.update_layout(violinmode='group', hovermode='x unified', yaxis_title = "TPM", template="plotly_dark", title= "Violin plot of Gene {}, Tissue {} divided by Gender and Age".format(gene_name, tissue), autosize=False, width=1000, height=1500, xaxis=dict(rangeslider=dict(
                     visible=True)))
    # fig.update_yaxes(autorange = True,fixedrange = False)
    return fig  


#api for pie charts
def request_api_gene_expression_with_tissue_and_death(gene, tissue):
  
    deaths = ["Ventilator%20case", "Fast%20death%20-%20violent", "Fast%20death%20-%20natural%20causes", "Intermediate%20death", "Slow%20death"]
    results = {}
    for death in deaths:
        response = requests.get("http://gtexportal.org/rest/v1/dataset/sample?datasetId=gtex_v8&tissueSiteDetailId={}&hardyScale={}&format=json&pageSize=2000&sortBy=sampleId&sortDirection=asc".format(tissue, death)).json()
        results[death.replace("%20", " ")] = response["recordsFiltered"]
    return results

def request_api_gene_expression_with_tissue_and_autolysisScore(gene, tissue):
    
    autolysisScore = ["None", "Mild", "Moderate", "Severe"]
    
    results = {}
    for score in autolysisScore:
        response = requests.get("http://gtexportal.org/rest/v1/dataset/sample?datasetId=gtex_v8&tissueSiteDetailId={}&autolysisScore={}&format=json&pageSize=2000&sortBy=sampleId&sortDirection=asc".format(tissue, score)).json()
        results[score] = response["recordsFiltered"]
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
    
    data_genders = {gender: [float(elem) for elem in list(df_genders['data'][df_genders['tissueSiteDetailId'] == tissue][df_genders['subsetGroup'] == gender].values[0])] for gender in genders}
    data_ages = {age: [float(elem) for elem in list(df_ages['data'][df_ages['tissueSiteDetailId'] == tissue][df_ages['subsetGroup'] == age].values[0])] for age in ages}
    data_score = request_api_gene_expression_with_tissue_and_autolysisScore(gene, tissue)
    data_deaths = request_api_gene_expression_with_tissue_and_death(gene, tissue)
    
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
    fig.update_layout(template="plotly_dark", hovermode='x unified', title= "Pie charts for Gene {} and Tissue {}".format(gene_name, tissue), xaxis =  {                                     
                      'showgrid': False}, yaxis = {'showgrid': True}, showlegend=False)    
    return fig