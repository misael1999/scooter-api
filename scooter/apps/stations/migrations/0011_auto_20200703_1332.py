# Generated by Django 2.2.7 on 2020-07-03 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0010_vehicle_type_vehicle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stationaddress',
            name='references',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
