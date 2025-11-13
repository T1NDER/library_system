from django.urls import path
from . import views

app_name = 'core'  # Это регистрирует namespace 'core'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reader-dashboard/', views.reader_dashboard, name='reader_dashboard'),
    path('', views.index, name='index')
]
