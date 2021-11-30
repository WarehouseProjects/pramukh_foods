from django.db.models.aggregates import Sum
from rest_framework import serializers
from apps.base.models import *
from django.forms.models import model_to_dict
from django.db.models import Q
from datetime import date,datetime
from .utils import update_profit
from django.db.models.functions import Lower
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'

class LoginSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','user_type']

class RegisterSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','phone_number','user_type']

class BillingAddressSerializers(serializers.ModelSerializer):
    class Meta:
        model = Billing_Address
        fields = '__all__'

class ShippingAddressSerializers(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = '__all__'

class InitialProductSerializer(serializers.ModelSerializer):
    
    name = serializers.CharField(source='product.name')
    product_id = serializers.CharField(source='product.id')
    product_item_no = serializers.CharField(source='product.item_no')
    initial_purchase_price = serializers.CharField(source='product.purchase_cost')
    class Meta:
        model = InitialProduct
        fields = '__all__'

class AdjustProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='product.name')
    product_id = serializers.CharField(source='product.id')
    product_item_no = serializers.CharField(source='product.item_no')
    initial_quanity_date = serializers.SerializerMethodField()
    adjust_quanity_date = serializers.SerializerMethodField()
    initial_product_selling = serializers.SerializerMethodField()
    adjust_product_selling = serializers.CharField(source='new_price')
    initial_product_purchase = serializers.SerializerMethodField()
    adjust_product_purchase = serializers.CharField(source='new_purchase_price')
    average_purchase_price = serializers.SerializerMethodField()

    class Meta:
        model = AdjustProduct
        fields = ('id','name','product_id','product_item_no','initial_product_selling','adjust_product_selling',
                    'initial_product_purchase','adjust_product_purchase','average_purchase_price','average_price',
                    'initial_quanity_date','adjust_quanity_date','notes')

    def get_initial_quanity_date(self,obj):
        qty = ""
        date = ""
        if obj.old_quantity:
            qty = str(obj.old_quantity)
        elif obj.product.available_quantity:
            qty = str(obj.product.available_quantity)

        if obj.date:
            date =  str(obj.date)
        elif obj.initial_date:
            date =  str(obj.initial_date)
        
        full_str = qty + " " + date
        return full_str
            

    def get_adjust_quanity_date(self,obj):
        if obj.new_quantity and obj.date:
            return (str(obj.new_quantity) + " "+ str(obj.date))
        else:
            return None
    
    def get_initial_product_selling(self,obj):
        if obj.old_price:
            return obj.old_price
        else:
            return obj.initial_amount
    
    def get_initial_product_purchase(self,obj):
        if obj.old_purchase_price: 
            return obj.old_purchase_price
        else:
            return obj.initial_purchase_amount
    
    def get_average_purchase_price(self,obj):

        if obj.average_purchase_price:
            return obj.average_purchase_price
        else:
            return 0.0
            
