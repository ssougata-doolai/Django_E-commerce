# Generated by Django 2.2.3 on 2020-01-15 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_cart_buy_now'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='place_order_now',
            field=models.BooleanField(default=False),
        ),
    ]
