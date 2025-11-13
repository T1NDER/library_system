from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Book, Genre
from .forms import BookForm, BookSearchForm
from users.decorators import admin_required

def book_list(request):
    """Список всех книг с поиском"""
    form = BookSearchForm(request.GET or None)
    books = Book.objects.all().select_related('author', 'genre')
    
    query = request.GET.get('query')
    genre_id = request.GET.get('genre')
    availability = request.GET.get('availability')
    
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query) |
            Q(genre__name__icontains=query)
        )
    
    if genre_id:
        books = books.filter(genre_id=genre_id)
    
    if availability == 'available':
        books = books.filter(available_copies__gt=0)
    elif availability == 'unavailable':
        books = books.filter(available_copies=0)
    
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'genres': Genre.objects.all(),
    }
    return render(request, 'books/book_list.html', context)

@login_required
def book_detail(request, book_id):
    """Детальная информация о книге"""
    book = get_object_or_404(Book, id=book_id)
    
    context = {
        'book': book,
    }
    return render(request, 'books/book_detail.html', context)

@admin_required
def add_book(request):
    """Добавление новой книги (только для администраторов)"""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Книга "{book.title}" успешно добавлена!')
            return redirect('books:book_detail', book_id=book.id)
    else:
        form = BookForm()
    
    return render(request, 'books/book_form.html', {'form': form, 'title': 'Добавить книгу'})

@admin_required
def edit_book(request, book_id):
    """Редактирование информации о книге"""
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'Книга "{book.title}" успешно обновлена!')
            return redirect('books:book_detail', book_id=book.id)
    else:
        form = BookForm(instance=book)
    
    return render(request, 'books/book_form.html', {'form': form, 'title': 'Редактировать книгу'})