# Generated by Django 2.2 on 2020-11-24 08:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=100, null=True)),
                ('password', models.CharField(max_length=256)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('phone_number', models.CharField(blank=True, max_length=16)),
                ('is_active', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('user_type', models.CharField(blank=True, choices=[('SALESPERSON', 'SALESPERSON'), ('ADMIN', 'ADMIN'), ('WAREHOUSE', 'WAREHOUSE')], max_length=12, null=True)),
                ('last_login', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Billing_Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField(blank=True, null=True)),
                ('city', models.CharField(blank=True, max_length=60, null=True)),
                ('state', models.CharField(blank=True, max_length=50, null=True)),
                ('country', models.CharField(blank=True, max_length=30, null=True)),
                ('zipcode', models.CharField(blank=True, max_length=10, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Category Name')),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('store_name', models.CharField(blank=True, max_length=60, null=True)),
                ('both_address_same', models.BooleanField(default=False)),
                ('min_threshold', models.IntegerField(default=0, verbose_name='Minimum threshold')),
                ('max_threshold', models.IntegerField(default=0, verbose_name='Maximum threshold')),
                ('sales_tax_id', models.CharField(blank=True, max_length=50, null=True)),
                ('sales_tax_image', models.FileField(blank=True, null=True, upload_to='media/')),
                ('terms', models.FileField(blank=True, null=True, upload_to='media/')),
                ('billing_address', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customers', to='base.Billing_Address')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ForceAppUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('android', models.CharField(max_length=10)),
                ('ios', models.CharField(max_length=10)),
                ('android_force', models.BooleanField(null=True)),
                ('ios_force', models.BooleanField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Miscellaneous',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
                ('content', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_no', models.CharField(blank=True, max_length=10, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('detail', models.TextField(blank=True, null=True, verbose_name='Order Details')),
                ('amount', models.IntegerField(blank=True, default=0, verbose_name='Total amount')),
                ('amount_recieved', models.IntegerField(default=0, verbose_name='Recieved amount')),
                ('remaining_amount', models.PositiveIntegerField(default=0)),
                ('payment_status', models.CharField(blank=True, choices=[('PARTIAL', 'PARTIALLY PAID'), ('FULL', 'FULLY PAID'), ('NOT_PAID', 'NOT PAID')], max_length=10, null=True)),
                ('status', models.CharField(blank=True, choices=[('OPEN', 'OPEN'), ('IN_PROCESS', 'IN_PROCESS'), ('COMPLETED', 'COMPLETED')], max_length=12, null=True)),
                ('submitted', models.BooleanField(default=False)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('delivery_date', models.DateField(blank=True, null=True)),
                ('verfication_status', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Customer')),
                ('ordered_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders_made', to=settings.AUTH_USER_MODEL)),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verifications_made', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PackSizes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(max_length=15)),
                ('deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ShippingAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField(blank=True, null=True)),
                ('city', models.CharField(blank=True, max_length=60, null=True)),
                ('state', models.CharField(blank=True, max_length=50, null=True)),
                ('country', models.CharField(blank=True, max_length=30, null=True)),
                ('zipcode', models.CharField(blank=True, max_length=10, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Categories')),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('key', models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='Key')),
                ('device_token', models.CharField(blank=True, max_length=256, null=True)),
                ('device_id', models.CharField(max_length=256)),
                ('device_type', models.CharField(blank=True, max_length=64, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Token',
                'verbose_name_plural': 'Tokens',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='ProductPackSizes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveSmallIntegerField(default=0)),
                ('packsize', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.PackSizes')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Product Name')),
                ('description', models.TextField(blank=True, null=True)),
                ('available_quantity', models.PositiveSmallIntegerField(default=0)),
                ('low_stock_qauntity', models.PositiveSmallIntegerField(default=5)),
                ('in_stock', models.BooleanField(default=True)),
                ('sale_price', models.PositiveSmallIntegerField(default=0, verbose_name='Selling Price')),
                ('purchase_cost', models.PositiveSmallIntegerField(default=0)),
                ('purchase_info', models.TextField(blank=True, null=True)),
                ('barcode_string', models.TextField(blank=True, null=True)),
                ('barcode_image', models.FileField(blank=True, null=True, upload_to='media/')),
                ('location', models.TextField(verbose_name='Warehouse Location')),
                ('updated_on', models.DateField(blank=True, null=True)),
                ('low_stock', models.BooleanField(default=False)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='base.Categories')),
                ('pack_size', models.ManyToManyField(blank=True, null=True, related_name='packs', to='base.ProductPackSizes')),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Vendor')),
            ],
        ),
        migrations.CreateModel(
            name='OrderQuantity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(default=0)),
                ('price', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('discount', models.PositiveSmallIntegerField(default=0)),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_quantities', to='base.Order')),
                ('pack_size', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.ProductPackSizes')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Product')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='shipping_address',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customers', to='base.ShippingAddress'),
        ),
        migrations.CreateModel(
            name='AdjustProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_price', models.PositiveIntegerField(default=0)),
                ('new_price', models.PositiveIntegerField(default=0)),
                ('old_quantity', models.PositiveSmallIntegerField(default=0)),
                ('new_quantity', models.PositiveSmallIntegerField(default=0)),
                ('date', models.DateField(null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Product')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.ShippingAddress'),
        ),
    ]
