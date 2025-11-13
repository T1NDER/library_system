from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Borrowing(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('returned', 'Возвращена'),
        ('overdue', 'Просрочена'),
    ]
    
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE, verbose_name='Книга')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    borrowed_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата выдачи')
    due_date = models.DateTimeField(verbose_name='Срок возврата', db_index=True)
    returned_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата возврата')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name='Статус', db_index=True)
    renew_count = models.IntegerField(default=0, verbose_name='Количество продлений')
    
    def __str__(self):
        return f"{self.book.title} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.due_date = timezone.now() + timedelta(days=30)
        
        if self.returned_date and self.status != 'returned':
            self.status = 'returned'
            self.book.available_copies += 1
            self.book.save()
        
        if not self.returned_date and timezone.now() > self.due_date:
            self.status = 'overdue'
        
        super().save(*args, **kwargs)
    
    def is_overdue(self):
        return not self.returned_date and timezone.now() > self.due_date
    
    def days_overdue(self):
        if self.is_overdue():
            return (timezone.now() - self.due_date).days
        return 0
    
    @property
    def days_until_due(self):
        """Количество дней до срока возврата"""
        if not self.returned_date and not self.is_overdue():
            return (self.due_date - timezone.now()).days
        return 0
    
    class Meta:
        verbose_name = 'Выдача книги'
        verbose_name_plural = 'Выдачи книг'
        ordering = ['-borrowed_date']