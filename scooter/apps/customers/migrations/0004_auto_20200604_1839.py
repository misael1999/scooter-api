# Generated by Django 2.2.7 on 2020-06-04 23:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_customeraddress_type_address'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='customeraddress',
            table='customers_customer_address',
        ),
    ]