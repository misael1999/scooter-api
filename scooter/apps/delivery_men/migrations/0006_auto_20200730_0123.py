# Generated by Django 2.2.7 on 2020-07-30 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery_men', '0005_auto_20200723_1528'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryman',
            name='last_time_update_location',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='deliverymanaddress',
            name='exterior_number',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='deliverymanaddress',
            name='postal_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='deliverymanaddress',
            name='street',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='deliverymanaddress',
            name='suburb',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
    ]
