from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.create, name="create_poll"),
    path('choice/', views.choice, name="select_choice"),
    path('', views.index, name="polls_list"),
]
