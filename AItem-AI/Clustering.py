from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np
from sklearn.neighbors import NearestNeighbors
import pandas as pd
import plotly.graph_objects as go
from OCC.Display.SimpleGui import init_display
from OCC.Extend.DataExchange import read_step_file
import pythreejs as p3js
import cadquery as cq
from sklearn.metrics import silhouette_score

def scale_and_pca(data):
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)

    pca = PCA()
    data_pca = pca.fit_transform(data_scaled)

    return data_pca, scaler, pca

def scaler_transform(df_entry):
    # Exclure les colonnes non numériques
    numeric_columns = df_entry.select_dtypes(include=[np.number]).columns
    df_numeric = df_entry[numeric_columns]

    # Centrer et réduire :
    scaler = StandardScaler()
    data_pieces_scaler = scaler.fit_transform(df_numeric)

    # Constructeur ACP
    mypca = PCA()
    mypca.fit(data_pieces_scaler)
    
    # Utilisation de l'ACP pour réduire la dimension
    data_pieces_pca = mypca.transform(data_pieces_scaler)
    
    return data_pieces_pca

    
def clustering_dbscan(df_entry, eps, min_samples):
    df_copy = df_entry.copy()
    df_copy.set_index("Fichier", inplace=True)

    data_pca, _, _ = scale_and_pca(df_copy)

    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = dbscan.fit_predict(data_pca)

    df_copy['Cluster'] = clusters
    df_return = df_copy.reset_index()

    return df_return


def nearest_neighbor(df_entry, nom_fichier):
    df_entry_copy = df_entry.copy()
    df_entry_copy.set_index("Fichier", inplace=True)

    # Centrer réduire :
    scaler = StandardScaler()
    scaler.fit(df_entry_copy)
    data_pieces_scaler = scaler.transform(df_entry_copy)

    # Constructeur ACP
    mypca = PCA()
    mypca.fit(data_pieces_scaler)

    # Utilisation de l'ACP pour réduire la dimension
    data_pieces_pca = mypca.transform(data_pieces_scaler)

    # Utilisation de NearestNeighbors pour trouver le voisin le plus proche
    neighbors_model = NearestNeighbors(n_neighbors=2)  # Considering the current point itself
    neighbors_model.fit(data_pieces_pca)

    # Trouver les indices et distances des voisins les plus proches
    distances, indices = neighbors_model.kneighbors(data_pieces_pca)

    # Trouver l'index du voisin le plus proche (éviter le premier index qui est l'élément lui-même)
    neighbor_index = indices[df_entry_copy.index == nom_fichier, 1][0]

    # Retourner la ligne du dataframe correspondant au voisin le plus proche
    return df_entry_copy.iloc[neighbor_index]


def plot_original_and_neighbor(df_pieces, nom_piece, df_clustered, neighbors_df):
    # Extraire les informations de la pièce initiale
    piece_initiale = df_pieces[df_pieces['Fichier'] == nom_piece]

    # Extraire le cluster de la pièce initiale
    cluster_piece_initiale = df_clustered[df_clustered['Fichier'] == nom_piece]['Cluster'].values[0]

    # Extraire le voisin le plus proche de la pièce initiale
    voisin = neighbors_df.iloc[0]

    # Convertir les valeurs numpy.float64 en float
    x_piece_initiale = float(piece_initiale['Lng_BBox'])
    y_piece_initiale = float(piece_initiale['Lrg_BBox'])
    z_piece_initiale = float(piece_initiale['Hauteur_BBox'])

    x_voisin = float(voisin['Lng_BBox'])
    y_voisin = float(voisin['Lrg_BBox'])
    z_voisin = float(voisin['Hauteur_BBox'])

    # Créer une figure 3D
    fig = go.Figure()

    # Ajouter la pièce initiale au graphe
    fig.add_trace(go.Scatter3d(
        x=[x_piece_initiale],
        y=[y_piece_initiale],
        z=[z_piece_initiale],
        mode='markers',
        marker=dict(size=10, color='blue'),
        name='Pièce Initiale'
    ))

    # Ajouter le voisin au graphe
    fig.add_trace(go.Scatter3d(
        x=[x_voisin],
        y=[y_voisin],
        z=[z_voisin],
        mode='markers',
        marker=dict(size=10, color='red'),
        name='Voisin'
    ))

    # Définir le layout
    fig.update_layout(
        scene=dict(
            xaxis_title='Longueur BBox',
            yaxis_title='Largeur BBox',
            zaxis_title='Hauteur BBox',
        ),
        title=f'Pièce Initiale et Voisin - Cluster {cluster_piece_initiale}',
    )

    # Afficher la figure
    fig.show()
    return None

# def generate_html_with_3d_viewer(file_path):
#     # Charger le modèle 3D à partir du fichier STEP
#     model = cq.importers.importStep(file_path)
#     shape = model.val()

#     # Exporter la forme pour obtenir les points
#     exported_shape = shape.exportStep("AR00000244409.stp")

#     # Convertir le modèle 3D en format JSON compatible avec pythreejs
#     geo = p3js.BufferGeometry.from_geometry(p3js.BoxGeometry(1, 1, 1))
    
#     # Utiliser les points exportés pour définir les attributs de position
#     geo.attributes["position"].array = np.array(exported_shape.vertices()).flatten()

