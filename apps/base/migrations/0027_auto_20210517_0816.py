# Generated by Django 2.2 on 2021-05-17 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0026_auto_20210517_0815'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='margin',
            field=models.CharField(blank=True, default='0', max_length=100),
        ),
        migrations.AddField(
            model_name='product',
            name='mark_up',
            field=models.CharField(blank=True, default='0', max_length=100),
        ),
    ]
