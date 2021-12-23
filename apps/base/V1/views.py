from django.db.models.functions.text import Ord
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet,ViewSet
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth import login , logout
from rest_framework.decorators import permission_classes,authentication_classes , action
from rest_framework.permissions import IsAuthenticated ,AllowAny
from django.db.models import Q , Sum ,Avg
from datetime import datetime , timezone
from datetime import timedelta
from django.conf import settings
from rest_framework.views import APIView
from django.core.mail import send_mail
import binascii , os , operator
from calendar import monthrange
from operator import itemgetter
import uuid 
import json

from apps.base.authentication import MyCustomAuth
from apps.base.models import *

from .serializers import *
from .utils import create_pdf, get_creditmemo_pdfdata

#import re 
class UserDelete(ViewSet):

    def destroy(self,request,pk=None):
        user = User.objects.filter(pk=pk).first()
        alltoken = Token.objects.filter(user=user)

        if user:
            user.delete()
            alltoken.delete()
            return Response({'status_code':status.HTTP_200_OK,
                    'message':'successfull',
                    'data':'successfully deleted'
                    },status=status.HTTP_200_OK)

        else:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                        'message':'No such user'
                        },status=status.HTTP_400_BAD_REQUEST)



@authentication_classes([])
class LoginUser(ViewSet):
    
    def create(self,request): 
        email = request.data.get('email')
        password = request.data.get('password')
        if not email: 
            return Response({
                            'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'email requried'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not password:
            return Response({
                            'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'password requried'
                            },
                            status=status.HTTP_400_BAD_REQUEST)
        # user = authenticate(request,email=email,password=password)
        user = User.objects.filter(email=email,password=password).first()

        if user:
            if request.data.get('user_type'):
                if user.user_type != request.data.get('user_type'):
                    return Response({
                            'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'You are not authorized to login'
                            },
                            status=status.HTTP_400_BAD_REQUEST)

            login(request,user)
            token = Token.objects.create(user=user,device_token=request.data.get('device_token'))
            serializers = UserSerializers(user)
            data = serializers.data.copy()
            data.update({
                'token':token.key
            })

            return Response(
                {
                    'status_code':status.HTTP_200_OK,
                    'message':'successfull',
                    'data':data,
                    },status=status.HTTP_200_OK
                )
            
        else:
            return Response({
                            'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'wrong email or password'
                            },status=status.HTTP_400_BAD_REQUEST)
    

    def destroy(self,request,pk=None):
        user = User.objects.filter(pk=pk).first()
    
        if user:
           TokenDelete = Token.objects.filter(user=user).delete()
           logout(request)
           return Response({   
                            'status_code':status.HTTP_200_OK,
                            'message':'successfull',
                            'data':'successfully loged out'
                            },status=status.HTTP_200_OK)
        else:
            return Response({
                            'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'no such user'
                            }
                            ,status=status.HTTP_400_BAD_REQUEST) 


    def get_permissions(self):
        if self.action == 'create':
            return []
        return super().get_permissions()           


@authentication_classes([])
class RegisterUser(ViewSet):

    def create(self,request):
        user_type = request.data.get('user_type')
        email = request.data.get('email')
        password=request.data.get('password')
        confirmpassword = request.data.get('confirm_password')
        phone_number =request.data.get('phone_number')
        user_type =request.data.get('user_type')
        address = request.data.get('address')
        full_name = request.data.get('full_name')
        # reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
        # pat = re.compile(reg)
        if not email:
            return Response({
                            'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'email requried'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not password:
            return Response({
                            'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'password requried'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not confirmpassword:
            return Response({
                            'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'confirmpassword requried'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not phone_number:
            return Response({
                            'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'phone number requried'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not user_type:
            return Response({
                            'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'user_type requried'
                            },status=status.HTTP_400_BAD_REQUEST)
        if password != confirmpassword :
            return Response({
                            'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'password do not match'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if len(password) < 6 or len(password) > 20:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'minimum password length must be 6 and upto 20 charater'
                            },status=status.HTTP_400_BAD_REQUEST)
        # mat = re.search(pat, password) 
        # if not mat:
        #     return Response({'status_code':status.HTTP_400_BAD_REQUEST,
        #                     'message':'password must be 6 to 20 character,one Capital character,one small letter ,one number and one symbol'})
        
        allUser = User.objects.all()
        if allUser.filter(email=email).exists():
            return Response({
                            'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'User with email already exists'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if allUser.filter(phone_number=phone_number).exists():
            return Response({
                            'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'phone number already exist'
                            },status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create(email=email,phone_number=phone_number,is_active=True ,user_type = user_type,full_name=full_name)
        # user.set_password(password)
        user.password = password
        user.save()

        if address:
            city =request.data.get('city')
            state =request.data.get('state')
            country = request.data.get('country')
            zipcode = request.data.get('zipcode')
            add = ShippingAddress.objects.create(
                address = address,city=city,state=state,country=country,zipcode=zipcode
            )
            user.address = add
            user.save()
       
        if user:
            login(request,user)
            token = Token.objects.create(user=user)
            serializers = LoginSerializers(user)
            login(request,user)
            serializer_data = serializers.data
            serializer_data.update({
                'token' : token.key
            })
            

            return Response({
                            'status_code':status.HTTP_200_OK,
                            'message':'success',
                            'data':serializer_data,
                            'login':'login success'
                            },status=status.HTTP_200_OK)
        else:
            return Response({
                            'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'some error has ouccured'
                            },status= status.HTTP_400_BAD_REQUEST)

class OrderDetail(ViewSet):
    
    @action(methods=['POST',],detail=False)
    def listview(self,request):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
                
        AllOrder = Order.objects.all()
        total_record = len(AllOrder)
        list_with_pagelimit = AllOrder[start:end]
        filter_record = len(list_with_pagelimit)
        serializers = OrderSerializers(list_with_pagelimit , many=True,context={'request':request})
        return Response({
                        'status_code':status.HTTP_200_OK,
                        'message':'Successfull',
                        'data':serializers.data,
                        'total_record':total_record,
                        'filter_record':filter_record
                        },status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        GetUser = request.user
        VerifyUser = User.objects.filter(email=GetUser).first()

        if VerifyUser.user_type == 'SALESPERSON':
            VerifyStatus = Order.objects.filter(pk=pk).first()
            if VerifyStatus.status == 'OPEN':  
                pname = request.data.get('name')
                VerifyName = Product.objects.filter(name=pname).first()
                if VerifyName:
                    VerifyStatus.products.add(VerifyName)
                    GetDetail = Order.objects.filter(pk=pk).first()
                    serializers = OrderSerializers(GetDetail)
                    return Response({
                                    'status_code':status.HTTP_200_OK,
                                    'message':'successfull',
                                    'data':serializers.data
                                    },status=status.HTTP_200_OK) 
                else:
                    return Response({
                                    'status_code':status.HTTP_400_BAD_REQUEST,
                                    'message':'No Such Products'
                                    },status=status.HTTP_400_BAD_REQUEST)

            else:
            
                return Response({
                                'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'status not open'
                                },status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({
                            'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'user is not SALESPERSON'
                            },status=status.HTTP_400_BAD_REQUEST)

    def destroy(self,request,pk=None):
        GetUser = request.user
        VerifyUser = User.objects.filter(email=GetUser).first()

        if VerifyUser.user_type == 'SALESPERSON':
            VerifyStatus = Order.objects.filter(pk=pk).first()
            if VerifyStatus.status == 'OPEN':  
                pname = request.data.get('name')
                if not pname:
                    return Response({
                                    'status_code':status.HTTP_400_BAD_REQUEST,
                                    'message':'product name needed'
                                    },status=status.HTTP_400_BAD_REQUEST)
                productname = Product.objects.filter(name=pname).first()
                if productname:
                    VerifyStatus.products.remove(productname)
                    serializers = OrderSerializers(VerifyStatus)
                    return Response({
                                    'status_code':status.HTTP_200_OK,
                                    'message':'success',
                                    'data':serializers.data
                                    },status=status.HTTP_200_OK)

                else:
                    return Response({
                                    'status_code':status.HTTP_400_BAD_REQUEST,
                                    'message':'no such product name'
                                    },status=status.HTTP_400_BAD_REQUEST)


            else:
                return Response({
                                'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'status is not open'
                                },status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'user is not SALESPERSON'
                            },status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,methods=['POST'])
    def app_order_detail(self,request,pk=None,**kwargs):
        try:
            order_obj = Order.objects.get(id=pk)
        except:
            response = {
                'status_code' : status.HTTP_404_NOT_FOUND,
                'message' : 'Invalid OrderID!'
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        # order_obj = order_obj.order_by('order_quantities__product__category__name','order_quantities__product__name')
        
        serializers =  OrderSerializersApp(order_obj ,context={'request':request})
        return Response({'status_code':status.HTTP_200_OK,
            'message':"sucessfull",
            'data':serializers.data,
            'filter_record':1,
            'total_record':1
            },status=status.HTTP_200_OK)


class DashBoard(ViewSet):

    def list(self,request):
        OpenStatus = Order.objects.filter(status='OPEN').count()
        InProcess = Order.objects.filter(status='IN_PROCESS').count()
        Completed= Order.objects.filter(status='COMPLETED').count()
        product_out_ofStock = Product.objects.filter(available_quantity=0,is_active=True).count()
        product_low_Stock = Product.objects.filter(low_stock = True,is_active=True).count()
        Count = {'new_orders':OpenStatus,'low_stock':product_low_Stock,'InProcess':InProcess,'Completed':Completed ,'product_out_of_stock':product_out_ofStock}
        return Response({'status_code':status.HTTP_200_OK,'message':'Successfull','data':Count},status=status.HTTP_200_OK)

    @action(methods=['POST',],detail=False)
    def new_order(self,request): 
        
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')
        customer_id = request.data.get('customer_id')
        sales_user_id = request.data.get('sales_user_id')
        open_orders = Order.objects.filter(status='OPEN').order_by('-created_at')
        if From_Date and To_Date:
            try:
                from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                open_orders = open_orders.filter(created_at__date__gt = from_date_obj , created_at__date__lt =to_date_obj)
            except Exception as e:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid date format date Format should year-month-date'
                                },status=status.HTTP_400_BAD_REQUEST)
        
        if customer_id:
            open_orders = open_orders.filter(customer=customer_id)
        
        if sales_user_id:
            open_orders = open_orders.filter(ordered_by=sales_user_id)
        
        total_record = len(open_orders)
        list_with_pagelimit = open_orders[start:end]
        filter_record = len(list_with_pagelimit)
        serializers =  OrderSerializersApp(list_with_pagelimit , many=True,context={'request':request})
        message ='successfull' if filter_record else 'No Data Found'
        return Response({'status_code':status.HTTP_200_OK,
                        'message':message,
                        'data':serializers.data,
                        'filter_record':filter_record,
                        'total_record':total_record
                        },status=status.HTTP_200_OK)


    @action(methods=['POST',],detail=False)
    def in_process(self,request): 
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit

        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')
        customer_id = request.data.get('customer_id')
        sales_user_id = request.data.get('sales_user_id')
        in_process = Order.objects.filter(status='IN_PROCESS').order_by('-created_at')
        
        if From_Date and To_Date:
            try:
                from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                to_date_obj = datetime.strptime(To_Date ,'%Y-%m-%d')
                in_process = in_process.filter(created_at__date__gt= from_date_obj ,created_at__date__lt=to_date_obj)
            
            except Exception as e:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'invalid date format try year-month-date format'
                                },status=status.HTTP_400_BAD_REQUEST)
        if customer_id:
            in_process = in_process.filter(customer=customer_id)

        if sales_user_id:
            in_process = in_process.filter(ordered_by=sales_user_id)
        
        total_record = len(in_process)
        list_with_pagelimit = in_process[start:end]
        filter_record = len(list_with_pagelimit)
        # serializers =  OpenStatusSerializers(list_with_pagelimit , many=True,context={'request':request})
        serializers =  OrderSerializersApp(list_with_pagelimit , many=True,context={'request':request})
        message ='successfull' if filter_record else 'No Data Found'
        return Response({'status_code':status.HTTP_200_OK,
                        'message':message,
                        'data':serializers.data,
                        'total_record':total_record,
                        'filter_record':filter_record
                        },status=status.HTTP_200_OK)


    @action(methods=['POST',],detail=False)
    def complete(self,request):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit

    
        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')
        customer_id = request.data.get('customer_id')
        sales_user_id = request.data.get('sales_user_id')
        verification_status = request.data.get('verification_status')
        completed = Order.objects.filter(status='COMPLETED').order_by('-created_at')
        if From_Date and To_Date:
            try:
                
                from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                to_date_obj = datetime.strptime(To_Date ,'%Y-%m-%d')
                completed = completed.filter(created_at__date__gt= from_date_obj,created_at__date__lt=to_date_obj)
            except Exception as e:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'invalid date format try year-month-date format'
                                },status=status.HTTP_400_BAD_REQUEST)
        if customer_id:
            completed = completed.filter(customer=customer_id).order_by('-created_at')
        if sales_user_id:
            completed = completed.filter(ordered_by = sales_user_id).order_by('-created_at')
        if verification_status:
            completed = completed.filter(verfication_status = verification_status).order_by('-created_at')

        # # logic for delivered, verified and non verified sorting
        # completed = completed.exclude(delivered_status=True)
        # verified_order_qs = completed.exclude(invoice_no__isnull=True).exclude(invoice_no__exact='')
        # verified_order_ids = verified_order_qs.values_list('id')
        # not_verified_order_qs = completed.exclude(id__in=verified_order_ids)
        # completed = not_verified_order_qs | verified_order_qs
        # completed = Order.objects.filter(id__in = completed).order_by('-created_at')
        
        total_record = len(completed)
        list_with_pagelimit = completed[start:end]
        filter_record = len(list_with_pagelimit)
        serializers =  OrderSerializersApp(list_with_pagelimit , many=True,context={'request':request})
        message ='successfull' if filter_record else 'No Data Found'
        return Response({'status_code':status.HTTP_200_OK,
                        'message':message,
                        'data':serializers.data,
                        'filter_record':filter_record,
                        'total_record':total_record
                        },status=status.HTTP_200_OK)


    @action(methods=['POST',],detail=False)
    def product_out_ofstock(self,request):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit

        allProduct = Product.objects.filter(available_quantity=0,is_active=True)
        search_field_value = request.data.get('search_field_value') 
        if search_field_value:
            allProduct = allProduct.filter(
                Q(name__icontains=search_field_value)|
                Q(item_no__icontains=search_field_value))

        name = request.data.get('name')
        if name:
            allProduct = allProduct.order_by(name)

        if allProduct:
            total_record = len(allProduct)
            list_with_pagelimit = allProduct[start:end]
            filter_record = len(list_with_pagelimit)
            serializers = ProductOutOfStock(list_with_pagelimit , many=True,context={'request':request})
            return Response({'status_code':status.HTTP_200_OK,
                            'message':'successfull',
                            'data':serializers.data,
                            'total_record':total_record,
                            'filter_record':filter_record,
                            },status=status.HTTP_200_OK)
        else:
            if search_field_value:
                total_record = len(allProduct)
                list_with_pagelimit = allProduct[start:end]
                filter_record = len(list_with_pagelimit)
                return Response({'status_code':status.HTTP_200_OK,
                                'message':'successfull',
                                'data':[],
                                'total_record':total_record,
                                'filter_record':filter_record,
                                },status=status.HTTP_200_OK)
            else:
                return Response({'status_code':status.HTTP_200_OK,
                                'message':'successfull',
                                'data':'no product out of stock'
                                },status=status.HTTP_200_OK)


class Search(ViewSet):
    
    @action(methods=['POST',],detail=False)
    def new_order(self,request):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        
        search_field_value = request.data.get('search_field_value') 
        order_qs = Order.objects.filter(status='OPEN')

        if search_field_value:
            order_qs = order_qs.filter(Q(invoice_no__icontains=search_field_value)|
                                        Q(customer__full_name =search_field_value)|
                                        Q(ordered_by__email__icontains=search_field_value) |
                                        Q(po_num__icontains=search_field_value) |
                                        Q(customer__store_name__icontains=search_field_value))

            total_record = len(order_qs)
            list_with_pagelimit = order_qs[start:end]
            filter_record = len(list_with_pagelimit)
            serializers = OrderSerializersApp(list_with_pagelimit ,many=True , context={'request':request})

        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')
        customer_id = request.data.get('customer_id')
        order_Status = request.data.get('order_status')

        if From_Date not in ["null","Null",None] and To_Date not in ["null","Null",None] :
            if From_Date and To_Date:
                try:
                    from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                    to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                    d = timedelta(days=1)
                    to_date_obj = to_date_obj + d #adding 1 day
                    order_qs = order_qs.filter(created_at__range=(from_date_obj,to_date_obj))
                except Exception as e:
                    return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                    'message':'Invalid date format date Format should year-month-date'
                                    },status=status.HTTP_400_BAD_REQUEST)
        
        if customer_id:
            order_qs = order_qs.filter(customer=customer_id)

        if order_Status:
            order_qs = order_qs.filter(status__icontains=order_Status)
        
        total_record = len(order_qs)
        list_with_pagelimit = order_qs[start:end]
        filter_record = len(list_with_pagelimit)
        serializers = OrderSerializersApp(list_with_pagelimit ,many=True , context={'request':request})

        if serializers.data:
            return Response({'status_code':status.HTTP_200_OK,
                            'message':'successfull',
                            'data':serializers.data,
                            'total_record':total_record,
                            'filter_record':filter_record,
                            },status=status.HTTP_200_OK)  
        else:
            return Response({'status_code':status.HTTP_200_OK,
                        'message':'No Data Found',
                        'data':[],
                        'total_record':0,
                        'filter_record':0,
                        },status=status.HTTP_200_OK)  
       
    @action(methods=['POST',],detail=False)
    def in_process(self,request):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        
        search_field_value = request.data.get('search_field_value')

        order_qs = Order.objects.filter(status='IN_PROCESS')

        if search_field_value:
            order_qs = order_qs.filter(Q(invoice_no__icontains=search_field_value)| 
                                        Q(customer__full_name =search_field_value)|
                                        Q(ordered_by__email__icontains=search_field_value) |
                                        Q(po_num__icontains=search_field_value) |
                                        Q(customer__store_name__icontains=search_field_value))
        
        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')
        customer_id = request.data.get('customer_id')
        order_Status = request.data.get('order_status')

        if From_Date not in ["null","Null",None] and To_Date not in ["null","Null",None] :
            if From_Date and To_Date:
                try:
                    from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                    to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                    d = timedelta(days=1)
                    to_date_obj = to_date_obj + d #adding 1 day
                    order_qs = order_qs.filter(created_at__range=(from_date_obj,to_date_obj))
                except Exception as e:
                    return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                    'message':'Invalid date format date Format should year-month-date'
                                    },status=status.HTTP_400_BAD_REQUEST)
        
        if customer_id:
            order_qs = order_qs.filter(customer=customer_id)

        if order_Status:
            order_qs = order_qs.filter(status__icontains=order_Status)
        
        total_record = len(order_qs)
        list_with_pagelimit = order_qs[start:end]
        filter_record = len(list_with_pagelimit)
        serializers = OrderSerializersApp(list_with_pagelimit ,many=True , context={'request':request})

        if serializers.data:
            return Response({'status_code':status.HTTP_200_OK,
                            'message':'successfull',
                            'data':serializers.data,
                            'total_record':total_record,
                            'filter_record':filter_record,
                            },status=status.HTTP_200_OK)  

        else:
            return Response({'status_code':status.HTTP_200_OK,
                        'message':'No Data Found',
                        'data':[],
                        'total_record':0,
                        'filter_record':0,
                        },status=status.HTTP_200_OK)  
       
  
    @action(methods=['POST',],detail=False)
    def completed(self,request):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        
        search_field_value = request.data.get('search_field_value')
            
        order_qs = Order.objects.filter(status='COMPLETED')

        if search_field_value:
            order_qs = order_qs.filter(Q(invoice_no__icontains=search_field_value)| 
                                        Q(customer__full_name =search_field_value)|
                                        Q(ordered_by__email__contains=search_field_value) |
                                        Q(po_num__icontains=search_field_value) |
                                        Q(customer__store_name__icontains=search_field_value))
        
        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')
        customer_id = request.data.get('customer_id')
        verfication_status = request.data.get('verfication_status')

        if From_Date not in ["null","Null",None] and To_Date not in ["null","Null",None] :
            if From_Date and To_Date:
                try:
                    from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                    to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                    d = timedelta(days=1)
                    to_date_obj = to_date_obj + d #adding 1 day
                    order_qs = order_qs.filter(created_at__range=(from_date_obj,to_date_obj))
                except Exception as e:
                    return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                    'message':'Invalid date format date Format should year-month-date'
                                    },status=status.HTTP_400_BAD_REQUEST)
        
        if customer_id:
            order_qs = order_qs.filter(customer=customer_id)

        if verfication_status in [1,0,'1','0',True,False]:
            order_qs = order_qs.filter(verfication_status=verfication_status)
        
        order_qs = order_qs.order_by('-id')
        total_record = len(order_qs)
        list_with_pagelimit = order_qs[start:end]
        filter_record = len(list_with_pagelimit)
        serializers = OrderSerializersApp(list_with_pagelimit ,many=True , context={'request':request})

        if serializers.data:
            return Response({'status_code':status.HTTP_200_OK,
                            'message':'successfull',
                            'data':serializers.data,
                            'total_record':total_record,
                            'filter_record':filter_record,
                            },status=status.HTTP_200_OK)  

        else:
            return Response({'status_code':status.HTTP_200_OK,
                        'message':'No Data Found',
                        'data':[],
                        'total_record':0,
                        'filter_record':0,
                        },status=status.HTTP_200_OK)  

    @action(methods=['POST',],detail=False)
    def product_out_ofstock(self,request):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit

        search_field_value = request.data.get('search_field_value') 
        
        allProduct = Product.objects.filter(available_quantity=0)
        
        if search_field_value:
            Product_Search = allProduct.filter(name__icontains=search_field_value)
            total_record = len(Product_Search)
            list_with_pagelimit =Product_Search[start:end]
            filter_record = len(list_with_pagelimit)
            serializers = ProductOutOfStock(list_with_pagelimit ,many=True , context={'request':request})
            return Response({
                            'status_code':status.HTTP_200_OK,
                            'message':'successfull',
                            'data':serializers.data,
                            'total_record':total_record,
                            'filter_record':filter_record,
                            },status=status.HTTP_200_OK)
        else:
            return Response({'status_code':status.HTTP_200_OK,
                        'message':'No Data Found',
                        'data':[],
                        'total_record':0,
                        'filter_record':0,
                        },status=status.HTTP_200_OK)  

#Chnage password API
class ChangePasswordView(APIView):
    authentication_classes = (MyCustomAuth,)
    
    def post(self, request, *args, **kwargs):
    
        if not request.data:
            # Retrun error message with 400 status
            return Response({"message": "Data is required.", "status_code": status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
    
        if not request.data.get('current_password'):
            # Retrun error message with 400 status
            return Response({"message": "Current Password is required.", "status_code":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

        if not request.data.get('new_password'):
            # Retrun error message with 400 status
            return Response({"message": "New Password is required.", "status_code":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)    

        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        user = User.objects.filter(id = request.user.id).first()
        
        if user:
            try:
                if user.password == current_password:
                    
                    if current_password == new_password:
                        return Response({"message": "Current password and new password are same.Please enter different password.", 'status_code': status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)    
                    
                    # user.set_password(new_password)
                    user.password=new_password

                    user.save()
                    return Response({"message": "Password changed successfully.",
                                    'status_code': status.HTTP_200_OK,
                                    'data':
                                    {
                                        'new_password':new_password
                                    }
                                    }, status.HTTP_200_OK)
                else:
                    return Response({"message": "Current password is incorrect.", 'status_code': status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message": "Error occured.", 'status_code': status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Please login to change password.", 'status_code':status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)    


# User Logout View
class UserLogoutView(APIView):
    authentication_classes = (MyCustomAuth,)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


    def destroy(self, request, *args, **kwargs):
        # simply delete the token to force a login
        auth_token = request.META.get("HTTP_AUTHORIZATION")
        auth_token = auth_token.split(' ')[1]

        token = Token.objects.filter(key = auth_token).first()        
             
        if token:
            token.delete()
        
        # Return success message with 200 status
        return Response({"message": "Logout successfully.",
                                    'status_code': status.HTTP_200_OK}, status.HTTP_200_OK)


    

#order api
class CreateOrder(ViewSet):
    
    def create(self,request):
        user = request.user

        customer  = request.data.get('customer') 
        due_date = request.data.get('due_date')
        category = request.data.get('category')
        vendor = request.data.get('vendor')
        product = request.data.get('product')
        quantity = request.data.get('quantity')
        packsize = request.data.get('packsize')
        OrderDetail = request.data.get('orderDetail')
        price = request.data.get('price')
        amount = request.data.get('amount')
        amount_recieved = request.data.get('amount_recieved')
        payment_status = request.data.get('payment_status')
        if not customer:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'customer required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not due_date:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'due date required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        due_date_obj = datetime.strptime(due_date,'%Y-%m-%d')
        
        if not category:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'category required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not product:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'product required'
                            },status=status.HTTP_400_BAD_REQUEST)
        if not quantity:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'quantity required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not packsize:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'packsize required'
                            },status=status.HTTP_400_BAD_REQUEST)

        if not price:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'price required'
                            },status=status.HTTP_400_BAD_REQUEST)   
        
        if not amount:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'amount required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not amount_recieved:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'amount recieved required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not payment_status:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'payment status requried'
                            },status =status.HTTP_400_BAD_REQUEST)

        customer_name = Customer.objects.filter(id=customer).first()
        
        if not customer_name:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid CustomerID'
                            },status =status.HTTP_400_BAD_REQUEST)

        pack_size_q = PackSizes.objects.filter(id=packsize).first()

        if not pack_size_q:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid PackSize ID'
                            },status =status.HTTP_400_BAD_REQUEST)

        product_q = Product.objects.filter(id=product).first()

        if not product_q:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid Product ID'
                            },status =status.HTTP_400_BAD_REQUEST)

        AddOrder = Order.objects.create(customer=customer_name,
                                        ordered_by = request.user,
                                        detail = OrderDetail,
                                        due_date = due_date_obj,
                                        amount=amount,
                                        amount_recieved =amount_recieved,
                                        status='OPEN',
                                        payment_status=payment_status)


        Orderq = OrderQuantity.objects.create(product=product_q,
                                             pack_size=pack_size_q,
                                             quantity=quantity,
                                             price=price,
                                             order=AddOrder)
        totalamount = float(quantity)*float(price)
        if Orderq:
            return Response({'status_code':status.HTTP_200_OK,
                            'message':'successfull',
                            'data':{
                                    'invoice_no':AddOrder.invoice_no,
                                    'total amount':totalamount
                                    },
                            },status=status.HTTP_200_OK)

        else:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'successfull',
                            'data':'cannot create order'
                            },status=status.HTTP_400_BAD_REQUEST)


    def destory(self,request):
        OrderQ = OrderQuantity.objects.filter(order=order).first()

        if  OrderQ:
            OrderQ.delete()
            return Response({'status_code':status.HTTP_200_OK,
                            'message':'successfull',
                            'data':'successfully removed product'
                            },status=status.HTTP_200_OK)
        
        else:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'no such product added'
                            },status=status.HTTP_400_BAD_REQUEST)

