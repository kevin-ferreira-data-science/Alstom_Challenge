from django.urls import path

from . import views

urlpatterns = [
    path('', views.SelectCategorieView, name='workpage.views.dashboard-home'),
    path('get3D/<int:item_id>/', views.get3D, name='workpage.views.get3D'),
    path('upload/', views.upload_file, name='workpage.views.upload_file'),
    path('workpage/<int:item_id>/', views.WorkItem, name='workpage.views.workpage'),
    path('cluster/<int:cluster_id>/', views.ClusterView, name='workpage.views.cluster'),
    path('search/', views.search_items, name='workpage.views.search_items'),
    path('history/', views.history, name='workpage.views.history'),
    path('history/delete/<int:item_id>/', views.delete_history, name='workpage.views.delete_history'),
]
