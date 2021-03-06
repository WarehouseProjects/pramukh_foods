# Generated by Django 2.2 on 2021-05-13 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0024_auto_20210429_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='margin',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='mark_up',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=55, verbose_name='Product Name'),
        ),
    ]
