# coding: utf-8
from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Buchette


class BuchetteForm(ModelForm):
    class Meta:
        model = Buchette
        exclude = ('date_buchette', 'status_buchette')


class UserCreationFormEmail(UserCreationForm):
    #  Surcharge du user creation form standard dans le but d'ajouter le champs email
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    """
    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    """