class AddProduct(ViewSet):

    def create(self,request):
        product = request.data.get('product')
        quantity = request.data.get('quantity')
        packsize = request.data.get('packsize')
        invoice_no = request.data.get('invoice_no')
        price = request.data.get('price')
        
        if not product:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'product required'
                            },status=status.HTTP_400_BAD_REQUEST)

        if not quantity:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'quantity required'
                            },status=status.HTTP_400_BAD_REQUEST)

        if not packsize:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'pack size required'
                            },status=status.HTTP_400_BAD_REQUEST)   

        if not invoice_no :
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'invoice required'
                            },status=status.HTTP_400_BAD_REQUEST)                                     
        
        if not price:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'price required'
                            },status=status.HTTP_400_BAD_REQUEST)


        packsize = packsize.split(',')
        quantity = quantity.split(',')
        product  = product.split(',')
        price    = price.split(',')
        if not (len(packsize) == len(quantity) == len(product) == len(price)):
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'all detail are not same'
                            },status=status.HTTP_400_BAD_REQUEST)
        n = len(product)
        
        order = Order.objects.filter(invoice_no=invoice_no).first()

        if not order:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid Invoice ID'
                            },status=status.HTTP_400_BAD_REQUEST)

    
        for i in range(n):
            packsizeobj = PackSizes.objects.filter(id=packsize[i]).first()
            productobj = Product.objects.filter(id= product[i]).first()
            Orderq = OrderQuantity.objects.create(product=productobj,
                                                pack_size=packsizeobj,
                                                quantity=quantity[i],
                                                price=price[i],
                                                order = order)
        
        return Response({'status_code':status.HTTP_200_OK,
                        'message':'successfull',
                        'data':'order created successfully'
                        },status=status.HTTP_200_OK)

