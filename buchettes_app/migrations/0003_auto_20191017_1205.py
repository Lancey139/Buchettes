# Generated by Django 2.2.5 on 2019-10-17 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buchettes_app', '0002_auto_20191016_1236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buchette',
            name='status_buchette',
            field=models.CharField(choices=[('D', 'Demande de Buchette en cours'), ('A', 'Buchette acceptée par le comité'), ('P', 'Buchette payée en attente de validation'), ('S', 'Buchette soldée'), ('R', 'Buchette refusée par le comité')], default='D', max_length=1),
        ),
    ]
