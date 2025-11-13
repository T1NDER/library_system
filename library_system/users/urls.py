from django.urls import path
from . import views
from .views import CustomLoginView  # Добавьте этот импорт

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),  # Используем кастомное представление
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('management/', views.user_management, name='user_management'),
    path('management/<int:user_id>/change-role/', views.change_user_role, name='change_user_role'),
]