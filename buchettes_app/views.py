from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls.base import reverse_lazy


# Create your views here.

@login_required
def home(request):
    return render(request, 'buchettes_app/home.html')