from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    company = forms.CharField()
    client = forms.CharField()
    first_name = forms.CharField()

    class Meta:
        model = User
        fields = ["username", "first_name", 'last_name', "email", "password1", "password2", "company", 'client']


class SourceForm(forms.Form):
    name = forms.CharField()
    url = forms.URLField()

    class Meta:
        model = Source
        fields = ['name', 'url']


class StoryForm(forms.Form):
    source = Source.objects.all()
    company = Company.objects.all()
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    source = forms.ModelChoiceField(queryset=source)
    pub_date = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'Published Date'}))
    body_text = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Body'}))
    url = forms.URLField(widget=forms.TextInput(attrs={'placeholder': 'Url'}))
    company = forms.ModelMultipleChoiceField(queryset=company)

    class Meta:
        model = Story
        fields = ['title', 'source', 'pub_date', 'body_text', 'url']
