# Generated by Django 2.2.7 on 2020-07-17 18:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0002_auto_20200704_1101'),
        ('delivery_men', '0004_deliveryman_vehicle'),
        ('common', '0003_auto_20200704_1155'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customers', '0002_customer_user'),
        ('orders', '0006_order_validate_qr'),
    ]

    operations = [
        migrations.CreateModel(
            name='RatingOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('rating', models.IntegerField(default=1)),
                ('delivery_man', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='delivery_men.DeliveryMan')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rated_order', to='orders.Order')),
                ('rating_customer', models.ForeignKey(help_text='Customer that emits the rating', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rating_customer', to='customers.Customer')),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stations.Station')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='common.Status')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
    ]