class ViewUser(ViewSet):

    @action(methods=['POST',],detail=False)
    def salesuser(self,request):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        
        search_params = request.data.get('search_params')
        
        full_name = request.data.get('full_name')
        phone_number = request.data.get('phone_number')
        email = request.data.get('email')

        order_by_obj= []
        if full_name:
            order_by_obj.append(full_name)
        if email:
            order_by_obj.append(email)
        if phone_number:
            order_by_obj.append(phone_number) 
       
        SalesUser = User.objects.filter(user_type = 'SALESPERSON')
        if order_by_obj:
            SalesUser = SalesUser.order_by(*order_by_obj)
            
        if search_params:
            filteruser = SalesUser.filter(Q(full_name__icontains=search_params)|Q(email__icontains=search_params)|Q(phone_number__icontains=search_params))
            
            if not filteruser:
                return Response({'status_code':status.HTTP_200_OK,
                            'message':'successfull',
                            'data':[],
                            'total_record':0,
                            'filter_record':0
                            },status=status.HTTP_200_OK)    

            SalesUser = filteruser
            

        total_record = len(SalesUser)
        list_with_pagelimit = SalesUser[start:end]
        filter_record = len(list_with_pagelimit)
        serializers =  UserSerializers(list_with_pagelimit , many=True,context={'request':request})

        if serializers:
            return Response({'status_code':status.HTTP_200_OK,
                            'message':'successfull',
                            'data':serializers.data,
                            'total_record':total_record,
                            'filter_record':filter_record
                            },status=status.HTTP_200_OK)    
        else:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'serializers error' 
                            },status=status.HTTP_400_BAD_REQUEST)
    

    @action(methods=['POST',],detail=False)
    def warehouseuser(self,request):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        search_params = request.data.get('search_params')
        warehouseuser = User.objects.filter(user_type= 'WAREHOUSE')
        full_name = request.data.get('full_name')
        phone_number = request.data.get('phone_number')
        email = request.data.get('email')

        order_by_obj= []
        if full_name:
            order_by_obj.append(full_name)
        if email:
            order_by_obj.append(email)
        if phone_number:
            order_by_obj.append(phone_number) 
        
        if order_by_obj:
            filter_user = warehouseuser.order_by(*order_by_obj)
            warehouseuser = filter_user

        if search_params:
            filter_user = warehouseuser.filter(Q(full_name__icontains=search_params)|Q(email__icontains=search_params)|Q(phone_number__icontains=search_params))
            if not filter_user:
                return Response({'status_code':status.HTTP_200_OK,
                            'message':'successfull',
                            'data':[],
                            'total_record':0,
                            'filter_record':0
                            },status=status.HTTP_200_OK)    

            warehouseuser = filter_user    
        total_record = len(warehouseuser)
        list_with_pagelimit = warehouseuser[start:end]
        filter_record = len(list_with_pagelimit)
        serializers =  UserSerializers(list_with_pagelimit , many=True,context={'request':request})
        
        if serializers:
            return Response({'status_code':status.HTTP_200_OK,
                            'message':'successfull',
                            'data':serializers.data,
                            'total_record':total_record,
                            'filter_record':filter_record
                            },status=status.HTTP_200_OK)    
        else:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'serializers error',
                            },status=status.HTTP_400_BAD_REQUEST)

