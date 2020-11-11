# Generated by Django 2.2.7 on 2020-11-10 23:53

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0015_typezone'),
        ('stations', '0008_station_area'),
    ]

    operations = [
        migrations.AddField(
            model_name='station',
            name='promotions_zones_activated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='stationschedule',
            name='is_open',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='StationZone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=120)),
                ('description', models.CharField(blank=True, max_length=150, null=True)),
                ('poly', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326)),
                ('base_rate_price', models.FloatField(blank=True, null=True)),
                ('from_hour', models.TimeField(blank=True, null=True)),
                ('to_hour', models.TimeField(blank=True, null=True)),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stations.Station')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='common.Status')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='common.TypeZone')),
            ],
            options={
                'ordering': ['-created'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
    ]
