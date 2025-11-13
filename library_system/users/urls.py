from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),  # ЭТА СТРОКА ДОЛЖНА БЫТЬ
    path('profile/', views.profile, name='profile'),
    path('management/', views.user_management, name='user_management'),
    path('management/<int:user_id>/change-role/', views.change_user_role, name='change_user_role'),
]