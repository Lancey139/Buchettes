# coding: utf-8
from apscheduler.schedulers.background import BackgroundScheduler

def start():
    scheduler = BackgroundScheduler()
    from .models import Buchette
    scheduler.add_job(Buchette.objects.update_buchette_temps_restant, 'interval', minutes=120)
    scheduler.start()

