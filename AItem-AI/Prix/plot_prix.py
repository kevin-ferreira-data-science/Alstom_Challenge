# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 09:47:46 2024

@author: anato
"""
#import plotly.io as pio
#pio.renderers.default='browser'
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_prices_file1(file1,df_cluster,df_prices):
    """
    Plot the price history and prediction of file1 and the history of the
    other related files (same category)

    Parameters
    ----------
    file1 : str
        Name of the file for which to plot the price.
    df_cluster : DataFrame
        Dataframe with at least 'Fichier' and 'Cluster'.
    df_prices : DataFrame
        Dataframe with columns 'Date', 'fileA','fileB'(name of the file), ...

    Returns
    -------
    None.

    """
    cluster_of_file1 = df_cluster[df_cluster['Fichier'] == file1]['Cluster'].iloc[0]
    print(cluster_of_file1)
    files_in_that_cluster =  list(df_cluster[df_cluster['Cluster']==cluster_of_file1]['Fichier'])
    files_in_that_cluster.remove(file1)
    # Création de la figure avec un subplot pour les boutons
    fig = make_subplots(rows=2, cols=1, subplot_titles=['Evolution des prix de '+file1+' et sa catégorie'])
    trace_file1 = go.Scatter(x=df_prices['Date'], y=df_prices[file1], mode='lines', name=file1, line=dict(color='blue', width=2))
    fig.add_trace(trace_file1, row=1, col=1)
    for other_file in files_in_that_cluster:
        fig.add_trace(go.Scatter(x=df_prices['Date'], y=df_prices[other_file], mode='lines', name=other_file, line=dict(color='gray', width=1, dash='dash')), row=1, col=1)
    # Création des boutons pour le contrôle des courbes
    visible_update=[True]+[True]*(len(files_in_that_cluster))+ [True, True]
    invisible_update=[True]+[False]*(len(files_in_that_cluster))+ [True, True]
    visible_button = dict(label='Avec sa catégorie', method='update', args=[{'visible': visible_update}])
    invisible_button = dict(label='Sans sa catégorie', method='update', args=[{'visible': invisible_update}])

    # Ajout des boutons au subplot
    fig.update_layout(showlegend=False, updatemenus=[{'type': 'buttons', 'showactive': False, 'buttons': [visible_button, invisible_button]}])

    # Mise en forme du layout
    fig.update_layout(xaxis=dict(title='Date'),
                    yaxis=dict(title='Prix(€)'))
    # Modélisation des données de file1 avec prédiction
    x = np.array(range(len(df_prices['Date'])))
    x = x.reshape(-1, 1)
    y = df_prices[file1].values
    model = LinearRegression().fit(x, y)

    # Prédiction du prochain point pour l'année suivante
    next_year_date = df_prices['Date'].iloc[-1] + pd.DateOffset(years=1)
    next_year_index = len(df_prices['Date'])
    next_year_x = np.array([[next_year_index]])
    next_year_prediction = model.predict(next_year_x)

    # Ajout du tracé de la prédiction en rouge
    fig.add_trace(go.Scatter(x=[next_year_date], y=[next_year_prediction[0]], mode='markers', name='Prédiction',
                             marker=dict(color='red', size=10)))

    # Lier le dernier point bleu avec le point prédit en rouge
    fig.add_trace(go.Scatter(x=[df_prices['Date'].iloc[-1], next_year_date], 
                             y=[df_prices[file1].iloc[-1], next_year_prediction[0]], 
                             mode='lines',
                             line=dict(color='red', width=2)))


    # Affichage du graphique
    fig.show()
    
if __name__ == '__main__':
    pass