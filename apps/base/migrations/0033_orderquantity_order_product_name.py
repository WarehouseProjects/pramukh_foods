# Generated by Django 2.2 on 2021-06-10 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0032_orderquantity_remaining_verfication_scan_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderquantity',
            name='order_product_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
