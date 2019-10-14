from django.contrib import admin
from .models import Buchette
# Register your models here.

# On créé une classe qui va permettre de personaliser l'interface admin pour les games
@admin.register(Buchette)
class BuchetteAdmin(admin.ModelAdmin):
    list_display = ('id', 'victime', 'status_buchette')
    list_editable = ('status_buchette', )