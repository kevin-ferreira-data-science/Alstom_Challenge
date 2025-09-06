from django.contrib import admin
from .models import Categorie, Item, Historique
from .models import ClusteringParameters
from .forms import ClusteringParametersForm

class ClusteringParametersAdmin(admin.ModelAdmin):
    form = ClusteringParametersForm
    list_display = ('type_clusterisation', 'epsilon', 'echantillon_min', 'num_clusters')  # Affiche ces champs dans la liste
    list_editable = ('type_clusterisation','epsilon', 'echantillon_min', 'num_clusters')  # Permet de modifier ces champs directement dans la liste
    list_display_links = None  # Désactive les liens menant à la page de détails
admin.site.register(ClusteringParameters, ClusteringParametersAdmin)



class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_creation', 'date_actualisation', 'date_suppression')
    list_editable = ()


class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'categorie', 'date_creation', 'date_actualisation', 'volume', 'surface', 'longueur_bbox', 'largeur_bbox',
        'hauteur_bbox', 'nombre_faces', 'nombre_aretes', 'nombre_sommets')
    list_editable = (
        'categorie', 'volume', 'surface', 'longueur_bbox', 'largeur_bbox', 'hauteur_bbox', 'nombre_faces',
        'nombre_aretes',
        'nombre_sommets')


class HistoriqueAdmin(admin.ModelAdmin):
    list_display = ('item', 'user', 'date_creation', 'date_actualisation', 'date_suppression')
    list_editable = ()


admin.site.register(Categorie, CategorieAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Historique, HistoriqueAdmin)
