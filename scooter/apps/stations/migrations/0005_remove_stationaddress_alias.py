# Generated by Django 2.2.7 on 2020-05-28 21:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0004_station_allow_cancellations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stationaddress',
            name='alias',
        ),
    ]