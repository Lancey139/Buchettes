# coding: utf-8
from django.apps import AppConfig



class BuchettesAppConfig(AppConfig):
    name = 'buchettes_app'

    def ready(self):
        from buchettes_app import appScheduler
        appScheduler.start()
