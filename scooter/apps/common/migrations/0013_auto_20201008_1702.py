# Generated by Django 2.2.7 on 2020-10-08 22:02

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0012_area_zone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='area',
            name='poly',
            field=django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326),
        ),
    ]