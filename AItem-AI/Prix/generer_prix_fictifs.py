import csv
import plotly.io as pio
pio.renderers.default='browser'
import pandas as pd
import random
import os
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta
from clustering import build_df, clustering
import plotly.graph_objects as go
from plotly.subplots import make_subplots
print(os.getcwd())

def generate_yearly_realistic_price_data(start_year, end_year, initial_price=100, trend_factor=0.02, volatility_factor=0.05):
    date_range = [datetime(year,1,1) for year in range(start_year, end_year+1)]
    prices = [initial_price]
    for i in range(1, end_year-start_year+1):
        previous_price = prices[i-1]
        
        # Appliquer une tendance générale
        trend = previous_price * trend_factor
        if random.random() > 0.5:
            trend *= -1  # 50% de chance de tendance à la baisse
        
        # Appliquer des fluctuations aléatoires
        volatility = previous_price * volatility_factor * random.uniform(0, 1)
        price_change = trend + volatility
        
        new_price = round(previous_price + price_change, 2)
        prices.append(new_price)
        data = [date_range, prices]

    return data

def generate_prices(start_year,end_year,models_dir,csv_name='prices.csv'):
    example_prices = {'Date':[]}
    df = build_df(models_dir)
    df['Fichier'] = df['Fichier'].str.replace('.stp', '')
    df_cluster=clustering(df)
    
    
    for cluster in df_cluster['Cluster'].unique():
        files_in_that_cluster =  df_cluster[df_cluster['Cluster']==cluster]['Fichier'].unique()
        # Générer les données de prix
        cluster_trend=random.uniform(0.01, 0.05)
        cluster_volatility=random.uniform(0.01, 0.1)
        for file in files_in_that_cluster:
            price_data = generate_yearly_realistic_price_data(start_year, end_year, 
                                    initial_price=round(random.uniform(50, 150), 2),
                                    trend_factor=cluster_trend,
                                    volatility_factor=cluster_volatility
                                    )
            example_prices[file]=price_data[1]
    example_prices['Date']=price_data[0]        
    df_prices=pd.DataFrame(example_prices)
    csv_file_name = 'prices.csv'
    df_prices.to_csv(csv_file_name)
    print(f"Les données ont été écrites dans le fichier CSV : {csv_file_name}")
    
if __name__ == '__main__':
    pass
    # Définir la période de temps et le nombre d'enregistrements
    # start_year = 2010
    # end_year = 2023
    # print(generate_yearly_realistic_price_data(2029,2030))
    # example_prices = {'Date':[]}
    # df = build_df('../3D')
    # df_cluster=clustering(df)
    # print(df_cluster[['Fichier','Cluster']])
    # print(df_cluster['Cluster'].unique())
    # for cluster in df_cluster['Cluster'].unique():
    #     files_in_that_cluster =  df_cluster[df_cluster['Cluster']==cluster]['Fichier'].unique()
    #     print(files_in_that_cluster)
    #     # Générer les données de prix
    #     cluster_trend=random.uniform(0.01, 0.05)
    #     cluster_volatility=random.uniform(0.01, 0.1)
    #     for file in files_in_that_cluster:
    #         price_data = generate_yearly_realistic_price_data(start_year, end_year, 
    #                                 initial_price=round(random.uniform(50, 150), 2),
    #                                 trend_factor=cluster_trend,
    #                                 volatility_factor=cluster_volatility
    #                                 )
    #         example_prices[file]=price_data[1]
    # example_prices['Date']=price_data[0]        
    # df_prices=pd.DataFrame(example_prices)
    # csv_file_name = 'prices.csv'
    # df_prices.to_csv(csv_file_name)
    # print(f"Les données ont été écrites dans le fichier CSV : {csv_file_name}")

    #Plot un fichier avec les autres de sa classe grisés
    # file1=df_cluster['Fichier'].iloc[13]
    # def plot_prices_file1(file1,df_cluster,df_prices):
    #     """
    #     Plot the price history and prediction of file1 and the history of the
    #     other related files (same category)

    #     Parameters
    #     ----------
    #     file1 : str
    #         Name of the file for which to plot the price.
    #     df_cluster : DataFrame
    #         Dataframe with at least 'Fichier' and 'Cluster'.
    #     df_prices : DataFrame
    #         Dataframe with columns 'Date', 'fileA','fileB'(name of the file), ...

    #     Returns
    #     -------
    #     None.

    #     """
    #     cluster_of_file1 = df_cluster[df_cluster['Fichier'] == file1]['Cluster'].iloc[0]
    #     print(cluster_of_file1)
    #     files_in_that_cluster =  list(df_cluster[df_cluster['Cluster']==cluster_of_file1]['Fichier'])
    #     files_in_that_cluster.remove(file1)
    #     # Création de la figure avec un subplot pour les boutons
    #     fig = make_subplots(rows=2, cols=1, subplot_titles=['Evolution des prix de '+file1+' et sa catégorie'])
    #     trace_file1 = go.Scatter(x=df_prices['Date'], y=df_prices[file1], mode='lines', name=file1, line=dict(color='blue', width=2))
    #     fig.add_trace(trace_file1, row=1, col=1)
    #     for other_file in files_in_that_cluster:
    #         fig.add_trace(go.Scatter(x=df_prices['Date'], y=df_prices[other_file], mode='lines', name=other_file, line=dict(color='gray', width=1, dash='dash')), row=1, col=1)
    #     # Création des boutons pour le contrôle des courbes
    #     visible_update=[True]+[True]*(len(files_in_that_cluster))+ [True, True]
    #     invisible_update=[True]+[False]*(len(files_in_that_cluster))+ [True, True]
    #     visible_button = dict(label='Avec sa catégorie', method='update', args=[{'visible': visible_update}])
    #     invisible_button = dict(label='Sans sa catégorie', method='update', args=[{'visible': invisible_update}])
    
    #     # Ajout des boutons au subplot
    #     fig.update_layout(showlegend=False, updatemenus=[{'type': 'buttons', 'showactive': False, 'buttons': [visible_button, invisible_button]}])
    
    #     # Mise en forme du layout
    #     fig.update_layout(xaxis=dict(title='Date'),
    #                     yaxis=dict(title='Prix(€)'))
    #     # Modélisation des données de file1 avec prédiction
    #     x = np.array(range(len(df_prices['Date'])))
    #     x = x.reshape(-1, 1)
    #     y = df_prices[file1].values
    #     model = LinearRegression().fit(x, y)
    
    #     # Prédiction du prochain point pour l'année suivante
    #     next_year_date = df_prices['Date'].iloc[-1] + pd.DateOffset(years=1)
    #     next_year_index = len(df_prices['Date'])
    #     next_year_x = np.array([[next_year_index]])
    #     next_year_prediction = model.predict(next_year_x)
    
    #     # Ajout du tracé de la prédiction en rouge
    #     fig.add_trace(go.Scatter(x=[next_year_date], y=[next_year_prediction[0]], mode='markers', name='Prédiction',
    #                              marker=dict(color='red', size=10)))
    
    #     # Lier le dernier point bleu avec le point prédit en rouge
    #     fig.add_trace(go.Scatter(x=[df_prices['Date'].iloc[-1], next_year_date], 
    #                              y=[df_prices[file1].iloc[-1], next_year_prediction[0]], 
    #                              mode='lines',
    #                              line=dict(color='red', width=2)))

    
    #     # Affichage du graphique
    #     fig.show()
    
    # plot_prices_file1(file1,df_cluster,df_prices)
