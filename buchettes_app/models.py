from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

BUCHETTE_STATUS_CHOICES = [
    ('D', 'Demande de Buchette en cours'),
    ('A', 'Buchette acceptée par le comité'),
    ('S', 'Buchette soldée'),
    ]

class BuchetteQuerySet(models.QuerySet):
    def buchettes_for_user(self, user):
        # Méthode en charge de renvoyer un qury set contenant toutes les games
        # d'un utilisateur
        return self.filter(victime=user)


class Buchette(models.Model):
    victime = models.ForeignKey(User, related_name="victime_buchette", on_delete=models.CASCADE)

    date_buchette = models.DateTimeField(auto_now_add=True)

    message_buchette = models.TextField()

    status_buchette = models.CharField(max_length=1, default='D',
                              choices=BUCHETTE_STATUS_CHOICES)

    # On déclare le manager associé
    objects = BuchetteQuerySet.as_manager()

