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
    class Meta:
        model = Poll
        fields = ('question',)
        widgets = {
            'question': forms.TextInput(attrs={
                'placeholder': 'Enter your poll question...',
                'class': 'form-input',
            })
        }
