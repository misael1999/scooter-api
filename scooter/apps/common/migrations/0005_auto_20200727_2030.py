# Generated by Django 2.2.7 on 2020-07-28 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_appversion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appversion',
            name='version_number',
            field=models.CharField(max_length=5),
        ),
    ]