#     # Créer un objet Mesh
#     mesh = p3js.Mesh(geo, p3js.MeshStandardMaterial(color="blue"))

#     # Créer la scène et y ajouter le mesh
#     scene = p3js.Scene(children=[mesh])

#     # Créer une caméra
#     camera = p3js.PerspectiveCamera(position=[5, 5, 5])

#     # Créer un widget pour le rendu 3D
#     renderer = p3js.Renderer(scene=scene, camera=camera)

#     # Ajouter des contrôles pour interagir avec la scène
#     controls = p3js.OrbitControls(controlling=camera)
#     renderer.controls = [controls]

#     # Générer le code HTML
#     html_content = p3js.to_html(renderer)

#     # Écrire le code HTML dans un fichier
#     with open('viewer.html', 'w') as f:
#         f.write(html_content)

def plot_dataframe(df_entry):
    
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

@staticmethod
def elbow_method(df_entry, k_range=range(1, 11)):
    # Méthode du coude pour trouver une valeur pertinente pour epsilon

    # Sélectionner uniquement les colonnes numériques
    numeric_columns = df_entry.select_dtypes(include=[np.number]).columns
    df_numeric = df_entry[numeric_columns]

    # Appliquer la mise à l'échelle et l'ACP
    data_pca, _, _ = scale_and_pca(df_numeric)

    # Calculer la distance moyenne des k-voisins pour différentes valeurs de k
    neighbors = NearestNeighbors(n_neighbors=max(k_range) + 1)
    neighbors.fit(data_pca)
    distances, _ = neighbors.kneighbors(data_pca)

    # Calculer la distance moyenne des k-voisins pour chaque point
    avg_distances = np.mean(distances[:, 1:], axis=1)

    # Tracer la courbe
    plt.plot(list(k_range), avg_distances, marker='o')  # Convertir k_range en liste
    plt.title('Elbow Method for Optimal Epsilon')
    plt.xlabel('Number of Neighbors (k)')
    plt.ylabel('Average Distance')
    plt.show()

@staticmethod
def evaluate_clusters(data_pca, clusters):
    # Utiliser l'indice de silhouette pour évaluer la qualité des clusters
    silhouette_avg = silhouette_score(data_pca, clusters)
    print(f"Silhouette Score: {silhouette_avg}")

################ tests ################
# IMPORT DES PIECES DANS UN DF
import os
import pandas as pd
import cadquery as cq

# Chemin vers le dossier contenant les fichiers STEP
dossier_stp = "C:/Users/kevin/OneDrive - LECNAM/CNAM - onedrive/Alstom/AItem-AI/3D"
# print(os.getcwd())
# Initialisation d'une liste pour stocker les données
data = []

# Parcourir tous les fichiers dans le dossier
for fichier in os.listdir(dossier_stp):
    if fichier.endswith(".stp") or fichier.endswith(".step"):
        path_to_stp_file = os.path.join(dossier_stp, fichier)

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
                "Volume": volume,
                "Surface": surface,
                "Lng_BBox": longueur,
                "Lrg_BBox": largeur,
                "Hauteur_BBox": hauteur,
                "Faces": faces,
                "Aretes": aretes,
                "Sommets": sommets
            })
        except Exception as e:
            print(f"Erreur lors du traitement du fichier {fichier}: {e}")

# Créer un DataFrame à partir des données
df_pieces = pd.DataFrame(data)
#########FIN IMPORT

# Tester la fonction de clustering
# df_clustered = clustering(df_pieces)
# print("DataFrame après clustering:")
# print(df_clustered)

# # Tester la fonction de tracé
# plot_dataframe(df_clustered)

# # Tester la fonction de recherche du voisin le plus proche
# nom_fichier_a_chercher = 'AR00000244409.stp'
# nearest_neighbor_result = nearest_neighbor(df_pieces, nom_fichier_a_chercher)
# print(f"Voisin le plus proche de {nom_fichier_a_chercher}:")
# print(nearest_neighbor_result)

# Tester l'affichage dans un plot 3D de la pièce initiale et de son voisin
# nom_fichier_a_chercher = 'AR00000244409.stp'
# nom_fichier_a_chercher_2 = 'AR00000233649--D.stp'

# neighbors_df = nearest_neighbor(df_pieces, nom_fichier_a_chercher)
# neighbors_df_2 = nearest_neighbor(df_pieces, nom_fichier_a_chercher_2)
# print(neighbors_df)
# print("----------------\n")
# print(neighbors_df_2)
# plot_original_and_neighbor(df_pieces, nom_fichier_a_chercher, df_clustered, neighbors_df)


# elbow_method(df_pieces)

# Appel de la fonction clustering pour obtenir des clusters avec un epsilon choisi
optimal_epsilon = 0.1  # Remplacez par la valeur que vous avez trouvée avec la méthode du coude
optimal_min_samples = 2
df_result = clustering_dbscan(df_pieces, eps=optimal_epsilon, min_samples=optimal_min_samples)

plot_dataframe(df_result)

# Appel de la fonction evaluate_clusters pour évaluer les clusters obtenus
# data_pca, _, _ = scale_and_pca(df_result.drop('categorie', axis=1))
# evaluate_clusters(data_pca, df_result['categorie'])

