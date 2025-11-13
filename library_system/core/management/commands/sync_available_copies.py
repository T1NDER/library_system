from django.core.management.base import BaseCommand
from books.models import Book

class Command(BaseCommand):
    help = 'Синхронизирует available_copies с фактическими выданными книгами'
    
    def handle(self, *args, **options):
        books = Book.objects.all()
        for book in books:
            book.update_availability()
        
        self.stdout.write(
            self.style.SUCCESS('Количество доступных копий успешно синхронизировано')
        )