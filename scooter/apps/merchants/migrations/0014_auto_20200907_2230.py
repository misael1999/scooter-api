# Generated by Django 2.2.7 on 2020-09-08 03:30

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0011_appversion_build_number'),
        ('merchants', '0013_merchant_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='merchant',
            name='from_preparation_time',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='merchant',
            name='to_preparation_time',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='categoryproducts',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='merchants/categories/', validators=[django.core.validators.FileExtensionValidator(['jpg', 'png', 'jpeg'])]),
        ),
        migrations.AlterField(
            model_name='merchant',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='merchants/pictures/', validators=[django.core.validators.FileExtensionValidator(['jpg', 'png', 'jpeg'])]),
        ),
        migrations.AlterField(
            model_name='product',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='merchants/products/', validators=[django.core.validators.FileExtensionValidator(['jpg', 'png', 'jpeg'])]),
        ),
        migrations.CreateModel(
            name='TypeMenuMerchant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=30)),
                ('slug_name', models.CharField(max_length=30)),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='common.Status')),
            ],
            options={
                'ordering': ['-created'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubcategoryProducts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=70)),
                ('picture', models.ImageField(blank=True, null=True, upload_to='merchants/subcategories/', validators=[django.core.validators.FileExtensionValidator(['jpg', 'png', 'jpeg'])])),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='merchants.CategoryProducts')),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='merchants.Merchant')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='common.Status')),
            ],
            options={
                'ordering': ['-created'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='merchant',
            name='type_menu',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='merchants.TypeMenuMerchant'),
        ),
        migrations.AddField(
            model_name='product',
            name='subcategory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='products', to='merchants.SubcategoryProducts'),
        ),
    ]