class CustomerDelete(ViewSet):
    def destroy(self,request,pk=None):
        user = Customer.objects.filter(pk=pk).first()

        if user:
            user.delete()
            return Response({'status_code':status.HTTP_200_OK,
                            'message':'successfull',
                            'data':'successfully deleted'
                            },status=status.HTTP_200_OK)
        
        else:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'No such Customer user'
                            },status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([])
class ForgotPassword(ViewSet):
    
    @action(methods=['POST',],detail=False)
    def sendmail(self,request):
        email = request.data.get('email')
        if not email:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'email requried'
                            },status=status.HTTP_400_BAD_REQUEST)

        VerifyUser =User.objects.filter(email=email).first()
           
        if VerifyUser:
            email = VerifyUser.email
            password = binascii.hexlify(os.urandom(6)).decode()
            # VerifyUser.set_password(password)
            VerifyUser.password=password
            VerifyUser.save()
            subject = 'Password Reset'
            message = 'Dear,{0} \n Your old password has been reset ,use this password: {1} to login into system . \n Please make sure you change this password to new password of your preference '.format(email,password)
            email_form = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email,]
            send_mail(subject,message,email_form,recipient_list)
            return Response({'status_code':status.HTTP_200_OK,
                    'message':'email send successfull',
                    },status=status.HTTP_200_OK)
        
        else:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'You are not the user'
                            },status=status.HTTP_400_BAD_REQUEST)



class SalesReports(ViewSet):
   
    
    @action(methods=['POST',],detail=False)
    def averagereport(self,request):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit

        month = request.data.get('month')
        year = request.data.get('year')

        product_name = request.data.get('product_name')
        total = request.data.get('total')
        average_ord = request.data.get('average_ord')

        search_value = request.data.get('search_value')
        order_by_obj = []
        
        if not month : 
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'month required'
                            },status=status.HTTP_400_BAD_REQUEST)

        if not year :
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'year required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        first_day = year+'-'+month+'-1'

        first_day = year+'-'+month+'-1'
        first_date_obj =  datetime.strptime(first_day,'%Y-%m-%d')
        last_day = monthrange(int(year),int(month))[1]
        last_date = year+'-'+month+'-'+str(last_day)
        last_date_obj = datetime.strptime(last_date,'%Y-%m-%d')
        allProd = Product.objects.all()
        total_record = len(allProd)
        value = []
        total_quantity = 0
        if allProd:
            for pro in allProd:
                filter_product = pro.orderquantity_set.filter(created_at__gt=first_date_obj,created_at__lt=last_date_obj)
                total_quantity = total_quantity+pro.available_quantity
                if filter_product:
                    sum_of_order = filter_product.aggregate(Sum('quantity'))
                    average = pro.available_quantity/sum_of_order.get('quantity__sum')
                    dic= {'product_name':pro.name,'total':sum_of_order.get('quantity__sum'),'average':average}
                    value.append(dic)
                
                else:
                    value.append({
                        'product_name':pro.name,'total':0,'average':0
                    })

    
            total_record = len(value)
            list_with_pagelimit = value
            if product_name:
                if product_name == '-product_name':
                    list_with_pagelimit =sorted(list_with_pagelimit,key=itemgetter('product_name'),reverse=True)
                else:
                    list_with_pagelimit= sorted(list_with_pagelimit,key=itemgetter('product_name'))
            if total:
                
                if total == '-total':
                    list_with_pagelimit = sorted(list_with_pagelimit,key=itemgetter('total'),reverse=True)
                else:
                 list_with_pagelimit=sorted(list_with_pagelimit,key=itemgetter('total'))
                
            if average_ord:
                if average_ord == '-average':
                    list_with_pagelimit = sorted(list_with_pagelimit,key=itemgetter('average'),reverse=True)
                else:
                    list_with_pagelimit = sorted(list_with_pagelimit,key=itemgetter('average'))

            if search_value:
                temp = []
                for a in list_with_pagelimit:
                    if a['product_name'].lower() == search_value.lower():           
                        temp.append(a)
                    if search_value.isnumeric():
                        if a['total'] == int(search_value):
                            temp.append(a)
                        if a['average'] == int(search_value):
                            temp.append(a)
                if len(temp) == 0 :
                    return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                    'message': 'your search parameter does not match any value'
                                    },status=status.HTTP_400_BAD_REQUEST)
                else:
                    total_record = len(temp)
                    list_with_pagelimit = temp[start:end]
                    filter_record = len(list_with_pagelimit)
                    return Response({'status_code':status.HTTP_200_OK,
                                    'message':'successfull',
                                    'data':list_with_pagelimit,
                                    'total_record':total_record,
                                    'filter_record':filter_record
                                    },status=status.HTTP_200_OK)
                    
            list_with_pagelimit = list_with_pagelimit[start:end]
            filter_record = len(list_with_pagelimit)
            return Response({'status_code':status.HTTP_200_OK,
                            'message':'successfull',
                            'data':list_with_pagelimit,
                            'total_record':total_record,
                            'filter_record':filter_record
                            },status=status.HTTP_200_OK)

        else:
            return Response({'status_code':status.HTTP_200_OK,
                            'message':'No Data Found',
                            },status=status.HTTP_200_OK)


class VerifyOrder(ViewSet):

    @action(methods=['POST',],detail=False)
    def verifyorder(self,request):
        try:
            barcode_string = request.data.get('barcode_string')
            invoice_id = request.data.get('invoice_id')
            if not barcode_string:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'barcode string required'
                                },status=status.HTTP_400_BAD_REQUEST)
            
            if not invoice_id:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'invoice_id required'
                                },status=status.HTTP_400_BAD_REQUEST)
            
            verify_barcode = Product.objects.filter(barcode_string=barcode_string).first()
            order_obj = Order.objects.filter(invoice_no=invoice_id,status='OPEN').first()
            if not verify_barcode :
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'invalid barcode or no such barcode exist'
                                },status=status.HTTP_400_BAD_REQUEST)
            if not order_obj:
               return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'no such invoice id or status is not open'
                                },status=status.HTTP_400_BAD_REQUEST)
            verify_ord = OrderQuantity.objects.filter(order=order_obj,product=verify_barcode)    
            if verify_ord:
                    total_quantity = 0
                    for quanti in verify_ord:
                        total_quantity = total_quantity+quanti.quantity
                    
                    is_available = verify_barcode.available_quantity - total_quantity   
                    if is_available > 0:
                        return Response({'status_code':status.HTTP_200_OK,
                                        'message':'successfull'
                                        },status=status.HTTP_200_OK)
                    else:
                        return Response({'statu_code':status.HTTP_400_BAD_REQUEST,
                                        'message':'available quantity is less than required quantity'
                                        },status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'product not in present in order'
                                },status=status.HTTP_400_BAD_REQUEST)
                
           
        except Exception as e:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'something went wrong'})

class productlisting(APIView):

    def get(self,request,*args,**kwargs):
        try:
            allProduct = Product.objects.all()
            serializers = ProductSerializers(allProduct,many = True)
            if not serializers:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'some error in serializers'
                                },status.HTTP_400_BAD_REQUEST)
            return Response({'status_code':status.HTTP_200_OK,
                            'messsage':'successful',
                            'data':serializers.data
                            },status.HTTP_200_OK)
        except Exception as e:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'some error'
                            },status.HTTP_400_BAD_REQUEST)


class PackSizeListing(ViewSet):

    @action(methods=['POST',],detail=False)
    def listview(self,request):
        try:
            product_id = request.data.get('product_id')
            if not product_id:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'product id required'
                                },status=status.HTTP_400_BAD_REQUEST)
            Pro_obj = Product.objects.filter(id=product_id).first()

            if not Pro_obj:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'no Product found for that id'
                                },status=status.HTTP_400_BAD_REQUEST)
                        
            product_pack = Pro_obj.pack_size.all()
            if not product_pack:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'no packsize found for that product'
                                },status=status.HTTP_400_BAD_REQUEST)
            
            serializers = ProductPackSizesSerializers(product_pack , many=True)
            return Response({'status_code':status.HTTP_200_OK,
                            'message':'successfull',
                            'data':serializers.data
                            },status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'something went wrong'
                            },status=status.HTTP_400_BAD_REQUEST)

class Vendorlist(ViewSet):
    
    @action(methods=['POST'],detail=False)
    def listview(self,request):
        try:
            print("---->",request.data)
            category_id = request.data.get('category')
            if not category_id:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'category id required'
                                },status=status.HTTP_400_BAD_REQUEST)

            cat_obj = Categories.objects.filter(id=category_id).first()
            if not cat_obj :
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'invalid category id'})

            vendor_list = cat_obj.vendor_set.all()
            if not vendor_list:
                return Response({'status_code':status.HTTP_200_OK,
                                'data' : [],
                                'message':'no vendor for that category'})
            serializers = VendorSerializer(vendor_list , many=True)

            
            return Response({'status_code':status.HTTP_200_OK,
                            'message':'successfull',
                            'data':serializers.data
                            },status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'something went wrong'
                            },status=status.HTTP_400_BAD_REQUEST)
            


