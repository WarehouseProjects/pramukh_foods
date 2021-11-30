from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime,timedelta
from django.db.models import Sum

from .serializers import *
from apps.base.models import *

filter_dict = {
    'from_date' : 'created_at__date__gte=',
    'to_date' : 'created_at__date__lte=',
    'order_status' : 'status=',
    'verfication_status' : 'verfication_status=',

}

class SalesMangement(ViewSet):

    @action(detail=False,methods=['GET'])
    def dashboard(self,request):
        date = datetime.now().date()
        start_date = datetime.now().date() - timedelta(days=30)
        end_date = datetime.now().date()
        data = {}
        pending = Order.objects.filter(created_at__date__lte=date).aggregate(Sum('amount_recieved'))
        data.update({
                'amount_recieved' : pending['amount_recieved__sum'] if pending['amount_recieved__sum'] else 0
            })
        
        total = Order.objects.filter(created_at__range = (start_date,end_date)).aggregate(Sum('amount'))
        data.update({
                'total_amount' : total['amount__sum'] if total['amount__sum'] else 0
            })

        open_orders = Order.objects.filter(status='OPEN').count()
        data.update({
                'open_order' : open_orders
            })

        COMPLETED = Order.objects.filter(status='COMPLETED').count()
        data.update({
                'completed_orders' : COMPLETED
            })

        product_out_ofStock = Product.objects.filter(available_quantity=0).count()
        product_low_Stock = Product.objects.filter(low_stock = True).count()

        data.update({
            'product_low_stock': product_low_Stock,
            'product_out_of_stock': product_out_ofStock,
        })

        remaining = Order.objects.filter(created_at__date__lte=date).aggregate(Sum('remaining_amount'))
        data.update({
                'remaining_amount' : remaining['remaining_amount__sum'] if remaining['remaining_amount__sum'] else 0
            })

        delta = timedelta(days=1)
        date_list = []
        while start_date <= end_date:
            date_list.append(start_date)
            start_date += delta

        date_list = date_list[::-1] # Reverse the list
        orders_list = []
        for date in date_list:
            start = str(date)+" 00:00:00"
            end = str(date) +" 23:59:59"

            # orders_list.append(Order.objects.filter(created_at__range = (start,end)).count())
            my_qs = Order.objects.filter(created_at__range = (start,end))
            val = my_qs.aggregate(Sum('amount')).get('amount__sum')
            if not val:
                val = 0
            orders_list.append(val)

        data.update({
            'date' : str(date),
            'y_axis' : date_list,
            'x_axis': orders_list,
        })
        response = {
                'status_code':status.HTTP_200_OK,
                'data':data,
                }

        return Response(response, status=status.HTTP_200_OK)

    def list(self,request,*args,**kwargs):
        print('list: ',request.data.get('New'))
        pass

