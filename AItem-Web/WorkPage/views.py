import os
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import trimesh
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from plotly.io import to_html

from .AItools import AItools
from .forms import FileUploadForm
from .models import Categorie, Item, Historique, ClusteringParameters


@login_required
def SelectCategorieView(request):
    # Récupérer les catégories avec les items associés
    categories = Categorie.objects.all().prefetch_related('items')

    return render(request, 'SelectCategorie.html', {
        'categories': categories,
        'page': 'select_categories',
    })


@login_required
def WorkItem(request, item_id):
    # Récupérer l'Item spécifique ou renvoyer une erreur 404 si non trouvé
    item = get_object_or_404(Item, id=item_id)

    # Récupérer l'utilisateur connecté
    user = request.user

    # Si l'utilisateur n'a pas consulté cet item, créer un nouvel historique
    if not item.historiques.filter(user=user, date_suppression=None).exists():
        Historique.objects.create(item=item, user=user)
    else:
        # Sinon, mettre à jour la date d'actualisation de l'historique existant
        historique = item.historiques.get(user=user, date_suppression=None)
        historique.save()

    # Exemple de visualisation 3D de l'item
    visualization_html = item_visualization_3D(item, "Visualisation 3D de " + item.nom)
    visualization_html2, nomItemProche, itemIdProche = item_visualization_nearest(item)
    # Graphiques
    chart_html_prix = graphique_prediction_prix(item)
    chart_html_cluster = graphique_clusterisation()
    # Prix prévisionnel (en dur pour l'instant)
    prix_previsionnel = AItools.predire_prix(item.nom,
                                             pd.read_csv(os.path.join(settings.STATICFILES_DIRS[0], 'prices.csv'),
                                                         parse_dates=['Date']))  # Exemple de prix prévisionnel

    # Récupérer la catégorie de l'item par le nom
    categorie = item.categorie

    # Pièce la plus proche - Exemple statique, à remplacer par la logique appropriée
    # Rendre la réponse avec les données de l'item et les visualisations
    return render(request, 'WorkPage.html', {
        'item': item,  # Passer l'objet item complet
        'categorie': categorie,
        'nomItemPlusProche': nomItemProche,
        'idItemPlusProche': itemIdProche,
        'itemSurface': round(item.surface * 1e-2, 4),
        'itemVolume': round(item.volume * 1e-3, 4),
        'chart_html_prix': chart_html_prix,
        'chart_html_cluster': chart_html_cluster,
        'visualization_html': visualization_html,
        'visualization_html2': visualization_html2,
        'prix_previsionnel': prix_previsionnel,  # Prix prévisionnel
        'piece_proche': nomItemProche,  # Pièce la plus proche
        'url_piece_proche': f'/dashboard/workpage/{itemIdProche}/',
        'afficher_choix_items': True,
    })


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('file')  # Récupère une liste de fichiers
            for file in files:
                nom_fichier = file.name[:-4]  # Nom de l'item = nom du fichier sans l'extension (.stp)
                extension_fichier = file.name[-3:]  # Extension du fichier
                if extension_fichier != 'stp':
                    print('Extension du fichier', nom_fichier, 'non supportée!')
                    continue
                print('Import du fichier', nom_fichier, '(' + extension_fichier + ')' + '...')
                try:
                    # Créer l'Item
                    item, created = Item.objects.get_or_create(
                        nom=nom_fichier,
                        defaults={'fichier': file}
                    )
                    if not created:
                        item.fichier = file
                        item.save()
                    print(f"Import du fichier {file.name} réussi!")
                except Exception as e:
                    print(f"Erreur lors de l'import du fichier {file.name}:", e)
            items_all = Item.objects.all()
            if items_all.exists():
                print('Récupération des caractéristiques...')
                df_items = pd.DataFrame.from_records(items_all.values(
                    'nom', 'volume', 'surface', 'longueur_bbox', 'largeur_bbox', 'hauteur_bbox',
                    'nombre_faces', 'nombre_aretes', 'nombre_sommets'
                ))

                params = ClusteringParameters.objects.first()

                if params:
                    choice_cluster = params.type_clusterisation
                    choice_epsilon = params.epsilon
                    choice_echantillon_min = params.echantillon_min
                    choice_clusters = params.num_clusters
                else:
                    # 1 : DBSCAN               (df_entry, epsilon, echantillon_min)
                    # 2 : Propagation sklearn  (df_entry)
                    # 3 : k-means              (df_entry, num_clusters)
                    choice_cluster = 3
                    choice_epsilon = 0.1
                    choice_echantillon_min = 2
                    choice_clusters = 3
                df_clustered = AItools.clustering_selector(df_items,
                                                           type_clusterisation=choice_cluster,
                                                           epsilon=choice_epsilon,
                                                           echantillon_min=choice_echantillon_min,
                                                           num_clusters=choice_clusters)
                print('Mise à jour des catégories...')
                for index, row in df_clustered.iterrows():
                    itemNom = row['nom']
                    cluster_id = row['categorie']
                    item = Item.objects.get(nom=itemNom)
                    categorie, created = Categorie.objects.get_or_create(nom=f"Cluster {cluster_id}")
                    item.categorie = categorie
                    item.save()
                categories_vide = Categorie.objects.annotate(num_items=Count('items')).filter(num_items=0)
                # Suppression des catégories sans items
                categories_vide.delete()
            return JsonResponse({'status': 'success'})
        else:
            # Reply error
            return JsonResponse({'status': 'error'})
    else:
        return JsonResponse({'status': 'error'})


