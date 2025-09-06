from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='landingpage.views.home')
]
