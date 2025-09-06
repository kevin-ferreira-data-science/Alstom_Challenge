import multiprocessing
import os

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver

from .AItools import convert_step_to_stl, compute_properties


class ClusteringParameters(models.Model):
    type_clusterisation = models.IntegerField(default=3, choices=[(1, 'DBSCAN'), (2, 'Propagation'), (3, 'K-Means')])
    epsilon = models.FloatField(default=0.1)
    echantillon_min = models.IntegerField(default=2)
    num_clusters = models.IntegerField(default=3)

    def __str__(self):
        return f"Paramètres de Clustering ({self.get_type_clusterisation_display()})"


class Categorie(models.Model):
    nom = models.CharField(max_length=255)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_actualisation = models.DateTimeField(auto_now=True)
    date_suppression = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nom


class Item(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    fichier = models.FileField(upload_to='items/', null=True, blank=True, unique=True)
    fichier_stl_needs_update = models.BooleanField(default=False)
    categorie = models.ForeignKey(Categorie, related_name='items', on_delete=models.CASCADE, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_actualisation = models.DateTimeField(auto_now=True)
    date_suppression = models.DateTimeField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    surface = models.FloatField(null=True, blank=True)
    longueur_bbox = models.FloatField(null=True, blank=True)
    largeur_bbox = models.FloatField(null=True, blank=True)
    hauteur_bbox = models.FloatField(null=True, blank=True)
    nombre_faces = models.IntegerField(null=True, blank=True)
    nombre_aretes = models.IntegerField(null=True, blank=True)
    nombre_sommets = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.nom


class Historique(models.Model):
    item = models.ForeignKey(Item, related_name='historiques', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='historiques', on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_actualisation = models.DateTimeField(auto_now=True)
    date_suppression = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.item.nom} - {self.user.username}"


# Supprimer les fichiers automatiquement lors de la suppression de l'Item
@receiver(post_delete, sender=Item)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.fichier:
        file_path = instance.fichier.path
        if os.path.isfile(file_path):
            print(f"Suppression du fichier {file_path}...")
            os.remove(file_path)

        # Supprimer également le fichier STL si existant
        stl_file_path = file_path.replace('.stp', '.stl')
        if os.path.isfile(stl_file_path):
            print(f"Suppression du fichier {stl_file_path}...")
            os.remove(stl_file_path)


# Supprimer les fichiers automatiquement lors de la modification de l'Item
@receiver(pre_save, sender=Item)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        if instance.fichier:
            instance.fichier_stl_needs_update = True
        return False

    try:
        old_file = Item.objects.get(pk=instance.pk).fichier
    except Item.DoesNotExist:
        if instance.fichier:
            instance.fichier_stl_needs_update = True
        return False

    new_file = instance.fichier
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            print(f"Suppression du fichier {old_file.path}...")
            os.remove(old_file.path)

        # Supprimer également l'ancien fichier STL si existant
        old_stl_file_path = old_file.path.replace('.stp', '.stl')
        if os.path.isfile(old_stl_file_path):
            print(f"Suppression du fichier {old_stl_file_path}...")
            os.remove(old_stl_file_path)

        if instance.fichier:
            instance.fichier_stl_needs_update = True


# Convertir le fichier STEP en STL
@receiver(post_save, sender=Item)
def auto_convert_step_to_stl(sender, instance, **kwargs):
    # Convertir le fichier STP en STL
    if instance.fichier and instance.fichier_stl_needs_update and instance.fichier.path.endswith('.stp'):
        step_file_path = instance.fichier.path
        stl_file_path = step_file_path.replace('.stp', '.stl')
        convert_step_to_stl(step_file_path, stl_file_path)
        # On est obligé de créer un process à part pour la conversion car cadquery ne lève pas d'exception en cas d'erreur et sinon ça fait crash le serveur
        #process = multiprocessing.Process(target=convert_step_to_stl, args=(step_file_path, stl_file_path))
        #process.start()
        #process.join()
        # Vérifie si la conversion a réussi
        if os.path.isfile(stl_file_path):
            print(f"Conversion du fichier {step_file_path} en {stl_file_path} réussie!")
        else:
            print(f"Conversion du fichier {step_file_path} en {stl_file_path} échouée!")
            raise Exception(f"Conversion du fichier {step_file_path} en {stl_file_path} échouée!")

        # Calcule les propriétés géométriques
        properties = compute_properties(step_file_path)

        if properties:
            print(f"Mise à jour des propriétés géométriques de l'item {instance.nom}...")
            # Mets à jour l'instance de l'item avec les nouvelles propriétés
            instance.volume = properties.get('volume')
            instance.surface = properties.get('surface')
            instance.longueur_bbox = properties.get('longueur')
            instance.largeur_bbox = properties.get('largeur')
            instance.hauteur_bbox = properties.get('hauteur')
            instance.nombre_faces = properties.get('faces')
            instance.nombre_aretes = properties.get('aretes')
            instance.nombre_sommets = properties.get('sommets')

        instance.fichier_stl_needs_update = False
        instance.save()