class VendorViewset(ViewSet):
    '''
    VendorViewset for all APIs related to Vendor Such as Create,delete,Update Vendor
    '''
    def create(self,request,*args,**kwargs):
       
        name =  request.data.get('name')
        contact_person_name =  request.data.get('contact_person_name')
        email =  request.data.get('email')
        phone =  request.data.get('phone')
        address =  request.data.get('address')
        city =  request.data.get('city')
        state =  request.data.get('state')
        zipcode =  request.data.get('zipcode')

        if not name:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'name is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not contact_person_name:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'contact_person_name is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not email:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'email is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not phone:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'phone is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not address:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'address is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not city:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'city is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not state:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'state is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not zipcode:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'zipcode is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        vendor = Vendor.objects.create(
                                name=name,
                                contact_person_name=contact_person_name,
                                email=email,
                                phone=phone,
                                address=address,
                                city=city,
                                state=state,
                                zipcode=zipcode
                        )
        vendor.category.add(*Categories.objects.all())
        vendor.save()
        serializer = VendorSerializer(vendor)
        response = {
                    'status_code':status.HTTP_200_OK,
                    'data':serializer.data
                    }
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False,methods=['POST'])
    def listview(self,request,*args,**kwargs):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        
        search_param = request.data.get('search_param')

        # sorting data
        sort_field = request.data.get("sort_field", "id")
        sort_type = request.data.get("sort_type", "desc")
        order_by = sort_field

        if sort_field == "name":
            order_by = "name"
        elif sort_field == "contact_person_name":
            order_by = "contact_person_name"
        elif sort_field == "email":
            order_by = "email"
        elif sort_field == "phone":
            order_by = "phone"
        elif sort_field == "address":
            order_by = "address"
        elif sort_field == "city":
            order_by = "city"
        elif sort_field == "state":
            order_by = "state"
        elif sort_field == "zipcode":
            order_by = "zipcode"
    
        if sort_type == "desc":
            order_by = "-" + order_by
        if sort_type == "asc":
            order_by = order_by

        vendors = Vendor.objects.all().order_by(order_by) 

        if search_param:
            vendors = Vendor.objects.filter(
                Q(name__icontains=search_param)|
                Q(contact_person_name__icontains=search_param)|
                Q(email__icontains= search_param)|
                Q(phone__icontains=search_param)|
                Q(address__icontains= search_param)|
                Q(city__icontains=search_param) |
                Q(state__icontains=search_param) |
                Q(zipcode__icontains=search_param) 
            )
         
        if not vendors:
            response = {
                'status_code':status.HTTP_200_OK,
                'message':'No Vendors Available',
                'data':[],
                'total_record':0,
                'filter_record':0,
                }

            return Response(response, status=status.HTTP_200_OK)

        total_record = len(vendors)
        vendors = vendors[start:end]
        filter_record = len(vendors)

        serializer = VendorSerializer(vendors,many=True)
        response = {
                'status_code':status.HTTP_200_OK,
                'data':serializer.data,
                'total_record':total_record,
                'filter_record':filter_record,
                }

        return Response(response, status=status.HTTP_200_OK)

    @action(detail=True,methods=['GET'])
    def view(self,request,pk=None,*args,**kwargs):
        vendor = Vendor.objects.filter(id=pk).first()
        if not vendor:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Invalid Vendor ID',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        serializer = VendorSerializer(vendor)
        response = {
                    'status_code':status.HTTP_200_OK,
                    'data':serializer.data
                    }
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=True,methods=['POST'])
    def edit(self,request,pk=None,*args,**kwargs):
        #this will api is used to create new Vendor
        name =  request.data.get('name')
        contact_person_name =  request.data.get('contact_person_name')
        email =  request.data.get('email')
        phone =  request.data.get('phone')
        address =  request.data.get('address')
        city =  request.data.get('city')
        state =  request.data.get('state')
        zipcode =  request.data.get('zipcode')

        if not name:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'name is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not contact_person_name:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'contact_person_name is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not email:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'email is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not phone:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'phone is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not address:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'address is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not city:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'city is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not state:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'state is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not zipcode:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'zipcode is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        vendor = Vendor.objects.filter(id=pk).first()
        if not vendor:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Invalid Vendor ID',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        vendor.name = name
        vendor.contact_person_name = contact_person_name
        vendor.email = email
        vendor.phone = phone
        vendor.address = address
        vendor.city = city
        vendor.state = state
        vendor.zipcode = zipcode

        vendor.save()
        response = {
                    'status_code':status.HTTP_200_OK,
                    'data':'Successfully Updated',
                    }
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self,request,pk=None,*args,**kwargs):
        vendor = Vendor.objects.filter(id=pk).first()
        if not vendor:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Invalid Vendor ID',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        vendor.delete()
        response = {
                    'status_code':status.HTTP_200_OK,
                    'data':'Successfully Deleted',
                    }
        return Response(response, status=status.HTTP_200_OK)


