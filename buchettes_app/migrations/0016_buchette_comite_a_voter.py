# Generated by Django 3.0.6 on 2020-05-26 14:07

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('buchettes_app', '0015_auto_20200526_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='buchette',
            name='comite_a_voter',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
