# Generated by Django 2.2.7 on 2020-06-06 03:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20200605_2011'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='from_address_id',
            new_name='from_address',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='to_address_id',
            new_name='to_address',
        ),
    ]