# Generated by Django 2.2.7 on 2020-10-24 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0026_merchant_have_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='merchant',
            name='delivery_payment',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='merchant',
            name='from_price_pay_delivery',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='merchant',
            name='pay_delivery',
            field=models.BooleanField(default=False),
        ),
    ]
