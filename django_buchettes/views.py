"""
Fonction de la page d'acceuil
"""

from django.shortcuts import render, redirect


def welcome(request):
    """
    Page d'acceuil
    """
    if request.user.is_authenticated:
        return redirect('player_home')
    else:
        return render(request, 'django_buchettes/welcome.html')
