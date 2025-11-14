from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Book, Genre
from .forms import BookForm, BookSearchForm
from users.decorators import librarian_required
from datetime import timedelta


def book_list(request):
    """Список всех книг с фильтрацией"""
    form = BookSearchForm(request.GET or None)
    books = Book.objects.all().select_related('author', 'genre')
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        genre = form.cleaned_data.get('genre')
        available_only = form.cleaned_data.get('available_only')
        
        if query:
            books = books.filter(
                Q(title__icontains=query) |
                Q(author__name__icontains=query) |
                Q(genre__name__icontains=query)
            )
        
        if genre:
            books = books.filter(genre=genre)
            
        if available_only:
            books = books.filter(available_copies__gt=0)
    
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
def book_detail(request, pk):
    """Детальная информация о книге"""
    book = get_object_or_404(Book, pk=pk)

    from .models import BorrowRecord
    user_has_book = BorrowRecord.objects.filter(
        user=request.user,
        book=book,
        returned=False
    ).exists()

    context = {
        'book': book,
        'user_has_book': user_has_book,
    }
    return render(request, 'books/book_detail.html', context)



@librarian_required
def add_book(request):
    """Добавление новой книги (ТОЛЬКО для библиотекарей)"""
    if not (hasattr(request.user, 'is_librarian') and request.user.is_librarian) and not (hasattr(request.user, 'is_admin') and request.user.is_admin):
        messages.error(request, 'Недостаточно прав доступа! Только библиотекари могут добавлять книги.')
        return redirect('books:book_list')
    
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Книга "{book.title}" успешно добавлена!')
            return redirect('books:book_list')
    else:
        form = BookForm()
    
    return render(request, 'books/add_book.html', {'form': form})


@librarian_required
def edit_book(request, book_id):
    """Редактирование информации о книге (только для библиотекарей и администраторов)"""
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'Книга "{book.title}" успешно обновлена!')
            return redirect('books:book_detail', pk=book.id)
    else:
        form = BookForm(instance=book)
    
    return render(request, 'books/book_form.html', {'form': form, 'title': 'Редактировать книгу'})


@login_required
def request_book(request, book_id):
    """Пользователь подает заявку на книгу"""
    book = get_object_or_404(Book, id=book_id)

    if request.user.is_librarian or request.user.is_admin:
        messages.error(request, 'Библиотекари и администраторы не могут подавать заявки на книги.')
        return redirect('books:book_detail', pk=book.id)

    # Проверяем, есть ли уже активная заявка или взятая книга
    existing_request = BookRequest.objects.filter(
        user=request.user,
        book=book,
        status__in=['pending', 'approved']
    ).exists()

    existing_borrow = BorrowRecord.objects.filter(
        user=request.user,
        book=book,
        returned=False
    ).exists()

    if existing_request:
        messages.warning(request, f'У вас уже есть активная заявка на книгу "{book.title}".')
        return redirect('books:book_detail', pk=book.id)

    if existing_borrow:
        messages.warning(request, f'У вас уже есть книга "{book.title}".')
        return redirect('books:book_detail', pk=book.id)

    # Создаем заявку
    book_request = BookRequest.objects.create(
        user=request.user,
        book=book,
        status='pending'
    )

    messages.success(request, f'Заявка на книгу "{book.title}" успешно подана! Ожидайте одобрения библиотекаря.')
    return redirect('books:book_detail', pk=book.id)


@login_required
def borrow_self(request, book_id):
    """Читатель берет книгу себе (только если заявка одобрена)"""
    book = get_object_or_404(Book, id=book_id)

    if request.user.is_librarian or request.user.is_admin:
        messages.info(request, 'Библиотекари и администраторы могут подать заявку на книгу.')
        return redirect('books:book_detail', pk=book.id)

    if not book.is_available:
        messages.error(request, 'Эта книга сейчас недоступна.')
        return redirect('books:book_list')

    # Проверяем одобренную заявку
    approved_request = BookRequest.objects.filter(
        user=request.user,
        book=book,
        status='approved'
    ).first()

    if not approved_request:
        messages.error(request, 'У вас нет одобренной заявки на эту книгу.')
        return redirect('books:book_detail', pk=book.id)

    existing_borrow = BorrowRecord.objects.filter(
        user=request.user,
        book=book,
        returned=False
    ).exists()

    if existing_borrow:
        messages.warning(request, f'У вас уже есть книга "{book.title}".')
        return redirect('books:book_list')

    from django.utils import timezone
    from datetime import timedelta

    borrow_record = BorrowRecord(
        user=request.user,
        book=book,
        borrow_date=timezone.now(),
        due_date=timezone.now() + timedelta(days=14),
        returned=False
    )
    borrow_record.save()

    book.available_copies -= 1
    book.save()

    # Помечаем заявку как выполненную (можно добавить новый статус, но пока оставим approved)
    approved_request.notes = f"Книга выдана {timezone.now().strftime('%d.%m.%Y %H:%M')}"
    approved_request.save()

    messages.success(request, f'Книга "{book.title}" успешно взята! Верните до {borrow_record.due_date.strftime("%d.%m.%Y")}.')
    return redirect('core:reader_dashboard')

@librarian_required
def delete_book(request, pk):
    """Удаление книги"""
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f'Книга "{book_title}" успешно удалена!')
        return redirect('books:book_list')
    
    return render(request, 'books/delete_book.html', {'book': book})