from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.create, name="create_poll"),
    path('update/', views.create, name="create_poll"),
    path('delete/', views.create, name="create_poll"),
    path('create_choice/', views.create, name="create_poll"),
    path('update_choice/', views.create, name="create_poll"),
    path('delete_choice/', views.create, name="create_poll"),
    path('choice/', views.choice, name="select_choice"),
    path('', views.index, name="polls_list"),
]
