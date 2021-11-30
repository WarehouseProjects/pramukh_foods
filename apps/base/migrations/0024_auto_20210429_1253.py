# Generated by Django 2.2 on 2021-04-29 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_auto_20210423_1100'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='lifetime_quantity',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='product',
            name='out_of_stock_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='city',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='contact_person_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='phone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='state',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='zipcode',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='adjustproduct',
            name='new_quantity',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='adjustproduct',
            name='old_quantity',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='initialproduct',
            name='quantity',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='orderquantity',
            name='quantity',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='orderquantity',
            name='scan_quantity',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='orderquantity',
            name='verfication_scan_quantity',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='available_quantity',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='low_stock_qauntity',
            field=models.FloatField(default=5),
        ),
    ]
