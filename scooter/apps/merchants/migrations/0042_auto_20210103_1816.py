# Generated by Django 2.2.7 on 2021-01-04 00:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0041_auto_20210103_1814'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='categoryproducts',
            options={'get_latest_by': 'created', 'ordering': ['ordering', '-created']},
        ),
    ]
