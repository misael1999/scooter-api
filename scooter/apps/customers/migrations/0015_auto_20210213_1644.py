# Generated by Django 2.2.7 on 2021-02-13 22:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0014_customer_total_orders'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerpromotion',
            name='history',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='customers.HistoryCustomerInvitation'),
        ),
    ]
