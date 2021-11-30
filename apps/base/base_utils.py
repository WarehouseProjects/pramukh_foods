from apps.base.models import *


def update_profit(order_obj = None):
    if order_obj.delivered_status == False:
        order_pro_qs = OrderQuantity.objects.filter(order=order_obj)
        val=0
        old_data_date = datetime(2021, 9, 2).date()

        for data in order_pro_qs:
            adjust_product_obj = AdjustProduct.objects.filter(product=data.product).last()
            if adjust_product_obj and adjust_product_obj.average_purchase_price != 0:
                purchase_price = adjust_product_obj.average_purchase_price
            else:
                purchase_price = data.product_purchase_price
            
            order_date = data.order.created_at.date()
            if order_date < old_data_date:
                order_price = data.product.sale_price
            else:
                order_price = data.net_price

            data_val = (order_price - purchase_price) * data.quantity
            val+= data_val

        try:
            val_percentage =  (float(val) / float(order_obj.amount)) * 100
        except ZeroDivisionError:
            val_percentage = 0
        order_obj.order_profit =  val
        order_obj.order_profit_percentage = round(val_percentage,2)
        order_obj.save()
    else:
        pass

def update_order_totals(order_obj = None):
    order_qs = OrderQuantity.objects.filter(order__pk=order_obj.pk)
    if len(order_qs) != 0:
        sub_total = order_qs.aggregate(Sum('product_amount'))['product_amount__sum']
    else:
        sub_total = 0

    order_obj.sub_total = sub_total
    order_obj.amount = order_obj.sub_total - order_obj.applied_credit
    order_obj.save()