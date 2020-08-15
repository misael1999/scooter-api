# Generated by Django 2.2.7 on 2020-08-13 05:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0006_categorymerchant_subcategorymerchant'),
        ('merchants', '0003_auto_20200812_2022'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=70)),
                ('description', models.CharField(max_length=400)),
                ('description_long', models.TextField(blank=True, null=True)),
                ('stock', models.PositiveIntegerField()),
                ('price', models.FloatField()),
                ('picture', models.ImageField(blank=True, null=True, upload_to='merchants/products/')),
                ('total_sales', models.PositiveIntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='merchants.CategoryProducts')),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='merchants.Merchant')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='common.Status')),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
    ]