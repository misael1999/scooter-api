# Generated by Django 2.2.7 on 2020-07-23 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0002_auto_20200704_1101'),
    ]

    operations = [
        migrations.AddField(
            model_name='station',
            name='phone_number',
            field=models.CharField(default=2384080578, max_length=15),
            preserve_default=False,
        ),
    ]
