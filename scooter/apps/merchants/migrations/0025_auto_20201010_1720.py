# Generated by Django 2.2.7 on 2020-10-10 22:20

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0024_auto_20201008_1642'),
    ]

    operations = [
        migrations.AddField(
            model_name='merchant',
            name='is_delivery_free',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='merchant',
            name='point',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]
