# Generated by Django 2.2 on 2021-03-19 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_auto_20210318_0921'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ageing',
            field=models.IntegerField(blank=True, default=0, max_length=100, null=True),
        ),
    ]
