# Generated by Django 5.0 on 2024-03-11 09:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offer', '0020_alter_offer_expiry_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='expiry_date',
            field=models.DateField(default=datetime.datetime(2024, 4, 10, 14, 57, 29, 154554)),
        ),
    ]
