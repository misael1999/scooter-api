# Generated by Django 2.2.7 on 2020-08-25 16:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0009_auto_20200818_0017'),
        ('merchants', '0008_auto_20200823_1129'),
        ('orders', '0015_auto_20200824_2305'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdetailmenu',
            name='name_option',
        ),
        migrations.RemoveField(
            model_name='orderdetailmenu',
            name='option',
        ),
        migrations.RemoveField(
            model_name='orderdetailmenu',
            name='price_option',
        ),
        migrations.CreateModel(
            name='OrderDetailMenuOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name_option', models.CharField(max_length=100)),
                ('price_option', models.FloatField(blank=True, default=0, null=True)),
                ('detail_menu', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='options', to='orders.OrderDetailMenu')),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='order_menu_option', to='merchants.ProductMenuOption')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='common.Status')),
            ],
            options={
                'db_table': 'orders_order_detail_menu_option',
            },
        ),
    ]
