from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.loginUser, name = "loginUser"),
    path('signup/', views.registerUser, name = "registerUser"),
]