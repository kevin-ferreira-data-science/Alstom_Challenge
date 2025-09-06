import cadquery as cq
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
from plotly.subplots import make_subplots
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from sklearn.cluster import DBSCAN
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import KMeans


class AItools:
    def __init__(self):
        # Initialisation des modèles, des outils de visualisation 3D, etc.
        pass

    @staticmethod
    def clustering_selector(df_entry, type_clusterisation=1, epsilon=.1, echantillon_min=2, num_clusters=3):
        
        if type_clusterisation == 1:
            df_return = AItools.clustering_dbscan(df_entry, epsilon, echantillon_min)
            
        elif type_clusterisation == 2:
            df_return = AItools.clustering_propagation(df_entry)
            
        elif type_clusterisation == 3:
            df_return = AItools.clustering_kmeans(df_entry, num_clusters)
    
        return df_return
    
    @staticmethod
    def clustering_dbscan(df_entry, epsilon, echantillon_min):
        df_copy = df_entry.copy()
        df_copy.set_index("nom", inplace=True)
        data_pca, _, _ = AItools.scale_and_pca(df_copy)
        dbscan = DBSCAN(eps=epsilon, min_samples= echantillon_min)
        clusters = dbscan.fit_predict(data_pca)
        df_copy['categorie'] = clusters
        df_return = df_copy.reset_index()
        
        return df_return
    
    @staticmethod
    def clustering_propagation(df_entry):
        df_return = df_entry.copy()
        df_return.set_index("nom", inplace=True)
        # Normaliser
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df_return)
        # Appliquer Affinity Propagation
        af = AffinityPropagation()
        cluster_labels = af.fit_predict(scaled_data)
        # Ajouter les étiquettes de cluster au DataFrame
        df_return['categorie'] = cluster_labels
        df_return = df_return.reset_index()
        return df_return
    
    @staticmethod
    def clustering_kmeans(df_entry, num_clusters):
        """
        Effectue la clusterisation K-means sur un DataFrame pandas.

        Args:
        - df (pd.DataFrame): Le DataFrame d'entrée.
        - num_clusters (int): Le nombre de clusters souhaités.

        Returns:
        - df_with_clusters (pd.DataFrame): Le DataFrame d'entrée avec une colonne 'clusters' ajoutée.
        """
        df_return = df_entry.copy()
        df_return.set_index("nom", inplace=True)
        
        # Créer un objet KMeans avec le nombre de clusters spécifié
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)

        # Sélectionner les colonnes numériques du DataFrame pour la clusterisation
        numeric_columns = df_return.select_dtypes(include=[np.number])

        # Adapter le modèle aux données
        kmeans.fit(numeric_columns)

        # Obtenir les étiquettes de cluster pour chaque ligne du DataFrame
        cluster_labels = kmeans.labels_
        
        df_return['categorie'] = cluster_labels
        df_return = df_return.reset_index()
        
        return df_return

    @staticmethod
    def plot_prices_file1(file1, df_cluster, df_prices):
        cluster_of_file1 = df_cluster[df_cluster['nom'] == file1]['categorie'].iloc[0]
        print(cluster_of_file1)
        files_in_that_cluster = list(df_cluster[df_cluster['categorie'] == cluster_of_file1]['nom'])

        # Calculez la moyenne par colonne en utilisant l'axe 0
        column_means = df_prices[files_in_that_cluster].mean(axis=1)

        # Convertissez la série résultante en liste
        mean_curve = column_means.tolist()

        files_in_that_cluster.remove(file1)
        # Création de la figure avec un subplot pour les boutons
        fig = make_subplots(rows=1, cols=1, subplot_titles=['Evolution des prix de ' + file1 + ' et sa catégorie'])
        trace_file1 = go.Scatter(x=df_prices['Date'], y=df_prices[file1], mode='lines', name=file1,
                                 line=dict(color='#052e45', width=2))
        fig.add_trace(trace_file1, row=1, col=1)
        i = 0
        for other_file in files_in_that_cluster:
            fig.add_trace(go.Scatter(x=df_prices['Date'], y=df_prices[other_file], mode='lines',
                                     name='Cat. ' + str(cluster_of_file1),
                                     line=dict(color='gray', width=1, dash='dot'),
                                     legendgroup='Cat. ' + str(cluster_of_file1),
                                     showlegend=True if i == 0 else False
                                     ), row=1, col=1
                          )
            i = i + 1
        # Plot de la courbe moyenne
        fig.add_trace(go.Scatter(x=df_prices['Date'], y=mean_curve, mode='lines', name='Moyenne',
                                 line=dict(color='black', width=1)), row=1, col=1)

        # Création des boutons pour le contrôle des courbes
        visible_update = [True] + [True] * (len(files_in_that_cluster)) + [True, True, True]
        invisible_update = [True] + [False] * (len(files_in_that_cluster)) + [False, True, True]
        visible_button = dict(label='Avec sa catégorie', method='update', args=[{'visible': visible_update}])
        invisible_button = dict(label='Sans sa catégorie', method='update', args=[{'visible': invisible_update}])

        # Ajout des boutons au subplot
        fig.update_layout(showlegend=True, updatemenus=[
            {'type': 'buttons', 'showactive': False, 'buttons': [visible_button, invisible_button]}])

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
                                 legendgroup='pred', marker=dict(color='red', size=10)))

        # Lier le dernier point bleu avec le point prédit en rouge
        fig.add_trace(go.Scatter(x=[df_prices['Date'].iloc[-1], next_year_date],
                                 y=[df_prices[file1].iloc[-1], next_year_prediction[0]],
                                 mode='lines',
                                 line=dict(color='red', width=2), legendgroup='pred',
                                 showlegend=False))
        # Calcul de l'intervalle de confiance

        # Modélisation des données de file1 avec prédiction
        x = np.array(range(len(df_prices['Date'])))
        X = sm.add_constant(x)  # adding a constant
        y = df_prices[file1].values

        model = sm.OLS(y, X).fit()

        # Prédiction du prochain point pour l'année suivante
        next_year_date = df_prices['Date'].iloc[-1] + pd.DateOffset(years=1)
        next_year_index = len(df_prices['Date'])
        next_year_x = np.array([[1, next_year_index]])  # note the added constant
        next_year_prediction = model.predict(next_year_x)

        return fig

    @staticmethod
    def nearest_neighbor(df_entry, nom_fichier):
        df_entry_copy = df_entry.copy()
        df_entry_copy.set_index("nom", inplace=True)

        # Centrer réduire :
        scaler = StandardScaler()
        scaler.fit(df_entry_copy)
        data_pieces_scaler = scaler.transform(df_entry_copy)

        # Transformation spécifique pour rendre les inverses symétriques équivalentes
        data_pieces_abs = abs(data_pieces_scaler)

        # Constructeur ACP
        mypca = PCA()
        mypca.fit(data_pieces_abs)

        # Utilisation de l'ACP pour réduire la dimension
        data_pieces_pca = mypca.transform(data_pieces_abs)

        # Utilisation de NearestNeighbors pour trouver le voisin le plus proche
        neighbors_model = NearestNeighbors(n_neighbors=2)  # Considering the current point itself
        neighbors_model.fit(data_pieces_pca)

        # Trouver les indices et distances des voisins les plus proches
        distances, indices = neighbors_model.kneighbors(data_pieces_pca)

        # Trouver l'index du voisin le plus proche (éviter le premier index qui est l'élément lui-même)
        neighbor_index = indices[df_entry_copy.index == nom_fichier, 1][0]
        
        nom_voisin = df_entry_copy.index[neighbor_index]
        print(nom_voisin)

        # # Récupérer la distance entre la pièce initiale et son voisin le plus proche
        # similarity_distance = distances[df_entry_copy.index == nom_fichier, 1][0]

        # # Normaliser la distance euclidienne
        # max_distance = np.max(distances)
        # normalized_similarity = round((1 - (similarity_distance / max_distance)) *100, 2)
        
        similarity_prct = AItools.similarity_distance(df_entry_copy.reset_index(), nom_fichier, nom_voisin)

        # Retourner l'indice du voisin le plus proche et le pourcentage de similarité
        return (nom_voisin, similarity_prct)
    
    @staticmethod
    def similarity_distance(df_entry, nom_piece, nom_voisin):
        
        selected_rows = pd.concat([df_entry[df_entry["nom"] == nom_piece],
                                df_entry[df_entry["nom"] == nom_voisin]])

        # Calculer le pourcentage de changement
        percentage_change_df = selected_rows.set_index("nom").pct_change()

        # Calculer la moyenne entre les variables (colonnes)
        average_percentage_change = percentage_change_df.mean(axis=1).iloc[1]


        similarity = round(100 - abs(percentage_change_df.mean(axis=1).iloc[1] *100) ,2)

        if similarity < 0:
            similarity = 0
        # si on à 0, mêmes pièces
        # si négatif, pièce voisine plus petite que pièce initiale
        # si positif, pièce voisine plus grande que pièce initiale
        # J'en conclus que plus on se rapproche de 0, plus elles sont similaires
        # Donc si je prends la valeur absolu j'obtiens le taux de similarité
        # Nb: même si on ne prend que les caractéristiques et non la forme des pièces, on sait que les pièces sont voisines,
        # donc assez similaires selon l'acp

        return similarity

    @staticmethod
    def scale_and_pca(data):
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)

        pca = PCA()
        data_pca = pca.fit_transform(data_scaled)

        return data_pca, scaler, pca

    @staticmethod
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

    @staticmethod
    def plot_clusterisation(df_entry):
        data_pca = AItools.scaler_transform(df_entry)

        colors = px.colors.qualitative.swatches()

        # Création d'une figure interactive en 3D avec Plotly Express
        fig = px.scatter_3d(df_entry, x=data_pca[:, 0], y=data_pca[:, 1], z=data_pca[:, 2],
                            color='categorie', opacity=0.8, size_max=20,
                            title='Clusters obtenus par DBSCAN après normalisation',
                            color_discrete_sequence=colors,
                            hover_data={'categorie': True, 'nom': True})
        return fig

    @staticmethod
    def predire_prix(item, df_prices, method='linear'):
        x = np.array(range(len(df_prices['Date'])))
        x = x.reshape(-1, 1)
        y = df_prices[item].values
        model = LinearRegression().fit(x, y)
        next_year_date = df_prices['Date'].iloc[-1] + pd.DateOffset(years=1)
        next_year_index = len(df_prices['Date'])
        next_year_x = np.array([[next_year_index]])
        next_year_prediction = model.predict(next_year_x)

        # Assurez-vous que next_year_prediction est un scalaire en accédant au premier élément
        next_year_prediction_scalar = next_year_prediction[0]

        # Appliquez la fonction round sur le scalaire
        return round(next_year_prediction_scalar, 3)

    @staticmethod
    def moyenne_prix(item, df_prices, nb_annee):
        """
        
        """


def convert_step_to_stl(step_file, stl_file):
    print(f"Conversion du fichier {step_file} en {stl_file}...")
    result = cq.importers.importStep(step_file)
    cq.exporters.export(result, stl_file)


def compute_properties(path_to_stp_file):
    print(f"Calcul des propriétés géométriques du fichier {path_to_stp_file}...")
    # Cette fonction est un placeholder pour ton code de traitement de fichier
    # Remplace le contenu par le code réel qui charge le modèle 3D, extrait les caractéristiques, etc.
    try:
        model = cq.importers.importStep(path_to_stp_file)
        shape = model.val()

        volume = shape.Volume()
        surface = shape.Area()
        bbox = shape.BoundingBox()
        longueur, largeur, hauteur = bbox.xlen, bbox.ylen, bbox.zlen
        faces = len(shape.Faces())
        aretes = len(shape.Edges())
        sommets = len(shape.Vertices())
        return {
            'volume': volume,
            'surface': surface,
            'longueur': longueur,
            'largeur': largeur,
            'hauteur': hauteur,
            'faces': faces,
            'aretes': aretes,
            'sommets': sommets
        }
    except Exception as e:
        print(f"Erreur lors du traitement du fichier {path_to_stp_file}: {e}")
        return None
