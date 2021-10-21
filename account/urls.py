from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name="account_register"),
    path('get-token/', views.get_token, name="account_get_token"),
    path('whoami/', views.whoami, name="account_whoami"),
    path('reset-token/', views.reset_token, name="account_reset_token"),
    path('reset-password/', views.reset_password, name="account_reset_password"),
]
