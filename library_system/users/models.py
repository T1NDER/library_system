from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('reader', 'Читатель'),
        ('librarian', 'Библиотекарь'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reader')
    phone = models.CharField(max_length=15, blank=True)
    

    def is_librarian(self):
        """Проверяет, является ли пользователь библиотекарем"""
        return hasattr(self, 'role') and self.role == 'librarian'
    
    def is_admin(self):
        """Проверяет, является ли пользователь администратором"""
        return hasattr(self, 'role') and self.role == 'admin' or self.is_superuser
    
    def is_reader(self):
        """Проверяет, является ли пользователь читателем"""
        return not (self.is_librarian() or self.is_admin())
    
    class Meta:
        db_table = 'library_users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'