"""AItemWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Redirige le chemin racine vers LandingPage.urls
    path('', include('LandingPage.urls')),
    # Redirige le chemin racine vers WorkPage.urls
    path('dashboard/', include('WorkPage.urls')),
    # Redirige le chemin racine vers AuthPage.urls
    path('login/', include('AuthPage.urls')),
]

# Ajouter la route uniquement si DEBUG est False
if not settings.DEBUG:
    urlpatterns += [
        # Ajoutez ici la route que vous souhaitez activer en production
        # Exemple : path('production-only/', views.production_only_view),
        # Cette règle redirigera toutes les URL non trouvées vers la page d'accueil
        path('<path:dummy>', RedirectView.as_view(url='/', permanent=False)),
    ]