@login_required
def history(request):
    # Récupérer l'utilisateur connecté
    user = request.user

    # Récupérer les historiques de l'utilisateur connecté
    historiques = Historique.objects.filter(user=user, date_suppression=None).order_by('date_creation')

    # Json
    data = []
    for historique in historiques:
        data.append({
            'id': historique.item.id,
            'nom': historique.item.nom,
        })

    return JsonResponse(list(data), safe=False)


@login_required
def delete_history(request, item_id):
    # Récupérer l'utilisateur connecté
    user = request.user

    # Récupérer l'historique de l'utilisateur connecté
    historique = Historique.objects.get(user=user, item__id=item_id, date_suppression=None)

    if historique is None:
        return JsonResponse({'status': 'error'})

    # Supprimer l'historique
    historique.date_suppression = datetime.now()
    historique.save()

    return JsonResponse({'status': 'success'})


def graphique_prediction_prix(item):
    file1 = item.nom
    # récupération de tout les items qui ont la méme catégorie que file1 et que les champs nom et cluster
    df_cluster = pd.DataFrame.from_records(Item.objects.filter(categorie=item.categorie).values('nom', 'categorie'))
    df_prices = pd.read_csv(os.path.join(settings.STATICFILES_DIRS[0], 'prices.csv'), parse_dates=['Date'])
    fig = AItools.plot_prices_file1(file1, df_cluster, df_prices)
    # Conversion du graphique en HTML
    return to_html(fig, full_html=False, include_plotlyjs=False)


def graphique_clusterisation():
    df_items = pd.DataFrame.from_records(Item.objects.all().values(
        'nom', 'categorie', 'volume', 'surface', 'longueur_bbox', 'largeur_bbox', 'hauteur_bbox',
        'nombre_faces', 'nombre_aretes', 'nombre_sommets'
    ))
    fig = AItools.plot_clusterisation(df_items)
    # Conversion du graphique en HTML
    return to_html(fig, full_html=False, include_plotlyjs=False)


@login_required
def search_items(request):
    query = request.GET.get('q', '')
    if query:
        items = Item.objects.filter(nom__icontains=query)[:10]  # Limitez les résultats pour les performances
        results = [{"id": item.id, 'nom': item.nom} for item in items]
    else:
        results = []
    return JsonResponse({'results': results})


