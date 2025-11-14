from django import forms
from books.models import Book
from .models import Borrowing
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class BorrowBookForm(forms.ModelForm):
    class Meta:
        model = Borrowing  
        fields = ['book', 'user', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'book': forms.Select(attrs={'class': 'form-select'}),
            'user': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'book': 'Книга',
            'user': 'Пользователь',
            'due_date': 'Срок возврата',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['book'].queryset = Book.objects.filter(available_copies__gt=0)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        user = cleaned_data.get('user')

        if book and user:
            existing_borrowing = Borrowing.objects.filter(
                user=user,
                book=book,
                status__in=['active', 'overdue']
            ).exists()

            if existing_borrowing:
                raise forms.ValidationError(
                    'Этот читатель уже взял данную книгу и еще не вернул ее.'
                )

        return cleaned_data

class ReturnBookForm(forms.Form):
    condition_choices = [
        ('excellent', 'Отличное'),
        ('good', 'Хорошее'),
        ('satisfactory', 'Удовлетворительное'),
        ('damaged', 'Повреждена'),
    ]
    condition = forms.ChoiceField(choices=condition_choices, label='Состояние книги')
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label='Примечания')

