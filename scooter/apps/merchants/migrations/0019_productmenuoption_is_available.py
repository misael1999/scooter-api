# Generated by Django 2.2.7 on 2020-09-10 02:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0018_product_section'),
    ]

    operations = [
        migrations.AddField(
            model_name='productmenuoption',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ]
