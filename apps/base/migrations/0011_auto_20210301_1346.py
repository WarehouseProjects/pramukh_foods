# Generated by Django 2.2 on 2021-03-01 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_order_invoice_pdf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='weight',
            field=models.FloatField(blank=True, null=True, verbose_name='Weight '),
        ),
    ]
