# Generated by Django 2.2.7 on 2020-07-04 16:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_notification_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderstatus',
            name='type_service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='common.Service'),
        ),
    ]
