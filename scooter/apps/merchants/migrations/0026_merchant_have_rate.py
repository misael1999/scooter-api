# Generated by Django 2.2.7 on 2020-10-21 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0025_auto_20201010_1720'),
    ]

    operations = [
        migrations.AddField(
            model_name='merchant',
            name='have_rate',
            field=models.BooleanField(default=True),
        ),
    ]