class CategoryViewset(ViewSet):
    '''
    CategoryViewset for all APIs related to Category Such as Create,delete,Update Vendor
    '''
    def create(self,request,*args,**kwargs):
        #this will api is used to create new Vendor
        name =  request.data.get('name',None)
        description =  request.data.get('description',None)
        if not name:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'name is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        vendor = Categories.objects.create(name=name,description=description)
        response = {
                    'status_code':status.HTTP_200_OK,
                    'data':{
                        'id':vendor.id,
                        'name':vendor.name
                    },
                    }
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=True,methods=['POST'])
    def edit(self,request,pk=None,*args,**kwargs):
        name =  request.data.get('name',None)
        description =  request.data.get('description',None)
        if not name:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'name is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        vendor = Categories.objects.filter(id=pk).first()
        if not vendor:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Invalid Vendor ID',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        vendor.name = name
        
        if description:
            vendor.description = description

        vendor.save()
        response = {
                    'status_code':status.HTTP_200_OK,
                    'data':'Successfully Updated',
                    }
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self,request,pk=None,*args,**kwargs):
        vendor = Categories.objects.filter(id=pk).first()
        if not vendor:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Invalid Vendor ID',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        vendor.delete()
        response = {
                    'status_code':status.HTTP_200_OK,
                    'data':'Successfully Deleted',
                    }
        return Response(response, status=status.HTTP_200_OK)
    
    @action(detail=True,methods=['GET'])
    def view(self,request,pk=None,*args,**kwargs):
        vendor = Categories.objects.filter(id=pk).first()
        if not vendor:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Invalid Vendor ID',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        serializer = CategoriesSerializers(vendor)
        response = {
                    'status_code':status.HTTP_200_OK,
                    'data':serializer.data
                    }
        return Response(response, status=status.HTTP_200_OK)


