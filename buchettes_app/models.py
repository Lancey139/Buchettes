from django.db import models
from django.contrib.auth.models import User

BUCHETTE_STATUS_CHOICES = [
    ('D', 'Demande de Buchette en cours'),
    ('A', 'Buchette acceptée par le comité'),
    ('S', 'Buchette soldée'),
    ]


class Buchette(models.Model):
    victime = models.ForeignKey(User, related_name="victime_buchette", on_delete=models.CASCADE)

    date_buchette = models.DateTimeField(auto_now_add=True)

    message_buchette = models.TextField()

    status_buchette = models.CharField(max_length=1, default='D',
                              choices=BUCHETTE_STATUS_CHOICES)