# Generated by Django 2.2.7 on 2020-09-01 07:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20200812_1953'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'get_latest_by': 'created', 'ordering': ['-created']},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'get_latest_by': 'created', 'ordering': ['-created']},
        ),
    ]
