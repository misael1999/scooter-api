# Generated by Django 2.2.7 on 2020-08-01 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0005_auto_20200731_2121'),
    ]

    operations = [
        migrations.AddField(
            model_name='customeraddress',
            name='category',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='customeraddress',
            name='alias',
            field=models.CharField(max_length=100),
        ),
    ]
