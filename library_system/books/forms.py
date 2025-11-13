from django import forms
from .models import Book, Author, Genre

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'isbn', 'description', 
                 'publication_year', 'publisher', 'total_copies']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'publication_year': forms.NumberInput(attrs={'min': 1000, 'max': 2100}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Сделаем ISBN необязательным в форме
        self.fields['isbn'].required = False
    
    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        # Обрабатываем случай когда isbn = None или пустая строка
        if isbn:
            isbn = isbn.strip()
            if not isbn:  # Если после strip осталась пустая строка
                return None
            return isbn
        return None  # Если isbn = None, возвращаем None
    
    def save(self, commit=True):
        book = super().save(commit=False)
        # Устанавливаем available_copies равным total_copies при создании
        if not book.pk:  # Если книга новая
            book.available_copies = book.total_copies
        if commit:
            book.save()
        return book
    
    
class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'biography', 'birth_date', 'death_date']
        widgets = {
            'biography': forms.Textarea(attrs={'rows': 4}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'death_date': forms.DateInput(attrs={'type': 'date'}),
        }

class BookSearchForm(forms.Form):
    query = forms.CharField(
        max_length=100, 
        required=False, 
        label='Поиск',
        widget=forms.TextInput(attrs={'placeholder': 'Название, автор, жанр...'})
    )
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        label='Жанр'
    )
    available_only = forms.BooleanField(
        required=False,
        label='Только доступные'
    )