class ProductListFromcatandVen(ViewSet):
    
    @action(methods=['POST'],detail=False)
    def search_product(self,request):
        try:
            search_params = request.data.get('search_params')
            if not search_params:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Search Parameters are required'
                },status=status.HTTP_400_BAD_REQUEST)

            filter_product = Product.objects.filter(Q(name__icontains=search_params)|
                                                    Q(item_no__icontains=search_params)).order_by('name')
            if not filter_product:
                return Response({'status_code':status.HTTP_200_OK,
                                'message':'No matching product found',
                                'data':[]
                                },status=status.HTTP_200_OK)

            serializers = ProductSerializersWithPack(filter_product,many=True)
            if serializers:
                return Response({'status_code':status.HTTP_200_OK,
                                'message':'successfull',
                                'data':serializers.data
                                },status=status.HTTP_200_OK)
            else:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'some serializers error'
                                },status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print('e: ', e)
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'some error'
                            },status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'],detail=False)
    def listview(self,request):
        try:
            
            category_id = request.data.get('category')
            vendor_id = request.data.get('vendor')
            if not category_id:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'category id required'
                                },status=status.HTTP_400_BAD_REQUEST)
            if not vendor_id:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'vendor id required'
                                },status=status.HTTP_400_BAD_REQUEST)
            filter_product = Product.objects.filter(category=category_id , vendor=vendor_id).order_by('name')
            if not filter_product:
                return Response({'status_code':status.HTTP_200_OK,
                                'message':'no product for that category and vendor',
                                'data':[]
                                },status=status.HTTP_200_OK)
            serializers = ProductSerializersWithPack(filter_product,many=True)
            if serializers:
                return Response({'status_code':status.HTTP_200_OK,
                                'message':'successfull',
                                'data':serializers.data
                                },status=status.HTTP_200_OK)
            else:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'some serializers error'
                                },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print('e: ', e)
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'some error'
                            },status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'],detail=False)
    def list_from_category(self,request):
        try:
            
            category_id = request.data.get('category')
            vendor_id = request.data.get('vendor')
            if not category_id:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'category id required'
                                },status=status.HTTP_400_BAD_REQUEST)
            
            filter_product = Product.objects.filter(category=category_id)
            if not filter_product:
                return Response({'status_code':status.HTTP_200_OK,
                                'message':'no product for that category and vendor',
                                'data':[]
                                },status=status.HTTP_200_OK)
            serializers = ProductSerializersWithPack(filter_product,many=True)
            if serializers:
                return Response({'status_code':status.HTTP_200_OK,
                                'message':'successfull',
                                'data':serializers.data
                                },status=status.HTTP_200_OK)
            else:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'some serializers error'
                                },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print('e: ', e)
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'some error'
                            },status=status.HTTP_400_BAD_REQUEST)

class Product_from_category(ViewSet):    
    @action(methods=['POST'],detail=False)
    def listview(self,request):
        '''
        List Product with packsiz and price from Category

        '''
        try:
            
            category_id = request.data.get('category')
            vendor_id = request.data.get('vendor')

            if not category_id:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'category id required'
                                },status=status.HTTP_400_BAD_REQUEST)
            
            if not vendor_id:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'vendor id required'
                                },status=status.HTTP_400_BAD_REQUEST)
                                

            filter_product = Product.objects.filter(category=category_id,vendor=vendor_id).order_by('name')
            if not filter_product:
                return Response({'status_code':status.HTTP_200_OK,
                                'message':'no product for that category',
                                'data':[]
                                },status=status.HTTP_200_OK)
            serializers = ProductSerializersWithPack(filter_product,many=True)
            if serializers:
                return Response({'status_code':status.HTTP_200_OK,
                                'message':'successfull',
                                'data':serializers.data
                                },status=status.HTTP_200_OK)
            else:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'some serializers error'
                                },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print('e: ', e)
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Something went wrong!',
                            'error':str(e)
                            },status=status.HTTP_400_BAD_REQUEST)


class VendorListingWithoutPagination(ViewSet):
    def list(self,request):
        vendor_list = Vendor.objects.all()

        serializers = VendorSerializer(vendor_list ,many=True)

        return Response({'status_code':status.HTTP_200_OK,
                        'message':'successfull',
                        'data':serializers.data 
                        },status=status.HTTP_200_OK)


class ProductPackSizesCrud(ViewSet):

    def list(self,request):
        product_packsize = ProductPackSizes.objects.all()

        serializers = ProductPackSizesSerializers(product_packsize , many=True)
        return Response({'status_code':status.HTTP_200_OK,
                        'message':'successfull',
                        'data':serializers.data
                        },status=status.HTTP_200_OK)
    
    def create(self,request):
        packsize = request.data.get('packsize')
        
        price = request.data.get('price')

        if not packsize:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'packsize required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        
        if not price:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'price required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        packsize_obj = PackSizes.objects.filter(id=packsize).first()
        
        if not packsize_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'no such packsize'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        product_packsize_obj = ProductPackSizes.objects.create(packsize=packsize_obj,price=price)
        if not product_packsize_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'could not create the pack size'
                            },status=status.HTTP_400_BAD_REQUEST)
        serializers = ProductPackSizesSerializers(product_packsize_obj)
        return Response({'status_code':status.HTTP_200_OK,
                        'message':'successfull',
                        'data':serializers.data
                        },status=status.HTTP_200_OK)
    
    def partial_update(self,request,pk=None):
        uid = pk
        packsize = request.data.get('packsize')
        price= request.data.get('price')

        if not uid:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'id required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        verify_id = ProductPackSizes.objects.filter(pk=uid).first()
        if not verify_id:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'no such product pack size'
                            },status=status.HTTP_400_BAD_REQUEST)
        if packsize:
            verify_packsize = PackSizes.objects.filter(id=packsize).first()
            if not verify_packsize:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'no such pack sizes',
                                },status=status.HTTP_400_BAD_REQUEST)
            ProductPackSizes.objects.filter(id=uid).update(packsize=verify_packsize)
        
        if price:
            ProductPackSizes.objects.filter(id=uid).update(price=price)
        
       
        obj = ProductPackSizes.objects.filter(id=uid)
        serializers = ProductPackSizesSerializers(obj , many=True)
        
        return Response({'status_code':status.HTTP_200_OK,
                        'message':'successfull',
                        'data':serializers.data
                        },status=status.HTTP_200_OK)

    def destroy(self,request,pk):

        uid = pk 
        if not uid:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'id required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        verify_packsize = ProductPackSizes.objects.filter(id=uid)

        if not verify_packsize:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'no such product paack size'
                            },status=status.HTTP_400_BAD_REQUEST)
        verify_packsize.delete()
        return Response({'status_code':status.HTTP_200_OK,
                        'message':'successfully  deleted'
                        },status=status.HTTP_200_OK)

    @action(detail=False,methods=['POST'])
    def listview(self,request,*args,**kwargs):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
    
        search_param = request.data.get('search_param')
        if search_param:
            pack_size = PackSizes.objects.filter(size__icontains=search_param)
            total_record = len(pack_size)
            pack_size = pack_size[start:end]
            filter_record = len(pack_size)

        else:
            pack_size = PackSizes.objects.all()
            total_record = len(pack_size)
            pack_size = pack_size[start:end]
            filter_record = len(pack_size)
        
        if pack_size:
            serilizer = ProductPackSizesSerializers(pack_size,many=True)
            response = {
                    'status_code':status.HTTP_200_OK,
                    'data':serilizer.data,
                    'total_record':total_record,
                    'filter_record':filter_record,
                    }
            return Response(response, status=status.HTTP_200_OK)

        response = {
            'status_code':status.HTTP_200_OK,
            'message':'No PackSize Available',
            'data':[],
            'total_record':0,
            'filter_record':0,
        }

        return Response(response, status=status.HTTP_200_OK)


class PaymentHistoryCrud(ViewSet):

    @action(methods=['POST',],detail=False)
    def listview(self,request):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        user = request.user
        customer_id = request.data.get('customer_id')
        customer_obj = Customer.objects.filter(id=customer_id).first()
        from_date = request.data.get('from_date')
        to_date = request.data.get('to_date')
        payment_method = request.data.get('payment_method')

        order_by_obj = []
        method = request.data.get('method')
        reference_no = request.data.get('reference_no')
        payment_date = request.data.get('payment_date')
        image = request.data.get('image')
        amount_recieved = request.data.get('amount_recieved')
        if method:
            order_by_obj.append(method)
        if reference_no:
            order_by_obj.append(reference_no)
        if payment_date:
            order_by_obj.append(payment_date)
        if image:
            order_by_obj.append(image)
        if amount_recieved:
            order_by_obj.append(amount_recieved)
        
        
        search_value = request.data.get('search_value')

        if not customer_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'invalid customerid',
                            },status=status.HTTP_400_BAD_REQUEST)
        
        allPayment = PaymentHistory.objects.filter(customer=customer_obj)
        if order_by_obj:
            allPayment = allPayment.order_by(*order_by_obj)
        if search_value:
            allPayment = allPayment.filter(Q(customer__full_name__icontains=search_value)|
                                           Q(method__icontains=search_value)|
                                           Q(reference_no__icontains=search_value)|
                                           Q(amount_recieved__icontains=search_value)
                                           )

        if from_date and to_date:
            try:
                from_date_obj= datetime.strptime(from_date,'%Y-%m-%d')
                to_date_obj = datetime.strptime(to_date,'%Y-%m-%d')
                allPayment= allPayment.filter(payment_date__gte=from_date_obj , payment_date__lte=to_date_obj)
        
            except Exception as e:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'date format should be YY-MM-DD'
                                },status=status.HTTP_400_BAD_REQUEST)
        
        if payment_method:
            allPayment = allPayment.filter(method=payment_method)

        total_record = len(allPayment)
        data_qs = CreditMemo.objects.filter(customer=customer_obj)
        sum_val = data_qs.aggregate(Sum('credit_amount'))['credit_amount__sum']
        customer_detail = {'customer_name':customer_obj.full_name,
                          'email_address':customer_obj.email,
                          'phone':customer_obj.phone,
                          'phone':customer_obj.phone,
                          'available_credit' : sum_val
                          }
        list_with_pagelimit =allPayment[start:end] 
        filter_record = len(list_with_pagelimit)
        serializers = PaymentHistorySerializers(list_with_pagelimit ,context={'request':request},many=True)
        data = {}
        data.update({'cusotmer_detail':customer_detail,
                'payment_detail':serializers.data})
        
        return Response({'status_code':status.HTTP_200_OK,
                        'message':'successfull',
                        'data':data,
                        'filter_record':filter_record,
                        'total_record':total_record
                        },status=status.HTTP_200_OK)

    @action(methods=['POST',],detail=False)
    def allpaymenthistory(self,request):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        
        
        
        from_date = request.data.get('from_date')
        to_date = request.data.get('to_date')
        payment_method = request.data.get('payment_method')

        order_by_obj = []
        method = request.data.get('method')
        reference_no = request.data.get('reference_no')
        payment_date = request.data.get('payment_date')
        image = request.data.get('image')
        amount_recieved = request.data.get('amount_recieved')
        if method:
            order_by_obj.append(method)
        if reference_no:
            order_by_obj.append(reference_no)
        if payment_date:
            order_by_obj.append(payment_date)
        if image:
            order_by_obj.append(image)
        if amount_recieved:
            order_by_obj.append(amount_recieved)
        
        
        search_value = request.data.get('search_value')
        
        allPayment = PaymentHistory.objects.all()
        
        if order_by_obj:
            allPayment = allPayment.order_by(*order_by_obj)
       
        if search_value:
           
           allPayment = allPayment.filter(Q(customer__full_name__icontains=search_value)|
                                           Q(method__icontains=search_value)|
                                           Q(reference_no__icontains=search_value)|
                                           Q(amount_recieved__icontains=search_value)
                                           )
           
        
        if from_date and to_date:
            try:
                from_date_obj= datetime.strptime(from_date,'%Y-%m-%d')
                to_date_obj = datetime.strptime(to_date,'%Y-%m-%d')
                allPayment= allPayment.filter(payment_date__gte=from_date_obj , payment_date__lte=to_date_obj)
        
            except Exception as e:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'date format should be YY-MM-DD'
                                },status=status.HTTP_400_BAD_REQUEST)
        
        if payment_method:
            allPayment = allPayment.filter(method=payment_method)
        

        
        total_record = len(allPayment)
        list_with_page_limit = allPayment[start:end]
        filter_record = len(list_with_page_limit)
        serializers = AllPaymentHistorySerializers(list_with_page_limit,context={'request':request},many=True)
        return Response({'status_code':status.HTTP_200_OK,
                        'message':'successfull',
                        'data':serializers.data,
                        'total_record':total_record,
                        'filter_record':filter_record
                        },status=status.HTTP_200_OK)



