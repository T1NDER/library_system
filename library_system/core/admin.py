# core/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .models import AuditLog

class LibraryAdminSite(admin.AdminSite):
    site_header = "Управление библиотекой"
    site_title = "Библиотека - Админка"
    index_title = "Статистика и управление"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('statistics/', self.admin_view(self.statistics_view), name='statistics'),
            path('overdue-list/', self.admin_view(self.overdue_list_view), name='overdue-list'),
            path('activity-monitor/', self.admin_view(self.activity_monitor_view), name='activity-monitor'),
            path('monthly-stats/', self.admin_view(self.monthly_statistics_view), name='monthly-stats'),
            path('popular-books/', self.admin_view(self.popular_books_view), name='popular-books'),
            path('active-readers/', self.admin_view(self.active_readers_view), name='active-readers'),
            path('audit-log/', self.admin_view(self.audit_log_view), name='audit-log'),
        ]
        return custom_urls + urls
    
    def statistics_view(self, request):
        from books.models import Book
        from borrowings.models import Borrowing
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if start_date and end_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        
        books_stats = Book.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).aggregate(
            total=Count('id'),
            available=Count('id', filter=Q(available_copies__gt=0)),
            borrowed=Count('id', filter=Q(available_copies=0))
        )
        
        borrowing_stats = Borrowing.objects.filter(
            borrowed_date__range=[start_date, end_date]
        ).aggregate(
            total_borrowings=Count('id'),
            returned=Count('id', filter=Q(status='returned')),
            active=Count('id', filter=Q(status='borrowed'))
        )
        
        total_stats = {
            'total_books': Book.objects.count(),
            'total_users': User.objects.count(),
            'total_borrowings': Borrowing.objects.count(),
        }
        
        context = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'books_stats': books_stats,
            'borrowing_stats': borrowing_stats,
            'total_stats': total_stats,
            'title': 'Статистика за период'
        }
        return render(request, 'admin/statistics.html', context)
    
    def overdue_list_view(self, request):
        from borrowings.models import Borrowing
        
        today = timezone.now().date()
        overdue_borrowings = Borrowing.objects.filter(
            due_date__lt=today,
            status='borrowed'
        ).select_related('book', 'user')
        
        for borrowing in overdue_borrowings:
            borrowing.overdue_days = (today - borrowing.due_date).days
        
        context = {
            'overdue_borrowings': overdue_borrowings,
            'today': today,
            'title': 'Список задолжников'
        }
        return render(request, 'admin/overdue_list.html', context)
    
    def activity_monitor_view(self, request):
        from borrowings.models import Borrowing
        from django.utils import timezone
        
        recent_activities = Borrowing.objects.select_related('book', 'user').order_by('-borrowed_date')[:50]
        
        today = timezone.now().date()
        for activity in recent_activities:
            if activity.status == 'borrowed':
                activity.days_until_due = (activity.due_date - today).days
                activity.is_overdue = activity.days_until_due < 0
                activity.overdue_days = max(0, -activity.days_until_due)
            else:
                activity.days_until_due = None
                activity.is_overdue = False
                activity.overdue_days = 0
        
        context = {
            'recent_activities': recent_activities,
            'title': 'Мониторинг активности системы'
        }
        return render(request, 'admin/activity_monitor.html', context)
    
    def monthly_statistics_view(self, request):
        """Статистика выдачи книг по месяцам"""
        from borrowings.models import Borrowing
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=365)
        
        monthly_data = []
        current_date = start_date
        while current_date <= end_date:
            year = current_date.year
            month = current_date.month
            
            count = Borrowing.objects.filter(
                borrowed_date__year=year,
                borrowed_date__month=month
            ).count()
            
            monthly_data.append({
                'period': f"{month:02d}/{year}",
                'count': count,
                'year': year,
                'month': month
            })
            
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1
            
            try:
                current_date = current_date.replace(year=year, month=month, day=1)
            except ValueError:
                break
        
        total_borrowings = sum(item['count'] for item in monthly_data)
        avg_per_month = total_borrowings / len(monthly_data) if monthly_data else 0
        
        context = {
            'monthly_data': monthly_data,
            'total_borrowings': total_borrowings,
            'avg_per_month': round(avg_per_month, 1),
            'start_date': start_date,
            'end_date': end_date,
            'title': 'Статистика выдачи по месяцам'
        }
        return render(request, 'admin/monthly_stats.html', context)
    
    def popular_books_view(self, request):
        """Самые популярные книги"""
        from books.models import Book
        
        popular_books = Book.objects.annotate(
            borrow_count=Count('borrowing')
        ).filter(borrow_count__gt=0).order_by('-borrow_count')[:20]
        
        genre_stats = Book.objects.values(
            'genre__name'
        ).annotate(
            total_books=Count('id'),
            total_borrowings=Count('borrowing')
        ).filter(total_borrowings__gt=0).order_by('-total_borrowings')
        
        author_stats = Book.objects.values(
            'author__name'
        ).annotate(
            total_books=Count('id'),
            total_borrowings=Count('borrowing')
        ).filter(total_borrowings__gt=0).order_by('-total_borrowings')[:10]
        
        context = {
            'popular_books': popular_books,
            'genre_stats': genre_stats,
            'author_stats': author_stats,
            'title': 'Популярные книги и авторы'
        }
        return render(request, 'admin/popular_books.html', context)
    
    def active_readers_view(self, request):
        """Активные читатели"""
        from django.contrib.auth import get_user_model
        from borrowings.models import Borrowing
        User = get_user_model()
        
        active_readers = User.objects.annotate(
            borrow_count=Count('borrowing'),
            active_borrowings=Count('borrowing', filter=Q(borrowing__status='borrowed'))
        ).filter(borrow_count__gt=0).order_by('-borrow_count')[:20]
        
        role_stats = User.objects.values(
            'role'
        ).annotate(
            total_users=Count('id'),
            active_readers=Count('id', filter=Q(borrowing__isnull=False)),
            total_borrowings=Count('borrowing')
        ).order_by('-active_readers')
        
        readers_with_overdue = User.objects.filter(
            borrowing__status='borrowed',
            borrowing__due_date__lt=timezone.now().date()
        ).annotate(
            overdue_count=Count('borrowing', filter=Q(borrowing__due_date__lt=timezone.now().date()))
        ).distinct()[:10]
        
        context = {
            'active_readers': active_readers,
            'role_stats': role_stats,
            'readers_with_overdue': readers_with_overdue,
            'title': 'Активные читатели'
        }
        return render(request, 'admin/active_readers.html', context)
    
    def audit_log_view(self, request):
        """Журнал аудита действий пользователей"""
        action_filter = request.GET.get('action')
        user_filter = request.GET.get('user')
        
        audit_logs = AuditLog.objects.all().select_related('user')
        
        if action_filter:
            audit_logs = audit_logs.filter(action=action_filter)
        
        if user_filter:
            audit_logs = audit_logs.filter(user_id=user_filter)
        
        paginator = Paginator(audit_logs, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        action_stats = AuditLog.objects.values(
            'action'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.all()
        
        context = {
            'page_obj': page_obj,
            'action_stats': action_stats,
            'users': users,
            'action_choices': AuditLog.ACTION_CHOICES,
            'title': 'Журнал аудита'
        }
        return render(request, 'admin/audit_log.html', context)

library_admin = LibraryAdminSite(name='library_admin')