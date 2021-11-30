from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.utils import timezone
import binascii
import os
from datetime import datetime,timedelta
from django.db.models import Sum
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        try:
            user = User.objects.get(email=email)

        except Exception as ex:
            user = self.model(
                email=self.normalize_email(email),
                last_login=timezone.now(),
                **extra_fields
            )

            user.set_password(password)
            user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):

        user = self.create_user(email, password=password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user


USER_TYPE = (
    ('SALESPERSON', 'SALESPERSON'),
    ('ADMIN', 'ADMIN'),
    ('WAREHOUSE', 'WAREHOUSE'),
)


class User(AbstractBaseUser):
    '''
    Default User Table
    '''
    full_name = models.CharField(max_length = 100 ,null=True,blank=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=16, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    user_type = models.CharField(
        choices=USER_TYPE,
        max_length=12,
        null=True,
        blank=True)

    address = models.ForeignKey('ShippingAddress',on_delete=models.SET_NULL,null=True,blank=True)
    last_login = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    def __unicode__(self):
        return u"%s" % self.username

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


class Token(models.Model):
    """
    The default authorization token model.
    """
    key = models.CharField("Key", max_length=40, primary_key=True)
    user = models.ForeignKey(User, verbose_name='User',
                             related_name='tokens', on_delete=models.CASCADE)
    
    device_token = models.CharField(max_length=256, null=True, blank=True)
    device_id = models.CharField(max_length=256, null=False, blank=False)
    device_type = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField("Created", auto_now_add=True)

    class Meta:
        verbose_name = "Token"
        verbose_name_plural = "Tokens"
        ordering = ('-created_at',)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key


ADDRESS_TYPE = (
    ("SHIPPING", "SHIPPING"),
    ("BILLING", "BILLING"),
    ("BOTH", "BOTH")
)


class BasicUserDetailsAbstract(models.Model):
    '''
    Abstract Model For Basic Details of Customer and Vendor
    '''
    full_name = models.CharField(max_length = 100,null=True,blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        abstract = True


class AddressAbstract(models.Model):
    # address_type = models.CharField(choices=ADDRESS_TYPE,null=True,max_length=10)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=60, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=30, null=True, blank=True)
    zipcode = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        abstract = True

class ShippingAddress(AddressAbstract):
    
    def __str__(self):
        return self.address

class Billing_Address(AddressAbstract):
    def __str__(self):
        return self.address


class Customer(BasicUserDetailsAbstract):
    store_name = models.CharField(max_length=60,null=True,blank=True)
    shipping_address = models.OneToOneField(ShippingAddress,on_delete=models.SET_NULL,null=True,blank=True,related_name='customers')
    billing_address = models.OneToOneField(Billing_Address,on_delete=models.SET_NULL,null=True,blank=True,related_name='customers')
    both_address_same = models.BooleanField(default=False)
    min_threshold = models.FloatField("Minimum threshold", default=0)
    max_threshold = models.FloatField("Maximum threshold", default=0)
    credit_balance= models.FloatField(default=0)
    sales_tax_id = models.CharField(max_length = 50,null=True,blank=True)
    sales_tax_image = models.FileField(upload_to='media/',null=True,blank=True)
    terms = models.FileField(upload_to='media/',null=True,blank=True)
    account_num = models.CharField(max_length=60,null=True,blank=True)
    sales_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_sales_person',
        limit_choices_to= {'user_type': 'SALESPERSON'}
        )
    
    statement_pdf = models.FileField(upload_to='pdf/',null=True,blank=True)
    def __str__(self):
        return str(self.full_name) + '-' + str(self.store_name)


class Vendor(models.Model):
    name = models.CharField(max_length = 30)
    contact_person_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=60, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    zipcode = models.CharField(max_length=10, null=True, blank=True)
    category = models.ManyToManyField("Categories",blank=True)

    def __str__(self):
        return self.name

class PackSizes(models.Model):
    size = models.CharField(max_length=15)
    deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.size

class ProductPackSizes(models.Model):
    packsize = models.ForeignKey(PackSizes,on_delete=models.CASCADE)
    # product = models.ForeignKey("Product",on_delete=models.CASCADE,related_name="pack_sizes")
    price = models.FloatField(default=0)

    def __str__(self):
        return (self.packsize.size)

class Categories(models.Model):
    '''
        Categories Table ,More details Awaited
    '''

    name = models.CharField("Category Name", max_length=50)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def orders(self):
        orders_list = []
        for orders in OrderQuantity.objects.filter(product__category=self):
            orders_list.append(orders.order)
        return orders_list

class Product(models.Model):

    name = models.CharField("Product Name", max_length=55)
    category = models.ForeignKey(
        Categories,
        on_delete=models.CASCADE,
        related_name='products')
    vendor = models.ForeignKey(Vendor,on_delete=models.SET_NULL,null=True,blank=True)
    description = models.TextField(null=True, blank=True)
    available_quantity = models.FloatField(default=0)
    low_stock_qauntity = models.FloatField(default=5)
    lifetime_quantity = models.FloatField(default=0.00)
    in_stock = models.BooleanField(default=True)
    sale_price = models.FloatField("Selling Price", default=0)
    purchase_cost = models.FloatField(default=0)
    purchase_info = models.TextField(null=True, blank=True)
    barcode_string = models.TextField(null=True, blank=True)
    barcode_image = models.FileField(upload_to='media/',null=True,blank=True)
    location = models.TextField("Warehouse Location", null=True,blank=True)
    updated_on = models.DateField(null=True,blank=True)
    low_stock = models.BooleanField(default=False)
    pack_size = models.ManyToManyField(
        ProductPackSizes,
        blank=True,related_name="packs")
    weight = models.FloatField("Weight ", null=True,blank=True)
    item_no = models.TextField('item_no', null=True,blank=True)
    out_of_stock_date = models.DateTimeField(blank=True,null=True)
    mark_up =  models.FloatField(default=0.00)
    margin = models.FloatField(default=0.00)
    is_active = models.BooleanField(default=True)

    @property
    def check_low_stock_fun(self):
        return (True if self.available_quantity <= self.low_stock_qauntity else False)
    
    @property
    def check_out_of_stock_date(self):
        save_date = None
        if self.available_quantity <= 0:
            save_date = timezone.now()
        return save_date
    
    @property
    def set_mark_up(self):
        markup = 0
        avg_obj = AdjustProduct.objects.filter(product=self).last()
        purchase = self.purchase_cost
        if avg_obj:
            if avg_obj.average_purchase_price and avg_obj.average_purchase_price != 0:
              purchase = avg_obj.average_purchase_price

        if self.sale_price and purchase:
            markup = ((self.sale_price - purchase) * 100 )/ purchase
        return "%.2f" % round(markup, 2)
    
    @property
    def set_margin(self):
        margin = 0
        purchase = self.purchase_cost
        avg_obj = AdjustProduct.objects.filter(product=self).last()
        if avg_obj:
            if avg_obj.average_purchase_price and avg_obj.average_purchase_price != 0:
              purchase = avg_obj.average_purchase_price

        if self.sale_price and purchase:
            margin = self.sale_price - purchase
        return "%.2f" % round(margin, 2)

    def __str__(self):
        return self.name
    
    def save(self,**kwargs):
        flag = self._state.adding #True if new product is created
        self.low_stock = self.check_low_stock_fun
        self.out_of_stock_date = self.check_out_of_stock_date
        self.mark_up = self.set_mark_up
        self.margin = self.set_margin
        super().save(**kwargs)
        if flag:
            self.create_initial_product_qauntity()
            self.create_adjust_product_qauntity()

        # Update each order-product price for profit calucaltion 
        if self.sale_price:
            order_qty_qs = OrderQuantity.objects.filter(product=self)
            for obj in order_qty_qs:
                obj.save()

    def create_adjust_product_qauntity(self):
        AdjustProduct.objects.create(
            product = self,
            initial_quanity = self.available_quantity,
            initial_date = datetime.now().date(),
            old_date = datetime.now().date(),
            initial_amount = self.sale_price,
            initial_purchase_amount = self.purchase_cost
        )

    def create_initial_product_qauntity(self):
        InitialProduct.objects.create(
            product = self,
            price = self.sale_price,
            date = datetime.now().date(),
            quantity = self.available_quantity
        )

class InitialProduct(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    price = models.FloatField(default=0)
    date = models.DateField(null=True)
    quantity = models.FloatField(default=0)

class AdjustProduct(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    initial_quanity = models.FloatField(null=True)
    initial_date = models.DateField(null=True)
    new_quantity = models.FloatField(null=True)
    old_quantity = models.FloatField(null=True)
    initial_amount = models.FloatField("Initial Sales Amount",null=True)
    old_price = models.FloatField("Old Sales Price",null=True)
    new_price = models.FloatField("New Sales Price",null=True)
    initial_purchase_amount = models.FloatField("Initial Purchase Amount",null=True)
    old_purchase_price = models.FloatField("Old Purchase Price",null=True)
    new_purchase_price = models.FloatField("New Purchase Price",null=True)
    average_purchase_price = models.FloatField(null=True)
    date = models.DateField("New Date",null=True,blank=True)
    old_date = models.DateField("Old Date",null=True,blank=True)
    average_price = models.FloatField("Average Selling Price",null=True)
    notes = models.TextField(null=True,blank=True)

    def save(self,**kwargs):
        self.average_price = self.get_average_price()
        self.average_purchase_price = self.get_average_purchase_price()
        super().save(**kwargs)

    def get_average_price(self):
        get_old_price = 0
        old_data = 0
        new_data = 0
        total_qty = 0
        val = 0
        if self.old_price:
            get_old_price = self.old_price
        elif self.initial_purchase_amount:
            get_old_price = self.initial_amount

        if self.old_quantity and self.new_price:
            old_data =  get_old_price * self.old_quantity
            new_data = self.new_price * float(self.new_quantity)
            total_qty = self.old_quantity + float(self.new_quantity)
    
        if total_qty != 0:
            val = round((old_data + new_data)/ total_qty ,2)
        return val
    
    def get_average_purchase_price(self):
        get_old_price = 0
        old_data = 0
        new_data = 0
        total_qty = 0
        val = 0
        if self.old_purchase_price:
            get_old_price = self.old_purchase_price
        elif self.initial_purchase_amount:
            get_old_price = self.initial_purchase_amount

        if self.old_quantity and self.new_purchase_price:
            old_data =  get_old_price * self.old_quantity
            new_data = self.new_purchase_price * float(self.new_quantity)
            total_qty = self.old_quantity + float(self.new_quantity)
    
        if total_qty != 0:
            val = round((old_data + new_data)/ total_qty ,2)
        return val

@receiver(post_save, sender=AdjustProduct)
def update_all_linked_order_profit(sender, instance, created, **kwargs):
    product_orders = OrderQuantity.objects.filter(product=instance.product).values_list('order',flat=True).distinct()

    # update_profit
    from .base_utils import update_profit
    for order_id in product_orders:
        order_obj = Order.objects.get(id=order_id)
        update_profit(order_obj=order_obj)

ORDER_STATUS = (
    ('OPEN', 'OPEN'),
    ('IN_PROCESS', 'IN_PROCESS'),
    ('COMPLETED', 'COMPLETED')
)

SCAN_STATUS = (
    ('NOT_SCANNED', 'NOT_SCANNED'),
    ('SCANNED', 'SCANNED'),
    ('PARTIALLY_SCANNED', 'PARTIALLY_SCANNED')
)


class OrderQuantity(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,blank=True)
    order_product_name = models.CharField(max_length=250, blank=True, null=True) 
    pack_size = models.ForeignKey(ProductPackSizes,on_delete=models.SET_NULL,null=True,blank=True)
    quantity = models.FloatField(default=0)
    price = models.FloatField('Product Sales Price',default = 0.00)
    net_price = models.FloatField(default = 0.00)
    product_purchase_price = models.FloatField(default = 0.00,null=True,blank=True)
    product_amount = models.FloatField(default = 0.00)
    order = models.ForeignKey('Order',on_delete = models.CASCADE,related_name = 'order_quantities',null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True)
    scan_status = models.CharField(choices=SCAN_STATUS,max_length=20,null=True,blank=True)
    scan_quantity = models.FloatField(default=0)
    remaining_scan_quantity = models.FloatField(default=0)

    discount = models.FloatField(default=0)
    verfication_scan_quantity = models.FloatField(default=0)
    remaining_verfication_scan_quantity = models.FloatField(default=0)
    verfication_scan_status = models.CharField(choices=SCAN_STATUS,null=True,blank=True,max_length=20)

    def save(self,**kwargs):
        
        if not self.pk:
            self.remaining_scan_quantity = self.quantity
            self.remaining_verfication_scan_quantity = self.quantity            
            self.order_product_name = self.product.name    
        else:
            self.remaining_scan_quantity = float(self.quantity) - float(self.scan_quantity)  
            self.remaining_verfication_scan_quantity = float(self.quantity) - float(self.verfication_scan_quantity)  
            
            if self.scan_quantity != 0:
                if float(self.scan_quantity) != float(self.quantity):
                    self.scan_status = 'PARTIALLY_SCANNED'
                else:
                    self.scan_status = 'SCANNED'
            
            if self.verfication_scan_quantity != 0:
                if float(self.verfication_scan_quantity) != float(self.quantity):
                    self.verfication_scan_status = 'PARTIALLY_SCANNED'
                else:
                    self.verfication_scan_status = 'SCANNED'

            # self.price = self.product.sale_price - self.discount
            # self.product_amount = self.price * self.quantity
        super().save(**kwargs)

 
PAYMENT_STATUS = (
    ('PARTIAL', 'PARTIALLY PAID'),
    ('FULL', 'FULLY PAID'),
    ('NOT_PAID', 'NOT PAID')
)

@receiver(post_save, sender=OrderQuantity)
@receiver(post_delete, sender=OrderQuantity)
def calculate_order_total_amount(sender, instance, **kwargs):
    from .base_utils import update_profit,update_order_totals

    # update total,sub_total and amount_due
    update_order_totals(order_obj=instance.order)
    # update_profit
    update_profit(order_obj=instance.order)
    

class Order(models.Model):
    invoice_no = models.CharField(max_length=10, blank=True)
    po_num = models.CharField(max_length=10,blank=True) 
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    
    ordered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_made')
    
    delivery_method = models.TextField(null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    detail = models.TextField("Order Details", null=True, blank=True)

    amount = models.FloatField(
        verbose_name='Total amount',
        default=0,
        blank=True)

    sub_total = models.FloatField(default=0,null=True, blank=True)
    applied_credit = models.FloatField(default=0,null=True, blank=True)
    amount_recieved = models.FloatField(
        verbose_name='Recieved amount', default=0)
    
    remaining_amount = models.FloatField(default=0)

    payment_status = models.CharField(
        choices=PAYMENT_STATUS,
        max_length=10,
        null=True,
        blank=True,default='NOT_PAID')
    
    status = models.CharField(
        choices=ORDER_STATUS,
        max_length=12,
        null=True,
        blank=True)
    
    submitted = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    invoice_date =  models.DateField(null=True, blank=True)
    ageing = models.IntegerField(null=True, blank=True,default = 0)
    term = models.CharField(max_length=100, null=True, blank=True)
    order_profit = models.FloatField(default=0)
    order_profit_percentage = models.FloatField(default=0)
    verfication_status = models.BooleanField(default=False)
    delivered_status = models.BooleanField(default=False)
    invoice_pdf = models.FileField(upload_to='pdf/',null=True,blank=True)
    sales_pdf = models.FileField(upload_to='pdf/',null=True,blank=True)

    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verifications_made')

    def save(self, *args, **kwargs):
        if not self.po_num:
            self.po_num = self.generate_po_num()
        
        self.remaining_amount = 0 if (float(self.amount) - float(self.amount_recieved))<0 else (float(self.amount) - float(self.amount_recieved))

        if self.delivery_date and self.term:
            start = self.term.find(' ')
            extra_day = self.term[start+1:]
            d = timedelta(days=int(extra_day))
            self.due_date = self.delivery_date + d

        today = datetime.now().date()
        if type(self.due_date) == str:
            self.due_date = datetime.strptime(self.due_date,"%Y-%m-%d")

        if self.due_date.__class__.__name__ == 'date':
            delta = today - self.due_date
        else:
            delta = today - self.due_date.date()    
        self.ageing = delta.days
        return super().save( **kwargs)

    def generate_po_num(self):
        # invoice_no = binascii.hexlify(os.urandom(5)).decode().upper()
        # if Order.objects.filter(invoice_no=invoice_no).exists():
        #     return self.generate_invoice_no(self)
        if Order.objects.all().last():
            last_id = Order.objects.all().last().po_num
            last_id = last_id.split("O")[1]
            new_po_num = int(last_id)+1
        else:
            new_po_num = 2300
        new_po_num = "PO"+str(new_po_num)
        return str(new_po_num)

    def __str__(self):
        return str(self.id)


class Miscellaneous(models.Model):
    name = models.CharField(max_length = 20, unique=True)
    content = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.name

class ForceAppUpdate(models.Model):
    android = models.CharField(max_length=10)
    ios = models.CharField(max_length=10)
    android_force = models.BooleanField(null=True)
    ios_force = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)

PAYMENT_METHOD = (
    ('CHECK',' CHECK'),
    ('CASH','CASH'),
    ('ONLINE','ONLINE TRANSFER')
)

class Invoice(models.Model):
    invoice = models.FileField()
    
class PaymentHistory(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    payment_date = models.DateField()
    image = models.FileField(upload_to='media/',null=True,blank=True)
    amount_recieved = models.FloatField(default=0)
    order = models.ForeignKey(Order,on_delete=models.CASCADE,null=True)
    reference_no = models.CharField(max_length=40)
    method = models.CharField(choices=PAYMENT_METHOD,max_length=20,null=True)

    def __str__(self):
        return self.customer.full_name + " on " + str(self.payment_date)

class Notification(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True)
    warehouse_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    date = models.DateTimeField(null=True)

CREDIT_STATUS = (
    ('FULLY', 'FULLY'),
    ('PARTIALLY', 'PARTIALLY')
)

class CreditMemo(models.Model):
    cm_no = models.CharField(max_length=100, blank=True, null=True)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order,on_delete=models.CASCADE,null=True, blank=True)
    payment_history = models.ForeignKey(PaymentHistory, on_delete=models.CASCADE,null=True, blank=True)
    payment_amount = models.FloatField(default=0, blank=True, null=True)
    open_balance = models.FloatField(default=0,  blank=True, null=True)
    credit_amount = models.FloatField(default=0,  blank=True, null=True)
    updated_credit_amount = models.FloatField(default=0,  blank=True, null=True)
    credit_applied_status = models.CharField(choices=CREDIT_STATUS,max_length=20,null=True,blank=True)
    description = models.TextField(null=True, blank=True)
    credit_memo_pdf = models.FileField(upload_to='pdf/',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return str(self.cm_no)

    def save(self, *args, **kwargs):
        if self.credit_amount:
            self.credit_amount = round(float(self.credit_amount), 2)
        if self.updated_credit_amount:
            self.updated_credit_amount = round(float(self.updated_credit_amount), 2)


        return super().save( **kwargs)
class CreditApplied(models.Model):
    credit_memo = models.ForeignKey(CreditMemo,on_delete=models.CASCADE, blank=True, null=True)
    credit_applied_order = models.ForeignKey(Order,on_delete=models.CASCADE,null=True, blank=True)
    applied_amount = models.FloatField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return str(self.id)