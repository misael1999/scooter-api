# Generated by Django 2.2.7 on 2020-07-27 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_order_member_station'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_safe_order',
            field=models.BooleanField(default=False),
        ),
    ]