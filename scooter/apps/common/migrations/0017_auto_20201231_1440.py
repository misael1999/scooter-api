# Generated by Django 2.2.7 on 2020-12-31 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0016_question'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='title',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]