class PaymentReceived(ViewSet):

    def create(self,request):
        customer_id = request.data.get('customer_id')
        payment_date = request.data.get('payment_date')

        if not customer_id:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'customer id required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not payment_date:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'payment date required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment_date_obj = datetime.strptime(payment_date,'%Y-%m-%d')
        except Exception as e:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'date format should be YY-MM-DD'
                            },status=status.HTTP_400_BAD_REQUEST)

        customer_obj = Customer.objects.filter(id=customer_id).first()
        if not customer_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'user is not customer'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        
        create_obj=PaymentHistory.objects.create(customer=customer_obj,payment_date=payment_date,
                                                amount_recieved=0,reference_no=0,method='CHECK')
        
        serializer = AllPaymentHistorySerializers(create_obj, context={'request':request} )
        return Response({'status_code':status.HTTP_200_OK,
                        'message':'successfull',
                        'data':serializer.data
                        },status=status.HTTP_200_OK)



class PaymentMethodCrud(APIView):

    
    def post(self,request,id=None):
        payment_history = PaymentHistory.objects.filter(id=id)
        if not payment_history:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'no such payment history available'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        payment_method = request.data.get('payment_method')
        amount_received = int(request.data.get('amount_received'))
        cheque_no = request.data.get('cheque_no')
        image = request.data.get('image')
        paymentData = request.data.get('paymentData')
        print(request.data)
        if not amount_received:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'amount received required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not payment_method:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'payment method required'
                            },status=status.HTTP_400_BAD_REQUEST)

        if payment_method =='CHECK':
            if not cheque_no:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'cheque no required'
                                },status=status.HTTP_400_BAD_REQUEST)
            
            payment_history.update(method=payment_method,reference_no=cheque_no,amount_recieved=amount_received)
        if payment_method == 'CASH':
            reference_no=uuid.uuid4().hex[:6].upper()
            payment_history.update(method=payment_method,reference_no=reference_no,amount_recieved=amount_received)
        
        if image:
            payment_history.update(image=image)

        customer_obj = payment_history[0].customer

        customer_order = Order.objects.filter(customer=customer_obj).order_by('created_at')

        for order in customer_order:
            if amount_received < 0:
                break
            
            if order.payment_status == 'FULL':
                continue
            
            if not paymentData:
                remain_amount = int(order.remaining_amount)
                if remain_amount-amount_received <= 0:
                    order.amount_recieved = order.amount
                    order.payment_status = 'FULL'
                    amount_received = amount_received- remain_amount
                    order.save()
                    continue
                
                if remain_amount-amount_received > 0:
                    order.amount_recieved = order.amount_recieved+amount_received
                    amount_received = amount_received -remain_amount 
                    order.payment_status = 'PARTIAL'
                    order.save() 
            else:
                data_dict = {}
                for d in paymentData:
                    data_dict[d["id"]]=d["payment"]

                if order.id in data_dict.keys():
                    order.amount_recieved = order.amount_recieved+ data_dict[order.id]
                    order.save()
                    
                    if order.remaining_amount > 0:
                        order.payment_status = 'PARTIAL'
                    else:
                        order.payment_status = 'FULL'
                    order.save()

        serializer = AllPaymentHistorySerializers(payment_history,many=True,context={'request':request})
        

        return Response({'status_code':status.HTTP_200_OK,
                        'message':'successfull',
                        'data':serializer.data
                        },status=status.HTTP_200_OK)


#backup of old API
# class AddUpdatePaymentHistory(APIView):

#     def post(self,request):
        
#         customer_id = request.data.get('customer_id')
#         payment_date = request.data.get('payment_date')
#         image = request.data.get('image')
#         amount_received = request.data.get('amount_received')
#         cheque_no = request.data.get('cheque_no')
#         payment_method = request.data.get('payment_method')
        
#         paymentData = json.loads(request.POST.get('paymentData'))

#         if not customer_id:
#             return Response({'status_code':status.HTTP_400_BAD_REQUEST,
#                             'message':'Customer id required'
#                             },status=status.HTTP_400_BAD_REQUEST)
        
#         customer_obj = Customer.objects.filter(id=customer_id).first()
#         if not customer_obj:
#             return Response({'status_code':status.HTTP_400_BAD_REQUEST,
#                             'message':'Invalid customer!'
#                             },status=status.HTTP_400_BAD_REQUEST)
        
        
#         if not amount_received:
#             return Response({'status_code':status.HTTP_400_BAD_REQUEST,
#                             'message':'amount received required'
#                             },status=status.HTTP_400_BAD_REQUEST)
#         else:
#             amount_received = float(amount_received)
        
#         if not payment_method:
#             return Response({'status_code':status.HTTP_400_BAD_REQUEST,
#                             'message':'payment method required'
#                             },status=status.HTTP_400_BAD_REQUEST)

#         reference_no = 0
#         if payment_method =='CHEQUE':
#             if not cheque_no:
#                 return Response({'status_code':status.HTTP_400_BAD_REQUEST,
#                                 'message':'cheque no required'
#                                 },status=status.HTTP_400_BAD_REQUEST)
            
#             reference_no=cheque_no
    
#         if payment_method == 'CASH':
#             reference_no=uuid.uuid4().hex[:6].upper()
            
#         if image:
#             check_img = image
#         else:
#             check_img = None
        
#         create_obj=PaymentHistory.objects.create(
#                                 customer=customer_obj,
#                                 payment_date=datetime.now().date(),
#                                 amount_recieved=amount_received,
#                                 reference_no=reference_no,
#                                 method=payment_method,
#                                 image=check_img)

        
#         customer_order = Order.objects.filter(customer=customer_obj).order_by('created_at')

#         for order in customer_order:
#             if amount_received < 0:
#                 break
            
#             if order.payment_status == 'FULL':
#                 continue
            
#             if not paymentData:
#                 remain_amount = int(order.remaining_amount)
#                 if remain_amount-amount_received <= 0:
#                     order.amount_recieved = order.amount
#                     order.payment_status = 'FULL'
#                     amount_received = amount_received- remain_amount
#                     order.save()
#                     continue
                
#                 if remain_amount-amount_received > 0:
#                     order.amount_recieved = order.amount_recieved+amount_received
#                     amount_received = amount_received -remain_amount 
#                     order.payment_status = 'PARTIAL'
#                     order.save() 
#             else:
#                 data_dict = {}
#                 for d in paymentData:
#                     data_dict[d["id"]]=d["payment"]

#                 if order.id in data_dict.keys():
#                     order.amount_recieved = order.amount_recieved + data_dict[order.id]
#                     order.save()
                    
#                     if order.remaining_amount > 0:
#                         order.payment_status = 'PARTIAL'
#                     else:
#                         order.payment_status = 'FULL'
#                     order.save()

#         serializer = AllPaymentHistorySerializers(create_obj,context={'request':request})
#         return Response({'status_code':status.HTTP_200_OK,
#                         'message':'successfull',
#                         'data':serializer.data
#                         },status=status.HTTP_200_OK)

