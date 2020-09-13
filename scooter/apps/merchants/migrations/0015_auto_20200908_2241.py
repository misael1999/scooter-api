# Generated by Django 2.2.7 on 2020-09-09 03:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('merchants', '0014_auto_20200907_2230'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoryproducts',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='subcategoryproducts',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='subcategoryproducts',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='subcategories', to='merchants.CategoryProducts'),
        ),
    ]