class AdjustProductViewset(ViewSet):
    def create(self,request):
        product_id = request.data.get('product_id')
        new_selling_price = request.data.get('new_selling_price')
        new_purchase_price = request.data.get('new_purchase_price')

        date = request.data.get('date')
        new_quantity = request.data.get('quantity')
        notes = request.data.get('notes')

        if not product_id:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'product_id is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not new_selling_price:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'new_selling_price is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not new_purchase_price:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'new_purchase_price is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not new_quantity:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'new_quantity is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not date:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'date is required',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        product = Product.objects.filter(id=product_id).first()
        if not product:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'product_id is invalid',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            date_obj = datetime.strptime(date,"%Y-%m-%d")
        except:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'date must be in YY-MM-DD format',
                }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        data_qs = AdjustProduct.objects.filter(product=product)
        response = {}

        if not data_qs: #first entry created from product-creations
            new = AdjustProduct.objects.create(product=product)
            new.notes = notes
            new.product=product
            new.new_quantity==float(new_quantity)
            new.old_quantity = new.product.available_quantity
            new.date=date_obj
            
            # Updated sales price
            new.new_price=float(new_selling_price)
            new.old_price = new.product.sale_price
            new.product.sale_price = float(new_selling_price)

            # Updated purchase price
            new.new_purchase_price=float(new_purchase_price)
            new.old_purchase_price = new.product.purchase_cost
            new.product.purchase_cost = float(new_purchase_price)

            new.product.save()
            new.save()

            response = {
                    'status_code':status.HTTP_200_OK,
                    'data':{'id':new.id, }
                }

        else:
            data_obj = data_qs.last()
            data_obj.notes = notes
            if data_obj.date and data_obj.initial_date: # For Adding New rows
                new_row_obj = AdjustProduct.objects.create(product=product)
                new_row_obj.notes = notes
                new_row_obj.initial_quanity = data_obj.initial_quanity
                new_row_obj.initial_date = data_obj.initial_date

                new_row_obj.old_quantity = data_obj.product.available_quantity
                new_row_obj.new_quantity = new_quantity
                
                new_row_obj.old_date = data_obj.date
                new_row_obj.date = date_obj

                # Set initial value same it is.
                new_row_obj.initial_amount = data_obj.initial_amount #initial_product_selling
                new_row_obj.initial_purchase_amount = data_obj.initial_purchase_amount #initial_product_purchase

                # Update old and new purchase_price
                # avg_purchase = sum([data_obj.old_purchase_price,data_obj.new_purchase_price]) /2
                new_row_obj.old_purchase_price = data_obj.new_purchase_price
                new_row_obj.new_purchase_price = float(new_purchase_price)

                # Update old and new selling_price
                # avg_selling = sum([data_obj.old_price,data_obj.new_price]) /2
                new_row_obj.old_price = data_obj.product.sale_price
                new_row_obj.new_price = float(new_selling_price)
                new_row_obj.product.save()
                new_row_obj.save()
                response = {
                            'status_code':status.HTTP_200_OK,
                            'data':{
                                'id':new_row_obj.id,
                            },
                            }
                
            else: #first time adjusting qty
                data_obj.new_quantity=float(new_quantity)
                data_obj.old_quantity = data_obj.product.available_quantity
                data_obj.date=date_obj

                # Updated sales price
                data_obj.new_price=float(new_selling_price)
                data_obj.old_price = data_obj.product.sale_price
                data_obj.product.sale_price = float(new_selling_price)

                # Updated purchase price
                data_obj.new_purchase_price=float(new_purchase_price)
                data_obj.old_purchase_price = data_obj.product.purchase_cost
                data_obj.product.purchase_cost = float(new_purchase_price)
                data_obj.product.save()
                data_obj.save()
            
                response = {
                            'status_code':status.HTTP_200_OK,
                            'data':{
                                'id':data_obj.id,
                            },
                            }
        
        current_qty = product.available_quantity
        product.available_quantity = current_qty + float(new_quantity)
        product.lifetime_quantity = product.lifetime_quantity + float(new_quantity)
        product.purchase_cost = float(new_purchase_price)
        product.sale_price = float(new_selling_price)
        product.save()
        return Response(response, status=status.HTTP_200_OK)

    @action(methods=['POST'],detail=False)
    def list_view(self,request,*arg,**kwargs):

        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        
        product__name = request.data.get('product__name')
        product__item_no = request.data.get('product__item_no')
        initial_quanity_date = request.data.get('initial_quanity_date')
        date = request.data.get('date')
        initial_amount = request.data.get('initial_amount')
        new_price = request.data.get('new_price')
        old_quantity = request.data.get('old_quantity')
        average_price = request.data.get('average_price')
        initial_purchase_amount = request.data.get('initial_purchase_amount')
        new_purchase_price = request.data.get('new_purchase_price')
        average_purchase_price = request.data.get('average_purchase_price')
        notes = request.data.get('notes')


        search_param = request.data.get("search_param")
        filter_by_product = request.data.get("filter_by_product")

        order_by_obj = []
        if date:
            order_by_obj.append(date)
        if product__name:
            order_by_obj.append(product__name)
        if product__item_no:
            order_by_obj.append(product__item_no)
        if old_quantity:
            order_by_obj.append(old_quantity)
        if new_price:
            order_by_obj.append(new_price)
        if initial_quanity_date:
            order_by_obj.append(initial_quanity_date)
        if initial_amount:
            order_by_obj.append(initial_amount)
        if average_price:
            order_by_obj.append(average_price)
        if initial_purchase_amount:
            order_by_obj.append(initial_purchase_amount)
        if new_purchase_price:
            order_by_obj.append(new_purchase_price)
        if average_purchase_price:
            order_by_obj.append(average_purchase_price)
        if notes:
            order_by_obj.append(notes)
        
        get_not_adjusted_product = AdjustProduct.objects.filter(date__exact=None).values_list('product',flat=True)
        objects = AdjustProduct.objects.exclude(product__in=get_not_adjusted_product)

        if order_by_obj:
            objects = objects.all().order_by(*order_by_obj)
        else:    
            objects = objects.all().order_by('-product__name')
        
        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')

        if From_Date and To_Date:
            try:
                from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                d = timedelta(days=1)
                to_date_obj = to_date_obj + d #adding 1 day
                objects = objects.filter(date__range=(from_date_obj,to_date_obj))

            except Exception as e:
                print(e)
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid date format date Format should year-month-date'
                                },status=status.HTTP_400_BAD_REQUEST)
        
        if filter_by_product:
            objects = objects.filter(product__id=filter_by_product) 
        
        if search_param:
            filter_qs = objects.filter(
                Q(product__name__icontains=search_param)|
                Q(product__item_no__icontains=search_param)|
                Q(initial_amount__icontains= search_param)|
                Q(new_price__icontains=search_param)|
                Q(initial_amount__icontains= search_param)|
                Q(date__icontains=search_param) |
                Q(initial_purchase_amount__icontains=search_param) |
                Q(new_purchase_price__icontains=search_param) 
            )

            total_record = len(objects)
            list_with_pagelimit = filter_qs[start:end]
            filter_record = len(list_with_pagelimit)
            serializer = AdjustProductSerializer(list_with_pagelimit,many=True)

        else:
            total_record = len(objects)
            list_with_pagelimit = objects[start:end]
            filter_record = len(list_with_pagelimit)
            serializer = AdjustProductSerializer(list_with_pagelimit,many=True)

        response = {
            'status_code':status.HTTP_200_OK,
            'data': serializer.data,
            'total_record':total_record,
            'filter_record':filter_record,
            'message':"Successfull"
        }
        return Response(response, status=status.HTTP_200_OK)

