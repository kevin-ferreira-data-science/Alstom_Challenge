from django.urls import path

from . import views

urlpatterns = [
    path('', views.login, name='authpage.views.login'),
    path('logout/', views.logout, name='authpage.views.logout'),
]
