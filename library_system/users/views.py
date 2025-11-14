from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView  # ✅ Правильное написание
from django.contrib import messages
from .forms import UserRegistrationForm, UserProfileForm, UserRoleForm
from .decorators import admin_required, librarian_required
from .models import User
from books.models import Book, BookRequest
from borrowings.models import Borrowing
from django.utils import timezone

def custom_logout(request):
    """Кастомный выход из системы"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('/') 

class CustomLoginView(LoginView):
    """Кастомное представление для входа в систему"""
    template_name = 'registration/login.html'  
    redirect_authenticated_user = True

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('/') 
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:profile') 
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})


@admin_required
def user_management(request):
    """Управление пользователями (только для администраторов)"""
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'users/user_management.html', {'users': users})

@admin_required
def change_user_role(request, user_id):
    """Изменение роли пользователя"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Роль пользователя {user.username} изменена на {user.get_role_display()}')
            return redirect('users:user_management') 
    else:
        form = UserRoleForm(instance=user)
    
    return render(request, 'users/change_role.html', {'form': form, 'user': user})


