from django.contrib import admin
from django.apps import apps
from .models import *
app = apps.get_app_config('base')

for model_name, model in app.models.items():
    if model_name == 'orderquantity':
        continue
    elif model_name == 'order':
        continue
    elif model_name == 'adjustproduct':
        continue
    elif model_name == 'product':
        continue
    elif model_name == 'creditmemo':
        continue
    elif model_name == 'creditapplied':
        continue
    else:
        admin.site.register(model)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'po_num','invoice_no','amount','amount_recieved','due_date','delivery_date','created_at')

class OrderQuantityAdmin(admin.ModelAdmin):
    list_display = ('id', 'order','order_product_name','quantity','scan_quantity','remaining_scan_quantity','remaining_verfication_scan_quantity','created_at')

class AdjustProductAdmin(admin.ModelAdmin):
    list_display = ('id','product','new_quantity','date')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','name','available_quantity','sale_price','purchase_cost','barcode_string')

class CreditMemoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cm_no','order','customer','payment_amount','credit_amount','created_at')

class CreditAppliedAdmin(admin.ModelAdmin):
    list_display = ('id', 'credit_memo','credit_applied_order','applied_amount','created_at')

admin.site.register(OrderQuantity, OrderQuantityAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(AdjustProduct, AdjustProductAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(CreditMemo, CreditMemoAdmin)
admin.site.register(CreditApplied, CreditAppliedAdmin)


