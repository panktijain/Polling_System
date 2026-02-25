from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Poll


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class PollCreationForm(forms.ModelForm):
    # Form for creating a poll, includes category and description
    class Meta:
        model = Poll
        fields = ('question', 'description', 'category')
        widgets = {
            'question': forms.TextInput(attrs={
                'placeholder': 'Enter your poll question...',
                'class': 'form-input',
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Enter a description (optional)...',
                'class': 'form-textarea',
                'rows': 3,
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
