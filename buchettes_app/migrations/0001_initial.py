# Generated by Django 2.2.5 on 2019-10-14 11:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Buchette',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_buchette', models.DateTimeField(auto_now_add=True)),
                ('message_buchette', models.TextField()),
                ('status_buchette', models.CharField(choices=[('D', 'Demande de Buchette en cours'), ('A', 'Buchette acceptée par le comité'), ('S', 'Buchette soldée')], default='F', max_length=1)),
                ('victime', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='victime_buchette', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]