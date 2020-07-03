# Generated by Django 2.2.7 on 2020-07-03 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0008_auto_20200624_1309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stationaddress',
            name='station',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='address', to='stations.Station'),
        ),
        migrations.AlterField(
            model_name='stationschedule',
            name='station',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='stations.Station'),
        ),
        migrations.AlterField(
            model_name='stationservice',
            name='station',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='stations.Station'),
        ),
    ]
