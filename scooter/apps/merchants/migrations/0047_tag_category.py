# Generated by Django 2.2.7 on 2021-01-21 20:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0018_auto_20201231_1728'),
        ('merchants', '0046_auto_20210117_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='common.CategoryMerchant'),
        ),
    ]