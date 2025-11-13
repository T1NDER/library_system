from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from books.models import Book, BorrowRecord
from .forms import BorrowBookForm
from users.decorators import librarian_required

@librarian_required
def borrow_form(request):
    """Форма для выдачи книги читателю (ТОЛЬКО для библиотекарей)"""
    initial = {}
    book_id = request.GET.get('book')
    if book_id:
        try:
            book = Book.objects.get(id=book_id)
            initial['book'] = book
        except Book.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = BorrowBookForm(request.POST)
        if form.is_valid():
            borrowing = form.save(commit=False)
            borrowing.borrow_date = timezone.now()
            borrowing.save()
            
            book = borrowing.book
            book.available_copies -= 1
            book.save()
            
            messages.success(request, f'Книга "{book.title}" успешно выдана читателю {borrowing.user.get_full_name()}!')
            return redirect('borrowings:active_borrowings')
    else:
        form = BorrowBookForm(initial=initial)
    
    return render(request, 'borrowings/borrow_form.html', {'form': form})

@login_required
def my_books(request):
    """Страница с книгами пользователя (только просмотр)"""
    current_borrows = BorrowRecord.objects.filter(
        user=request.user, 
        returned=False
    ).select_related('book', 'book__author', 'book__genre')
    
    borrow_history = BorrowRecord.objects.filter(
        user=request.user, 
        returned=True
    ).select_related('book', 'book__author', 'book__genre').order_by('-return_date')[:20]
    
    context = {
        'current_borrows': current_borrows,
        'borrow_history': borrow_history,
    }
    return render(request, 'borrowings/my_books.html', context)

@librarian_required
def active_borrowings(request):
    """Активные заимствования (ТОЛЬКО для библиотекарей)"""
    active_borrowings = BorrowRecord.objects.filter(
        returned=False
    ).select_related('book', 'book__author', 'user').order_by('-borrow_date')
    
    context = {
        'active_borrowings': active_borrowings,
    }
    return render(request, 'borrowings/active_borrowings.html', context)

@login_required
def return_book(request, borrowing_id):
    """Вернуть книгу (доступно и читателям для своих книг)"""
    borrowing = get_object_or_404(BorrowRecord, id=borrowing_id)
    
    # Проверяем права: библиотекарь ИЛИ владелец книги
    is_librarian = hasattr(request.user, 'is_librarian') and request.user.is_librarian()
    if not is_librarian and borrowing.user != request.user:
        messages.error(request, 'У вас нет прав для возврата этой книги.')
        return redirect('borrowings:my_books')
    
    if borrowing.returned:
        messages.warning(request, 'Эта книга уже была возвращена.')
        return redirect('borrowings:active_borrowings' if is_librarian else 'borrowings:my_books')
    
    if request.method == 'POST':
        borrowing.returned = True
        borrowing.return_date = timezone.now()
        borrowing.save()
        
        book = borrowing.book
        book.available_copies += 1
        book.save()
        
        messages.success(request, f'Книга "{book.title}" успешно возвращена!')
        
        if is_librarian:
            return redirect('borrowings:active_borrowings')
        else:
            return redirect('borrowings:my_books')
    
    return render(request, 'borrowings/return_book.html', {'borrowing': borrowing})