# Generated by Django 2.2.7 on 2020-09-01 07:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0018_orderdetailmenu_price'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'get_latest_by': 'created', 'ordering': ['-created']},
        ),
        migrations.AlterModelOptions(
            name='ratingorder',
            options={'get_latest_by': 'created', 'ordering': ['-created']},
        ),
    ]
