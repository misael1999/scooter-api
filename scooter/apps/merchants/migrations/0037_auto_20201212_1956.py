# Generated by Django 2.2.7 on 2020-12-13 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0036_merchant_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='productmenucategory',
            name='is_option_repeatable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='productmenuoption',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
