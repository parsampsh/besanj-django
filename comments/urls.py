from django.urls import path
from . import views


urlpatterns = [
    path('send/', views.send, name='send_comment'),
    path('delete/', views.delete, name='delete_comment'),
    path('user_comments/', views.comments_by_user, name='comments_by_user'),
    path('poll_comments/', views.comments_on_poll, name='comments_on_poll'),
]
