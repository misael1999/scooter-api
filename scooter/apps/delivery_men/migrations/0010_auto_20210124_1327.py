# Generated by Django 2.2.7 on 2021-01-24 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery_men', '0009_auto_20201107_2255'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryman',
            name='device_name',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='deliveryman',
            name='device_version',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='deliveryman',
            name='is_android',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='deliveryman',
            name='version_code',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
