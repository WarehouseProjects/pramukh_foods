# Generated by Django 2.2 on 2021-05-21 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0028_auto_20210521_1313'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='margin',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='product',
            name='mark_up',
            field=models.FloatField(default=0.0),
        ),
    ]