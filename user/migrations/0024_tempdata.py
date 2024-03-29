# Generated by Django 5.0 on 2024-03-02 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0023_alter_wishlist_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='TempData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_method', models.CharField(max_length=50)),
                ('address_id', models.CharField(max_length=50)),
                ('instructions', models.CharField(max_length=100)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
    ]
