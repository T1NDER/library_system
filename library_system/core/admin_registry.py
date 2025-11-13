def register_models():
    """Функция для регистрации моделей в кастомной админке"""
    from core.admin import library_admin
    from books.models import Book, Author, Genre
    from books.admin import BookAdmin, AuthorAdmin, GenreAdmin
    from borrowings.models import Borrowing
    from borrowings.admin import BorrowingAdmin
    from users.models import User
    from users.admin import CustomUserAdmin
    
    library_admin.register(Book, BookAdmin)
    library_admin.register(Author, AuthorAdmin)
    library_admin.register(Genre, GenreAdmin)
    library_admin.register(Borrowing, BorrowingAdmin)
    library_admin.register(User, CustomUserAdmin)