class OrderSerializers(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_store = serializers.CharField(source='customer.store_name', read_only=True)
    class Meta:
        model = Order
        fields = ['id','invoice_no' , 'customer_name' ,'customer_store','status','due_date','delivery_date']

class specificUserorderSerializers(serializers.ModelSerializer):
    detail_data = serializers.SerializerMethodField()

    class Meta:
        model= Order
        fields = ['id','ordered_by','invoice_no','created_at','detail','amount','amount_recieved','remaining_amount','payment_status','submitted','due_date','delivery_date','verfication_status','customer','verified_by','detail_data']

    def get_detail_data(self,obj): 
        extra_data = self.context['extra_data']
        start = extra_data.get('start')
        end = extra_data.get('end')
        product_list = []
        datalist = []
        qs = obj.order_quantities.all()
        total = 0
        if qs:
            for product in qs:
                
                product_list.append({
                    'product_id':product.product.id,
                    'product_name':product.product.name,
                    'quantity':product.quantity,
                    'sales_rate':product.product.sale_price,
                    'order_price':product.price,
                    'discount': product.discount,
                    'final_order_amount':product.product_amount,
                    
                })
                total = total+product.price

        else:
            product_list.append({
                'product_id':0,
                'product_name':'no product'
            })

        total_record =len(product_list)
        billing_address = ""
        shipping_address = ""
        shipaddress = obj.customer.shipping_address
        biladd = obj.customer.billing_address
        if shipaddress:
            shipping_address = shipaddress.id
        if biladd:
            billing_address = biladd.id
        datalist.append({
            'invoice_no':obj.invoice_no,
            'customer_name':obj.customer.full_name,
            'customer_store':obj.customer.store_name,  
            'status':obj.status,
            'prouct_list':product_list,
            'total_record':total_record,
            'shipping_address':shipping_address,
            'billing_address': billing_address,
            'sub_total': 1000,
            'total':total,
            'order_date':obj.created_at,
            'order_status':obj.status,
            'due_date':obj.due_date,
            'amount_received':obj.amount_recieved,
            'amount_due':obj.remaining_amount 
        })
        return datalist
            

class AverageSalesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = ('id',)

class OrderDetailSerializers(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_store = serializers.CharField(source='customer.store_name', read_only=True)
    products_list = serializers.SerializerMethodField()
    filter_record = serializers.SerializerMethodField()
    total_record = serializers.SerializerMethodField()

    shipping_city = serializers.SerializerMethodField()
    shipping_state = serializers.SerializerMethodField()
    shipping_country = serializers.SerializerMethodField()
    shipping_zipcode = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()

    billing_city = serializers.SerializerMethodField()
    billing_state = serializers.SerializerMethodField()
    billing_country = serializers.SerializerMethodField()
    billing_zipcode = serializers.SerializerMethodField()
    billing_address = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id','invoice_no' ,'po_num', 'customer_name' ,'customer_store','status','products_list','filter_record','total_record',
                    'shipping_city','shipping_state','shipping_country','shipping_zipcode','shipping_address',
                    'billing_city','billing_state','billing_country','billing_zipcode','billing_address','delivered_status']
    
    def get_products_list(self,obj):
        extra_data = self.context['extra_data']
        search_param = extra_data.get('search_param')
        start = extra_data.get('start')
        end = extra_data.get('end')
        ordered_by = '-id'
        data_list = [] 
        if "for_app" not in extra_data:
            if extra_data['sort_type'] == 'asc':
                ordered_by = Lower(extra_data['order_by']).asc()
            elif extra_data['sort_type'] == 'desc':
                ordered_by = Lower(extra_data['order_by']).desc()

        if search_param:
            qs = obj.order_quantities.filter(Q(order_product_name__icontains=search_param)|
                                                Q(product__name__icontains=search_param) |
                                                Q(product__item_no__icontains=search_param) |
                                                Q(product__category__name__icontains=search_param) |
                                                Q(quantity__icontains=search_param))\
                .order_by(ordered_by)
            self.total_record = qs.count()
            # qs = qs.order_by('product__category__name','order_product_name')
            qs = qs[start:end]
            self.filter_record = qs.count()
        else:
            qs = obj.order_quantities.all().order_by(ordered_by)
            self.total_record = qs.count()
            # qs = qs.order_by('product__category__name','order_product_name')
            qs = qs[start:end]
            self.filter_record = qs.count()
        if obj.status != 'COMPLETED':
            for product in qs:
                scan_text = None
                if product.scan_status=='PARTIALLY_SCANNED':
                    qtyy = str(product.quantity)
                    sub_ans = str(product.quantity - product.scan_quantity)
                    if len(qtyy) != len(sub_ans):
                        sub_ans = sub_ans[:len(qtyy)]
                    scan_text = '{0} Packets Scanning left'.format(sub_ans)
                    
                data_list.append({
                    'order_quantity_id': product.id,
                    'category_id': product.product.category.id,
                    'category_name': product.product.category.name,
                    'vendor_id': product.product.vendor.id,
                    'vendor_name': product.product.vendor.name,
                    'product_id':product.product.id,
                    'product_name':product.product.name,
                    'order_product_name':product.order_product_name,
                    'quantity':product.quantity,
                    'sales_rate':product.product.sale_price,
                    'order_price':product.price,
                    'order_net_price':product.net_price,
                    'discount': product.discount,
                    'final_order_amount':product.product_amount,
                    'scan_status':product.scan_status,
                    'scan_text' : scan_text,
                    'pack_size': product.pack_size.__str__(),
                    'pack_size_id': product.pack_size.id,
                    'product_location':product.product.location,
                    'scanned_quantity' : product.scan_quantity,
                    'barcode_string' : product.product.barcode_string,
                    'category_id':product.product.category.id,
                    'product_price':product.pack_size.price,
                    "isSelected":False,
                    'item_no':product.product.item_no,
                    'weight':product.product.weight,
                    'available_quantity':product.product.available_quantity
                })
                old_data_date = datetime(2021, 9, 2).date()
                order_date = product.order.created_at.date()

                if order_date < old_data_date:
                    data_list[0]["order_price"] = product.price
                    data_list[0]["order_net_price"] = 0

        else:
            for product in qs:
                scan_text = None

                if product.verfication_scan_status=='PARTIALLY_SCANNED':
                    qtyy = str(product.quantity)
                    sub_ans = str(product.quantity - product.verfication_scan_quantity)
                    if len(qtyy) != len(sub_ans):
                        sub_ans = sub_ans[:len(qtyy)]
                    scan_text = '{0} Packets Scanning left'.format(sub_ans)

                data_list.append({
                    'order_quantity_id': product.id,
                    'product_id':product.product.id,
                    'order_product_name':product.order_product_name,
                    'product_name':product.product.name,
                    'quantity':product.quantity,
                    'sales_rate':product.product.sale_price,
                    'order_price':product.price,
                    'order_net_price':product.net_price,
                    'discount': product.discount,
                    'final_order_amount':product.product_amount,
                    'scan_status':product.verfication_scan_status,
                    'scan_text' : scan_text,
                    'pack_size': product.pack_size.__str__(),
                    'pack_size_id': product.pack_size.id,
                    'product_location':product.product.location,
                    'scanned_quantity' : product.verfication_scan_quantity,
                    'barcode_string' : product.product.barcode_string,
                    'category_id':product.product.category.id,
                    'category_name': product.product.category.name,
                    'vendor_id': product.product.vendor.id,
                    'vendor_name': product.product.vendor.name,
                    "isSelected":False,
                    'item_no':product.product.item_no,
                    'weight':product.product.weight,
                    'available_quantity':product.product.available_quantity
                })
                old_data_date = datetime(2021, 9, 2).date()
                order_date = product.order.created_at.date()

                if order_date < old_data_date:
                    data_list[0]["order_price"] = product.price
                    data_list[0]["order_net_price"] = 0

        # print(data_list)
        if "for_app" in extra_data:
            not_scanned = []
            scanned = []
            partialy_scanned = []
            for item in data_list:
                if item["scan_status"] in [None,'NOT_SCANNED']:
                    not_scanned.append(item)
                elif item["scan_status"] == 'SCANNED':
                    scanned.append(item)
                elif item["scan_status"] == 'PARTIALLY_SCANNED':
                    partialy_scanned.append(item)

            data_list = not_scanned + partialy_scanned + scanned 
        return data_list

    def get_filter_record(self,obj):
        return self.filter_record

    def get_total_record(self,obj):
        return self.total_record
    
    def get_shipping_city(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.shipping_address:
                data = obj.customer.shipping_address.city
        return data

    def get_shipping_state(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.shipping_address:
                data = obj.customer.shipping_address.state
        return data
    
    def get_shipping_country(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.shipping_address:
                data = obj.customer.shipping_address.country
        return data

    def get_shipping_zipcode(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.shipping_address:
                data = obj.customer.shipping_address.zipcode
        return data

    def get_shipping_address(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.shipping_address:
                data = obj.customer.shipping_address.address
        return data

    def get_billing_address(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.billing_address:
                data = obj.customer.billing_address.address
        return data
    
    def get_billing_zipcode(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.billing_address:
                data = obj.customer.billing_address.zipcode
        return data

    def get_billing_city(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.billing_address:
                data = obj.customer.billing_address.city
        return data
    
    def get_billing_state(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.billing_address:
                data = obj.customer.billing_address.state
        return data
    
    def get_billing_country(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.billing_address:
                data = obj.customer.billing_address.country
        return data

class OrderProductDetailSerializers(serializers.ModelSerializer):
    name = serializers.CharField(source='product.name')   
    product_item_no = serializers.CharField(source='product.item_no')
    category_name = serializers.CharField(source='product.category.name')
    vendor_name = serializers.CharField(source='product.vendor.name')


    class Meta:
        model = OrderQuantity
        fields = '__all__'

class UserSerializers(serializers.ModelSerializer):
    address = serializers.SerializerMethodField('get_address')
    city = serializers.SerializerMethodField('get_city')
    state = serializers.SerializerMethodField('get_state')
    country = serializers.SerializerMethodField('get_country')
    zipcode = serializers.SerializerMethodField('get_zipcode')
    user_passowrd = serializers.SerializerMethodField('get_user_passowrd')
    
    class Meta:
        model = User
        # fields = '__all__'
        exclude = ('last_login','is_active','is_staff','is_superuser','created_at','updated_at','password')

    def get_address(self,obj):
        if obj.address:
            return obj.address.address
        else:
            return ""

    def get_city(self,obj):
        if obj.address:
            return obj.address.city
        else:
            return ""

    def get_state(self,obj):
            if obj.address:
                return obj.address.state
            else:
                return ""

    def get_country(self,obj):
            if obj.address:
                return obj.address.country
            else:
                return ""

    def get_zipcode(self,obj):
            if obj.address:
                return obj.address.zipcode
            else:
                return ""

    def get_user_passowrd(self,obj):
        password_val = ""
        if self.context:
            if 'request' in self.context:
                user = self.context['request'].user
                if user.user_type == "ADMIN":
                    password_val = obj.password
        return password_val

class CustomerSerializers(serializers.ModelSerializer):
    all_order = serializers.SerializerMethodField()
    total_order_amount = serializers.SerializerMethodField()
    # billing_address_full = serializers.SerializerMethodField()
    # shipping_address_full = serializers.SerializerMethodField()
    open_balance = serializers.SerializerMethodField()
    sign_off_process = serializers.SerializerMethodField()
    billing_city  = serializers.SerializerMethodField()
    billing_address = serializers.SerializerMethodField()
    billing_state= serializers.SerializerMethodField()
    billing_country= serializers.SerializerMethodField()
    billing_zipcode= serializers.SerializerMethodField()
    shipping_city= serializers.SerializerMethodField()
    shipping_address= serializers.SerializerMethodField()
    shipping_state = serializers.SerializerMethodField()
    shipping_country = serializers.SerializerMethodField()
    shipping_zipcode= serializers.SerializerMethodField()

    
    class Meta:
        model = Customer
        fields = '__all__'

    def get_sign_off_process(self,obj):
        return "Left"

    def get_open_balance(self,obj):
        sum = obj.order_set.aggregate(Sum('remaining_amount'))['remaining_amount__sum']
        return sum if sum else 0

    def get_all_order(self, obj):
        return str(obj.order_set.all().count())
    
    def get_total_order_amount(self, obj):
        total = obj.order_set.aggregate(Sum('amount'))['amount__sum']
        return total if total else 0
    
    def get_billing_address(self,obj):
        if obj.billing_address:
            address = obj.billing_address.address
            if address:
                return address
            else :
                return ""
        else:
            return "" 
    
    
    def get_billing_city(self,obj):
        if obj.billing_address:
            city = obj.billing_address.city
            if city:
                return city
            else :
                return ""
        else:
            return "" 
    
    def get_billing_state(self,obj):
        if obj.billing_address:
            city = obj.billing_address.state
            if city:
                return city
            else :
                return ""
        else:
            return "" 
    def get_billing_country(self,obj):
        if obj.billing_address:
            city = obj.billing_address.country
            if city:
                return city
            else :
                return ""
        else:
            return "" 
    def get_billing_zipcode(self,obj):
        if obj.billing_address:
            city = obj.billing_address.zipcode
            if city:
                return city
            else :
                return ""
        else:
            return "" 
    def get_shipping_address(self,obj):
        if obj.shipping_address:
            city = obj.shipping_address.address
            if city:
                return city
            else :
                return ""
        else:
            return "" 
    def get_shipping_city(self,obj):
        if obj.shipping_address:
            city = obj.shipping_address.city
            if city:
                return city
            else :
                return ""
        else:
            return "" 
    def get_shipping_state(self,obj):
        if obj.shipping_address:
            city = obj.shipping_address.state
            if city:
                return city
            else :
                return ""
        else:
            return "" 
    def get_shipping_country(self,obj):
        if obj.shipping_address:
            city = obj.shipping_address.country
            if city:
                return city
            else :
                return ""
        else:
            return ""  
    def get_shipping_zipcode(self,obj):
        if obj.shipping_address:
            city = obj.shipping_address.zipcode
            if city:
                return city
            else :
                return ""
        else:
            return "" 


class PackSizesSerializers(serializers.ModelSerializer):

    class Meta:
        model = PackSizes
        fields = '__all__'

class CategoriesSerializers(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'

class CategoriesListSerializers(serializers.ModelSerializer):
    vendor_id = serializers.SerializerMethodField()
    vendor_name =  serializers.SerializerMethodField()

    class Meta:
        model = Categories
        fields = '__all__'

    def get_vendor_id(self,obj):
        vendors = Vendor.objects.filter(category=obj)
        if not vendors:
            return None
        
        if vendors.filter(name__iexact='All').exists():
            return vendors.filter(name__iexact='All').first().id

        return vendors.first().id

    def get_vendor_name(self,obj):
        vendors = Vendor.objects.filter(category=obj)
        if not vendors:
            return ""

        if vendors.filter(name__iexact='All').exists():
            return vendors.filter(name__iexact='All').first().name

        return vendors.first().name

class SalesProductListSerializers(serializers.ModelSerializer):
    category_id = serializers.ReadOnlyField(source='category.id')
    category_name = serializers.ReadOnlyField(source='category.name')
    warehouse_location = serializers.ReadOnlyField(source='location')
    
    class Meta:
        model = Product
        fields = ['id','name','category_id','category_name','available_quantity','warehouse_location','item_no','sale_price','weight']

class ProductListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name']

class ProductSerializers(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    average_purchase_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_category_name(self,obj):
        return obj.category.name
    
    def get_average_purchase_price(self,obj):
        # obj.purchase_cost = obj.purchase_cost
        # obj.save() # Refreshing the data
        avg_obj = AdjustProduct.objects.filter(product=obj).last()
        purchase_cost = obj.purchase_cost
        if avg_obj:
            if avg_obj.average_purchase_price and avg_obj.average_purchase_price!=0:
                purchase_cost = avg_obj.average_purchase_price

        return purchase_cost
class ProductSerializersWithPack(serializers.ModelSerializer):
    pack_size_array = serializers.SerializerMethodField()
    category_id = serializers.ReadOnlyField(source='category.id')
    category_name = serializers.ReadOnlyField(source='category.name')
    vendor_id = serializers.ReadOnlyField(source='vendor.id')
    vendor_name = serializers.ReadOnlyField(source='vendor.name')
    product_id = serializers.ReadOnlyField(source='id')
    product_name = serializers.ReadOnlyField(source='name')

    class Meta:
        model = Product
        fields = ('product_id','product_name','pack_size_array','sale_price','category_id','category_name','vendor_id','vendor_name','weight','item_no','available_quantity')

    def get_pack_size_array(self,obj):
        data = []
        for _ in obj.pack_size.all():
            data.append({
                'id':_.id,
                'pack_size' : _.packsize.size,
                'price' : _.price
            })
        return data
        
class OrderStatusSerializers(serializers.ModelSerializer):
    salesman = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()

    class Meta:
        model = Order
        exclude = ('ordered_by',)

    def get_salesman(self,obj):
        if obj.ordered_by:
            return obj.ordered_by.full_name
        else:
            return None

    def get_customer_name(self,obj):
        return obj.customer.full_name
    
    def get_store_name(self,obj):
        return obj.customer.store_name
    
    def get_profit(self,obj):
        update_profit(order_obj=obj)
        return obj.order_profit

class OpenStatusSerializers(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_store = serializers.CharField(source='customer.store_name', read_only=True)
    count = serializers.CharField(source='products.count',read_only=True)
    class Meta:
        model = Order
        fields = ['invoice_no','customer_name','customer_store','count','created_at']

class OrderSerializersApp(serializers.ModelSerializer):
    salesman = serializers.SerializerMethodField()
    detail_data = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    billing_contact = serializers.SerializerMethodField()
    min_threshold = serializers.SerializerMethodField()
    max_threshold = serializers.SerializerMethodField()

    shipping_city = serializers.SerializerMethodField()
    shipping_state = serializers.SerializerMethodField()
    shipping_country = serializers.SerializerMethodField()
    shipping_zipcode = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()

    billing_city = serializers.SerializerMethodField()
    billing_state = serializers.SerializerMethodField()
    billing_country = serializers.SerializerMethodField()
    billing_zipcode = serializers.SerializerMethodField()
    billing_address = serializers.SerializerMethodField()

    class Meta:
        model = Order
        exclude = ('ordered_by',)

    def get_salesman(self,obj):
        if obj.ordered_by:
            return obj.ordered_by.full_name
        else:
            return None
    
    def get_customer_name(self,obj):
        return obj.customer.full_name

    def get_min_threshold(self,obj):
        return obj.customer.min_threshold

    def get_max_threshold(self,obj):
        return obj.customer.max_threshold
    
    def get_shipping_city(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.shipping_address:
                data = obj.customer.shipping_address.city
        return data

    def get_shipping_state(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.shipping_address:
                data = obj.customer.shipping_address.state
        return data
    
    def get_shipping_country(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.shipping_address:
                data = obj.customer.shipping_address.country
        return data

    def get_shipping_zipcode(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.shipping_address:
                data = obj.customer.shipping_address.zipcode
        return data

    def get_shipping_address(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.shipping_address:
                data = obj.customer.shipping_address.address
        return data

    def get_billing_address(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.billing_address:
                data = obj.customer.billing_address.address
        return data
    
    def get_billing_zipcode(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.billing_address:
                data = obj.customer.billing_address.zipcode
        return data

    def get_billing_city(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.billing_address:
                data = obj.customer.billing_address.city
        return data
    
    def get_billing_state(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.billing_address:
                data = obj.customer.billing_address.state
        return data
    
    def get_billing_country(self,obj):
        data = "-"
        if obj.customer:
            if obj.customer.billing_address:
                data = obj.customer.billing_address.country
        return data
    
    def get_billing_contact(self,obj):
        data = "-"
        if obj.customer:
            data = obj.customer.phone
        return data
    
    def get_detail_data(self,obj):
        context = {
            'extra_data':{
                'start':None,
                'end':None,
                'order_by':['id'],
                'for_app':True
            }
        }

        shipping_address_string = ""
        if obj.customer.shipping_address:
            for x in obj.customer.shipping_address._meta.get_fields()[3:]:
                if getattr(obj.customer.shipping_address,x.name):
                    shipping_address_string +=getattr(obj.customer.shipping_address,x.name) + ","

            shipping_address_string = shipping_address_string.strip(",")

        billing_address_string = ""
        if obj.customer.billing_address:
            for x in obj.customer.billing_address._meta.get_fields()[2:]:
                if getattr(obj.customer.billing_address,x.name):
                    billing_address_string +=getattr(obj.customer.billing_address,x.name) + ","

            billing_address_string = billing_address_string.strip(",")

        serializer = OrderDetailSerializers(obj,context = context)
        data = serializer.data
        data.update({
            'shipping_address':shipping_address_string,
            'billing_address' : billing_address_string,
        })
        return data


class ProductOutOfStock(serializers.ModelSerializer):
    
    isSelected = serializers.SerializerMethodField()
    date_out_of_stock = serializers.SerializerMethodField()
    time_out_of_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields=['id','name','available_quantity','item_no','isSelected','date_out_of_stock','time_out_of_stock','lifetime_quantity']

    def get_isSelected(self,obj):
        return False
    
    def get_date_out_of_stock(self,obj):
        val = ""
        if obj.out_of_stock_date:
            val = obj.out_of_stock_date.date()
        return val
    
    def get_time_out_of_stock(self,obj):
        val = ""
        if obj.out_of_stock_date:
            val = obj.out_of_stock_date.time()
        return val
        

class ProductPackSizesSerializers(serializers.ModelSerializer):
    size = serializers.SerializerMethodField()

    class Meta:
        model = ProductPackSizes
        fields = '__all__'
    
    def get_size(self,obj):
        return obj.packsize.size


class PaymentHistorySerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    invoice_no = serializers.SerializerMethodField()
    invoice_date = serializers.SerializerMethodField()
    available_credit = serializers.SerializerMethodField()

    class Meta:
        model = PaymentHistory
        fields = '__all__'

    def get_image(self,obj):
        if obj.image:
            request = self.context.get('request')
            complete_url = obj.image.url
            return request.build_absolute_uri(complete_url)
        else:
            a= 'Null'
            return a

    def get_invoice_no(self,obj):
        if obj.order:
            value =  obj.order.invoice_no
        else:
            value = ""
        return value
        
    def get_invoice_date(self,obj):
        if obj.order:
            value =  obj.order.invoice_date
        else:
            value = ""
        return value

    def get_available_credit(self,obj):
        if obj.customer and obj.order:
            data_qs = CreditMemo.objects.filter(customer=obj.customer,order=obj.order)
            sum_val = data_qs.aggregate(Sum('credit_amount'))['credit_amount__sum']
        else:
            sum_val = ""
        return sum_val

class AllPaymentHistorySerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    customer_name = serializers.CharField(source='customer.full_name',read_only=True)

    class Meta:
        model = PaymentHistory
        fields = '__all__'

    def get_image(self,obj):
        if obj.image:
            request = self.context.get('request')
            complete_url = obj.image.url
            return request.build_absolute_uri(complete_url)
        else:
            a= 'Null'
            return a


class ReceivedPaymentSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model= PaymentHistory
        fields = '__all__'
    def get_image(self,obj):
        if obj.image :
            request = self.context.get('request')
            complete_url = obj.image.url
            return request.build_absolute_uri(complete_url)
        else:
            a= 'Null'
            return a


class OrderFromCustomerIDSerializers(serializers.ModelSerializer):
    salesman = serializers.CharField(source='ordered_by.full_name')
    open_balance = serializers.CharField(source='remaining_amount',read_only=True)

    class Meta:
        model = Order
        fields ='__all__'
    

class NotificationsSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    name = serializers.CharField(source='product.name')   
    product_item_no = serializers.CharField(source='product.item_no')   

    class Meta:
        model = Notification
        fields = '__all__'

    def get_date(self,obj):
        return obj.date.date()

    def get_time(self,obj):
        return obj.date.time()


class AgeingReportSerializers(serializers.ModelSerializer):
    store_name = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    customer_id = serializers.SerializerMethodField()

    class Meta:
        model= Order
        fields=['id','invoice_no','store_name','delivery_date','due_date','remaining_amount','term','customer_name','customer_id']
    
    def get_store_name(self,obj):
        return obj.customer.store_name
    
    def get_customer_name(self,obj):
        return obj.customer.full_name
    
    def get_customer_id(self,obj):
        return obj.customer.id

class AgeingReportNewSerializers(serializers.ModelSerializer):
    store_name = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    customer_id = serializers.SerializerMethodField()
    open_balance = serializers.CharField(source='remaining_amount',read_only=True)
    total_amount = serializers.CharField(source='amount',read_only=True)
    ageing = serializers.SerializerMethodField()

    class Meta:
        model= Order
        fields=['id','invoice_no','po_num','term','store_name','due_date','created_at','delivery_date','customer_name','customer_id','ageing','total_amount','amount_recieved','open_balance']
    
    def get_store_name(self,obj):
        return obj.customer.store_name
    
    def get_customer_name(self,obj):
        return obj.customer.full_name
    
    def get_customer_id(self,obj):
        return obj.customer.id

    def get_ageing(self,obj):
        today = datetime.now().date()
        if type(obj.due_date) == str:
            obj.due_date = datetime.strptime(obj.due_date,"%Y-%m-%d").date()

        delta = today - obj.due_date
        if obj.ageing != delta.days:
            obj.ageing = delta.days
            obj.save()
        
        return obj.ageing


class OrderInvoiceDataSerializers(serializers.ModelSerializer):
    open_balance = serializers.SerializerMethodField()
    ageing = serializers.SerializerMethodField()
    order_type = serializers.SerializerMethodField()

    class Meta:
        model= Order
        fields=['id','order_type','created_at','invoice_no','po_num','term','due_date','ageing','open_balance']
    
    def get_ageing(self,obj):
        today = datetime.now().date()
        if type(obj.due_date) == str:
            obj.due_date = datetime.strptime(obj.due_date,"%Y-%m-%d").date()

        delta = today - obj.due_date
        if obj.ageing != delta.days:
            obj.ageing = delta.days
            obj.save()
        
        return obj.ageing

    def get_open_balance(self,obj):
        if obj.remaining_amount:
            value = "%.2f" % round(obj.remaining_amount, 2)
        return value

    def get_order_type(self,obj):
        return "Invoice"

class AdminAgeingReportSerializers(serializers.ModelSerializer):
    store_name = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    customer_id = serializers.SerializerMethodField()
    total_of_open_balance = serializers.SerializerMethodField()
    total_store_name = serializers.SerializerMethodField()
    invoice_data = serializers.SerializerMethodField()

    class Meta:
        model= Customer
        fields=['customer_id','store_name','customer_name','invoice_data','total_of_open_balance','total_store_name']
    
    def get_store_name(self,obj):
        return obj.store_name
    
    def get_customer_name(self,obj):
        return obj.full_name
    
    def get_customer_id(self,obj):
        return obj.id
    
    def get_invoice_data(self,obj):
        today = datetime.now().date()
        order_qs = Order.objects.filter(customer=obj,remaining_amount__gt=0.0)
        serializer = OrderInvoiceDataSerializers(order_qs, many=True)
        serializer_data = serializer.data
        return serializer_data
    
    def get_total_store_name(self,obj):
        name = "Total " + str(obj.store_name)
        return name

    def get_total_of_open_balance(self,obj):
        today = datetime.now().date()
        order_qs = Order.objects.filter(customer=obj,remaining_amount__gt=0.0)
        total_open_balance = order_qs.aggregate(Sum('remaining_amount'))['remaining_amount__sum']
        if not total_open_balance:
            total_open_balance = 0
        
        total_open_balance = "%.2f" % round(total_open_balance, 2)
        return total_open_balance

class StoreSerializers(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id','store_name','full_name','email']

class ProductOrdersSerializers(serializers.ModelSerializer):
    order_id = serializers.CharField(source='order.id')
    order_created_date = serializers.CharField(source='order.created_at')
    invoice_no = serializers.CharField(source='order.invoice_no')
    store_name = serializers.CharField(source='order.customer.store_name')
    store_id = serializers.CharField(source='order.customer.id')

    product_original_name = serializers.CharField(source='product.name')   
    product_item_no = serializers.CharField(source='product.item_no')
    product_description = serializers.CharField(source='product.description')
    product_original_price = serializers.CharField(source='product.sale_price')
    
    product_order_quantity = serializers.CharField(source='quantity')
    product_order_sales_price = serializers.CharField(source='price')
    product_order_discount = serializers.CharField(source='discount')
    total_of_amount = serializers.CharField(source='product_amount') 

    class Meta:
        model = OrderQuantity
        fields = ['id','order_id','order_created_date','invoice_no','store_name','store_id','order_product_name',
                    'product_original_name','product_item_no','product_description','product_original_price',
                    'product_order_sales_price','product_order_quantity','product_order_discount','total_of_amount']


class CreditMemoSerializers(serializers.ModelSerializer):
    invoice_no = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    credit_applied_invoice_no= serializers.SerializerMethodField()

    class Meta:
        model = CreditMemo
        fields ='__all__'

    def get_invoice_no(self,obj):
        if obj.order:
            value =  obj.order.invoice_no
        else:
            value = ""
        return value
    
    def get_store_name(self,obj):
        if obj.customer:
            value =  obj.customer.store_name
        else:
            value = ""
        return value
    
    def get_credit_applied_invoice_no(self,obj):
        qs = CreditApplied.objects.filter(credit_memo=obj).values("credit_applied_order__invoice_no","applied_amount")
        return qs