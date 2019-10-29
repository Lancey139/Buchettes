# coding: utf-8
from django.forms import ModelForm, Textarea
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Buchette


class BuchetteForm(ModelForm):
    class Meta:
        model = Buchette
        exclude = ('date_buchette', 'status_buchette', 'message_defense', 'temps_restant')


class DefenceForm(ModelForm):
    class Meta:
        model = Buchette
        exclude = ('date_buchette', 'status_buchette', 'victime', 'temps_restant')
        widgets = {
            'message_buchette': Textarea(attrs={'readonly': True}),
        }


class UserCreationFormEmail(UserCreationForm):
    #  Surcharge du user creation form standard dans le but d'ajouter le champs email
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

