# Generated by Django 2.2.7 on 2020-09-01 07:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0009_auto_20200825_2239'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='categoryproducts',
            options={'get_latest_by': 'created', 'ordering': ['-created']},
        ),
        migrations.AlterModelOptions(
            name='merchant',
            options={'get_latest_by': 'created', 'ordering': ['-created']},
        ),
        migrations.AlterModelOptions(
            name='merchantaddress',
            options={'get_latest_by': 'created', 'ordering': ['-created']},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'get_latest_by': 'created', 'ordering': ['-created']},
        ),
        migrations.AlterModelOptions(
            name='productmenucategory',
            options={'get_latest_by': 'created', 'ordering': ['created']},
        ),
        migrations.AlterModelOptions(
            name='productmenuoption',
            options={'get_latest_by': 'created', 'ordering': ['created']},
        ),
        migrations.AlterModelOptions(
            name='typeoption',
            options={'get_latest_by': 'created', 'ordering': ['-created']},
        ),
    ]
