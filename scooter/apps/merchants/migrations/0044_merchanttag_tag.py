# Generated by Django 2.2.7 on 2021-01-16 17:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0018_auto_20201231_1728'),
        ('merchants', '0043_auto_20210114_1555'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='common.Status')),
            ],
            options={
                'ordering': ['-created'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MerchantTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('tag_name', models.CharField(max_length=50)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='tags', to='merchants.Merchant')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='common.Status')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='merchants_tags', to='merchants.Tag')),
            ],
            options={
                'ordering': ['-created'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
    ]