# Generated by Django 2.2.7 on 2020-12-06 00:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0034_auto_20201205_1557'),
        ('payments', '0004_card_conekta_id'),
        ('orders', '0024_order_date_update_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='card_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='payments.Card'),
        ),
        migrations.AddField(
            model_name='order',
            name='is_payment_online',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='order_conekta_id',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='merchants.MerchantPaymentMethod'),
        ),
    ]
