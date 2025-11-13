from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False, label='Телефон')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['role']
        labels = {
            'role': 'Роль пользователя'
        }