class AdjustProductData(ViewSet): 
    @action(methods=['POST',],detail=False)
    def modify_salesprice(self,request):
        product_id = request.data.get('product_id')
        new_sales_price = request.data.get('new_sales_price')

        if not product_id:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'product_id required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        product_obj = Product.objects.filter(id=product_id).first()
        if not product_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid product!'
                            },status=status.HTTP_400_BAD_REQUEST)
        

        if not new_sales_price:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'New_sales_price required'
                            },status=status.HTTP_400_BAD_REQUEST)

        new_obj = AdjustProduct.objects.create(product=product_obj)
        new_obj.new_quantity = 0
        new_obj.old_quantity = product_obj.available_quantity
        new_obj.date = timezone.now().date()
        
        # Updated sales price
        new_obj.new_price=float(new_sales_price)
        new_obj.old_price = new_obj.product.sale_price
        new_obj.product.sale_price = float(new_sales_price)

        # Updated purchase price
        new_obj.new_purchase_price = new_obj.product.purchase_cost
        new_obj.old_purchase_price = new_obj.product.purchase_cost

        new_obj.product.save()
        # print("ccc",new_obj.old_purchase_price)
        new_obj.save()
        # new_obj. 
        response = {
                    'status_code':status.HTTP_200_OK,
                    'data':'Successfully Updated',
                    }
        return Response(response, status=status.HTTP_200_OK)

    @action(methods=['POST',],detail=False)
    def change_active_status(self,request,*args,**kwargs):
        product_id =  request.data.get('product_id')
        product_status =  request.data.get('product_status')
        
        if not product_id:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'product_id required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        product_obj = Product.objects.filter(id=product_id).first()
        if not product_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid product!'
                            },status=status.HTTP_400_BAD_REQUEST)
        

        if not product_status:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'product_status required'
                            },status=status.HTTP_400_BAD_REQUEST)
        else:
            if product_status not in ["active","inactive"]:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid product_status value !'
                            },status=status.HTTP_400_BAD_REQUEST)
            else:
                updated_status = True if product_status == "active" else False
                
        product_obj.is_active = updated_status
        product_obj.save()
        response = {
                    'status_code':status.HTTP_200_OK,
                    'data':'Successfully Updated',
                    }
        return Response(response, status=status.HTTP_200_OK)

class AegingReportViewset(ViewSet):
   
    @action(methods=['POST'],detail=False)
    def list_view(self,request,*arg,**kwargs):

        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        
        order_qs = Order.objects.filter(status='COMPLETED').order_by('-created_at')
        
        total_record = len(order_qs)
        list_with_pagelimit = order_qs[start:end]
        filter_record = len(list_with_pagelimit)
        serializer = AgeingReportSerializers(list_with_pagelimit,many=True)

        response = {
            'status_code':status.HTTP_200_OK,
            'data': serializer.data,
            'total_record':total_record,
            'filter_record':filter_record,
            'message':"Successfull"
        }
        return Response(response, status=status.HTTP_200_OK)