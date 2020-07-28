# Generated by Django 2.2.7 on 2020-07-27 23:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_auto_20200704_1155'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('alias', models.CharField(max_length=30)),
                ('comments', models.CharField(max_length=40)),
                ('version_number', models.FloatField()),
                ('priority', models.BooleanField(default=False)),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='common.Status')),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
    ]
