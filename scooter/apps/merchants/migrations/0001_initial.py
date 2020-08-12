# Generated by Django 2.2.7 on 2020-08-12 00:46

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0006_categorymerchant_subcategorymerchant'),
        ('customers', '0006_auto_20200801_1243'),
    ]

    operations = [
        migrations.CreateModel(
            name='Merchant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('contact_person', models.CharField(max_length=80)),
                ('picture', models.ImageField(blank=True, null=True, upload_to='merchants/pictures/')),
                ('merchant_name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=15)),
                ('is_delivery_by_store', models.BooleanField(default=False)),
                ('information_is_complete', models.BooleanField(default=False)),
                ('reputation', models.FloatField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='common.CategoryMerchant')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='common.Status')),
                ('subcategory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='common.SubcategoryMerchant')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MerchantAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('full_address', models.CharField(max_length=300)),
                ('references', models.CharField(blank=True, max_length=150, null=True)),
                ('point', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('merchant', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='address', to='merchants.Merchant')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='common.Status')),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MerchantSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('from_hour', models.TimeField()),
                ('to_hour', models.TimeField()),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='merchants.Merchant')),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='common.Schedule')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='common.Status')),
            ],
            options={
                'unique_together': {('merchant', 'schedule')},
            },
        ),
        migrations.CreateModel(
            name='MemberMerchant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('total_orders', models.PositiveIntegerField(default=0)),
                ('total_orders_cancelled', models.PositiveIntegerField(default=0)),
                ('first_order_date', models.DateTimeField(auto_now_add=True)),
                ('last_order_date', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.Customer')),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='merchants.Merchant')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='common.Status')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'merchants_member_merchant',
                'unique_together': {('merchant', 'customer')},
            },
        ),
    ]