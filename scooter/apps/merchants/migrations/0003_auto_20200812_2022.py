# Generated by Django 2.2.7 on 2020-08-13 01:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0002_categoryproducts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoryproducts',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='merchants/categories/'),
        ),
    ]