class AddUpdatePaymentHistory(APIView):

    def post(self,request):
        
        customer_id = request.data.get('customer_id')
        image = request.data.get('image')
        cheque_no = request.data.get('cheque_no')
        payment_method = request.data.get('payment_method')
        
        paymentData = json.loads(request.POST.get('paymentData'))

        if not customer_id:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Customer id required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        customer_obj = Customer.objects.filter(id=customer_id).first()
        if not customer_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid customer!'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not payment_method:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'payment method required'
                            },status=status.HTTP_400_BAD_REQUEST)

        reference_no = 0
        if payment_method =='CHECK':
            if not cheque_no:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'cheque no required'
                                },status=status.HTTP_400_BAD_REQUEST)
            
            reference_no=cheque_no
    
        if payment_method == 'CASH':
            reference_no=uuid.uuid4().hex[:6].upper()
            
        if image:
            check_img = image
        else:
            check_img = None
        
        if not paymentData:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'paymentData id required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        customer_order = Order.objects.filter(customer=customer_obj).order_by('created_at')

        for order in customer_order:
            data_dict = {}
            for invoice_data in paymentData:
                data_dict[invoice_data["invoice_id"]]= invoice_data

            if order.id in data_dict.keys():
                order.amount_recieved = order.amount_recieved + data_dict[order.id]["payment_amount"]
                order.save()
                
                if order.remaining_amount > 0:
                    order.payment_status = 'PARTIAL'
                else:
                    order.payment_status = 'FULL'
                order.save()
                
                # Add entry in PaymentHistory table 
                payment_history_obj = PaymentHistory.objects.create(
                                        order = order,
                                        customer=customer_obj,
                                        payment_date=datetime.now().date(),
                                        amount_recieved = data_dict[order.id]["payment_amount"],
                                        reference_no=reference_no,
                                        method=payment_method,
                                        image=check_img)
                serializer = AllPaymentHistorySerializers(payment_history_obj,context={'request':request})

                # add entry in cretememo if payment status in [over]
                if data_dict[order.id]["payment_status"] == "over":
                    previous_obj = CreditMemo.objects.all().last()
                    if previous_obj:
                        new_cm_no =  "CM - " + str(int(previous_obj.cm_no[4:]) + 1)
                    else:
                        new_cm_no = 'CM - 501'

                    credit_amount = data_dict[order.id]["payment_amount"] - data_dict[order.id]["open_balance"]
                    creditmemo_obj = CreditMemo.objects.create(
                                            cm_no = new_cm_no,
                                            order = order,
                                            customer=customer_obj,
                                            payment_history = payment_history_obj,
                                            payment_amount = data_dict[order.id]["payment_amount"],
                                            open_balance = data_dict[order.id]["open_balance"],
                                            credit_amount = credit_amount,
                                            updated_credit_amount = credit_amount,
                                            description = "Credit received"
                                            )

            
                    #  Generate PDF for credit_memo 
                    pdfdata_res = get_creditmemo_pdfdata(creditmemo_obj=creditmemo_obj) #Fetch PDF-Data
                    if pdfdata_res["status_code"] != True:
                        return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        pdf_data = pdfdata_res.get("pdf_data")
                        num_of_row_data  = pdfdata_res.get("num_of_row_data")
                    
                    # Creating PDF 
                    filename = 'file' + new_cm_no + '.pdf' 
                    createpdf_res = create_pdf(request = request,
                                        pdf_type = "credit_memo_pdf",
                                        pdf_data = pdf_data,
                                        filename = filename,
                                        order_obj = creditmemo_obj,
                                        num_of_row_data = num_of_row_data,
                                    )
                    if createpdf_res["status_code"] != True:
                        return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        data = {}
                        data['pdf_url'] = createpdf_res.get("pdf_url")



        return Response({'status_code':status.HTTP_200_OK,
                        'message':'successfull',
                        'data':serializer.data
                        },status=status.HTTP_200_OK)


class UpdateCheckImg(APIView):

    def post(self,request):
        
        payment_history_id = request.data.get('payment_history_id')
        check_image = request.data.get('check_image')

        if not payment_history_id:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'payment_history_id is required'
                            },status=status.HTTP_400_BAD_REQUEST)
        else:
            payment_history_obj = PaymentHistory.objects.filter(id=payment_history_id).last()
            if not payment_history_obj:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid payment_history!'
                            },status=status.HTTP_400_BAD_REQUEST)

        if not check_image:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'check_image is required'
                            },status=status.HTTP_400_BAD_REQUEST)

        payment_history_obj.image = check_image
        payment_history_obj.save()

        return Response({'status_code':status.HTTP_200_OK,
                        'message':'successfull'},
                        status=status.HTTP_200_OK)

class OrderDisplayFromCustomerid(ViewSet): 
    @action(methods=['POST',],detail=False)
    def displayorder(self,request):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit


        customer_id = request.data.get('customer_id')
        if not customer_id:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'customer id required'
                            },)
        customer_obj = Customer.objects.filter(id=customer_id).first()
        if not customer_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'invalid CustomerID'
                },)

        order_by_obj = []
        
        search_value = request.data.get('search_params')
        created_at = request.data.get('created_at')
        invoice_no = request.data.get('invoice_no')
        due_date = request.data.get('due_date')
        amount = request.data.get('amount')
        status_order = request.data.get('status')
        verfication_status = request.data.get('verfication_status')
        amount_recieved = request.data.get('amount_recieved')
        payment_status = request.data.get('payment_status')
        ordered_by = request.data.get('ordered_by')

        # Filters
        for_payment = request.data.get('for_payment',None)
        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')

        if created_at:
            order_by_obj.append(created_at)
        if invoice_no:
            order_by_obj.append(invoice_no)
        if due_date:
            order_by_obj.append(due_date)
        if amount:
            order_by_obj.append(amount)
        if status_order:
            order_by_obj.append(status_order)
        if verfication_status:
            order_by_obj.append(verfication_status)
        if amount_recieved:
            order_by_obj.append(amount_recieved)
        if payment_status:
            order_by_obj.append(payment_status)
        if ordered_by:
            ordered_by = ordered_by+"__full_name"
            print('ordered_by: ', ordered_by)
            order_by_obj.append(ordered_by)
        
        # start_date = datetime.now().date() - timedelta(days=30)
        # end_date = datetime.now().date()

        # allorder = Order.objects.filter(customer=customer_obj,remaining_amount__gt=0.0,created_at__range = (start_date,end_date)).order_by('-created_at')
        
        allorder = Order.objects.filter(customer=customer_obj,remaining_amount__gt=0.0).order_by('-created_at')
        if for_payment:
            allorder = allorder.exclude(payment_status='FULL')

        if From_Date not in ["null","Null",None] and To_Date not in ["null","Null",None] :
            if From_Date and To_Date:
                try:
                    from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                    to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                    d = timedelta(days=1)
                    to_date_obj = to_date_obj + d #adding 1 day
                    allorder = allorder.filter(invoice_date__range=(from_date_obj,to_date_obj))
                except Exception as e:
                    return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                    'message':'Invalid date format date Format should year-month-date'
                                    },status=status.HTTP_400_BAD_REQUEST)

        if order_by_obj:
            allorder = allorder.order_by(*order_by_obj)

            # allorder = allorder.order_by(*ordered_by)
        if search_value:
            allorder = allorder.filter( Q(created_at__icontains=search_value)|
                                        Q(invoice_no__icontains=search_value)|
                                        Q(due_date__icontains=search_value)|
                                        Q(amount__icontains=search_value)|
                                        Q(amount_recieved__icontains=search_value)|
                                        Q(payment_status__icontains=search_value)|
                                        Q(ordered_by__full_name__icontains=search_value)|
                                        Q(verfication_status__icontains=search_value)
                                        )
        total_record = len(allorder)

        list_with_page_limit = allorder[start:end]
        filter_record=len(list_with_page_limit)
        serializer = OrderFromCustomerIDSerializers(list_with_page_limit , many=True)
        serializer_data = serializer.data
        data = {}

        customer_allorder = Order.objects.filter(customer=customer_obj)
        total_remaining_amount = customer_allorder.aggregate(Sum('remaining_amount'))['remaining_amount__sum']
        total_amount = customer_allorder.aggregate(Sum('amount'))['amount__sum']
        total_amount_received = customer_allorder.aggregate(Sum('amount_recieved'))['amount_recieved__sum']
        
        # for order in customer_allorder:
        #     total_remaining_amount=total_remaining_amount+order.remaining_amount
        #     total_amount = total_amount+order.amount
        #     total_amount_received += order.amount_recieved

        data.update({
            'customer_id':customer_obj.id,
            'customer_name':customer_obj.full_name,
            'customer_number':customer_obj.phone,
            'customer_email':customer_obj.email,
            'total_remaining_amount':total_remaining_amount,
            'credit_balance':customer_obj.credit_balance,
            'total_amount':total_amount,
            'total_amount_received':total_amount_received,
            'allorder':serializer_data
        })

        return Response({'status_code':status.HTTP_200_OK,
                        'message':'successfull',
                        'data':data,
                        'filter_record':filter_record,
                        'total_record':total_record
                        },status=status.HTTP_200_OK)

