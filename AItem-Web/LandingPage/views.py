from django.shortcuts import render


def home(request):
    return render(request, 'LandingPage.html')  # Nom de ton fichier HTML

