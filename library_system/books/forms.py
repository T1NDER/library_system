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