class CreditMemoView(ViewSet):

    def create(self,request,*args,**kwargs):
        customer_id = request.data.get('customer_id')
        credit_amount = request.data.get('credit_amount')
        description = request.data.get('description')

        if not customer_id:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Customer id required'
                            },status=status.HTTP_400_BAD_REQUEST)

        customer_obj = Customer.objects.filter(id=customer_id).first()
        if not customer_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid CustomerID'
                },)

        if not credit_amount:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                        'message':'credit_amount required'
                        },status=status.HTTP_400_BAD_REQUEST)

        # CM_no genration code
        previous_obj = CreditMemo.objects.all().last()
        # if previous_obj:
        #     new_cm_no =  "CM_" + str(int(previous_obj.cm_no[3:]) + 1)
        # else:
        #     new_cm_no = 'CM_1'

        if previous_obj:
            new_cm_no =  "CM - " + str(int(previous_obj.cm_no[4:]) + 1)
        else:
            new_cm_no = 'CM - 501'

        creditmemo_obj = CreditMemo.objects.create(
                                            cm_no = new_cm_no,
                                            customer=customer_obj,
                                            credit_amount = credit_amount,
                                            updated_credit_amount = credit_amount,
                                            description=description)

       #  Generate PDF for credit_memo 
        pdfdata_res = get_creditmemo_pdfdata(creditmemo_obj=creditmemo_obj) #Fetch PDF-Data
        if pdfdata_res["status_code"] != True:
            return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
        else:
            pdf_data = pdfdata_res.get("pdf_data")
            num_of_row_data  = pdfdata_res.get("num_of_row_data")
        
        # Creating PDF 
        filename = 'file' + new_cm_no + '.pdf' 
        createpdf_res = create_pdf(request = request,
                            pdf_type = "credit_memo_pdf",
                            pdf_data = pdf_data,
                            filename = filename,
                            order_obj = creditmemo_obj,
                            num_of_row_data = num_of_row_data,
                        )
        if createpdf_res["status_code"] != True:
            return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {}
            data['pdf_url'] = createpdf_res.get("pdf_url")

        response_data = {
            'status_code':status.HTTP_200_OK,
            'message':"Successfull"
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(methods=['POST',],detail=False)
    def edit(self,request,*args,**kwargs):
        cm_no = request.data.get('cm_no')
        customer_or_store_id = request.data.get('customer_or_store_id')
        credit_amount = request.data.get('credit_amount')
        description = request.data.get('description')

        if not cm_no:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'cm_no id required'
                            },status=status.HTTP_400_BAD_REQUEST)
        else:
            creditmemo_obj = CreditMemo.objects.filter(cm_no=cm_no).first() 
            if not creditmemo_obj:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid CM NO'
                    },)

            if creditmemo_obj.credit_applied_status in ['FULLY','PARTIALLY']:
                
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Can not edit this credit memos.'
                    },)

        if customer_or_store_id:
            customer_obj = Customer.objects.filter(id=customer_or_store_id).first()
            if not customer_obj:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid CustomerID'
                    },)
            if creditmemo_obj.order:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Can not edit customer_or_store in automatic credit memos.'
                    },)

            creditmemo_obj.customer=customer_obj

        if credit_amount:
            if creditmemo_obj.order:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Can not edit credit_amount in automatic credit memos.'
                    },)
            creditmemo_obj.credit_amount = credit_amount
            creditmemo_obj.updated_credit_amount = credit_amount


        if description:
            creditmemo_obj.description=description

        creditmemo_obj.save()
        # Generate PDF for credit_memo 
        pdfdata_res = get_creditmemo_pdfdata(creditmemo_obj=creditmemo_obj) #Fetch PDF-Data
        if pdfdata_res["status_code"] != True:
            return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
        else:
            pdf_data = pdfdata_res.get("pdf_data")
            num_of_row_data  = pdfdata_res.get("num_of_row_data")
        
        # Creating PDF 
        filename = 'file' + creditmemo_obj.cm_no + '.pdf' 
        createpdf_res = create_pdf(request = request,
                            pdf_type = "credit_memo_pdf",
                            pdf_data = pdf_data,
                            filename = filename,
                            order_obj = creditmemo_obj,
                            num_of_row_data = num_of_row_data,
                        )
        if createpdf_res["status_code"] != True:
            return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {}
            data['pdf_url'] = createpdf_res.get("pdf_url")

        response_data = {
            'status_code':status.HTTP_200_OK,
            'message':"Successfull"
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(methods=['POST',],detail=False)
    def details(self,request,*args,**kwargs):
        cm_id = request.data.get('cm_id')
        
        if not cm_id:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'cm_id required'
                            },status=status.HTTP_400_BAD_REQUEST)
        else:
            creditmemo_obj = CreditMemo.objects.filter(id=cm_id).first() 
            if not creditmemo_obj:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid CM NO'
                    },)

        serializer = CreditMemoSerializers(creditmemo_obj,context={'request':request})
        serializer_data = serializer.data

        response_data = {
            'status_code':status.HTTP_200_OK,
            'message':"Successfull",
            'data':serializer_data
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(methods=['POST',],detail=False)
    def show_list(self,request):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit

        # sorting data
        sort_field = request.data.get("sort_field", "id")
        sort_type = request.data.get("sort_type", "desc")
        order_by = sort_field

        if sort_field == "id":
            order_by = "id"
        elif sort_field == "cm_no":
            order_by = "cm_no"
        elif sort_field == "payment_amount":
            order_by = "payment_amount"
        elif sort_field == "credit_amount":
            order_by = "credit_amount"
        elif sort_field == "invoice_no":
            order_by = "order__invoice_no"
        elif sort_field == "store_name":
            order_by = "customer__store_name"

        if sort_type == "desc":
            order_by = "-" + order_by
        if sort_type == "asc":
            order_by = order_by

        # Search
        search_value = request.data.get('search_params')
    
        # Filters
        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')
        store_name_id = request.data.get('store_name_id')
        cm_no = request.data.get('cm_no')
        invoice_no = request.data.get('invoice_no')


        all_data = CreditMemo.objects.all().order_by(order_by)
        
        ## -- filters 
        if From_Date not in ["null","Null",None] and To_Date not in ["null","Null",None] :
            if From_Date and To_Date:
                try:
                    from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                    to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                    d = timedelta(days=1)
                    to_date_obj = to_date_obj + d #adding 1 day
                    all_data = all_data.filter(created_at__range=(from_date_obj,to_date_obj))
                except Exception as e:
                    return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                    'message':'Invalid date format date Format should year-month-date'
                                    },status=status.HTTP_400_BAD_REQUEST)

        
        if store_name_id:
            all_data = all_data.filter(customer__id = store_name_id)
        if cm_no:
            all_data = all_data.filter(cm_no = cm_no)
        if invoice_no:
            all_data = all_data.filter(order__invoice_no = invoice_no)
        
        ## -- searching  
        if search_value:
            all_data = all_data.filter( Q(created_at__icontains=search_value)|
                                        Q(order__invoice_no__icontains=search_value)|
                                        Q(customer__store_name__icontains=search_value)|
                                        Q(payment_amount__icontains=search_value) |
                                        Q(credit_amount__icontains=search_value) |
                                        Q(updated_credit_amount__icontains=search_value) |
                                        Q(description__icontains=search_value) |
                                        Q(cm_no__icontains=search_value)
                                        )
        
        if order_by:
            all_data = all_data.order_by(order_by)
        if sort_field == "cm_no":
            reverse_rows = True if sort_type == 'desc' else False
            all_data = sorted(all_data, key=lambda CreditMemo: CreditMemo.cm_no.replace(" ", ""),reverse=reverse_rows)

        total_record = len(all_data)
        list_with_page_limit = all_data[start:end]
        filter_record=len(list_with_page_limit)
        serializer = CreditMemoSerializers(list_with_page_limit , many=True)
        serializer_data = serializer.data

        return Response({'status_code':status.HTTP_200_OK,
                        'message':'successfull',
                        'data':serializer_data,
                        'filter_record':filter_record,
                        'total_record':total_record
                        },status=status.HTTP_200_OK)

    @action(methods=['POST',],detail=False)
    def customer_or_store_credit(self,request):
        customer_id = request.data.get('customer_or_store_id')
        if not customer_id:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'customer_or_store_id required'
                            },)

        customer_obj = Customer.objects.filter(id=customer_id).first()
        if not customer_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid customer or store!'
                            },status=status.HTTP_400_BAD_REQUEST)

        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit

        # sorting data
        sort_field = request.data.get("sort_field", "id")
        sort_type = request.data.get("sort_type", "desc")
        order_by = sort_field

        if sort_field == "id":
            order_by = "id"
        elif sort_field == "cm_no":
            order_by = "cm_no"
        elif sort_field == "payment_amount":
            order_by = "payment_amount"
        elif sort_field == "credit_amount":
            order_by = "credit_amount"
        elif sort_field == "invoice_no":
            order_by = "order__invoice_no"
        elif sort_field == "store_name":
            order_by = "customer__store_name"

        if sort_type == "desc":
            order_by = "-" + order_by
        if sort_type == "asc":
            order_by = order_by

        # Search
        search_value = request.data.get('search_params')
    
        # Filters
        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')
        store_name_id = request.data.get('store_name_id')
        cm_no = request.data.get('cm_no')
        invoice_no = request.data.get('invoice_no')


        all_data = CreditMemo.objects.filter(customer=customer_obj).order_by(order_by)
        
        ## -- filters 
        if From_Date not in ["null","Null",None] and To_Date not in ["null","Null",None] :
            if From_Date and To_Date:
                try:
                    from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                    to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                    d = timedelta(days=1)
                    to_date_obj = to_date_obj + d #adding 1 day
                    all_data = all_data.filter(created_at__range=(from_date_obj,to_date_obj))
                except Exception as e:
                    return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                    'message':'Invalid date format date Format should year-month-date'
                                    },status=status.HTTP_400_BAD_REQUEST)

        
        if store_name_id:
            all_data = all_data.filter(customer__id = store_name_id)
        if cm_no:
            all_data = all_data.filter(cm_no = cm_no)
        if invoice_no:
            all_data = all_data.filter(order__invoice_no = invoice_no)
        
        ## -- searching  
        if search_value:
            all_data = all_data.filter( Q(created_at__icontains=search_value)|
                                        Q(order__invoice_no__icontains=search_value)|
                                        Q(customer__store_name=search_value)|
                                        Q(payment_amount=search_value) |
                                        Q(cm_no=search_value)
                                        )
        
        if order_by:
            all_data = all_data.order_by(order_by)

        total_record = len(all_data)
        list_with_page_limit = all_data[start:end]
        filter_record=len(list_with_page_limit)
        serializer = CreditMemoSerializers(list_with_page_limit , many=True,context={'request':request})
        serializer_data = serializer.data

        return Response({'status_code':status.HTTP_200_OK,
                        'message':'successfull',
                        'data':serializer_data,
                        'filter_record':filter_record,
                        'total_record':total_record
                        },status=status.HTTP_200_OK)

    @action(methods=['POST',],detail=False)
    def delete(self,request,*args,**kwargs):
        creditmemo_id = request.data.get('creditmemo_id')
        
        if not creditmemo_id:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'creditmemo_id required'
                            },status=status.HTTP_400_BAD_REQUEST)

        data_obj = CreditMemo.objects.filter(id=creditmemo_id).first()
        if not data_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid creditmemo_id'
                },)

        data_obj.delete()
        
        response_data = {
            'status_code':status.HTTP_200_OK,
            'message':"Successfull"
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(methods=['POST',],detail=False)
    def apply_credit_to_order(self,request,*args,**kwargs):
        credit_applied_order_id = request.data.get('credit_applied_order_id')
        credit_memo_list = json.loads(request.POST.get('credit_memo_list'))
        
        if not credit_applied_order_id:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'credit_applied_order_id required'
                            },status=status.HTTP_400_BAD_REQUEST)

        order_obj = Order.objects.filter(id=credit_applied_order_id).first()
        if not order_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid order'
                },)


        for row in credit_memo_list:

            credit_memo_id = row["cm_id"]
            credit_applied = row["credit_applied"]
            credit_memo_obj = CreditMemo.objects.filter(id=credit_memo_id).last()
            credit_memo_obj.updated_credit_amount = credit_memo_obj.updated_credit_amount - credit_applied
            order_obj.applied_credit += credit_applied
            order_obj.save()

            from .utils import update_order_totals
            update_order_totals(order_obj=order_obj)

            CreditApplied.objects.create(credit_memo=credit_memo_obj,credit_applied_order=order_obj,applied_amount=credit_applied)
            if credit_memo_obj.credit_amount == credit_applied:
                credit_memo_obj.credit_applied_status = "FULLY"
                
            elif credit_memo_obj.credit_amount > credit_applied:
                credit_memo_obj.credit_applied_status = "PARTIALLY"
            else:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Amount can not be above the credit amount.'
                            },status=status.HTTP_400_BAD_REQUEST)

            credit_memo_obj.save()
        response_data = {
            'status_code':status.HTTP_200_OK,
            'message':"Successfull"
        }
        return Response(response_data, status=status.HTTP_200_OK)