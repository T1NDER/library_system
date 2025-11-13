from django.urls import path
from . import views

app_name = 'core'  # Это регистрирует namespace 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
]