# forms.py
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'block text-sm font-medium text-gray-600 mt-1 p-2 w-full border rounded',
        'id': 'username',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'block text-sm font-medium text-gray-600 mt-1 p-2 w-full border rounded',
        'id': 'password',
    }))
