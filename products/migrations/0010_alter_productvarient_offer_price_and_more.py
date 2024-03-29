# Generated by Django 5.0 on 2024-02-21 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_productvarient_offer_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvarient',
            name='offer_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AlterField(
            model_name='productvarient',
            name='stock',
            field=models.FloatField(),
        ),
    ]
