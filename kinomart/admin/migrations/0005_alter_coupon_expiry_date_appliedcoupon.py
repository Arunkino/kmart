# Generated by Django 5.0 on 2024-02-16 07:01

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_unique_admin', '0004_alter_coupon_coupon_code_alter_coupon_expiry_date'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='expiry_date',
            field=models.DateField(default=datetime.datetime(2024, 3, 17, 12, 31, 38, 328145)),
        ),
        migrations.CreateModel(
            name='AppliedCoupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_unique_admin.coupon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
