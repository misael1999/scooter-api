# Generated by Django 2.2.7 on 2020-12-08 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0025_auto_20201205_1833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
