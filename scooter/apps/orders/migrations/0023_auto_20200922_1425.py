# Generated by Django 2.2.7 on 2020-09-22 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0022_auto_20200921_1949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ratingorder',
            name='rating',
            field=models.IntegerField(default=1),
        ),
    ]
