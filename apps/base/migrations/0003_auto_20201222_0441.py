# Generated by Django 2.2 on 2020-12-22 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_auto_20201216_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adjustproduct',
            name='new_price',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='adjustproduct',
            name='old_price',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='customer',
            name='max_threshold',
            field=models.FloatField(default=0, verbose_name='Maximum threshold'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='min_threshold',
            field=models.FloatField(default=0, verbose_name='Minimum threshold'),
        ),
        migrations.AlterField(
            model_name='order',
            name='amount',
            field=models.FloatField(blank=True, default=0, verbose_name='Total amount'),
        ),
        migrations.AlterField(
            model_name='order',
            name='amount_recieved',
            field=models.FloatField(default=0, verbose_name='Recieved amount'),
        ),
        migrations.AlterField(
            model_name='order',
            name='remaining_amount',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='orderquantity',
            name='discount',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='orderquantity',
            name='price',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='paymenthistory',
            name='amount_recieved',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='purchase_cost',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='sale_price',
            field=models.FloatField(default=0, verbose_name='Selling Price'),
        ),
        migrations.AlterField(
            model_name='productpacksizes',
            name='price',
            field=models.FloatField(default=0),
        ),
    ]
