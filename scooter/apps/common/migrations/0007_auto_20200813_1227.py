# Generated by Django 2.2.7 on 2020-08-13 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0006_categorymerchant_subcategorymerchant'),
    ]

    operations = [
        migrations.AddField(
            model_name='categorymerchant',
            name='image',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='subcategorymerchant',
            name='image',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
