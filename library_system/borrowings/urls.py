from django.urls import path
from . import views

app_name = 'borrowings'

urlpatterns = [
    path('my-books/', views.my_books, name='my_books'),
    path('active/', views.active_borrowings, name='active_borrowings'),
    path('borrow-form/', views.borrow_form, name='borrow_form'),
    path('return/<int:borrowing_id>/', views.return_book, name='return_book'),
]