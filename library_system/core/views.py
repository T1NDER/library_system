from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from books.models import Book, BorrowRecord
from django.utils import timezone
from users.models import User


# Получаем модель пользователя
User = get_user_model()

def index(request):
    """Главная страница для всех пользователей"""
    featured_books = Book.objects.filter(available_copies__gt=0).order_by('?')[:6]
    
    context = {
        'featured_books': featured_books,
    }
    return render(request, 'index.html', context)

@login_required
def dashboard(request):
    """Панель управления для авторизованных пользователей"""
    user = request.user
    context = {}
    
    if user.role == 'reader':
        # Для читателя: текущие выдачи и рекомендованные книги
        # Сначала получаем полный QuerySet для подсчетов
        all_current_borrowings = BorrowRecord.objects.filter(
            user=user, 
            returned=False
        ).select_related('book', 'book__author')
        
        # Затем берем срез для отображения
        current_borrowings = all_current_borrowings[:5]
        
        recommended_books = Book.objects.filter(
            available_copies__gt=0
        ).order_by('?')[:4]
        
        context.update({
            'current_borrowings': current_borrowings,
            'recommended_books': recommended_books,
            'user_borrowings_count': all_current_borrowings.count(),  # Используем полный QuerySet
            'user_overdue_count': all_current_borrowings.filter(  # Используем полный QuerySet
                due_date__lt=timezone.now()
            ).count(),
            'total_books': Book.objects.count(),
            'available_books': Book.objects.filter(available_copies__gt=0).count(),
        })
        
    elif user.role == 'librarian':
        # Для библиотекаря: активные выдачи и статистика
        active_borrowings = BorrowRecord.objects.filter(returned=False)
        overdue_borrowings = active_borrowings.filter(due_date__lt=timezone.now())
        recent_borrowings = active_borrowings.select_related('book', 'user').order_by('-borrow_date')[:5]
        
        context.update({
            'active_borrowings_count': active_borrowings.count(),
            'overdue_borrowings_count': overdue_borrowings.count(),
            'recent_borrowings': recent_borrowings,
            'total_books': Book.objects.count(),
            'available_books': Book.objects.filter(available_copies__gt=0).count(),
        })
        
    elif user.role == 'admin':
        # Для администратора: полная статистика
        total_users = User.objects.count()
        total_books = Book.objects.count()
        active_borrowings = BorrowRecord.objects.filter(returned=False)
        librarians_count = User.objects.filter(role='librarian').count()
        readers_count = User.objects.filter(role='reader').count()
        
        context.update({
            'total_users': total_users,
            'total_books': total_books,
            'active_borrowings_count': active_borrowings.count(),
            'overdue_borrowings_count': active_borrowings.filter(
                due_date__lt=timezone.now()
            ).count(),
            'librarians_count': librarians_count,
            'readers_count': readers_count,
            'available_books': Book.objects.filter(available_copies__gt=0).count(),
            'borrowed_books_count': active_borrowings.count(),
        })
    
    return render(request, 'core/dashboard.html', context)