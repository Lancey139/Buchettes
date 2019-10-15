from django.forms import ModelForm

from .models import Buchette

class BuchetteForm(ModelForm):
    class Meta:
        model = Buchette
        exclude = ('date_buchette', 'status_buchette')

