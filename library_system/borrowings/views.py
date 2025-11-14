from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from books.models import Book, BorrowRecord, BookRequest
from .models import Borrowing
from .forms import BorrowBookForm
from users.decorators import librarian_required
from datetime import timedelta

@librarian_required
def borrow_form(request):
    """Форма для выдачи книги читателю (ТОЛЬКО для библиотекарей)"""
    if not (hasattr(request.user, 'is_librarian') and request.user.is_librarian) and not (hasattr(request.user, 'is_admin') and request.user.is_admin):
        messages.error(request, 'Недостаточно прав доступа! Только библиотекари могут выдавать книги.')
        return redirect('books:book_list')
    
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
    """Страница с книгами пользователя"""
    current_borrows = Borrowing.objects.filter(
        user=request.user,
        status__in=['active', 'overdue']
    ).select_related('book', 'book__author', 'book__genre')

    borrow_history = Borrowing.objects.filter(
        user=request.user,
        status='returned'
    ).select_related('book', 'book__author', 'book__genre').order_by('-returned_date')[:20]

    context = {
        'current_borrows': current_borrows,
        'borrow_history': borrow_history,
    }
    return render(request, 'borrowings/my_books.html', context)

@librarian_required
def active_borrowings(request):
    """Активные заимствования (ТОЛЬКО для библиотекарей)"""
    active_borrowings = Borrowing.objects.filter(
        status__in=['active', 'overdue']
    ).select_related('book', 'book__author', 'user').order_by('-borrowed_date')

    context = {
        'active_borrowings': active_borrowings,
    }
    return render(request, 'borrowings/active_borrowings.html', context)

@login_required
def return_book(request, borrowing_id):
    """Вернуть книгу (доступно читателям для своих книг)"""
    borrowing = get_object_or_404(Borrowing, id=borrowing_id)

    if borrowing.status == 'returned':
        messages.warning(request, 'Эта книга уже была возвращена.')
        return redirect('borrowings:my_books')

    is_owner = borrowing.user == request.user
    is_librarian = hasattr(request.user, 'is_librarian') and request.user.is_librarian
    is_admin = hasattr(request.user, 'is_admin') and request.user.is_admin

    if not is_owner and not is_librarian and not is_admin:
        messages.error(request, 'У вас нет прав для возврата этой книги.')
        return redirect('borrowings:my_books')

    borrowing.status = 'returned'
    borrowing.returned_date = timezone.now()
    borrowing.save()

    book = borrowing.book
    book.available_copies += 1
    book.save()

    messages.success(request, f'Книга "{book.title}" успешно возвращена!')

    if is_librarian or is_admin:
        return redirect('borrowings:active_borrowings')
    else:
        return redirect('borrowings:my_books')

@librarian_required
def manage_requests(request):
    """Управление заявками на книги (ТОЛЬКО для библиотекарей)"""
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')

        book_request = get_object_or_404(BookRequest, id=request_id)

        if action == 'approve':
            book_request.status = 'approved'
            book_request.approved_date = timezone.now()
            book_request.notes = notes
            book_request.save()
            messages.success(request, f'Заявка на книгу "{book_request.book.title}" одобрена для пользователя {book_request.user.username}.')
        elif action == 'reject':
            book_request.status = 'rejected'
            book_request.rejected_date = timezone.now()
            book_request.notes = notes
            book_request.save()
            messages.success(request, f'Заявка на книгу "{book_request.book.title}" отклонена для пользователя {book_request.user.username}.')

        return redirect('borrowings:manage_requests')

    # Получаем все заявки со связанными объектами
    pending_requests = BookRequest.objects.filter(status='pending').select_related('user', 'book', 'book__author')
    approved_requests = BookRequest.objects.filter(status='approved').select_related('user', 'book', 'book__author').order_by('-approved_date')[:50]
    rejected_requests = BookRequest.objects.filter(status='rejected').select_related('user', 'book', 'book__author').order_by('-rejected_date')[:50]

    context = {
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
    }
    return render(request, 'borrowings/manage_requests.html', context)
