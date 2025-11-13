# core/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Вход в систему'),
        ('logout', 'Выход из системы'),
        ('borrow', 'Выдача книги'),
        ('return', 'Возврат книги'),
        ('add_book', 'Добавление книги'),
        ('edit_book', 'Редактирование книги'),
        ('delete_book', 'Удаление книги'),
        ('add_user', 'Добавление пользователя'),
        ('edit_user', 'Редактирование пользователя'),
        ('view_report', 'Просмотр отчета'),
    ]
    
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.timestamp}"