# Generated by Django 2.2.7 on 2020-09-10 02:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0017_subcategorysectionproducts'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='products', to='merchants.SubcategorySectionProducts'),
        ),
    ]
