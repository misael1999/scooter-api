# Generated by Django 2.2.7 on 2021-01-03 23:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0038_remove_productmenuoption_quantity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='categoryproducts',
            old_name='ordering',
            new_name='order',
        ),
    ]
