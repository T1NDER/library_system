from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Author(models.Model):
    name = models.CharField(max_length=200, verbose_name='Имя автора')
    bio = models.TextField(blank=True, null=True, verbose_name='Биография')
    biography = models.TextField(blank=True, null=True, verbose_name='Биография (расширенная)')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    death_date = models.DateField(blank=True, null=True, verbose_name='Дата смерти')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

class Genre(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название жанра')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Жанр')
    isbn = models.CharField(
        max_length=13, 
        unique=True, 
        blank=True, 
        null=True,  
        verbose_name='ISBN'
    )
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    total_copies = models.IntegerField(default=1, verbose_name='Всего копий')
    available_copies = models.IntegerField(default=1, verbose_name='Доступные копии')
    published_date = models.DateField(blank=True, null=True, verbose_name='Дата публикации')
    publication_year = models.IntegerField(blank=True, null=True, verbose_name='Год публикации')
    publisher = models.CharField(max_length=200, blank=True, null=True, verbose_name='Издательство')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    def save(self, *args, **kwargs):
        if not self.pk:  
            self.available_copies = self.total_copies
        super().save(*args, **kwargs)
    
    @property
    def is_available(self):
        return self.available_copies > 0
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['title']


class BookRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает рассмотрения'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Книга')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    requested_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата заявки')
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата одобрения')
    rejected_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата отклонения')
    notes = models.TextField(blank=True, null=True, verbose_name='Примечания')

    def __str__(self):
        return f"Заявка: {self.book.title} - {self.user.username} ({self.get_status_display()})"

    class Meta:
        verbose_name = 'Заявка на книгу'
        verbose_name_plural = 'Заявки на книги'
        ordering = ['-requested_date']
        unique_together = ['user', 'book', 'status']  # Предотвращает дублирование активных заявок


class BorrowRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Книга')
    borrow_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата выдачи')
    due_date = models.DateTimeField(verbose_name='Срок возврата')
    returned = models.BooleanField(default=False, verbose_name='Возвращена')
    return_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата возврата')

    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.due_date:
                self.due_date = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Проверка, просрочена ли книга"""
        return not self.returned and timezone.now() > self.due_date

    @property
    def days_overdue(self):
        """Количество дней просрочки"""
        if self.is_overdue:
            return (timezone.now() - self.due_date).days
        return 0

    @property
    def days_until_due(self):
        """Количество дней до срока возврата"""
        if not self.returned and not self.is_overdue:
            return (self.due_date - timezone.now()).days
        return 0

    def __str__(self):
        return f"{self.book.title} - {self.user.username}"

    class Meta:
        verbose_name = 'Запись о выдаче'
        verbose_name_plural = 'Записи о выдачах'
        ordering = ['-borrow_date']
