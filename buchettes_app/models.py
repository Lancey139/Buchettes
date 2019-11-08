# coding: utf-8
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
import datetime as dt
import pytz

BUCHETTE_STATUS_CHOICES = [
    ('D', 'Demande de Buchette en effectuée'),
    ('E', 'L\'accusé a écrit sa défence'),
    ('A', 'Buchette acceptée par le comité'),
    ('P', 'Buchette payée en attente de validation'),
    ('S', 'Buchette soldée'),
    ('R', 'Buchette refusée par le comité'),
    ]

class BuchetteQuerySet(models.QuerySet):
    def buchettes_for_user(self, user):
        # Méthode en charge de renvoyer un query set contenant toutes les games
        # d'un utilisateur
        return self.filter(victime=user)

    def buchette_a_payer_for_user(self, user):
        # Méthode en charge de renvoyer un query set contenant toutes les games
        # d'un utilisateur
        return self.filter(victime=user, status_buchette='A')

    def buchette_a_defendre_for_user(self, user):
        # Méthode en charge de renvoyer un query set contenant toutes les games
        # d'un utilisateur
        return self.filter(victime=user, status_buchette='D')

    def buchettes_a_valider(self):
        return self.filter(status_buchette='E')

    def buchette_payees_a_confirmer_exclude_user(self, user):
        l_buchette_payee = self.filter(
            Q(status_buchette='P') | Q(status_buchette='V')
            )
        return l_buchette_payee.exclude(victime=user)

    def buchette_payees_a_confirmer_for_user(self, user):
        l_buchette_payee = self.filter(
            Q(status_buchette='P') | Q(status_buchette='V')
            )
        return l_buchette_payee.filter(victime=user)

    def buchette_totale_sans_R_for_user(self, user):
        l_buchette_totale = self.filter(victime=user)
        return l_buchette_totale.exclude(status_buchette='R')

    def update_buchette_temps_restant(self):
        # Méthode en charge de parcourir toutes les buchettes pour mettre a jour le temps de défense restant
        l_list_buchette_a_update = self.filter(status_buchette='D')

        for l_buche in l_list_buchette_a_update:
            l_current_date = dt.datetime.now()
            timezone = pytz.timezone("Europe/Paris")
            l_current_date_with_utc = timezone.localize(l_current_date)
            l_buche.temps_restant = dt.timedelta(days=2) - (l_current_date_with_utc - l_buche.date_buchette)
            if l_buche.temps_restant < dt.timedelta(seconds=0):
                l_buche.status_buchette = 'E'
                l_buche.message_defense = "Il est trop tard pour se défendre"
            l_buche.save()



class Buchette(models.Model):
    victime = models.ForeignKey(User, related_name="victime_buchette", on_delete=models.CASCADE)

    date_buchette = models.DateTimeField(auto_now_add=True)

    message_buchette = models.TextField(max_length=300)

    status_buchette = models.CharField(max_length=1, default='D',
                              choices=BUCHETTE_STATUS_CHOICES)

    message_defense = models.TextField(default='', max_length=300)

    temps_restant = models.DurationField(default=dt.timedelta(seconds=57))

    nom_membre_comite = models.TextField(default="")

    # On déclare le manager associé
    objects = BuchetteQuerySet.as_manager()

