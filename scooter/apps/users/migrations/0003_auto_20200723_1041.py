# Generated by Django 2.2.7 on 2020-07-23 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='comments',
            field=models.TextField(blank=True, null=True),
        ),
    ]
