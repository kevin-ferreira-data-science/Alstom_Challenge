# forms.py
from django import forms
from django.core.validators import FileExtensionValidator
from django import forms
from .models import ClusteringParameters


class FileUploadForm(forms.Form):
    file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["stp"])])

class ClusteringParametersForm(forms.ModelForm):
    class Meta:
        model = ClusteringParameters
        fields = '__all__'  # Inclut tous les champs du modèle
