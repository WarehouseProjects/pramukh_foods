# Generated by Django 2.2 on 2021-05-21 13:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0027_auto_20210517_0816'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='margin',
        ),
        migrations.RemoveField(
            model_name='product',
            name='mark_up',
        ),
    ]