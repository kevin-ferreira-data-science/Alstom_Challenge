from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy

from .forms import LoginForm


def login(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Si le formulaire est valide, on essaye d'authentifier l'utilisateur
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )

            # Si l'utilisateur est authentifié
            if user is not None:
                # On le connecte
                auth_login(request, user)
            else:
                # Sinon, on affiche un message d'erreur
                form.add_error(None, 'Nom d\'utilisateur ou mot de passe incorrect')

    # Si l'utilisateur est authentifié, on le redirige vers le dashboard
    if request.user.is_authenticated:
        # Récupérer l'url du dashboard
        dashboard_url = reverse_lazy('workpage.views.dashboard-home')

        # Redirection vers le dashboard
        return HttpResponseRedirect(dashboard_url)
    else:
        # Sinon, on affiche le formulaire de connexion
        return render(request, 'LoginPage.html', {
            'form': form,
        })


def logout(request):
    # On déconnecte l'utilisateur
    auth_logout(request)

    # Récupérer l'url de la page d'accueil
    home_url = reverse_lazy('landingpage.views.home')

    # On redirige vers la page d'accueil
    return HttpResponseRedirect(home_url)