def item_visualization_3D(item, titre, scale_factor=0.5):
    # Assurez-vous que le chemin vers le fichier STL est correct
    # Note: Adaptez le chemin en fonction de l'emplacement réel de vos fichiers STL
    stl_file = item.fichier.path.replace('.stp', '.stl')
    # Charger le fichier STL
    mesh = trimesh.load_mesh(stl_file)
    # Extraire les vertices et les faces du maillage
    vertices = np.array(mesh.vertices)
    faces = np.array(mesh.faces)

    # Redimensionner les coordonnées des vertices en multipliant par le facteur d'échelle
    vertices *= scale_factor

    # Créer une figure Plotly avec les données du maillage 3D
    fig = go.Figure(data=[go.Mesh3d(
        x=vertices[:, 0],  # Coordonnées X des vertices
        y=vertices[:, 1],  # Coordonnées Y des vertices
        z=vertices[:, 2],  # Coordonnées Z des vertices
        i=faces[:, 0],  # Indices des vertices formant chaque face (premier vertex)
        j=faces[:, 1],  # Indices des vertices formant chaque face (deuxième vertex)
        k=faces[:, 2],  # Indices des vertices formant chaque face (troisième vertex)
        color='#1e3246',  # Couleur du maillage
        opacity=0.50,  # Transparence du maillage
        name=item.nom  # Nom de l'item pour la légende (facultatif)
    )])

    # Mise à jour de la mise en page de la figure
    fig.update_layout(
        title=titre,  # Titre de la figure
        scene=dict(  # Configuration de la scène 3D
            xaxis_title='X',  # Titre de l'axe X
            yaxis_title='Y',  # Titre de l'axe Y
            zaxis_title='Z'  # Titre de l'axe Z
        ),
        # margin=dict(l=0, r=0, b=0, t=0),  # Marges de la figure
    )
    # Conversion de la figure en HTML pour l'intégration dans le template Django
    visualization_html = to_html(fig, full_html=False, include_plotlyjs=False)
    return visualization_html


def item_visualization_nearest(item):
    df_items = pd.DataFrame.from_records(Item.objects.all().values(
        'nom', 'volume', 'surface', 'longueur_bbox', 'largeur_bbox', 'hauteur_bbox',
        'nombre_faces', 'nombre_aretes', 'nombre_sommets'
    ))
    nomItemProche, similarity = AItools.nearest_neighbor(df_items, item.nom)
    # Trouver l'item proche par le nom pour obtenir son ID
    itemProche = Item.objects.get(nom=nomItemProche)  # Assurez-vous que le nom est unique ou gérez les doublons
    idItemProche = itemProche.id
    return item_visualization_3D(itemProche, "Pièce la plus proche de " + str(
        nomItemProche) + "<br>Similarité des caractéristiques : " + str(similarity) + " %"), nomItemProche, idItemProche


## Page de cluster
@login_required
def ClusterView(request, cluster_id):
    # On récupère la catégorie
    categorie = get_object_or_404(Categorie, id=cluster_id)
    # On récupère les items en fonction de l'id de la catégorie puis on les trie par nom
    items = categorie.items.all().order_by('nom')

    return render(request, 'SelectItem.html', {
        'nom_cluster': categorie,
        'items': items,
    })


def get3D(request, item_id):
    # Récupérer l'Item spécifique ou renvoyer une erreur 404 si non trouvé
    item = get_object_or_404(Item, id=item_id)

    stl_file = os.path.join(settings.MEDIA_ROOT, 'items', item.nom + '.stl')
    # Charger le fichier STL
    mesh = trimesh.load_mesh(stl_file)
    # Extraire les vertices et les faces du maillage
    vertices = np.array(mesh.vertices)
    faces = np.array(mesh.faces)

    # Redimensionner les coordonnées des vertices en multipliant par le facteur d'échelle
    vertices *= 0.5

    # Créer une figure Plotly avec les données du maillage 3D
    fig = go.Figure(data=[go.Mesh3d(
        x=vertices[:, 0],  # Coordonnées X des vertices
        y=vertices[:, 1],  # Coordonnées Y des vertices
        z=vertices[:, 2],  # Coordonnées Z des vertices
        i=faces[:, 0],  # Indices des vertices formant chaque face (premier vertex)
        j=faces[:, 1],  # Indices des vertices formant chaque face (deuxième vertex)
        k=faces[:, 2],  # Indices des vertices formant chaque face (troisième vertex)
        color='lightblue',  # Couleur du maillage
        opacity=0.50,  # Transparence du maillage
        name=item.nom  # Nom de l'item pour la légende (facultatif)
    )])

    # Mise à jour de la mise en page de la figure
    fig.update_layout(
        scene=dict(  # Configuration de la scène 3D
            xaxis_title='X',  # Titre de l'axe X
            yaxis_title='Y',  # Titre de l'axe Y
            zaxis_title='Z'  # Titre de l'axe Z
        )
    )
    fig_json = fig.to_json()

    # Retourner les données JSON en réponse à la requête AJAX
    return JsonResponse({'plot_data': fig_json})
