# Generated by Django 5.0 on 2024-02-16 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0016_alter_wallet_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallet',
            name='last_transaction',
            field=models.CharField(default='0.00', max_length=100),
        ),
    ]