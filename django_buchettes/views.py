"""
Fonction de la page d'acceuil
"""

from django.shortcuts import render, redirect


def welcome(request):
    """
    Page d'acceuil
    """
    return redirect('player_home')

