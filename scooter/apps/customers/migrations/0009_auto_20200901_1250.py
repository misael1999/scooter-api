# Generated by Django 2.2.7 on 2020-09-01 17:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0010_auto_20200901_0256'),
        ('customers', '0008_auto_20200901_0256'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CustomerInvitation',
            new_name='CustomerPromotion',
        ),
        migrations.AlterModelTable(
            name='customerpromotion',
            table='customers_customer_promotions',
        ),
    ]
