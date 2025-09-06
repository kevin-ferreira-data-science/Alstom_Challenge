from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pandas as pd
import cadquery as cq
import os

def build_df(folder):

    # Initialisation d'une liste pour stocker les données
    data = []

    # Parcourir tous les fichiers dans le dossier
    for fichier in os.listdir(folder):
        if fichier.endswith(".stp") or fichier.endswith(".step"):
            path_to_stp_file = os.path.join(folder, fichier)
            try:
                # Charger le modèle 3D à partir du fichier STEP
                model = cq.importers.importStep(path_to_stp_file)
                shape = model.val()

                # Extraire les caractéristiques
                volume = shape.Volume()
                surface = shape.Area()
                bbox = shape.BoundingBox()
                longueur, largeur, hauteur = bbox.xlen, bbox.ylen, bbox.zlen
                faces = len(shape.Faces())
                aretes = len(shape.Edges())
                sommets = len(shape.Vertices())

                # Ajouter au DataFrame
                data.append({
                    "Fichier": fichier,
                    "Vol": volume,
                    "Surf": surface,
                    "Lng_BBox": longueur,
                    "Lrg_BBox": largeur,
                    "Ht_BBox": hauteur,
                    "Faces": faces,
                    "Aretes": aretes,
                    "Sommets": sommets
                })
            except Exception as e:
                print(f"Erreur lors du traitement du fichier {fichier}: {e}")

    # Créer un DataFrame à partir des données
    df = pd.DataFrame(data)
    return df


def scaler_transform(df_entry):
       
    # Centrer réduire :
    scaler = StandardScaler()

    scaler.fit(df_entry)
    data_pieces_scaler = scaler.transform(df_entry)

    # Constructeur ACP
    mypca = PCA()
    mypca.fit(data_pieces_scaler)
    
    # Utilisation de l'ACP pour réduire la dimension
    data_pieces_pca = mypca.transform(data_pieces_scaler)
    
    return data_pieces_pca
    


def clustering(df_entry):
    
    df_entry_copy = df_entry.copy()
    df_entry_copy.set_index("Fichier", inplace=True) # on garde que les valeurs quantitatives continues
    
    data_pieces_pca = scaler_transform(df_entry_copy)
    
    # Utilisation de DBSCAN pour le clustering
    # espilon = distance max entre 2 pts
    # Plus on augmente epsilon, moins les clusters sont sensibles aux bruits
    # dbscan = DBSCAN(eps=0.5, min_samples= 2)
    dbscan = DBSCAN(eps=.9, min_samples= 2) 
    clusters = dbscan.fit_predict(data_pieces_pca)
    # NB: Cluster "-1" contient les bruits

    # Ajout des informations de clustering aux données d'origine
    df_entry_copy['Cluster'] = clusters
    df_return = df_entry_copy.reset_index()

    return df_return


def plot_dataframe(df_entry):
    #df_entry = df_entry.select_dtypes(include=['float64', 'int64'])
    data_pca = scaler_transform(df_entry)

    colors = px.colors.qualitative.swatches()

    # Création d'une figure interactive en 3D avec Plotly Express
    fig = px.scatter_3d(df_entry, x=data_pca[:, 0], y=data_pca[:, 1], z=data_pca[:, 2],
                        color='Cluster', opacity=0.8, size_max=20,
                        title='Clusters obtenus par DBSCAN après normalisation',
                        color_discrete_sequence=colors,
                        hover_data={'Cluster': True, 'Fichier': True})
    # Affichage de la figure interactive
    fig.show() # ou return fig et tu fais un plot_dataframe(df_entry).show() sur ta page web

if __name__ == '__main__':
    example_prices = {}
    df = build_df('../3D')
    df_cluster=clustering(df)
    print(df_cluster[['Fichier','Cluster']])
    print(df_cluster['Cluster'].unique())
    for cluster in df_cluster['Cluster'].unique():
        files_in_that_cluster =  df_cluster[df_cluster['Cluster']==cluster]['Fichier'].unique()
        print(files_in_that_cluster)
        