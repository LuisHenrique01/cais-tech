# Generated by Django 4.2.1 on 2023-05-26 19:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicotransacao',
            name='api_status',
        ),
    ]
