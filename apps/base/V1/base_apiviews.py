from datetime import date
from datetime import timedelta
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.decorators import permission_classes,authentication_classes,action
from pyzbar.pyzbar import decode
from PIL import Image
from django.db.models import Q
import requests
import json
from django.conf import settings
from dateutil.relativedelta import *
from django.core.mail import send_mail
import operator
import pytz
import math
import pdfkit
from pyvirtualdisplay import Display
import email
from django.core.files import File
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.template.loader import get_template
from django.http import HttpResponse
import pathlib
from urllib.request import pathname2url
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from io import BytesIO
from xhtml2pdf import pisa
from django.core.files.base import ContentFile
from django.db.models.functions import Lower

from apps.base.img_src import krishiv_logo
from apps.base.img_src import ramdev_logo
from apps.base.models import *
from apps.base.authentication import *
from .utils import create_pdf, send_notification, send_pdf_mail, get_order_pdfdata, update_profit
from .serializers import *

class Add_Pack(viewsets.ViewSet):

    def create(self,request,*args,**kwargs):
        data = request.data.get("size")
        if not data:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Content is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        packsize = PackSizes.objects.create(size=data)
        serializer = PackSizesSerializers(packsize)
        
        print('serializer: ', serializer.data)

        return Response({
                'status_code':status.HTTP_200_OK,
                'message':'successfull',
                'data':serializer.data
                },status=status.HTTP_200_OK)

    @action(detail=False,methods=['POST'])
    def listview(self,request,*args,**kwargs):
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit

        product_id = request.data.get('product_id')
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
        
        if product_id:
            product_obj = Product.objects.get(id=product_id)
            current_pack_size = product_obj.pack_size.first()
            pack_size = PackSizes.objects.exclude(size=current_pack_size.packsize.size)
            total_record = len(pack_size)
            pack_size = pack_size[start:end]
            filter_record = len(pack_size)
            serilizer = PackSizesSerializers(pack_size,many=True)
            new_data = serilizer.data.copy()
            new_data.append({
                'id':current_pack_size.id,
                'size': current_pack_size.packsize.size,
                'deleted' : current_pack_size.packsize.deleted
            })

            response = {
                    'status_code':status.HTTP_200_OK,
                    'data':new_data,
                    'total_record':total_record,
                    'filter_record':filter_record,
                    }
            return Response(response, status=status.HTTP_200_OK)


        if pack_size:
            serilizer = PackSizesSerializers(pack_size,many=True)
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

    @action(detail=True,methods=['POST'])
    def edit(self,request,pk=None,*args,**kwargs):

        pack = PackSizes.objects.filter(id=pk).first()
        size = request.data.get('size')

        if not size:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Size is required',
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


        if not pack:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Invalid PackID',
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        pack.size = size
        pack.save()
        serilizer = PackSizesSerializers(pack)
        response = {
                'status_code':status.HTTP_200_OK,
                'data':serilizer.data,
            }

        return Response(response, status=status.HTTP_200_OK)

    def destroy(self,request,pk=None,*args,**kwargs):
        pack = PackSizes.objects.filter(id=pk).first()
        if not pack:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Invalid PackID',
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        pack.delete()

        response = {
                'status_code':status.HTTP_200_OK,
                'data':'Sucessfully Deleted',
            }

        return Response(response, status=status.HTTP_200_OK)


class About_Us(viewsets.ViewSet):

    def create(self,request,*args,**kwargs):
        data = request.data.get("content")
        if not data:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Content is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        about_us_obj,created = Miscellaneous.objects.get_or_create(name='About_us')
        about_us_obj.content = data
        about_us_obj.save()
        return Response({
                'status_code':status.HTTP_200_OK,
                'message':'successfull',
                'data':'Ok',
                },status=status.HTTP_200_OK)

    def list(self,request,*args,**kwargs):
        
        about = Miscellaneous.objects.filter(name='About_us').first()
        if about:
            response = {
                    'status_code':status.HTTP_200_OK,
                    'data':about.content,
                    }
            return Response(response, status=status.HTTP_200_OK)

        response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'No data Found',
                }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

class Contact_us(viewsets.ViewSet):

    def create(self,request,*args,**kwargs):
        data = request.data.get("content")
        if not data:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Content is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        about_us_obj,created = Miscellaneous.objects.get_or_create(name='Contact_us')
        about_us_obj.content = data
        about_us_obj.save()
        return Response({
                'status_code':status.HTTP_200_OK,
                'message':'successfull',
                'data':'Ok',
                },status=status.HTTP_200_OK)

    def list(self,request,*args,**kwargs):
        
        about = Miscellaneous.objects.filter(name='Contact_us').first()
        if about:
            response = {
                    'status_code':status.HTTP_200_OK,
                    'data':about.content,
                    }
            return Response(response, status=status.HTTP_200_OK)

        response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'No data Found',
                }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

class Privacy(viewsets.ViewSet):

    def create(self,request,*args,**kwargs):
        data = request.data.get("content")
        if not data:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Content is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        about_us_obj,created = Miscellaneous.objects.get_or_create(name='Privacy')
        about_us_obj.content = data
        about_us_obj.save()
        return Response({
                'status_code':status.HTTP_200_OK,
                'message':'successfull',
                'data':'Ok',
                },status=status.HTTP_200_OK)

    def list(self,request,*args,**kwargs):
        
        about = Miscellaneous.objects.filter(name='Privacy').first()
        if about:
            response = {
                    'status_code':status.HTTP_200_OK,
                    'data':about.content,
                    }
            return Response(response, status=status.HTTP_200_OK)

        response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'No data Found',
                }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

class Terms(viewsets.ViewSet):

    def create(self,request,*args,**kwargs):
        data = request.data.get("content")
        if not data:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Content is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        about_us_obj,created = Miscellaneous.objects.get_or_create(name='Terms')
        about_us_obj.content = data
        about_us_obj.save()
        return Response({
                'status_code':status.HTTP_200_OK,
                'message':'successfull',
                'data':'Ok',
                },status=status.HTTP_200_OK)

    def list(self,request,*args,**kwargs):
        
        about = Miscellaneous.objects.filter(name='Terms').first()
        if about:
            response = {
                    'status_code':status.HTTP_200_OK,
                    'data':about.content,
                    }
            return Response(response, status=status.HTTP_200_OK)

        response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'No data Found',
                }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

# @authentication_classes([])
class ProductViewset(viewsets.ViewSet):
    authentication_classes = (MyCustomAuth,)
    def create(self,request,*args,**kwargs):
        name = request.data.get('name')
        vendor = request.data.get('vendor')
        description = request.data.get('description')
        available_quantity = request.data.get('available_quantity')
        low_stock_qauntity = request.data.get('low_stock_qauntity')
        packsize_id = request.data.get('packsize_id')
        
        in_stock = request.data.get('in_stock')
        sale_price = request.data.get('sale_price')
        purchase_cost = request.data.get('purchase_cost')
        weight = request.data.get('weight')
        purchase_info = request.data.get('purchase_info')
        barcode_image = request.data.get('barcode_image')
        location = request.data.get('location')
        updated_on = request.data.get('updated_on')
        pack_size = request.data.get('pack_size')
        pack_size = PackSizes.objects.all().first()
        pack_size_obj = ProductPackSizes.objects.create(packsize=pack_size,price=sale_price)
        pack_size = pack_size_obj.id
        new_data=request.data.copy()
        new_data['pack_size']=pack_size
        new_data['lifetime_quantity']=float(available_quantity)
        new_data['vendor'] = Vendor.objects.filter(name='All').first().id
        new_data['is_active'] = True

        serializer = ProductSerializers(data=new_data)

        if serializer.is_valid():
            product_obj = serializer.save()

            # Fetching Barcode String From Barcode and Saving it for Further Use
            if barcode_image:
                try:
                    barcode_str = decode(Image.open(product_obj.barcode_image.path))[0][0]
                    product_obj.barcode_string = barcode_str.decode("utf-8")
                    product_obj.save()
                except:
                    product_obj.delete()
                    response = {
                    'status_code':status.HTTP_400_BAD_REQUEST,
                    'message':"Coundn't decode barcode from image,Please try again",
                    }
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'status_code':status.HTTP_200_OK,
                'message':'successfull',
                'data':serializer.data,
                },status=status.HTTP_200_OK)
        else:
            errors = []
            
            for key,value in serializer.errors.items():
                print(key,">>",value[0])
                errors.append(
                        key +" : "+ value[0])

            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':errors,
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
    def partial_update(self,request,pk=None):
        if not pk:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Id is required',
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        barcode_image = request.data.get('barcode_image')
        product =  Product.objects.filter(id=pk).first()
        if not product:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Invalid Product ID',
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        # old_image = product.barcode_image
        product_pack_size = product.pack_size.first()
        product_pack_size.price = request.data.get('sale_price')
        product_pack_size.save()
        product.pack_size.all().update(price=float(request.data.get('sale_price')))
        new_pack_size = request.data.get('pack_size',0)
        new_data = request.data.copy()
        new_data['pack_size'] = product_pack_size.id
        new_data['vendor'] = Vendor.objects.filter(name='All').first().id
        serializer = ProductSerializers(product,data=new_data,partial=True)

        if serializer.is_valid():
            product_obj = serializer.save()

            return Response({
                'status_code':status.HTTP_200_OK,
                'message':'successfull',
                'data':serializer.data,
                },status=status.HTTP_200_OK)

        else:
            errors = []
            for key,value in serializer.errors.items():
                errors.append(
                        key +" : "+ value[0])

            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':errors,
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self,request,pk=None,*args,**kwargs):
        pack = Product.objects.filter(id=pk).first()
        if not pack:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Invalid ProductID',
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        pack.delete()

        response = {
                'status_code':status.HTTP_200_OK,
                'data':'Sucessfully Deleted',
            }

        return Response(response, status=status.HTTP_200_OK)

class UserListView(APIView):
    authentication_classes = (MyCustomAuth,)
    
    def post(self, request,format=None):
        try:
            page = int(request.data.get('page',1))
            limit = int(request.data.get('limit',10))
            start = (page - 1) * limit
            end = start + limit
            
            search_param = request.data.get('search_param')
            
            order_by = "id"

            user_qs = User.objects.all().order_by(order_by)
            total_record = len(user_qs)

            # searching data
            if search_param:
                filter_data_qs = user_qs.filter(Q(full_name__icontains = search_param) |
                                                    Q(phone_number__icontains = search_param) |
                                                    Q(email__icontains = search_param))
                
                filter_record = len(filter_data_qs)
                list_with_pagelimit = filter_data_qs[start:end]
                serializer = UserSerializers(list_with_pagelimit, many=True, context={'request':request})
                serializer_data = serializer.data
                
                
            else:
                list_with_pagelimit = user_qs[start:end]
                filter_record = len(list_with_pagelimit)
                serializer = UserSerializers(list_with_pagelimit, many=True, context={'request':request})
                serializer_data = serializer.data

        except Exception as e:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Somthing went wrong',
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if len(serializer_data) == 0:
            response = {'status_code' : status.HTTP_404_NOT_FOUND,'message' : 'NO DATA FOUND.'}
            return Response(response, status.HTTP_404_NOT_FOUND)  
        else:
            msg = 'Data fetch succesfully'   

        response = {
            'status_code':status.HTTP_200_OK,
            'data': serializer_data,
            'total_record':total_record,
            'filter_record':filter_record,
            'message':msg
        }
        return Response(response, status=status.HTTP_200_OK)

# @authentication_classes([])
class UserGetView(APIView):
    authentication_classes = (MyCustomAuth,)
    def get(self, request, id, format=None):
        try:
            user_obj = User.objects.get(id=id)
        except:
            response = {
                'status_code' : status.HTTP_404_NOT_FOUND,
                'message' : 'User not found!'
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializers(user_obj,context={'request':request})
        data = serializer.data
        
        if user_obj.address:
            add = user_obj.address
            data.update({
                'address' : add.address,
                'city' : add.city,
                'state' : add.state,
                'country' : add.country,
                'zipcode' : add.zipcode

            })

        else:
            data.update({
                'address' : None,
                'city' : None,
                'state' : None,
                'country' : None,
                'zipcode' : None,

            })

        response = {
            'status_code' : status.HTTP_200_OK,
            'message': 'Data fetch succesfully',
            'data' : data,
        }
        
        return Response(response, status=status.HTTP_200_OK)

import traceback

# @authentication_classes([])
class CustomerListView(APIView):
    authentication_classes = (MyCustomAuth,)
    def post(self, request,format=None):
        try:
            page = int(request.data.get('page',1))
            limit = int(request.data.get('limit',10))
            start = (page - 1) * limit
            end = start + limit
            
            search_param = request.data.get('search_param')
            
            full_name = request.data.get('full_name')
            phone = request.data.get('phone')
            email = request.data.get('email')
            min_threshold = request.data.get('min_threshold')
            sales_tax_id = request.data.get('sales_tax_id')
            no_of_orders = request.data.get('order')
            store_name = request.data.get('store_name')
            order_by_obj = []
            if full_name:
                order_by_obj.append(full_name)
            if phone:
                order_by_obj.append(phone)
            if email:
                order_by_obj.append(email)
            if min_threshold:
                order_by_obj.append(min_threshold)
            if sales_tax_id:
                order_by_obj.append(sales_tax_id)
            # if no_of_orders:
            #     order_by_obj.append(no_of_orders)
            if store_name:
                order_by_obj.append(store_name)

            if request.user.user_type == 'SALESPERSON':
                customer_qs = Customer.objects.filter(sales_person=request.user)
            else:
                customer_qs = Customer.objects.all()

            if order_by_obj:
                customer_qs = customer_qs.order_by(*order_by_obj)
                total_record = len(customer_qs)
                
            else:
                order_by = "id"

                customer_qs = customer_qs.order_by(order_by)
                total_record = len(customer_qs)

            # searching data
            if search_param:
                
                filter_data_qs = customer_qs.filter(Q(full_name__icontains = search_param) |
                                                    Q(store_name__icontains = search_param) |
                                                    Q(sales_tax_id__icontains = search_param)|
                                                    Q(phone__icontains=search_param)|
                                                    Q(email__icontains = search_param)|
                                                    Q(min_threshold__icontains=search_param))
                
                filter_record = len(filter_data_qs)
                list_with_pagelimit = filter_data_qs[start:end]
                serializer = CustomerSerializers(list_with_pagelimit, many=True, context={'request':request})
                serializer_data = serializer.data
                
                
            else:
                list_with_pagelimit = customer_qs[start:end]
                filter_record = len(list_with_pagelimit)
                serializer = CustomerSerializers(list_with_pagelimit, many=True, context={'request':request})
                serializer_data = serializer.data

            # Order_by On serilizers Field       
            if request.data.get("total_order_amount"):
                
                if request.data.get("total_order_amount")[0] == '-':
                    flag = True
                else:
                    flag = False
                try:
                    serializer_data = sorted(serializer_data, key=lambda k: k['total_order_amount'], reverse=flag)
                    response = serializer_data

                except:
                    serializer_data = sorted(serializer_data, key=lambda k: k['total_order_amount'], reverse=flag)
                    response = serializer_data 
            
        except Exception as e:
            print('e: ', e)
            print(traceback.format_exc())
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Somthing went wrong',
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if len(serializer_data) == 0:
            response = {
                'status_code':status.HTTP_200_OK,
                'data': [],
                'total_record':0,
                'filter_record':0,
                'message':'No data found'
            }
            return Response(response, status=status.HTTP_200_OK)

        response = {
            'status_code':status.HTTP_200_OK,
            'data': serializer_data,
            'total_record':total_record,
            'filter_record':filter_record,
            'message':'Suceessfull'
        }
        
        return Response(response, status=status.HTTP_200_OK)

# @authentication_classes([])
class CustomerGetView(APIView):
    authentication_classes = (MyCustomAuth,)
    def get(self, request, id, format=None):
        try:
            customer_obj = Customer.objects.get(id=id)
        except:
            response = {
                'status_code' : status.HTTP_404_NOT_FOUND,
                'message' : 'Customer not found!'
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # if customer_obj.sales_tax_id:
        #     sales_tax_id = request.build_absolute_uri(customer_obj.sales_tax_id.url)
        # else:
        #     sales_tax_id = None

        serializer = CustomerSerializers(customer_obj)

        response = {
            'status_code' : status.HTTP_200_OK,
            'message': 'Data fetch succesfully',
            'data' : serializer.data}
        
        return Response(response, status=status.HTTP_200_OK)


# @authentication_classes([])
class PackSizesListView(APIView):
    authentication_classes = (MyCustomAuth,)
    def post(self, request,format=None):
        try:
            page = int(request.data.get('page',1))
            limit = int(request.data.get('limit',10))
            start = (page - 1) * limit
            end = start + limit
            
            search_param = request.data.get('search_param')
            
            order_by = "id"

            packSize_qs = PackSizes.objects.all().order_by(order_by)
            total_record = len(packSize_qs)

            # searching data
            if search_param:
                filter_data_qs = packSize_qs.filter(Q(size__icontains = search_param) |
                                                    Q(deleted__icontains = search_param))
                
                filter_record = len(filter_data_qs)
                list_with_pagelimit = filter_data_qs[start:end]
                serializer = PackSizesSerializers(list_with_pagelimit, many=True, context={'request':request})
                serializer_data = serializer.data
                
                
            else:
                list_with_pagelimit = packSize_qs[start:end]
                filter_record = len(list_with_pagelimit)
                serializer = PackSizesSerializers(list_with_pagelimit, many=True, context={'request':request})
                serializer_data = serializer.data
        
        except Exception as e:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Somthing went wrong',
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if len(serializer_data) == 0:
            response = {'status_code' : status.HTTP_404_NOT_FOUND,'message' : 'NO DATA FOUND.'}
            return Response(response, status.HTTP_404_NOT_FOUND)  
        else:
            msg = 'Data fetch succesfully'   

        response = {
            'status_code':status.HTTP_200_OK,
            'data': serializer_data,
            'total_record':total_record,
            'filter_record':filter_record,
            'message':msg
        }
        return Response(response, status=status.HTTP_200_OK)

# @authentication_classes([])
class PackSizesGetView(APIView):
    authentication_classes = (MyCustomAuth,)
    def get(self, request, id, format=None):
        try:
            packSizes_obj = PackSizes.objects.get(id=id)
        except:
            response = {
                'status_code' : status.HTTP_404_NOT_FOUND,
                'message' : 'PackSizes not found!'
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        serializer = PackSizesSerializers(packSizes_obj)

        response = {
            'status_code' : status.HTTP_200_OK,
            'message': 'Data fetch succesfully',
            'data' : serializer.data}
        
        return Response(response, status=status.HTTP_200_OK)


# @authentication_classes([])
class CategoriesListView(APIView):
    authentication_classes = (MyCustomAuth,)
    def post(self, request,format=None):
        try:
            page = int(request.data.get('page',1))
            limit = int(request.data.get('limit',10))
            start = (page - 1) * limit
            end = start + limit
            
            search_param = request.data.get('search_param')
            
            order_by = "name"

            order_by_obj=[]
            name = request.data.get('name')
            description = request.data.get('description')

            if name:
                order_by_obj.append(name)
            
            if description:
                order_by_obj.append(description)

            if order_by_obj:
                categories_qs = Categories.objects.all().order_by(*order_by_obj)
            else:    
                categories_qs = Categories.objects.all().order_by(order_by)
            total_record = len(categories_qs)

            # searching data
            if search_param:
                filter_data_qs = categories_qs.filter(Q(name__icontains = search_param) |
                                                    Q(description__icontains = search_param))
                
                filter_record = len(filter_data_qs)
                list_with_pagelimit = filter_data_qs[start:end]
                serializer = CategoriesSerializers(list_with_pagelimit, many=True, context={'request':request})
                serializer_data = serializer.data
                
                
            else:
                list_with_pagelimit = categories_qs[start:end]
                filter_record = len(list_with_pagelimit)
                serializer = CategoriesSerializers(list_with_pagelimit, many=True, context={'request':request})
                serializer_data = serializer.data
            
        except Exception as e:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Somthing went wrong',
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if len(serializer_data) == 0:
            response = {
            'status_code':status.HTTP_200_OK,
            'data': [],
            'total_record':0,
            'filter_record':0,
            'message':"No Data Found"
            }
            return Response(response, status=status.HTTP_200_OK)

        else:
            msg = 'Data fetch succesfully'   

        response = {
            'status_code':status.HTTP_200_OK,
            'data': serializer_data,
            'total_record':total_record,
            'filter_record':filter_record,
            'message':msg
        }
        return Response(response, status=status.HTTP_200_OK)

class CategoriesListViewNoPagination(APIView):
    authentication_classes = (MyCustomAuth,)
    def get(self, request,format=None):
        try:
            categories_qs = Categories.objects.all().order_by('name')
            serializer = CategoriesListSerializers(categories_qs, many=True, context={'request':request})
            serializer_data = serializer.data
            
        except Exception as e:
            print('e: ', e)
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Somthing went wrong',
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if len(serializer_data) == 0:
            response = {'status_code' : status.HTTP_404_NOT_FOUND,'message' : 'NO DATA FOUND.'}
            return Response(response, status.HTTP_404_NOT_FOUND)  
        
        else:
            msg = 'Data fetch succesfully'   

        response = {
            'status_code':status.HTTP_200_OK,
            'data': serializer_data,
            'message':msg
        }
        return Response(response, status=status.HTTP_200_OK)

# @authentication_classes([])
class CategoriesGetView(APIView):
    authentication_classes = (MyCustomAuth,)
    def get(self, request, id, format=None):
        try:
            categories_obj = Categories.objects.get(id=id)
        except:
            response = {
                'status_code' : status.HTTP_404_NOT_FOUND,
                'message' : 'Category not found!'
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        serializer = CategoriesSerializers(categories_obj)

        response = {
            'status_code' : status.HTTP_200_OK,
            'message': 'Data fetch succesfully',
            'data' : serializer.data}
        
        return Response(response, status=status.HTTP_200_OK)        


# @authentication_classes([])
class ProductListView(APIView):
    authentication_classes = (MyCustomAuth,)
    def post(self, request,format=None):
        try:
            page = int(request.data.get('page',1))
            limit = int(request.data.get('limit',10))
            start = (page - 1) * limit
            end = start + limit
            
            search_param = request.data.get('search_param')
            
            name = request.data.get('name')
            filter_by = request.data.get('filter')
            category = request.data.get('category')
            description = request.data.get('description')
            sale_price = request.data.get('sale_price')
            purchase_cost = request.data.get('purchase_cost')
            available_quantity = request.data.get('available_quantity')
            category_id_filter = request.data.get('category_id_filter')
            vendor_id_filter = request.data.get('vendor_id_filter')
            product_name_filter = request.data.get('product_name_filter')
            weight = request.data.get('weight')
            item_no = request.data.get('item_no')
            mark_up = request.data.get('mark_up')
            margin = request.data.get('margin')

            order_by_obj = []
            # order_by_obj.append('name')
            if name:
                order_by_obj.append(name)
            if category:
                order_by_obj.append(category)
            if description:
                order_by_obj.append(description)
            if sale_price:
                order_by_obj.append(sale_price)
            if purchase_cost:
                order_by_obj.append(purchase_cost)
            if available_quantity:
                order_by_obj.append(available_quantity)
            if weight:
                order_by_obj.append(weight)
            if item_no:
                order_by_obj.append(item_no)
            if mark_up:
                order_by_obj.append(mark_up)
            if margin:
                order_by_obj.append(margin)
            
            if order_by_obj:
                print("order_by_obj",order_by_obj)
                product_qs = Product.objects.all().order_by(*order_by_obj)
                total_record = len(product_qs)
                
            else:            
                order_by_obj = ["name"]
                print("order_by_obj  gg",order_by_obj)
                product_qs = Product.objects.all().order_by(*order_by_obj)
                total_record = len(product_qs)

            if filter_by:
                if filter_by == 'out_of_stock':
                    product_qs=product_qs.filter(available_quantity=0,is_active=True)
                if filter_by == 'low_stock':
                    product_qs=product_qs.filter(low_stock=True,is_active=True)

            if product_name_filter:
                if type(product_name_filter) != list:
                    response = {
                        'status_code':status.HTTP_400_BAD_REQUEST,
                        'message':'Product_name_filter must be array.',
                        }
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

                product_qs=product_qs.filter(id__in = product_name_filter)

            if category_id_filter:
                product_qs=product_qs.filter(category_id = category_id_filter)
            
            if vendor_id_filter:
                product_qs=product_qs.filter(vendor_id = vendor_id_filter)

            if not product_qs:
                response = {
                    'status_code':status.HTTP_200_OK,
                    'data': [],
                    'total_record':0,
                    'filter_record':0,
                    'message':"No Data Found"
                }
                return Response(response, status=status.HTTP_200_OK)
        
            # searching data
            if search_param:
                filter_data_qs = product_qs.filter(Q(name__icontains = search_param) |
                                                    Q(description__icontains = search_param) |
                                                    Q(available_quantity__icontains = search_param) |
                                                    Q(low_stock_qauntity__icontains = search_param) |
                                                    Q(in_stock__icontains = search_param)|
                                                    Q(sale_price__icontains=search_param)|
                                                    Q(category__name__icontains=search_param)|
                                                    Q(item_no__icontains=search_param)|
                                                    Q(barcode_string__icontains=search_param))


                filter_data_qs=filter_data_qs.order_by(*order_by_obj)
                filter_record = len(filter_data_qs)
                list_with_pagelimit = filter_data_qs[start:end]
                serializer = ProductSerializers(list_with_pagelimit, many=True, context={'request':request})
                serializer_data = serializer.data
                
                
            else:
                filter_record = len(product_qs)
                list_with_pagelimit = product_qs[start:end]
                serializer = ProductSerializers(list_with_pagelimit, many=True, context={'request':request})
                serializer_data = serializer.data
        
        except Exception as e:
            print('e: ', e)
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Somthing went wrong',
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if len(serializer_data) == 0:
            response = {
                    'status_code':status.HTTP_200_OK,
                    'data': [],
                    'total_record':0,
                    'filter_record':0,
                    'message':"No Data Found"
                }
            return Response(response, status=status.HTTP_200_OK)
        else:
            msg = 'Data fetch succesfully'   

        response = {
            'status_code':status.HTTP_200_OK,
            'data': serializer_data,
            'total_record':total_record,
            'filter_record':filter_record,
            'message':msg
        }
        return Response(response, status=status.HTTP_200_OK)

# @authentication_classes([])
class ProductGetView(APIView):
    authentication_classes = (MyCustomAuth,)
    def get(self, request, id, format=None):
        try:
            product_obj = Product.objects.get(id=id)
        except:
            response = {
                'status_code' : status.HTTP_404_NOT_FOUND,
                'message' : 'Product not found!'
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializers(product_obj)

        response = {
            'status_code' : status.HTTP_200_OK,
            'message': 'Data fetch succesfully',
            'data' : serializer.data
            }
        
        return Response(response, status=status.HTTP_200_OK)


# @authentication_classes([])
class OrderListView(APIView):
    authentication_classes = (MyCustomAuth,)
    def post(self, request,format=None):
        # try:
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        
        search_param = request.data.get('search_param')
        
        created_at = request.data.get('created_at')
        invoice_no = request.data.get('invoice_no')
        due_date = request.data.get('due_date')
        amount = request.data.get('amount')
        po_num = request.data.get('po_num')

        # pass key as "status" over here 
        status_verify = request.data.get('status_verify')
        verfication_status = request.data.get('verfication_status')
        amount_recieved = request.data.get('amount_recieved')
        remaining_amount = request.data.get('remaining_amount')
        payment_status = request.data.get('payment_status')
        ordered_by = request.data.get('ordered_by')
        customer__store_name = request.data.get('customer__store_name')
        status1 = request.data.get('status')
        order_profit = request.data.get('order_profit')

        filter_from_date = request.data.get('filter_from_date')
        filter_to_date = request.data.get('filter_to_date')
        filter_due_date_start = request.data.get('filter_due_date_start')
        filter_due_date_end = request.data.get('filter_due_date_end')
        filter_payment_status = request.data.get('filter_payment_status')
        filter_customer_name = request.data.get('filter_customer_name')
        filter_store_name = request.data.get('filter_store_name')
        filter_order_status = request.data.get('filter_order_status')
        filter_verification_status = request.data.get('filter_verification_status')

        order_by_obj = []
        if created_at:
            order_by_obj.append(created_at)
        if invoice_no:
            order_by_obj.append(invoice_no)
        if due_date:
            order_by_obj.append(due_date)
        if amount:
            order_by_obj.append(amount)
        if status_verify:
            order_by_obj.append(status_verify)
        if verfication_status:
            order_by_obj.append(verfication_status)
        if amount_recieved:
            order_by_obj.append(amount_recieved)
        if remaining_amount:
            order_by_obj.append(remaining_amount)
        if payment_status:
            order_by_obj.append(payment_status)
        if ordered_by:
            order_by_obj.append(ordered_by)
        if customer__store_name:
            order_by_obj.append(customer__store_name)
        if status1:
            order_by_obj.append(status1)
        if order_profit:
            order_by_obj.append(order_profit)
        if po_num:
            order_by_obj.append(po_num)

        if order_by_obj:
            order_qs = Order.objects.all().order_by(*order_by_obj)
            
            total_record = len(order_qs)
        else:
            order_by_obj = ["-created_at"]

            order_qs = Order.objects.all().order_by(*order_by_obj)
            total_record = len(order_qs)

        if filter_due_date_start and filter_due_date_end:
            print(":")
            try:
                filter_due_date_start_obj = datetime.strptime(filter_due_date_start,'%Y-%m-%d')
                filter_due_date_end_obj = datetime.strptime(filter_due_date_end,'%Y-%m-%d')
                order_qs = order_qs.filter(due_date__range=(filter_due_date_start_obj,filter_due_date_end_obj))

            except Exception as e:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'date format should be YY-MM-DD'
                                },status=status.HTTP_400_BAD_REQUEST)

        if filter_from_date and filter_to_date:
            try:
                filter_from_date_obj = datetime.strptime(filter_from_date,'%Y-%m-%d')
                filter_to_date_obj = datetime.strptime(filter_to_date,'%Y-%m-%d')
                order_qs = order_qs.filter(created_at__gte=filter_from_date_obj,created_at__lte=filter_to_date_obj)

            except Exception as e:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'date format should be YY-MM-DD'
                                },status=status.HTTP_400_BAD_REQUEST)

        if filter_payment_status:
            order_qs = order_qs.filter(payment_status=filter_payment_status)
        if filter_customer_name:
            order_qs = order_qs.filter(customer__full_name=filter_customer_name)
        if filter_store_name:
            order_qs = order_qs.filter(customer__store_name=filter_store_name)
        if filter_order_status:
            order_qs = order_qs.filter(status=filter_order_status)
        if filter_verification_status:
            order_qs = order_qs.filter(verfication_status=filter_verification_status)

        # searching data
        if search_param:
            filter_data_qs = order_qs.filter(Q(invoice_no__icontains = search_param) |
                                                Q(po_num__icontains = search_param) |
                                                Q(detail__icontains = search_param)|
                                                Q(created_at__icontains=search_param)|
                                                Q(due_date__icontains=search_param)|
                                                Q(amount__icontains=search_param)|
                                                Q(amount_recieved__icontains=search_param)|
                                                Q(remaining_amount__icontains=search_param)|
                                                Q(payment_status__icontains=search_param)|
                                                Q(status__icontains =search_param)|
                                                Q(payment_status__icontains=search_param)|
                                                Q(ordered_by__full_name__icontains=search_param)|
                                                Q(customer__store_name__icontains=search_param)|
                                                Q(customer__full_name__icontains=search_param))

            filter_data_qs=filter_data_qs.order_by(*order_by_obj)
            filter_record = len(filter_data_qs)
            list_with_pagelimit = filter_data_qs[start:end]
            serializer = OrderStatusSerializers(list_with_pagelimit, many=True, context={'request':request})
            serializer_data = serializer.data
            

        else:
            filter_record = len(order_qs)
            list_with_pagelimit = order_qs[start:end]
            serializer = OrderStatusSerializers(list_with_pagelimit, many=True, context={'request':request})
            serializer_data = serializer.data
            
        # except Exception as e:
        #     print('e: ', e)
        #     response = {
        #         'status_code':status.HTTP_400_BAD_REQUEST,
        #         'message':'Somthing went wrong',
        #         }
        #     return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if len(serializer_data) == 0:
            response = {
            'status_code':status.HTTP_200_OK,
            'data': [],
            'total_record':0,
            'filter_record':0,
            'message':"No Data Found"
            }
            return Response(response, status=status.HTTP_200_OK)

        else:
            msg = 'Data fetch succesfully'   

        count_data = {}
        pending = order_qs.aggregate(Sum('amount_recieved'))
        count_data.update({
                'amount_recieved' : pending['amount_recieved__sum'] if pending['amount_recieved__sum'] else 0
            })
        
        total = order_qs.aggregate(Sum('amount'))
        count_data.update({
                'total_amount' : total['amount__sum'] if total['amount__sum'] else 0
            })

        open_orders = order_qs.filter(status='OPEN').count()
        count_data.update({
                'open_order' : open_orders
            })

        COMPLETED = order_qs.filter(status='COMPLETED').count()
        count_data.update({
                'completed_orders' : COMPLETED
            })

        product_out_ofStock = Product.objects.filter(available_quantity=0).count()
        product_low_Stock = Product.objects.filter(low_stock = True).count()

        count_data.update({
            'product_low_stock': product_low_Stock,
            'product_out_of_stock': product_out_ofStock,
        })

        remaining = order_qs.aggregate(Sum('remaining_amount'))
        count_data.update({
                'remaining_amount' : remaining['remaining_amount__sum'] if remaining['remaining_amount__sum'] else 0
            })

        response = {
            'status_code':status.HTTP_200_OK,
            'count_data':count_data,
            'data': serializer_data,
            'total_record':total_record,
            'filter_record':filter_record,
            'message':msg
        }
        return Response(response, status=status.HTTP_200_OK)

# @authentication_classes([])
class OrderGetView(APIView):
    authentication_classes = (MyCustomAuth,)
    def post(self, request, id, format=None):
        try:
            order_obj = Order.objects.get(id=id)
        except:
            response = {
                'status_code' : status.HTTP_404_NOT_FOUND,
                'message' : 'Order not found!'
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
  
        search_param = request.data.get('search_param')
        sort_field = request.data.get("sort_field", "order_product_name")
        sort_type = request.data.get("sort_type", "asc")
        order_by = sort_field

        if sort_field == "order_product_name":
            order_by = "order_product_name"
        elif sort_field == "item_no":
            order_by = "product__item_no"
        elif sort_field == "category_name":
            order_by = "product__category__name"

        order_by_obj = order_by
        extra_data = {
            'page':page,
            'limit':limit,
            'start' : start,
            'end' : end,
            'order_by':order_by_obj,
            'sort_type':sort_type,
            'search_param':search_param
        }
        
        shipping_address_string = ""
        if order_obj.customer.shipping_address:
            for x in order_obj.customer.shipping_address._meta.get_fields()[3:]:
                if getattr(order_obj.customer.shipping_address,x.name):
                    shipping_address_string +=getattr(order_obj.customer.shipping_address,x.name) + ","

            shipping_address_string = shipping_address_string.strip(",")

        billing_address_string = ""
        if order_obj.customer.billing_address:
            for x in order_obj.customer.billing_address._meta.get_fields()[2:]:
                if getattr(order_obj.customer.billing_address,x.name):
                    billing_address_string +=getattr(order_obj.customer.billing_address,x.name) + ","

            billing_address_string = billing_address_string.strip(",")

        serializer = OrderDetailSerializers(order_obj,context={'extra_data':extra_data})
        
        data = serializer.data.copy()
        creditmemo_list = CreditApplied.objects.filter(credit_applied_order=order_obj).values_list("credit_memo__cm_no",flat=True).distinct()

        data.update({
            'invoice_no':order_obj.invoice_no,
            'customer_name':order_obj.customer.full_name,
            'shipping_address':shipping_address_string,
            'billing_address' : billing_address_string,
            'sub_total' : order_obj.sub_total,
            'total' :order_obj.amount,
            'applied_credit' :order_obj.applied_credit,
            'creditmemo_list' :creditmemo_list,
            'order_date':order_obj.created_at.strftime("%Y-%m-%d"),
            'order_status':order_obj.status,
            'due_date':order_obj.due_date.strftime("%Y-%m-%d") if order_obj.due_date else None,
            'delivery_date':order_obj.delivery_date.strftime("%Y-%m-%d") if order_obj.delivery_date else None,
            'amount_received':order_obj.amount_recieved,
            'amount_due':order_obj.remaining_amount
        }) 

        response = {
            'status_code' : status.HTTP_200_OK,
            'message': 'Data fetch succesfully',
            'data' : data}
        
        return Response(response, status=status.HTTP_200_OK)                

        
# salesuser/warehouse user edit profile apis
# @authentication_classes([])
class EditProfile(APIView):
    authentication_classes = (MyCustomAuth,)

    def put(self, request, id, format=None):
        try:
            user_obj = User.objects.get(id=id)
        except:
            response = {
                'status_code' : status.HTTP_404_NOT_FOUND,
                'message' : 'User not found!'
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        fullname = request.data.get("full_name")
        phone_no = request.data.get('phone')
        email = request.data.get('email')
        address = request.data.get('address')
        city = request.data.get('city')
        state = request.data.get('state')
        country = request.data.get('country')
        zipcode = request.data.get('zipcode')
        password = request.data.get('password')

        if address:
            shipping_address_obj = user_obj.address
            if shipping_address_obj:
                serializer = ShippingAddressSerializers(shipping_address_obj,data=request.data,partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()

            else:
                serializer = ShippingAddressSerializers(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    obj = serializer.save()
                    user_obj.address = obj
                    user_obj.save()

        if fullname:
            user_obj.full_name = fullname
        if phone_no:
            user_obj.phone_no = phone_no
        if email:
            user_obj.email = email
        if password:
            # user_obj.set_password(password)
            user_obj.password = password

        user_obj.save()
        
        serializers = UserSerializers(user_obj)
        data = serializers.data
        data.update({
            'token' : request.META.get('HTTP_AUTHORIZATION').split(" ")[1]
        })
        response = {
            'status_code' : status.HTTP_200_OK,
            'message' : "User details updated!",
            'data':data
                }
        return Response(response, status=status.HTTP_200_OK)
        

class ForceUpdate(viewsets.ViewSet):
    def create(self,request,*args,**kwargs):
        
        android_version = request.data.get("android_version")
        if not android_version:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"android_version is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        ios_version = request.data.get("ios_version")
        if not ios_version:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"ios_version is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        force_android = request.data.get("force_android")
        if not force_android:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"force_android is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        force_ios = request.data.get("force_ios")
        if not force_ios:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"force_ios is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        obj = ForceAppUpdate.objects.all().first()
        if not obj:
            ForceAppUpdate.objects.create(android=android_version,ios=ios_version,android_force=force_android,ios_force=force_ios)
        
        else:
            obj.android=android_version
            obj.ios=ios_version
            obj.android_force = force_android
            obj.ios_force = force_ios
            obj.save()    

        return Response({
                'status_code':status.HTTP_200_OK,
                'message':'successfull',
                },status=status.HTTP_200_OK)

    def list(self,request):
        obj = ForceAppUpdate.objects.all().first()

        return Response({
                'status_code':status.HTTP_200_OK,
                'data':{
                    'android_version' : obj.android if obj else "" ,
                    'ios_version':obj.ios if obj else "" ,
                    'android_force':obj.android_force if obj else "" ,
                    'ios_force' : obj.ios_force if obj else "" 
                }
                },status=status.HTTP_200_OK)


class ScanOrder(viewsets.ViewSet):
    def create(self,request,*args,**kwargs):
        order_id = request.data.get("order_id")
        barcode_string = request.data.get("barcode_string")
        quantity_to_be_scanned = float(request.data.get("quantity",1))

        if not order_id:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"order ID is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not barcode_string:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Barcode String is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        order_obj = Order.objects.filter(id=order_id).first()
        if not order_obj:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Invalid OrderID",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        product_obj = Product.objects.filter(barcode_string=barcode_string).first()
        if not product_obj:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Not matching product for barcode",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        order_quantity_qs = OrderQuantity.objects.filter(order=order_obj,product=product_obj)
        if len(order_quantity_qs) == 0:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Scanned product not in order",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        quantity_to_scan = quantity_to_be_scanned

        if quantity_to_scan > product_obj.available_quantity:
            scan_diff = quantity_to_scan - product_obj.available_quantity
            quantity_to_scan = quantity_to_scan - scan_diff 

        if quantity_to_scan <= product_obj.available_quantity:
            try:
                new_to_scan = quantity_to_scan
                for order_quantity in order_quantity_qs:

                    if order_quantity.remaining_scan_quantity != 0:
                        old = order_quantity.remaining_scan_quantity 

                        if old < new_to_scan :
                            to_scan = old
                            new_to_scan = new_to_scan - to_scan
                        elif old >= new_to_scan:
                            to_scan = new_to_scan
                            new_to_scan = new_to_scan - to_scan

                        order_quantity.scan_status = 'SCANNED'
                        order_quantity.scan_quantity +=  to_scan
                        product_obj.available_quantity -= to_scan 
                        order_quantity.remaining_scan_quantity -= to_scan
                        product_obj.save()
                        order_quantity.save()

                        if new_to_scan == 0:
                            break
                
                response = {
                    'status_code':status.HTTP_200_OK,
                    'message' : "Product Scanned Successfully",
                }

                if product_obj.available_quantity <= product_obj.low_stock_qauntity:
                    product_obj.low_stock = True
                
                if product_obj.available_quantity == 0:
                    product_obj.in_stock = False

                product_obj.save()
                if order_quantity.scan_quantity != order_quantity.quantity:
                    order_quantity.scan_status = 'PARTIALLY_SCANNED'
                    order_quantity.save()
                    response.update({
                        'data': {
                            'remaining_quanity':'{0} Packets Scanning left'.format(order_quantity.quantity - order_quantity.scan_quantity)
                        }
                    })
            except Exception as e:
                response = {
                    'status_code':status.HTTP_400_BAD_REQUEST,
                    'message':"Something went wrong!",
                    'error':str(e)
                    }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        else:
            order_quantity = OrderQuantity.objects.filter(order=order_obj,product=product_obj).first()
            new_scanned_quantity = product_obj.available_quantity
            order_quantity.scan_quantity += new_scanned_quantity
            order_quantity.scan_status = 'PARTIALLY_SCANNED'
            order_quantity.save()
            product_obj.available_quantity -= new_scanned_quantity
            response = None
            
            
            if product_obj.available_quantity <= product_obj.low_stock_qauntity:
                product_obj.low_stock = True
                response = {
                    'status_code':status.HTTP_200_OK,
                    'message' : "Inform Admin About Low Stock",
                }

            if product_obj.available_quantity == 0:
                product_obj.in_stock = False
                response = {
                    'status_code':status.HTTP_200_OK,
                    'message' : "Inform Admin About Out of Stock",
                }
            if not response:
                response = {
                    'status_code':status.HTTP_200_OK,
                    'message' : "Product scanned Partially",
                    }
            product_obj.save()
            response.update({
                'data': {
                    'remaining_quanity':'{0} Packets Scanning left'.format(order_quantity.quantity - order_quantity.scan_quantity)
                }
            })

        if order_obj.status=='OPEN':
            if OrderQuantity.objects.filter(order=order_obj).exclude(scan_status='SCANNED').exists():
                order_obj.status = 'IN_PROCESS'
            else:
                order_obj.status = 'COMPLETED'
        elif order_obj.status=='IN_PROCESS':
            order_obj.status = 'IN_PROCESS'


        order_obj.save()
        return Response(response, status=status.HTTP_200_OK)


    @action(methods=['POST'],detail=True)
    def verify_order(self,request,pk=None,**kwargs):
        order_obj = Order.objects.filter(id=pk).first()
        if not order_obj:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Invalid OrderID",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not order_obj.invoice_no:
            kpo_number_qs = Order.objects.filter(invoice_no__startswith='KPO').order_by('invoice_no')
            next_kpo_num = 0
            if len(kpo_number_qs) == 0:
                next_kpo_num = 'KPO' + str(2300)
            else:
                last_kpo_number = kpo_number_qs.last()
                new_num = int(last_kpo_number.invoice_no[3:]) + 1
                next_kpo_num = 'KPO' + str(new_num)
            order_obj.invoice_no = next_kpo_num
            order_obj.invoice_date = datetime.now().date()

        order_obj.verfication_status = True
        order_obj.save()
        response = {
            'status_code':status.HTTP_200_OK,
            'message' : "Order verification complete.",
        }
        return Response(response, status=status.HTTP_200_OK)
    
    @action(methods=['POST'],detail=True)
    def mark_complete(self,request,pk=None,**kwargs):
        '''
        This function changes order status to complete
        '''
        order_obj = Order.objects.filter(id=pk).first()
        if not order_obj:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Invalid OrderID",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        order_obj.status = 'COMPLETED'
        order_obj.save()

        subject = 'Order Completed'
        message = 'Please check completed order details,\n\n1.Order ID : {0}\n2. Order Amount : {1}\n 3.Due Date : {2}'.format(order_obj.id,order_obj.amount,order_obj.due_date)

        email_form = settings.DEFAULT_FROM_EMAIL
        recipient_list = User.objects.filter(user_type='ADMIN').values_list('email',flat=True).distinct()
        recipient_list = list(recipient_list)

        send_mail(subject,message,email_form,recipient_list)
        response = {
                'status_code':status.HTTP_200_OK,
                'message' : "Order complete.",
        }
        return Response(response, status=status.HTTP_200_OK)

    @action(methods=['POST'],detail=False)
    def verfication_scan(self,request,**kwargs):
        order_id = request.data.get("order_id")
        barcode_string = request.data.get("barcode_string")
        quantity_to_scan = float(request.data.get("quantity",1))

        if not order_id:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"order ID is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not barcode_string:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Barcode String is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        order_obj = Order.objects.filter(id=order_id).first()
        if not order_obj:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Invalid OrderID",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        product_obj = Product.objects.filter(barcode_string=barcode_string).first()
        if not product_obj:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Not matching product for barcode",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        order_quantity_qs = OrderQuantity.objects.filter(order=order_obj,product=product_obj)
        if len(order_quantity_qs) == 0:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Scanned product not in order",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
    
        # if quantity_to_scan >= (order_quantity.quantity - order_quantity.verfication_scan_quantity):
        new_to_scan = quantity_to_scan
        for order_quantity in order_quantity_qs:
            
            if order_quantity.remaining_verfication_scan_quantity != 0:
                old = order_quantity.remaining_verfication_scan_quantity 

                if old < new_to_scan :
                    to_scan = old
                    new_to_scan = new_to_scan - to_scan
                elif old >= new_to_scan:
                    to_scan = new_to_scan
                    new_to_scan = new_to_scan - to_scan
                
                order_quantity.verfication_scan_status = 'SCANNED'
                order_quantity.verfication_scan_quantity +=  to_scan
                order_quantity.remaining_verfication_scan_quantity -= to_scan
                product_obj.save()
                order_quantity.save()

                if new_to_scan == 0:
                    if order_quantity.remaining_verfication_scan_quantity != 0:
                        order_quantity.verfication_scan_status = 'PARTIALLY_SCANNED'
                        order_quantity.save()

                        response = {
                                    'status_code':status.HTTP_200_OK,
                                    'message' : "Product scanned Partially",
                                    'data': '{0} Packets Scanning left'.format(order_quantity.remaining_verfication_scan_quantity)
                        }
                    else:
                        response = {
                            'status_code':status.HTTP_200_OK,
                            'message' : "Product Scanned Successfully",
                        }
                    break


        return Response(response, status=status.HTTP_200_OK)

class InvoicePDF_url(viewsets.ViewSet):
    def create(self,request,*args,**kwargs):        
        invoice_no = request.data.get('invoice_no')
        order_obj = Order.objects.filter(invoice_no=invoice_no).first()
        
        if not order_obj:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Order ID is Invalid",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Fetch PDF-Data
        pdfdata_res = get_order_pdfdata(order_obj)
        if pdfdata_res["status_code"] != True:
            return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
        else:
            pdf_data = pdfdata_res.get("pdf_data")
            num_of_row_data  = pdfdata_res.get("num_of_row_data")
        
        # Creating PDF 
        filename = 'file' + invoice_no + '.pdf' 
        createpdf_res = create_pdf(request = request,
                            pdf_type = "invoice_pdf",
                            pdf_data = pdf_data,
                            filename = filename,
                            order_obj = order_obj,
                            num_of_row_data = num_of_row_data,
                        )
        if createpdf_res["status_code"] != True:
            return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {}
            data['pdf_url'] = createpdf_res.get("pdf_url")

        response = {'message':"PDF is retrieved successfully.", 'status':status.HTTP_200_OK, 'data': data}

        return Response(response, status.HTTP_200_OK)

class InvoicePDF(viewsets.ViewSet):
    def create(self,request,*args,**kwargs):
        invoice_no = request.data.get('invoice_no')
        order_obj = Order.objects.filter(invoice_no=invoice_no).first()
        print('order_obj: ', order_obj)
        if not order_obj:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Order ID is Invalid",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        customer_obj = order_obj.customer
        products_data_for_pdf = []
        sum_of_weights = 0
        sum_of_qty = 0
        for order in OrderQuantity.objects.filter(order=order_obj).order_by('product__category__name',Lower('order_product_name')):
            product_obj = order.product
            # sum_of_weights+= product_obj.weight if product_obj.weight else 0
            sum_of_weights+= product_obj.weight * float(order.quantity) if product_obj.weight else 0
            sum_of_qty+=order.quantity if order.quantity else 0
            products_data_for_pdf.append({'product_id':product_obj.id,'category':product_obj.category,
                                                'description':order.order_product_name,'price':"%.2f" % round(order.net_price, 2),
                                                'scan_qty':order.scan_quantity,
                                                'qty':int(order.quantity) if order.quantity.is_integer() else order.quantity,
                                                'amount':"%.2f" % round(order.product_amount, 2),
                                                "item_no":product_obj.item_no
                                                })

        pdf_data = dict()
        pdf_data['products']= products_data_for_pdf
        pdf_data['invoice_no'] = order_obj.invoice_no
        pdf_data['krishiv_src']= krishiv_logo.src_data
        pdf_data['ramdev_src']= ramdev_logo.src_data

        pdf_data['date'] = order_obj.invoice_date
        if customer_obj.both_address_same == False:
            if customer_obj.billing_address is not None:
                pdf_data['billing_address'] = customer_obj.billing_address.address
                pdf_data['billing_city'] = customer_obj.billing_address.city
                pdf_data['billing_state'] = customer_obj.billing_address.state
                pdf_data['billing_zipcode'] = customer_obj.billing_address.zipcode
                # pdf_data['billing_country'] = customer_obj.billing_address.country
            if customer_obj.shipping_address is not None:
                pdf_data['shipping_address'] = customer_obj.shipping_address.address
                pdf_data['shipping_city'] = customer_obj.shipping_address.city
                pdf_data['shipping_state'] = customer_obj.shipping_address.state
                pdf_data['shipping_zipcode'] = customer_obj.shipping_address.zipcode
                # pdf_data['shipping_country'] = customer_obj.shipping_address.country

        else:
            if customer_obj.shipping_address is not None:
                pdf_data['billing_address'] = customer_obj.shipping_address.address
                pdf_data['billing_city'] = customer_obj.shipping_address.city
                pdf_data['billing_state'] = customer_obj.shipping_address.state
                pdf_data['billing_zipcode'] = customer_obj.shipping_address.zipcode
                pdf_data['billing_country'] = customer_obj.shipping_address.country
                pdf_data['shipping_address'] = customer_obj.shipping_address.address
                pdf_data['shipping_city'] = customer_obj.shipping_address.city
                pdf_data['shipping_state'] = customer_obj.shipping_address.state
                pdf_data['shipping_zipcode'] = customer_obj.shipping_address.zipcode
                # pdf_data['shipping_country'] = customer_obj.shipping_address.country
        pdf_data['po_num'] = order_obj.po_num
        pdf_data['delivery_method'] = order_obj.delivery_method if order_obj.delivery_method else '-'
        pdf_data['total'] = "%.2f" % round(order_obj.amount, 2)
        pdf_data['due_date'] = order_obj.due_date
        pdf_data['ship_date']= order_obj.delivery_date
        pdf_data['account_num'] = customer_obj.account_num.replace("-", "") if customer_obj.account_num else '-'
        if customer_obj.phone:
            pdf_data['mobilenumber'] =  '({0}) {1}-{2}'.format(customer_obj.phone[:3],customer_obj.phone[3:6],customer_obj.phone[6:])
        else:
            pdf_data['mobilenumber'] = ''
        pdf_data['weight']= "%.2f" % round(sum_of_weights, 2)
        sum_of_qty =  str(sum_of_qty)
        val = sum_of_qty.find(".")
        sum_part_2 = sum_of_qty[val+1:]
        if len(sum_part_2) > 2:
            part_2 = sum_part_2[:2]
            sum_of_qty = sum_of_qty.replace(sum_part_2,part_2)
        pdf_data['total_qty']= sum_of_qty
        pdf_data['terms']= order_obj.term
        pdf_data['store_name']= customer_obj.store_name
        pdf_data['customer_name']= customer_obj.full_name
        pdf_data['rep']= '-'
        pdf_data['page_title']= 'INVOICE'
        pdf_data['date_title']= 'Invoice#'

        if customer_obj.sales_person:
            full_name = customer_obj.sales_person.full_name
            data = full_name.split(' ')
            if len(data) != 0:
                pdf_data['rep']= data[0][0] 
                if len(data) >= 2:
                    pdf_data['rep'] = pdf_data['rep'] + data[1][0]

        # Getting extra row needs to add in last page of PDF 
        num_of_row_data = len(products_data_for_pdf)

        total_page_rows = num_of_row_data + (26 - num_of_row_data) % 26

        extra_rows = total_page_rows - num_of_row_data
        if extra_rows == 1:
            extra_rows += 1
        elif  extra_rows == 2:
            extra_rows = 0
        elif extra_rows >= 3:
            extra_rows -= 1
        # elif extra_rows == 0:
        #     extra_rows = 25
        
        pdf_data['loop_times'] = range(1, extra_rows+1)
        
        template=get_template(settings.BASE_DIR +'/templates/invoice_pdf.html')
        html = template.render(pdf_data)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result,
                                encoding='UTF-8')
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            # response = HttpResponse(pdf, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'
            return response
        return None 

class CreateOrderNew(viewsets.ViewSet):
    def create(self,request,*args,**kwargs):
        due_date = request.data.get("due_date")
        delivery_date = request.data.get("delivery_date")
        products_data = request.data.get("products")
        customer = request.data.get("customer_id")
        delivery_method = request.data.get('delivery_method')
        term = request.data.get('term')
        flag_email = request.data.get("flag_email")

        if not customer:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Customer ID is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        customer_obj = Customer.objects.filter(id=customer).first()
        if not customer_obj:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Customer ID is Invalid",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not due_date:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Due Date is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not delivery_date:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Delivery Date is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if term == None:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Term is required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            due_date_obj = datetime.strptime(due_date,"%Y-%m-%d")
            delivery_date_obj = datetime.strptime(delivery_date,"%Y-%m-%d")
        
        except:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Dates should be in YY-MM-DD format",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not products_data:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Products are required",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        order_obj = Order.objects.create(customer=customer_obj,ordered_by=request.user,status='OPEN',
                                        delivery_date=delivery_date_obj.date(),due_date=due_date_obj.date(),
                                        delivery_method=delivery_method,term="Net " + str(term))
        response_msg = None

        flag = 0
        products_data_for_pdf = []
        sum_of_weights = 0.0
        sum_of_qty = 0
        for product in products_data:
            if not product['ProductId'] :
                continue
            
            product_obj = Product.objects.filter(id=product['ProductId']).first()
            
            packsize_obj = product_obj.pack_size.first()
            discount =0 if product['Discount'] == "" or product['Discount'] == None else float(product['Discount'])
            price = product['PackagePrice']
            net_price = float(price) - float(discount)
            purchase_price = product_obj.purchase_cost
            product_amount = 0 if product['Total'] == "" or product['Total'] == None else float(product['Total'])
            if product['ProductId'] and product['Count']:
                if not product_obj:
                    response_msg = "Invalid productID in products list"
                    break

                if not packsize_obj:
                    response_msg = "Invalid PacksizeID in products list"
                    break

                OrderQuantity.objects.create(
                    product=product_obj,pack_size=packsize_obj,quantity = product['Count'],
                    discount=discount,price = price,net_price=net_price,product_amount=product_amount,order=order_obj,
                    product_purchase_price = purchase_price)
                # order_obj.amount+=product_amount
                round_price=round(float(price),2)
                
                sum_of_weights+= product_obj.weight * float(product['Count']) if product_obj.weight else 0
                sum_of_qty += float(product['Count']) if product['Count'] else 0
                products_data_for_pdf.append({'product_id':product_obj.item_no,'category':product_obj.category,
                                            'description':product_obj.name,'price':"%.2f" % round(net_price, 2),
                                            'qty':int(product['Count']) if float(product['Count']).is_integer() else product['Count'],
                                            'scan_qty':'0','item_no':product_obj.item_no,
                                            'amount':"%.2f" % round(product_amount, 2),
                                            })

            else:
                print("sdsdas")
                flag = 1

        order_obj.save()
        
        # sort data by category and order_product_name 
        products_data_for_pdf = sorted(products_data_for_pdf, key = lambda i: (i['category'].name, i['description'].lower()))

        if response_msg:
            OrderQuantity.objects.filter(order=order_obj).delete()
            order_obj.delete()
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':response_msg,
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not OrderQuantity.objects.filter(order=order_obj).exists():
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Order not created due to no valid product data",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderSerializers(order_obj)
        message = "Some of the items were cancelled from order as all the data was not filled up for those products." if flag else 'Order Successfully Created'
        response = {
                'status_code':status.HTTP_200_OK,
                'data':serializer.data,
                'message' : message,
                }
 
        pdf_data = dict()
        pdf_data['products']= products_data_for_pdf
        pdf_data['invoice_no'] = order_obj.invoice_no

        pdf_data['date'] = datetime.now().date()
        if customer_obj.both_address_same == False:
            if customer_obj.billing_address is not None:
                pdf_data['billing_address'] = customer_obj.billing_address.address
                pdf_data['billing_city'] = customer_obj.billing_address.city
                pdf_data['billing_state'] = customer_obj.billing_address.state
                pdf_data['billing_zipcode'] = customer_obj.billing_address.zipcode
                pdf_data['billing_country'] = customer_obj.billing_address.country
            if customer_obj.shipping_address is not None:
                pdf_data['shipping_address'] = customer_obj.shipping_address.address
                pdf_data['shipping_city'] = customer_obj.shipping_address.city
                pdf_data['shipping_state'] = customer_obj.shipping_address.state
                pdf_data['shipping_zipcode'] = customer_obj.shipping_address.zipcode
                pdf_data['shipping_country'] = customer_obj.shipping_address.country

        else:
            if customer_obj.shipping_address is not None:
                pdf_data['billing_address'] = customer_obj.shipping_address.address
                pdf_data['billing_city'] = customer_obj.shipping_address.city
                pdf_data['billing_state'] = customer_obj.shipping_address.state
                pdf_data['billing_zipcode'] = customer_obj.shipping_address.zipcode
                pdf_data['billing_country'] = customer_obj.shipping_address.country
                pdf_data['shipping_address'] = customer_obj.shipping_address.address
                pdf_data['shipping_city'] = customer_obj.shipping_address.city
                pdf_data['shipping_state'] = customer_obj.shipping_address.state
                pdf_data['shipping_zipcode'] = customer_obj.shipping_address.zipcode
                pdf_data['shipping_country'] = customer_obj.shipping_address.country
        pdf_data['po_num'] = order_obj.po_num
        pdf_data['invoice_no'] = order_obj.po_num
        pdf_data['total'] = "%.2f" % round(order_obj.amount, 2)
        pdf_data['weight']= "%.2f" % round(sum_of_weights, 2)
        sum_of_qty =  str(sum_of_qty)
        val = sum_of_qty.find(".")
        sum_part_2 = sum_of_qty[val+1:]
        if len(sum_part_2) > 2:
            part_2 = sum_part_2[:2]
            sum_of_qty = sum_of_qty.replace(sum_part_2,part_2)
        pdf_data['total_qty']= "%.2f" % round(float(sum_of_qty), 2)
        pdf_data['due_date'] = order_obj.due_date
        pdf_data['ship_date']= order_obj.delivery_date
        pdf_data['account_num'] = customer_obj.account_num.replace("-", "") if customer_obj.account_num else '-'
        if customer_obj.phone:
            pdf_data['mobilenumber'] =  '({0}) {1}-{2}'.format(customer_obj.phone[:3],customer_obj.phone[3:6],customer_obj.phone[6:])
        else:
            pdf_data['mobilenumber'] = ''
        pdf_data['terms']= order_obj.term
        pdf_data['store_name']= customer_obj.store_name
        pdf_data['customer_name']= customer_obj.full_name
        pdf_data['delivery_method'] = order_obj.delivery_method if order_obj.delivery_method else '-'
        pdf_data['rep']= '-'
        pdf_data['page_title']= 'SALES ORDER'
        pdf_data['date_title']= 'PO No#'

        num_of_row_data = len(products_data_for_pdf)

        if customer_obj.sales_person:
            full_name = customer_obj.sales_person.full_name
            data = full_name.split(' ')
            if len(data) != 0:
                pdf_data['rep']= data[0][0] 
                if len(data) >= 2:
                    pdf_data['rep'] = pdf_data['rep'] + data[1][0]

        # Creating PDF 
        filename = 'salesorder'+str(order_obj.po_num) + '-'+ str(datetime.now().date()) + '.pdf'
        createpdf_res = create_pdf(request = request,
                            pdf_type = "sales_pdf",
                            pdf_data = pdf_data,
                            filename = filename,
                            order_obj = order_obj,
                            num_of_row_data = num_of_row_data,
                        )
        if createpdf_res["status_code"] != True:
            return Response(createpdf_res, status=status.HTTP_400_BAD_REQUEST)
        else:
            pdf_url = createpdf_res.get("pdf_url")

        # Send PDF to the mail
        email_subject = customer_obj.store_name + ' - PO No# ' + str(order_obj.po_num)
        email_body = "Please check new order details\n\n" + \
                "PO No# : {}\n".format(order_obj.po_num) + \
                "Order Amount : $ {}\n".format("%.2f" % round(order_obj.amount, 2)) + \
                "Due Date : {} \n".format(order_obj.due_date.strftime('%m-%d-%Y')) + \
                "Please click to below link to download sales-order PDF:\n{}".format(pdf_url)
        
        recipient_list = User.objects.filter(user_type='ADMIN').values_list('email',flat=True).distinct()
        recipient_list = list(recipient_list)
        recipient_list.append(order_obj.ordered_by.email)
        if flag_email in [True,"true","True"]:
            recipient_list.append(order_obj.customer.email)

        send_pdf_response = send_pdf_mail(order_obj = order_obj,
                                        flag_email = flag_email,
                                        filename = filename,
                                        email_body = email_body,
                                        email_subject = email_subject,
                                        recipient_list = recipient_list
                                        )
        if send_pdf_response["status_code"] != True:
            return Response(send_pdf_response, status=status.HTTP_400_BAD_REQUEST)

        # send_notification
        device_tokens = Token.objects.filter(user__user_type='WAREHOUSE').values_list('device_token', flat = True).distinct()
        extra_content = {
            "order_id": order_obj.id,
            "type" : "order"
        }
        title = 'New Order'
        body = 'Please check new order'
        send_notification(title=title,body=body,device_tokens=list(device_tokens),extra_content=extra_content)

        return Response(response, status=status.HTTP_200_OK)

    def destroy(self,request,pk=None,*args,**kwargs):
        order_obj = Order.objects.filter(id=pk).first()
        if not order_obj:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Invalid OrderID",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        order_obj.delete()
        response = {
                'status_code':status.HTTP_200_OK,
                'message':"Order Deleted Sucessfully",
                }
        return Response(response, status=status.HTTP_200_OK)

    @action(methods=['POST'],detail=True)
    def update_order(self,request,pk=None):
        uid = pk
        due_date = request.data.get("due_date")
        delivery_date = request.data.get("delivery_date")
        products_data = request.data.get("products")
        customer = request.data.get("customer_id")
        delivery_method = request.data.get("delivery_method")
        term = request.data.get("term")
        flag_email = request.data.get("flag_email")

        if not uid:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'id required'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        verify_order = Order.objects.filter(id=uid).first()
        if not verify_order:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'no order for given id'
                            },status=status.HTTP_400_BAD_REQUEST)
        if not due_date:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'due date required'
                            },status=status.HTTP_400_BAD_REQUEST)
        if not delivery_date:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'delivery date required'
                            },status=status.HTTP_400_BAD_REQUEST)
        if not products_data:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'products data required'
                            },status=status.HTTP_400_BAD_REQUEST)
        if not customer:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'customer required'
                            },status=status.HTTP_400_BAD_REQUEST)
        if term == None:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'term required'
                            },status=status.HTTP_400_BAD_REQUEST)

        try:
            due_date_obj = datetime.strptime(due_date,'%Y-%m-%d')
            delivery_date_obj = datetime.strptime(delivery_date,'%Y-%m-%d')

        except Exception as e:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'date format should be YY-MM-DD'
                            },status=status.HTTP_400_BAD_REQUEST)
        customer_obj = Customer.objects.filter(id=customer).first()
        if not customer_obj :
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'invalid customer id'
                            },status=status.HTTP_400_BAD_REQUEST)

        verify_order.customer=customer_obj
        verify_order.ordered_by=request.user
        verify_order.status='OPEN'
        verify_order.delivery_date=delivery_date_obj.date()
        verify_order.due_date=due_date_obj.date()
        verify_order.term = "Net " + str(term)
        verify_order.save()

        response_msg = None
        OrderQuantity.objects.filter(order=verify_order).delete()
        verify_order.amount=0
        
        flag = 0
        products_data_for_pdf = []
        sum_of_weights = 0.0
        sum_of_qty = 0
        for product in products_data:
            if not product['ProductId'] :
                continue
            product_obj = Product.objects.filter(id=product['ProductId']).first()
            packsize_obj =  product_obj.pack_size.first()
            discount =0 if product['Discount'] == "" or product['Discount'] == None else float(product['Discount'])
            # price =0 if product['Total'] == "" or product['Total'] == None else int(product['Total'])
            price = product['PackagePrice']
            net_price = float(price) - float(discount)
            purchase_price = product_obj.purchase_cost 
            product_amount = 0 if product['Total'] == "" or product['Total'] == None else float(product['Total'])
            if not product_obj:
                response_msg = "Invalid productID in products list"
                break

            OrderQuantity.objects.create(
                product=product_obj,pack_size=packsize_obj,quantity = product['Count'],
                discount=discount,price = price,net_price=net_price,product_amount=product_amount,order=verify_order,
                product_purchase_price = purchase_price
                )
            # verify_order.amount+=product_amount
            round_price=round(float(price),2)
                
            sum_of_weights+= product_obj.weight * float(product['Count']) if product_obj.weight else 0
            sum_of_qty += product['Count'] if product['Count'] else 0
            products_data_for_pdf.append({'product_id':product_obj.item_no,'category':product_obj.category,
                                        'description':product_obj.name,'price':"%.2f" % round(net_price, 2),
                                        'qty':int(product['Count']) if float(product['Count']).is_integer() else product['Count'],
                                        'scan_qty':'0','item_no':product_obj.item_no,
                                        'amount':"%.2f" % round(product_amount, 2),
                                        })
        
        # sort data by category and order_product_name 
        products_data_for_pdf = sorted(products_data_for_pdf, key = lambda i: (i['category'].name, i['description'].lower()))

        verify_order.delivery_method=delivery_method
        verify_order.save()
        if response_msg:
            OrderQuantity.objects.filter(order=verify_order).delete()
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':response_msg,
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
    
        verify_order.due_date = due_date_obj.date()
        verify_order.delivery_date = delivery_date_obj.date()
        verify_order.save()
        serializer = OrderSerializers(verify_order)
        
        pdf_data = dict()
        pdf_data['products']= products_data_for_pdf
        pdf_data['invoice_no'] = verify_order.invoice_no

        pdf_data['date'] = datetime.now().date()
        if customer_obj.both_address_same == False:
            if customer_obj.billing_address is not None:
                pdf_data['billing_address'] = customer_obj.billing_address.address
                pdf_data['billing_city'] = customer_obj.billing_address.city
                pdf_data['billing_state'] = customer_obj.billing_address.state
                pdf_data['billing_zipcode'] = customer_obj.billing_address.zipcode
                pdf_data['billing_country'] = customer_obj.billing_address.country
            if customer_obj.shipping_address is not None:
                pdf_data['shipping_address'] = customer_obj.shipping_address.address
                pdf_data['shipping_city'] = customer_obj.shipping_address.city
                pdf_data['shipping_state'] = customer_obj.shipping_address.state
                pdf_data['shipping_zipcode'] = customer_obj.shipping_address.zipcode
                pdf_data['shipping_country'] = customer_obj.shipping_address.country

        else:
            if customer_obj.shipping_address is not None:
                pdf_data['billing_address'] = customer_obj.shipping_address.address
                pdf_data['billing_city'] = customer_obj.shipping_address.city
                pdf_data['billing_state'] = customer_obj.shipping_address.state
                pdf_data['billing_zipcode'] = customer_obj.shipping_address.zipcode
                pdf_data['billing_country'] = customer_obj.shipping_address.country
                pdf_data['shipping_address'] = customer_obj.shipping_address.address
                pdf_data['shipping_city'] = customer_obj.shipping_address.city
                pdf_data['shipping_state'] = customer_obj.shipping_address.state
                pdf_data['shipping_zipcode'] = customer_obj.shipping_address.zipcode
                pdf_data['shipping_country'] = customer_obj.shipping_address.country
        pdf_data['total'] = "%.2f" % round(verify_order.amount, 2)
        pdf_data['weight']= "%.2f" % round(sum_of_weights, 2)
        sum_of_qty =  str(sum_of_qty)
        val = sum_of_qty.find(".")
        sum_part_2 = sum_of_qty[val+1:]
        if len(sum_part_2) > 2:
            part_2 = sum_part_2[:2]
            sum_of_qty = sum_of_qty.replace(sum_part_2,part_2)
        pdf_data['total_qty']= "%.2f" % round(float(sum_of_qty), 2)
        pdf_data['due_date'] = verify_order.due_date
        pdf_data['ship_date']= verify_order.delivery_date
        pdf_data['account_num'] = customer_obj.account_num.replace("-", "") if customer_obj.account_num else '-'
        if customer_obj.phone:
            pdf_data['mobilenumber'] =  '({0}) {1}-{2}'.format(customer_obj.phone[:3],customer_obj.phone[3:6],customer_obj.phone[6:])
        else:
            pdf_data['mobilenumber'] = ''
        pdf_data['terms']= verify_order.term
        pdf_data['store_name']= customer_obj.store_name
        pdf_data['customer_name']= customer_obj.full_name
        pdf_data['delivery_method'] = verify_order.delivery_method if verify_order.delivery_method else '-'
        pdf_data['rep']= '-'
        pdf_data['page_title']= 'SALES ORDER'
        pdf_data['date_title']= 'PO No#'

        pdf_data['po_num'] = verify_order.po_num
        pdf_data['invoice_no'] = verify_order.invoice_no if verify_order.invoice_no else verify_order.po_num

        if customer_obj.sales_person:
            full_name = customer_obj.sales_person.full_name
            data = full_name.split(' ')
            if len(data) != 0:
                pdf_data['rep']= data[0][0] 
                if len(data) >= 2:
                    pdf_data['rep'] = pdf_data['rep'] + data[1][0]
        
        # Getting extra row needs to add in last page of PDF 
        num_of_row_data = len(products_data_for_pdf)
        
        # Creating PDF 
        filename = 'salesorder'+str(verify_order.po_num) + '-'+ str(datetime.now().date()) + '.pdf'
        createpdf_res = create_pdf(request = request,
                            pdf_type = "sales_pdf",
                            pdf_data = pdf_data,
                            filename = filename,
                            order_obj = verify_order,
                            num_of_row_data = num_of_row_data,
                        )
        if createpdf_res["status_code"] != True:
            return Response(createpdf_res, status=status.HTTP_400_BAD_REQUEST)
        else:
            pdf_url = createpdf_res.get("pdf_url")

        # Send PDF to the mail
        email_subject = customer_obj.store_name + ' - PO No# ' + verify_order.po_num
        email_body = "Please check updated order details\n\n" + \
                "PO No# : {}\n".format(verify_order.po_num) + \
                "Order Amount : $ {}\n".format("%.2f" % round(verify_order.amount, 2)) + \
                "Due Date : {} \n".format(verify_order.due_date.strftime('%m-%d-%Y')) + \
                "Please click to below link to download sales-order PDF:\n{}".format(pdf_url)

        recipient_list = User.objects.filter(user_type='ADMIN').values_list('email',flat=True).distinct()
        recipient_list = list(recipient_list)
        recipient_list.append(verify_order.ordered_by.email)
        if flag_email in [True,"true","True"]:
            recipient_list.append(verify_order.customer.email)

        send_pdf_response = send_pdf_mail(order_obj = verify_order,
                                        flag_email = flag_email,
                                        filename = filename,
                                        email_body = email_body,
                                        email_subject = email_subject,
                                        recipient_list = recipient_list
                                        )
        if send_pdf_response["status_code"] != True:
            return Response(send_pdf_response, status=status.HTTP_400_BAD_REQUEST)

        # send_notification
        device_tokens = Token.objects.filter(user__user_type='WAREHOUSE').values_list('device_token', flat = True).distinct()
        extra_content = {
            "order_id": verify_order.id,
            "type" : "order"
        }
        title = 'New Order'
        body = 'Please check new order'
        send_notification(title=title,body=body,device_tokens=list(device_tokens),extra_content=extra_content)

        response = {
                'status_code':status.HTTP_200_OK,
                'message':'successfully updated',
                'data':serializer.data,
                }
        return Response(response, status=status.HTTP_200_OK)

class EditOrderAdmin(viewsets.ViewSet):
    
    @action(methods=['POST'],detail=True)
    def add_product(self,request,pk=None,**kwargs):

        order_obj = Order.objects.filter(id=pk).first()
        product_id = request.data.get('product_id')
        quantity = float(request.data.get('quantity',1))
        discount = float(request.data.get('discount',0))
        packsize_id = request.data.get('packsize_id')
        price = float(request.data.get('price',0))

        if not order_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid OrderID'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        product_obj = Product.objects.filter(id=product_id).first()
        packsize_obj = product_obj.pack_size.first()

        if not packsize_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid Packsize ID'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if price:
            net_price = price - discount
            product_amount = net_price * quantity
        else:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Price is requried!'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        purchase_price = product_obj.purchase_cost
        OrderQuantity.objects.create(
            product=product_obj,pack_size=packsize_obj,quantity = quantity,
            discount=discount,price = price,net_price=net_price,order=order_obj,product_amount =product_amount,
            product_purchase_price = purchase_price
        )
        order_obj = Order.objects.filter(id=pk).first() #To Get updated value
        if order_obj.invoice_no:

            # Fetch PDF-Data
            pdfdata_res = get_order_pdfdata(order_obj)
            if pdfdata_res["status_code"] != True:
                return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
            else:
                pdf_data = pdfdata_res.get("pdf_data")
                num_of_row_data  = pdfdata_res.get("num_of_row_data")
            
            # Creating PDF 
            filename = 'file' + order_obj.invoice_no + '.pdf' 
            createpdf_res = create_pdf(request = request,
                                pdf_type = "invoice_pdf",
                                pdf_data = pdf_data,
                                filename = filename,
                                order_obj = order_obj,
                                num_of_row_data = num_of_row_data,
                            )
            if createpdf_res["status_code"] != True:
                return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {}
                data['pdf_url'] = createpdf_res.get("pdf_url")


        if order_obj.po_num:
            # Fetch PDF-Data
            pdfdata_res = get_order_pdfdata(order_obj,pdf_type="sales_pdf")
            if pdfdata_res["status_code"] != True:
                return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
            else:
                pdf_data = pdfdata_res.get("pdf_data")
                num_of_row_data  = pdfdata_res.get("num_of_row_data")
            
            # Creating PDF 
            filename =  'salesorder'+str(order_obj.po_num) + '-'+ str(datetime.now().date()) + '.pdf'
            createpdf_res = create_pdf(request = request,
                                pdf_type = "sales_pdf",
                                pdf_data = pdf_data,
                                filename = filename,
                                order_obj = order_obj,
                                num_of_row_data = num_of_row_data,
                            )
            if createpdf_res["status_code"] != True:
                return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {}
                data['pdf_url'] = createpdf_res.get("pdf_url")

        response = {
            'status_code':status.HTTP_200_OK,
            'message':"Product Added Order",
            }
        return Response(response, status=status.HTTP_200_OK)   
  
    @action(methods=['POST'],detail=True)
    def edit_product(self,request,pk=None,**kwargs):

        order_obj = Order.objects.filter(id=pk).first()
        product_id = request.data.get('product_id')
        order_quantity_id = request.data.get('order_quantity_id')
        quantity = float(request.data.get('quantity',1))
        discount = float(request.data.get('discount',0))
        packsize_id = request.data.get('packsize_id')
        price = float(request.data.get('price',0))
        order_product_name = request.data.get('order_product_name')
        update_calculations = request.data.get('update_calculations')


        if not order_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid OrderID'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not order_quantity_id:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'order_quantity_id is requried!'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if not update_calculations:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'update_calculations is requried!'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        product_obj = Product.objects.filter(id=product_id).first()
        packsize_obj = product_obj.pack_size.first()
        
        if not packsize_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid Packsize ID'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if price:
            net_price = price - discount
            product_amount = net_price * quantity
        else:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Price is requried!'
                            },status=status.HTTP_400_BAD_REQUEST)
        
        purchase_price = product_obj.purchase_cost
        order_quantity_obj = OrderQuantity.objects.filter(id=order_quantity_id).first()
        old_quantity = order_quantity_obj.quantity

        if update_calculations in ["false","False",False]:
            order_quantity_obj.order_product_name=order_product_name
        else:
            order_quantity_obj.product=product_obj
            order_quantity_obj.order_product_name=order_product_name
            order_quantity_obj.pack_size=packsize_obj
            order_quantity_obj.quantity = quantity
            order_quantity_obj.discount=discount
            order_quantity_obj.price = price
            order_quantity_obj.net_price = net_price
            order_quantity_obj.order=order_obj
            order_quantity_obj.product_amount = product_amount
            order_quantity_obj.product_purchase_price = purchase_price

        order_quantity_obj.save()

        if old_quantity != quantity:
            val = old_quantity - quantity
            product_obj.available_quantity += val
            product_obj.save()

        order_obj = Order.objects.filter(id=pk).first() #To Get updated value
        if order_obj.invoice_no:
            
            # Fetch PDF-Data
            pdfdata_res = get_order_pdfdata(order_obj)
            if pdfdata_res["status_code"] != True:
                return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
            else:
                pdf_data = pdfdata_res.get("pdf_data")
                num_of_row_data  = pdfdata_res.get("num_of_row_data")
            
            # Creating PDF 
            filename = 'file' + order_obj.invoice_no + '.pdf' 
            createpdf_res = create_pdf(request = request,
                                pdf_type = "invoice_pdf",
                                pdf_data = pdf_data,
                                filename = filename,
                                order_obj = order_obj,
                                num_of_row_data = num_of_row_data,
                            )
            if createpdf_res["status_code"] != True:
                return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {}
                data['pdf_url'] = createpdf_res.get("pdf_url")

        if order_obj.po_num:
            # Fetch PDF-Data
            pdfdata_res = get_order_pdfdata(order_obj,pdf_type="sales_pdf")
            if pdfdata_res["status_code"] != True:
                return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
            else:
                pdf_data = pdfdata_res.get("pdf_data")
                num_of_row_data  = pdfdata_res.get("num_of_row_data")
            
            # Creating PDF 
            filename =  'salesorder'+str(order_obj.po_num) + '-'+ str(datetime.now().date()) + '.pdf'
            createpdf_res = create_pdf(request = request,
                                pdf_type = "sales_pdf",
                                pdf_data = pdf_data,
                                filename = filename,
                                order_obj = order_obj,
                                num_of_row_data = num_of_row_data,
                            )
            if createpdf_res["status_code"] != True:
                return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {}
                data['pdf_url'] = createpdf_res.get("pdf_url")

        response = {
            'status_code':status.HTTP_200_OK,
            'message':"Updated successfully",
            }
        return Response(response, status=status.HTTP_200_OK)   
  
    @action(methods=['POST'],detail=True)
    def edit_other_details(self,request,pk=None,**kwargs):
        '''
        Api to edit payment due date of Order for admin panel
        '''
        order_obj = Order.objects.filter(id=pk).first()

        if not order_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid OrderID'
                            },status=status.HTTP_400_BAD_REQUEST)


        payment_delivery_date = request.data.get('payment_delivery_date')
        if not payment_delivery_date:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Payment delivery date is required'
                                },status=status.HTTP_400_BAD_REQUEST)


        try:
            #converting Date string to datetime object for saving in DB
            date_obj = datetime.strptime(payment_delivery_date,"%Y-%m-%d")
        except:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Date must be in YY-MM-DD format'
                            },status=status.HTTP_400_BAD_REQUEST)

        order_obj.delivery_date = date_obj
        order_obj.save()
        return Response({'status_code':status.HTTP_200_OK,
                            'message':'Order Edited Successfully'
                            },status=status.HTTP_200_OK)


    @action(methods=['POST'],detail=False)
    def delete_product(self,request,**kwargs):
        '''
        This api will delete product from order, meaning will delete OrderQuantity object for given ID
        '''
        order_quantity_id = request.data.get('order_quantity_id')
        obj = OrderQuantity.objects.filter(id=order_quantity_id).first()
        obj.product.available_quantity += obj.quantity
        obj.product.save()
        obj.order.amount -= obj.product_amount
        obj.order.save()
        obj.delete()
        update_profit(order_obj = obj.order)

        order_obj = obj.order

        if order_obj.invoice_no:

            # Fetch PDF-Data
            pdfdata_res = get_order_pdfdata(order_obj)
            if pdfdata_res["status_code"] != True:
                return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
            else:
                pdf_data = pdfdata_res.get("pdf_data")
                num_of_row_data  = pdfdata_res.get("num_of_row_data")
            
            # Creating PDF 
            filename = 'file' + order_obj.invoice_no + '.pdf' 
            createpdf_res = create_pdf(request = request,
                                pdf_type = "invoice_pdf",
                                pdf_data = pdf_data,
                                filename = filename,
                                order_obj = order_obj,
                                num_of_row_data = num_of_row_data,
                            )
            if createpdf_res["status_code"] != True:
                return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {}
                data['pdf_url'] = createpdf_res.get("pdf_url")
        
        if order_obj.po_num:
            # Fetch PDF-Data
            pdfdata_res = get_order_pdfdata(order_obj,pdf_type="sales_pdf")
            if pdfdata_res["status_code"] != True:
                return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
            else:
                pdf_data = pdfdata_res.get("pdf_data")
                num_of_row_data  = pdfdata_res.get("num_of_row_data")
            
            # Creating PDF 
            filename =  'salesorder'+str(order_obj.po_num) + '-'+ str(datetime.now().date()) + '.pdf'
            createpdf_res = create_pdf(request = request,
                                pdf_type = "sales_pdf",
                                pdf_data = pdf_data,
                                filename = filename,
                                order_obj = order_obj,
                                num_of_row_data = num_of_row_data,
                            )
            if createpdf_res["status_code"] != True:
                return Response(pdfdata_res, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {}
                data['pdf_url'] = createpdf_res.get("pdf_url")

        response = {
            'status_code':status.HTTP_200_OK,
            'message':"Product Deleted From Order",
            }
        return Response(response, status=status.HTTP_200_OK)   

    @action(methods=['POST'],detail=True)
    def get_product_data(self,request,pk=None,**kwargs):
        '''
        Get OrderQuantity object details for given ID
        '''
        order_obj = OrderQuantity.objects.filter(id=pk).first()
        if not order_obj:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Invalid OrderQuantity ID'
                            },status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderProductDetailSerializers(order_obj)
        response = {
            'status_code':status.HTTP_200_OK,
            'data': serializer.data,
            'message':"Successfull"
            }
        return Response(response, status=status.HTTP_200_OK)   
  

class ClearOrderPayment(viewsets.ViewSet):
    def create(self,request,*args,**kwargs):
        for payment in request.data:
            order_obj = Order.objects.get(id = payment['orderId'])
            amount = payment['payment']
            order_obj.remaining_amount -= amount
            order_obj.amount_recieved += amount
            if order_obj.remaining_amount < 0:
                order_obj.payment_status = 'FULL'

            order_obj.save()

        return Response({'status_code':status.HTTP_200_OK,
                        'message':'Order Payment updated'
                        },status=status.HTTP_200_OK)

class Initial_Product_Quantity(viewsets.ViewSet):
    '''
        This Viewset is for APIs for Initial Product Quanity Reports
    '''
    def create(self,request,*args,**kwargs):

        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        
        date = request.data.get('date')
        product__name = request.data.get('product__name')
        product__item_no = request.data.get('product__item_no')
        quantity = request.data.get('quantity')
        price = request.data.get('price')
        product__purchase_cost = request.data.get('product__purchase_cost')

        search_param = request.data.get("search_param")
        filter_by_product = request.data.get("filter_by_product")

        order_by_obj = []
        if date:
            order_by_obj.append(date)
        if product__name:
            order_by_obj.append(product__name)
        if product__item_no:
            order_by_obj.append(product__item_no)
        if quantity:
            order_by_obj.append(quantity)
        if price:
            order_by_obj.append(price)
        if product__purchase_cost:
            order_by_obj.append(product__purchase_cost)
        
        if order_by_obj:
            objects = InitialProduct.objects.all().order_by(*order_by_obj)
        else:    
            objects = InitialProduct.objects.all().order_by('-product__name')
        
        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')
    
        if From_Date and To_Date:
            try:
                from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                objects = objects.filter(date__gt = from_date_obj,date__lt =to_date_obj)

            except Exception as e:
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid date format date Format should year-month-date'
                                },status=status.HTTP_400_BAD_REQUEST)
        
        if filter_by_product:
            objects = objects.filter(product__id=filter_by_product) 

        if search_param:
            filter_qs = objects.filter(
                Q(product__name__icontains=search_param)|
                Q(product__item_no__icontains=search_param)|
                Q(price__icontains= search_param)|
                Q(quantity__icontains=search_param) |
                Q(product__purchase_cost__icontains=search_param)
            )
            
            print('filter_qs: ', filter_qs)
            total_record = len(objects)
            list_with_pagelimit = filter_qs[start:end]
            filter_record = len(list_with_pagelimit)
            serializer = InitialProductSerializer(list_with_pagelimit,many=True)

        else:
            total_record = len(objects)
            list_with_pagelimit = objects[start:end]
            filter_record = len(list_with_pagelimit)
            serializer = InitialProductSerializer(list_with_pagelimit,many=True)

        response = {
            'status_code':status.HTTP_200_OK,
            'data': serializer.data,
            'total_record':total_record,
            'filter_record':filter_record,
            'message':"Successfull"
        }
        return Response(response, status=status.HTTP_200_OK)

class Average_sales_report(viewsets.ViewSet):

    def create(self,request,*args,**kwargs):
       
        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')
        product_id = request.data.get("product_id")
        category_id = request.data.get("category_id")
        search_param = request.data.get("search_param")
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit

        month = datetime.now().month
        year = datetime.now().year
        first_day_str = str(year) +"-"+str(month)+"-1"
        first_day_obj = datetime.strptime(first_day_str,"%Y-%m-%d")
        last_day = first_day_obj + relativedelta(day=33)
        
        order_by = []
        if request.data.get("name"):
            order_by.append(request.data.get("name"))
        if request.data.get("item_no"):
            order_by.append(request.data.get("item_no"))

        orders = OrderQuantity.objects.filter(created_at__range=(first_day_obj,last_day)).aggregate(Sum("scan_quantity"))['scan_quantity__sum']
        if From_Date and To_Date:
            try:
                from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                d = timedelta(days=1)
                to_date_obj = to_date_obj + d #adding 1 day
                orders = OrderQuantity.objects.filter(created_at__range=(from_date_obj,to_date_obj)).aggregate(Sum("scan_quantity"))['scan_quantity__sum']
                
            except Exception as e:
                print(e,"---")
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid date format date Format should year-month-date'
                                },status=status.HTTP_400_BAD_REQUEST)
        
        if orders:
            orders=orders
        else:
            orders = 0

        y_axis = []  #Y Axis - Product name
        x_axis = []  #X Axis - Average sales 

        data = []

        if order_by:
            qs = Product.objects.all().order_by(*order_by)
        else:
            qs = Product.objects.all()

        if search_param:
            qs = qs.filter(
                Q(name__icontains=search_param)|
                Q(item_no__icontains=search_param))
        
        if product_id:
            try:
                qs = Product.objects.filter(id=product_id)
            except Exception as e:
                print(e,"---")
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid product!'
                                },status=status.HTTP_400_BAD_REQUEST)
        if category_id:
            try:
                qs = Product.objects.filter(category__id=category_id)
            except Exception as e:
                print(e,"---")
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid category_id!'
                                },status=status.HTTP_400_BAD_REQUEST)


        for x in qs:

            product_orders = OrderQuantity.objects.filter(product=x)
            if From_Date and To_Date: 
                from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                d = timedelta(days=1)
                to_date_obj = to_date_obj + d #adding 1 day
                product_orders = product_orders.filter(created_at__range=(from_date_obj,to_date_obj))
            
            sum_of_quanity = product_orders.aggregate(Sum("quantity"))['quantity__sum']
            order_product_sales_price = 0
            for order_obj in product_orders:
                order_product_sales_price += order_obj.quantity * order_obj.price

            y_axis.append(x.name)
            if sum_of_quanity and product_orders:
                # average = orders/sum_of_quanity
                average = order_product_sales_price/sum_of_quanity
                x_axis.append(average)
            else:
                average = 0
                x_axis.append(average)

            data.append({
                'product_id':x.id,
                'name':x.name,
                'product_item_no':x.item_no,
                'order_quanity_recieved':sum_of_quanity if sum_of_quanity else 0,
                'average': average,
                'category_id': x.category.id,
                'category_name': x.category.name,


            })

        total_record = len(data)
        list_with_pagelimit = data[start:end]
        filter_record = len(list_with_pagelimit)

        new_data = list_with_pagelimit
        
        if request.data.get("order_quantity_recieved"):
            
            if request.data.get("order_quantity_recieved")[0] == '-':
                flag = True
            else:
                flag = False
            try:
                new_data = sorted(new_data, key=lambda k: k['order_quanity_recieved'], reverse=flag)
                response = new_data

            except:
                new_data = sorted(new_data, key=lambda k: k['order_quanity_recieved'], reverse=flag)
                response = new_data

        elif request.data.get("average"):
            if request.data.get("average")[0] == '-':
                flag = True
            else:
                flag = False

            try:
                new_data = sorted(new_data, key=lambda k: k['average'], reverse=flag)
                response = new_data
            except:
                new_data = sorted(new_data, key=lambda k: k['average'], reverse=flag)
                response = new_data

        elif request.data.get("category_name"):
            if request.data.get("category_name")[0] == '-':
                flag = True
            else:
                flag = False

            try:
                new_data = sorted(new_data, key=lambda k: k['category_name'], reverse=flag)
                response = new_data
            except:
                new_data = sorted(new_data, key=lambda k: k['category_name'], reverse=flag)
                response = new_data

        chart = Average_sales_report.as_view(
				{'post': 'chart'})(request._request).data

        final_data = {
            'chart':chart['data'],
            'products' : new_data
        }
        response_data = {
            'status_code':status.HTTP_200_OK,
            'data': final_data,
            'total_record':total_record,
            'filter_record':filter_record,
            'message':"Successfull"
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(methods=['POST'],detail=False)
    def chart(self,request):

        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')
        product_id = request.data.get("product_id")
        
        month = datetime.now().month
        year = datetime.now().year
        first_day_str = str(year) +"-"+str(month)+"-1"       
        first_day_obj = datetime.strptime(first_day_str,"%Y-%m-%d")
        last_day = first_day_obj + relativedelta(day=33)
        
        orders = OrderQuantity.objects.filter(created_at__range=(first_day_obj,last_day)).aggregate(Sum("scan_quantity"))['scan_quantity__sum']
        if From_Date and To_Date:
            try:
                from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                d = timedelta(days=1)
                to_date_obj = to_date_obj + d #adding 1 day
                orders = OrderQuantity.objects.filter(created_at__range=(from_date_obj,to_date_obj)).aggregate(Sum("scan_quantity"))['scan_quantity__sum']
     
            except Exception as e:
                print(e,"---")
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid date format date Format should year-month-date'
                                },status=status.HTTP_400_BAD_REQUEST)
               
        if orders:
            orders=orders
        else:
            orders = 0

        y_axis = []  #Y Axis - Product name
        x_axis = []  #X Axis - Average sales 

        data = []

        qs = Product.objects.all()
        if product_id:
            try:
                qs = Product.objects.filter(id=product_id)
            except Exception as e:
                print(e,"---")
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid product!'
                                },status=status.HTTP_400_BAD_REQUEST)


        for x in qs:
            sum_of_quanity = OrderQuantity.objects.filter(product=x,created_at__range=(first_day_obj,last_day)).aggregate(Sum("scan_quantity"))['scan_quantity__sum']
            if From_Date and To_Date:
                try:
                    from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                    to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                    d = timedelta(days=1)
                    to_date_obj = to_date_obj + d #adding 1 day
                    sum_of_quanity = OrderQuantity.objects.filter(product=x,created_at__range=(from_date_obj,to_date_obj)).aggregate(Sum("scan_quantity"))['scan_quantity__sum']
        
                except Exception as e:
                    print(e,"---")
                    return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                    'message':'Invalid date format date Format should year-month-date'
                                    },status=status.HTTP_400_BAD_REQUEST)
            
            
            y_axis.append(x.name)
            if sum_of_quanity and orders:
                average = orders/sum_of_quanity
                x_axis.append(average)
            else:
                average = 0
                x_axis.append(average)

            data.append({
                'name':x.name,
                'order_quanity_recieved': sum_of_quanity,
                'average': average
            })

        data = {
            'x':x_axis,
            'y':y_axis
        }

        response = {
            'status_code':status.HTTP_200_OK,
            'data': data,
            'message':"Successfull"
        }
        return Response(response, status=status.HTTP_200_OK)


    @action(methods=['POST'],detail=False)
    def get_product_orders(self,request):
        
        # Requried
        product_id = request.data.get("product_id")
        # Filter
        from_date = request.data.get('from_date')
        to_date = request.data.get('to_date')
        store_id = request.data.get("store_id")
        # Pagination
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
    

        if product_id == None or product_id == '':
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"product_id is requried!"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                product_obj = Product.objects.get(id=product_id)
            except Exception as e:
                print(e,"---")
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid product!'
                                },status=status.HTTP_400_BAD_REQUEST)

        # sorting data
        sort_field = request.data.get("sort_field", "id")
        sort_type = request.data.get("sort_type", "desc")
        order_by = sort_field

        if sort_field == "id":
            order_by = "id"
        elif sort_field == "order_id":
            order_by = "order__id"
        elif sort_field == "invoice_no":
            order_by = "order__invoice_no"
        elif sort_field == "order_created_date":
            order_by = "order__created_at"
        elif sort_field == "store_name":
            order_by = "order__customer__store_name"
        elif sort_field == "store_id":
            order_by = "order__customer__id"

        elif sort_field == "order_product_name":
            order_by = "order_product_name"
        elif sort_field == "product_original_name":
            order_by = "product__name"
        elif sort_field == "product_original_price":
            order_by = "product__sale_price"
        elif sort_field == "product_order_sales_price":
            order_by = "price"

        elif sort_field == "product_order_quantity":
            order_by = "quantity"
        elif sort_field == "product_order_discount":
            order_by = "discount"
        elif sort_field == "total_of_amount":
            order_by = "product_amount"
    
        if sort_type == "desc":
            order_by = "-" + order_by
        if sort_type == "asc":
            order_by = order_by

        product_orders = OrderQuantity.objects.filter(product=product_obj) # Main query
        
        if from_date and to_date:
            try:
                from_date_obj = datetime.strptime(from_date,'%Y-%m-%d')
                to_date_obj = datetime.strptime(to_date,'%Y-%m-%d')
                d = timedelta(days=1)
                to_date_obj = to_date_obj + d #adding 1 day

            except Exception as e:
                print(e,"---")
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid date format date Format should year-month-date'
                                },status=status.HTTP_400_BAD_REQUEST)

            product_orders = product_orders.filter(created_at__range=(from_date_obj,to_date_obj))
        
        if store_id:
            try:
                store_obj = Customer.objects.get(id=store_id)
            except:
                response = {
                    'status_code' : status.HTTP_404_NOT_FOUND,
                    'message' : 'Store not found!'
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
       
            product_orders = product_orders.filter(order__customer=store_obj)

        product_orders = product_orders.order_by(order_by)
        total_record = len(product_orders)
        list_with_pagelimit = product_orders[start:end]
        filter_record = len(list_with_pagelimit)
        serializer = ProductOrdersSerializers(list_with_pagelimit, many=True)
        serializer_data = serializer.data

        response = {
            'status_code':status.HTTP_200_OK,
            'data': serializer_data,
            'total_record':total_record,
            'filter_record':filter_record,
            'msg' : 'Data fetch succesfully'   
        }
        return Response(response, status=status.HTTP_200_OK)
        
class SalesUserOrderListFilterAndSearch(APIView):
    authentication_classes = (MyCustomAuth,)

    def post(self, request,format=None):
    # try:
        user = request.user
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        
        order_id = request.data.get('order_id')

        search_param = request.data.get('search_param')
        
        created_at = request.data.get('created_at')
        invoice_no = request.data.get('invoice_no')
        due_date = request.data.get('due_date')
        amount = request.data.get('amount')
        # pass key as "status" over here 
        status_verify = request.data.get('status_verify')
        verfication_status = request.data.get('verfication_status')
        amount_recieved = request.data.get('amount_recieved')
        remaining_amount = request.data.get('remaining_amount')
        payment_status = request.data.get('payment_status')
        ordered_by = request.data.get('ordered_by')
        order_by_obj = []
        if created_at:
            order_by_obj.append(created_at)
        if invoice_no:
            order_by_obj.append(invoice_no)
        if due_date:
            order_by_obj.append(due_date)
        if amount:
            order_by_obj.append(amount)
        if status_verify:
            order_by_obj.append(status_verify)
        if verfication_status:
            order_by_obj.append(verfication_status)
        if amount_recieved:
            order_by_obj.append(amount_recieved)
        if remaining_amount:
            order_by_obj.append(remaining_amount)
        if payment_status:
            order_by_obj.append(payment_status)
        if ordered_by:
            order_by_obj.append(ordered_by)
        order_qs = Order.objects.filter(ordered_by=user)
        
        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')
        customer_id = request.data.get('customer_id')
        order_Status = request.data.get('order_status')

        if From_Date and To_Date:
            try:
                from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                d = timedelta(days=1)
                to_date_obj = to_date_obj + d #adding 1 day
                order_qs = order_qs.filter(created_at__range=(from_date_obj,to_date_obj))
     
            except Exception as e:
                print(e,"---")
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid date format date Format should year-month-date'
                                },status=status.HTTP_400_BAD_REQUEST)
        
        if customer_id:
            order_qs = order_qs.filter(customer=customer_id)

        if order_Status:
            order_qs = order_qs.filter(status__icontains=order_Status)

        if order_id:
            order_qs = order_qs.filter(id=order_id)

        if order_by_obj:
            
            order_qs = order_qs.order_by(*order_by_obj)
            
            total_record = len(order_qs)
        
        else:
            order_by = "id"

            order_qs = order_qs.order_by(order_by)
            total_record = len(order_qs)

        extra_data = {
        'page':page,
        'limit':limit,
        'start' : start,
        'end' : end,
        'order_by':order_by_obj,
        'search_param':search_param
        }   

        # searching data
        if search_param:
            
            filter_data_qs = order_qs.filter(Q(invoice_no__icontains = search_param) |
                                                Q(detail__icontains = search_param)|
                                                Q(created_at__icontains=search_param)|
                                                Q(due_date__icontains=search_param)|
                                                Q(amount__icontains=search_param)|
                                                Q(amount_recieved__icontains=search_param)|
                                                Q(remaining_amount__icontains=search_param)|
                                                Q(payment_status__icontains=search_param)|
                                                Q(status__icontains =search_param)|
                                                Q(payment_status__icontains=search_param)|
                                                Q(ordered_by__full_name__icontains=search_param) |
                                                Q(invoice_no__icontains=search_param) |
                                                Q(po_num__icontains=search_param) |
                                                Q(customer__store_name__icontains=search_param))

            total_record = len(filter_data_qs)
            list_with_pagelimit = filter_data_qs[start:end]
            filter_record = len(list_with_pagelimit)
            serializer = OrderSerializersApp(list_with_pagelimit, many=True, context={'request':request})
            serializer_data = serializer.data
        else:
            list_with_pagelimit = order_qs[start:end]
            filter_record = len(list_with_pagelimit)
            serializer = OrderSerializersApp(list_with_pagelimit, many=True, context={'request':request})
            serializer_data = serializer.data
        
    
        if len(serializer_data) == 0:
            response = {
            'status_code':status.HTTP_200_OK,
            'data': [],
            'total_record':0,
            'filter_record':0,
            'message':"No Data Found"
            }
            return Response(response, status=status.HTTP_200_OK)

        else:
            msg = 'Data fetch succesfully'   

        response = {
            'status_code':status.HTTP_200_OK,
            'data': serializer_data,
            'total_record':total_record,
            'filter_record':filter_record,
            'message':msg
        }
        return Response(response, status=status.HTTP_200_OK)
# SalesUserOrderList
# SalesUserOrderListFilterAndSearch
class SalesUserOrderList(APIView):
    authentication_classes = (MyCustomAuth,)

    def post(self, request,format=None):
        # try:
            user = request.user
            page = int(request.data.get('page',1))
            limit = int(request.data.get('limit',10))
            start = (page - 1) * limit
            end = start + limit
            
            order_id = request.data.get('order_id')

            search_param = request.data.get('search_param')
            
            created_at = request.data.get('created_at')
            invoice_no = request.data.get('invoice_no')
            due_date = request.data.get('due_date')
            amount = request.data.get('amount')
            # pass key as "status" over here 
            status_verify = request.data.get('status_verify')
            verfication_status = request.data.get('verfication_status')
            amount_recieved = request.data.get('amount_recieved')
            remaining_amount = request.data.get('remaining_amount')
            payment_status = request.data.get('payment_status')
            ordered_by = request.data.get('ordered_by')
            order_by_obj = []
            if created_at:
                order_by_obj.append(created_at)
            if invoice_no:
                order_by_obj.append(invoice_no)
            if due_date:
                order_by_obj.append(due_date)
            if amount:
                order_by_obj.append(amount)
            if status_verify:
                order_by_obj.append(status_verify)
            if verfication_status:
                order_by_obj.append(verfication_status)
            if amount_recieved:
                order_by_obj.append(amount_recieved)
            if remaining_amount:
                order_by_obj.append(remaining_amount)
            if payment_status:
                order_by_obj.append(payment_status)
            if ordered_by:
                order_by_obj.append(ordered_by)
            order_qs = Order.objects.filter(ordered_by=user).order_by('-created_at')
            if order_id:
                order_qs = order_qs.filter(id=order_id)

            if order_by_obj:
                
                order_qs = order_qs.order_by(*order_by_obj)
                
                total_record = len(order_qs)
            
            else:
                order_by = "-created_at"

                order_qs = order_qs.order_by(order_by)
                total_record = len(order_qs)

            extra_data = {
            'page':page,
            'limit':limit,
            'start' : start,
            'end' : end,
            'order_by':order_by_obj,
            'search_param':search_param
            }   

            # searching data
            if search_param:
                
                filter_data_qs = order_qs.filter(Q(invoice_no__icontains = search_param) |
                                                    Q(detail__icontains = search_param)|
                                                    Q(created_at__icontains=search_param)|
                                                    Q(due_date__icontains=search_param)|
                                                    Q(amount__icontains=search_param)|
                                                    Q(amount_recieved__icontains=search_param)|
                                                    Q(remaining_amount__icontains=search_param)|
                                                    Q(payment_status__icontains=search_param)|
                                                    Q(status__icontains =search_param)|
                                                    Q(payment_status__icontains=search_param)|
                                                    Q(ordered_by__full_name__icontains=search_param))
                total_record = len(filter_data_qs)
                list_with_pagelimit = filter_data_qs[start:end]
                filter_record = len(list_with_pagelimit)
                serializer = OrderSerializersApp(list_with_pagelimit, many=True, context={'request':request})
                serializer_data = serializer.data
            else:
                list_with_pagelimit = order_qs[start:end]
                filter_record = len(list_with_pagelimit)
                serializer = OrderSerializersApp(list_with_pagelimit, many=True, context={'request':request})
                serializer_data = serializer.data
            
        
            if len(serializer_data) == 0:
                response = {
                'status_code':status.HTTP_200_OK,
                'data': [],
                'total_record':0,
                'filter_record':0,
                'message':"No Data Found"
                }
                return Response(response, status=status.HTTP_200_OK)

            else:
                msg = 'Data fetch succesfully'   

            response = {
                'status_code':status.HTTP_200_OK,
                'data': serializer_data,
                'total_record':total_record,
                'filter_record':filter_record,
                'message':msg
            }
            return Response(response, status=status.HTTP_200_OK)

class Notify(viewsets.ViewSet):
    @action(methods=['POST'],detail=False)
    def out_of_stock(self,request,**kwargs):

        ids = request.data.get('products_id')
        ids=json.loads(ids)
        tz_pst = pytz.timezone('US/Central')
        products_name =[]
        requested_user = request.user
        for x in ids:
            products_name.append(Product.objects.get(id=x).name)
            time = datetime.now(tz=tz_pst)
            Notification.objects.create(product=Product.objects.get(id=x),date=time,warehouse_user=requested_user)
        
        products_name =', '.join(products_name)
        subject = 'Product Out of Stock'
        message = 'Following Products are out of Stock\n\n{0}'.format(products_name)
        email_form = settings.DEFAULT_FROM_EMAIL
        recipient_list = User.objects.filter(user_type='ADMIN').values_list('email',flat=True).distinct()
        recipient_list = list(recipient_list)

        send_mail(subject,message,email_form,recipient_list)

        return Response({'status_code':status.HTTP_200_OK,
                        'message':'Admin Notified successfully',
                        },status=status.HTTP_200_OK)

    @action(methods=['POST'],detail=False)
    def low_stock(self,request,**kwargs):

        ids = request.data.get('products_id')
        ids=json.loads(ids)
        
        products_name =[]
        for x in ids:
            products_name.append(Product.objects.get(id=x).name)
        
        products_name =', '.join(products_name)
        
        subject = 'Product Low Stock'
        message = 'Following Products are in Low Stock\n\n{0}'.format(products_name)
        email_form = settings.DEFAULT_FROM_EMAIL
        recipient_list = User.objects.filter(user_type='ADMIN').values_list('email',flat=True).distinct()
        recipient_list = list(recipient_list)

        send_mail(subject,message,email_form,recipient_list)

        return Response({'status_code':status.HTTP_200_OK,
                        'message':'Admin Notified successfully',
                        },status=status.HTTP_200_OK)

class Notifications(viewsets.ViewSet):
    
    @action(methods=['POST'],detail=False)
    def list_view(self,request):
        
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        
        product = request.data.get('product')
        product__item_no = request.data.get('product__item_no')

        date = request.data.get('date')
        time = request.data.get('time')
        order_by_obj = []
        if product:
            order_by_obj.append(product)
        if product__item_no:
            order_by_obj.append(product__item_no)
        if date:
            order_by_obj.append(date)
        if time:
            order_by_obj.append(time)
        
        if order_by_obj:
            qs = Notification.objects.filter(product__is_active=True).order_by(*order_by_obj)
            total_record = len(qs)
        else:
            qs = Notification.objects.filter(product__is_active=True).order_by('-date')
            total_record = len(qs)

        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')

        if From_Date and To_Date:
            try:
                from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                d = timedelta(days=1)
                to_date_obj = to_date_obj + d #adding 1 day
                qs = qs.filter(date__range=(from_date_obj,to_date_obj))

            except Exception as e:
                print(e)
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid date format date Format should year-month-date'
                                },status=status.HTTP_400_BAD_REQUEST)

        search_param = request.data.get('search_param')
        if search_param:
            qs = qs.filter(
                Q(product__name__icontains=search_param) |
                Q(product__item_no__icontains=search_param) 
            )

        total_record = len(qs)
        list_with_pagelimit = qs[start:end]
        filter_record = len(list_with_pagelimit)
        serializer = NotificationsSerializer(list_with_pagelimit, many=True, context={'request':request})
        serializer_data = serializer.data

        response = {
            'status_code':status.HTTP_200_OK,
            'data': serializer_data,
            'total_record':total_record,
            'filter_record':filter_record,
            'message':"Successfull"
        }
        return Response(response, status=status.HTTP_200_OK)

    @action(methods=['POST'],detail=False)
    def delete_view(self,request):
        notification_id = request.data.get('notification_id')
        if notification_id == None or notification_id == '':
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Notification_id is requried!"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            notify_obj = Notification.objects.get(id=notification_id)
        except Exception as e:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Invalid notification id"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if notify_obj:
            notify_obj.delete()
        else:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Invalid notification id!"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        response = {
            'status_code':status.HTTP_200_OK,
            'message':"Deleted successfully!"
        }
        return Response(response, status=status.HTTP_200_OK)



class GenratePdf(viewsets.ViewSet):

    def create(self,request):
        invoice_no = request.data.get('invoice_number')

        allOrder = Order.objects.filter(invoice_no=invoice_no)

        data = []

class UpdateOrderQty(APIView):
    authentication_classes = (MyCustomAuth,)

    def post(self, request,format=None):
    
        user = request.user

        order_id = request.data.get('order_id')
        product_id = request.data.get('product_id')
        qty = request.data.get('qty')
        
        if not order_id:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Order id is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:    
                order_obj = Order.objects.get(id=order_id)
            except Exception as e:
                response = {
                    "status_code" : status.HTTP_400_BAD_REQUEST,
                    'message' : 'Invalid order id!'
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
            if order_obj.status != "IN_PROCESS":
                response = {
                    "status_code" : status.HTTP_400_BAD_REQUEST,
                    'message' : 'Invalid order status!'
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not product_id:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Product id is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:    
                product_obj = Product.objects.get(id=product_id)
            except Exception as e:
                response = {
                    "status_code" : status.HTTP_400_BAD_REQUEST,
                    'message' : 'Invalid product id!'
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not qty:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Quntity is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

           
        qty_obj = OrderQuantity.objects.filter(product=product_obj,order=order_obj).last()
        if qty_obj is None:
                response = {
                    "status_code" : status.HTTP_400_BAD_REQUEST,
                    'message' : 'Invalid product or order id!'
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        base_price = float(product_obj.sale_price)
        discount_val = float(qty_obj.discount)
        final_price = ((float(qty) * base_price) - discount_val)  
        
        if float(qty) != 0.0:
            qty_obj.quantity=qty
            qty_obj.product_amount = final_price
            qty_obj.scan_status='SCANNED'
            qty_obj.save()
        else:
            qty_obj.delete()

        order_qty_qs = OrderQuantity.objects.filter(order=order_obj)
        total_order_amount = sum(order_qty_qs.values_list('product_amount', flat=True))
        order_obj.amount = total_order_amount
        order_obj.save()
        
        response = {
            "status_code" : status.HTTP_200_OK,
            'message' : 'Data updated!'
        }
        return Response(response, status=status.HTTP_200_OK)

class AdminAgeingReport(APIView):
    authentication_classes = (MyCustomAuth,)

    def post(self, request,format=None):
    
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        
        search_value = request.data.get('search_value')

        # filtering data
        invoice_no = request.data.get('invoice_no')
        from_order_date = request.data.get('from_order_date')
        to_order_date = request.data.get('to_order_date')
        from_due_date = request.data.get('from_due_date')
        to_due_date = request.data.get('to_due_date')
        customer_or_store = request.data.get('customer_or_store')
        
        # sorting data
        sort_field = request.data.get("sort_field", "id")
        sort_type = request.data.get("sort_type", "desc")
        order_by = sort_field

        if sort_field == "invoice_no":
            order_by = "invoice_no"
        elif sort_field == "order_date":
            order_by = "created_at"
        elif sort_field == "due_date":
            order_by = "due_date"
        elif sort_field == "customer_name":
            order_by = "customer__full_name"
        elif sort_field == "store_name":
            order_by = "customer__store_name"
        elif sort_field == "open_balance":
            order_by = "remaining_amount"
        elif sort_field == "ageing":
            order_by = "ageing"
        elif sort_field == "total_amount":
            order_by = "amount"
        elif sort_field == "amount_recieved":
            order_by = "amount_recieved"
        elif sort_field == "open_balance":
            order_by = "remaining_amount"
        elif sort_field == "po_num":
            order_by = "po_num"
        elif sort_field == "term":
            order_by = "term"


        if sort_type == "desc":
            order_by = "-" + order_by
        if sort_type == "asc":
            order_by = order_by

        # Data fetch - Main Condition
        today = datetime.now().date()
         # order_qs = Order.objects.filter(due_date__lt=today,remaining_amount__gt=0.0).order_by(order_by)
        order_qs = Order.objects.filter(payment_status__in = ['PARTIAL','NOT_PAID'],remaining_amount__gt=0.0).order_by(order_by)

        # Refreshing data to get aging-value
        for obj in order_qs:
            old_data = obj.term
            obj.term = old_data
            obj.save()

        order_qs = order_qs.exclude(ageing__lt = 1)
        # filtering data
        if from_order_date and to_order_date:
            try:
                order_from_date_obj = datetime.strptime(from_order_date,'%Y-%m-%d')
                order_to_date_obj = datetime.strptime(to_order_date,'%Y-%m-%d')
                d = timedelta(days=1)
                order_to_date_obj = order_to_date_obj + d #adding 1 day
                order_qs = order_qs.filter(created_at__range=(order_from_date_obj,order_to_date_obj))
     
            except Exception as e:
                print(e,"---")
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid date format date Format should year-month-date'
                                },status=status.HTTP_400_BAD_REQUEST)
        
        if from_due_date and to_due_date:
            try:
                due_from_date_obj = datetime.strptime(from_due_date,'%Y-%m-%d')
                due_to_date_obj = datetime.strptime(to_due_date,'%Y-%m-%d')
                d = timedelta(days=1)
                due_to_date_obj = due_to_date_obj + d #adding 1 day
                order_qs = order_qs.filter(due_date__range=(due_from_date_obj,due_to_date_obj))
     
            except Exception as e:
                print(e,"---")
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid date format date Format should year-month-date'
                                },status=status.HTTP_400_BAD_REQUEST)
        
        if invoice_no:
            order_qs = order_qs.filter(invoice_no=invoice_no)
        
        if customer_or_store:
            order_qs = order_qs.filter( Q(customer__full_name=customer_or_store) | 
                                        Q(customer__store_name=customer_or_store))


        # searching data
        if search_value:
            order_qs = order_qs.filter( Q(created_at__icontains=search_value)|
                                        Q(invoice_no__icontains=search_value)|
                                        Q(po_num__icontains=search_value)|
                                        Q(term__icontains=search_value)|
                                        Q(due_date__icontains=search_value)|
                                        Q(amount__icontains=search_value)|
                                        Q(amount_recieved__icontains=search_value)|
                                        Q(ordered_by__full_name__icontains=search_value)|
                                        Q(customer__full_name__icontains=search_value) |
                                        Q(remaining_amount__icontains=search_value) |
                                        Q(ageing__icontains=search_value)

                                        )

        total_record = len(order_qs)
        list_with_pagelimit = order_qs[start:end]
        filter_record = len(list_with_pagelimit)
        serializer = AgeingReportNewSerializers(list_with_pagelimit, many=True, context={'request':request})
        serializer_data = serializer.data
        
        total_open_balance = sum(order_qs.values_list('remaining_amount', flat=True))
        summary = {
            'total_open_balance':total_open_balance
        }
        response = {
            'status_code':status.HTTP_200_OK,
            'data': serializer_data,
            'summary':summary,
            'total_record':total_record,
            'filter_record':filter_record,
            'message':"Successfull"
        }
        return Response(response, status=status.HTTP_200_OK)

class NewAdminAgeingReport(APIView):
    authentication_classes = (MyCustomAuth,)

    def post(self, request,format=None):
    
        # filtering data
        customer_or_store = request.data.get('customer_or_store')
        
        # Data fetch - Main Condition
        all_data = Customer.objects.all()
        data_list = []
        for obj in all_data:
            order_count = Order.objects.filter(customer=obj,remaining_amount__gt=0.0).count()
            if order_count != 0:
                data_list.append(obj.id)

        data_qs = Customer.objects.filter(id__in=data_list).order_by('store_name')

        # filtering data
        if customer_or_store:
            data_qs = data_qs.filter( Q(full_name=customer_or_store) | 
                                        Q(store_name=customer_or_store))

        total_record = len(data_qs)
        serializer = AdminAgeingReportSerializers(data_qs, many=True, context={'request':request})
        serializer_data = list(serializer.data)
        for data in serializer_data:
            if len(data['invoice_data']) == 0:
                serializer_data.remove(data)

        main_total = sum([float(i['total_of_open_balance']) for i in serializer_data])
        report_date = datetime.now().date()
        report_time = datetime.now().time()
        summary = {
            'report_date' : report_date,
            'report_time': report_time,
            'main_total':"%.2f" % round(main_total, 2)
        }
        
        response = {
            'status_code':status.HTTP_200_OK,
            'data': serializer_data,
            'summary':summary,
            'total_record':total_record,
            'message':"Successfull"
        }
        return Response(response, status=status.HTTP_200_OK)


class UpdateDeliveryStatus(APIView):
    authentication_classes = (MyCustomAuth,)
    def post(self, request, id, format=None):
        try:
            order_obj = Order.objects.get(id=id)
        except:
            response = {
                'status_code' : status.HTTP_404_NOT_FOUND,
                'message' : 'Order not found!'
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        flag_email = request.data.get('flag_email')
        order_obj.delivered_status = True
        order_obj.delivery_date = datetime.now().date()
        order_obj.save()

        
        if not order_obj.invoice_pdf:
            return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                            'message':'Please download invoice first.'
                            },status=status.HTTP_400_BAD_REQUEST)
        else:
            pdf_url = request.build_absolute_uri(order_obj.invoice_pdf.url)

        filename = "media/" + order_obj.invoice_pdf.name
        body = 'Please check invoice.\n\nInvoice No : {0}\nInvoice Amount : ${1}\nDue Date : {2}\nPlease click to below link to download sales-order PDF:\n{3}'.format(order_obj.invoice_no,"%.2f" % round(order_obj.amount, 2),order_obj.due_date.strftime('%m-%d-%Y'),pdf_url)
        message = MIMEMultipart()
        message['subject']= order_obj.customer.store_name + ' - Invoice No ' + order_obj.invoice_no
       
        message.attach(MIMEText(body, "plain"))
        binary_pdf = open(filename, 'rb')
        payload = MIMEBase('application/pdf', 'octate-stream', Name=filename + '.pdf')
        payload.set_payload((binary_pdf).read())
        
        # enconding the binary into base64
        encoders.encode_base64(payload)
        
        # add header with pdf name
        payload.add_header('Content-Decomposition', 'attachment', filename=filename)
        message.attach(payload)
        # Add attachment to message and convert message to string
        # message.attach(part)
        text = message.as_string()
        email_form = settings.EMAIL_HOST_USER
        password = settings.EMAIL_HOST_PASSWORD
        recipient_list = User.objects.filter(user_type='ADMIN').values_list('email',flat=True).distinct()
        recipient_list = list(recipient_list)
        recipient_list.append(order_obj.ordered_by.email)
        if flag_email in [True,"true","True"]:
            recipient_list.append(order_obj.customer.email)

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_form, password)
            server.sendmail(email_form, recipient_list, text)

        response = {
            'status_code' : status.HTTP_200_OK,
            'message': 'Status updated succesfully',
        }
        
        return Response(response, status=status.HTTP_200_OK)

class StoreList(APIView):
    authentication_classes = (MyCustomAuth,)
    def get(self, request, format=None):

        data_qs = Customer.objects.all().order_by(Lower('store_name'))
        serializer = StoreSerializers(data_qs, many=True, context={'request':request})
        serializer_data = serializer.data

        response = {
            'status_code' : status.HTTP_200_OK,
            'message': 'Data fetch succesfully',
            'data':serializer_data
        }
        
        return Response(response, status=status.HTTP_200_OK)

class CmNoList(APIView):

    def get(self, request, format=None):

        data_qs = CreditMemo.objects.all().values_list('cm_no',flat=True)
 
        response = {
            'status_code' : status.HTTP_200_OK,
            'message': 'Data fetch succesfully',
            'data':data_qs
        }
        
        return Response(response, status=status.HTTP_200_OK)

class InvoiceNoList(APIView):

    def get(self, request, format=None):

        data_qs = Order.objects.exclude(invoice_no__isnull=True).exclude(invoice_no__exact='').values_list('invoice_no',flat=True)
 
        response = {
            'status_code' : status.HTTP_200_OK,
            'message': 'Data fetch succesfully',
            'data':data_qs
        }
        
        return Response(response, status=status.HTTP_200_OK)

class average_onhand_product(viewsets.ViewSet):

    def create(self,request,*args,**kwargs):
       
        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')
        product_id = request.data.get("product_id")
        search_param = request.data.get("search_param")
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit

        month = datetime.now().month
        year = datetime.now().year
        first_day_str = str(year) +"-"+str(month)+"-1"
        first_day_obj = datetime.strptime(first_day_str,"%Y-%m-%d")
        last_day = first_day_obj + relativedelta(day=33)
        
        order_by = []
        if request.data.get("name"):
            order_by.append(request.data.get("name"))
        if request.data.get("item_no"):
            order_by.append(request.data.get("item_no"))

        orders = OrderQuantity.objects.filter(created_at__range=(first_day_obj,last_day)).aggregate(Sum("quantity"))['quantity__sum']
        if From_Date and To_Date:
            try:
                from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                d = timedelta(days=1)
                to_date_obj = to_date_obj + d #adding 1 day
                orders = OrderQuantity.objects.filter(created_at__range=(from_date_obj,to_date_obj)).aggregate(Sum("quantity"))['quantity__sum']
                
            except Exception as e:
                print(e,"---")
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid date format date Format should year-month-date'
                                },status=status.HTTP_400_BAD_REQUEST)
        
        if orders:
            orders=orders
        else:
            orders = 0

        y_axis = []  #Y Axis - Product name
        x_axis = []  #X Axis - Average sales 

        data = []

        if order_by:
            qs = Product.objects.all().order_by(*order_by)
        else:
            qs = Product.objects.all()

        if search_param:
            qs = qs.filter(
                Q(name__icontains=search_param)|
                Q(item_no__icontains=search_param))
        
        if product_id:
            try:
                qs = Product.objects.filter(id=product_id)
            except Exception as e:
                print(e,"---")
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid product!'
                                },status=status.HTTP_400_BAD_REQUEST)


        for x in qs:
            sum_of_quanity = OrderQuantity.objects.filter(product=x,created_at__range=(first_day_obj,last_day)).aggregate(Sum("quantity"))['quantity__sum']
            
            if From_Date and To_Date:
                try:
                    from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                    to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                    d = timedelta(days=1)
                    to_date_obj = to_date_obj + d #adding 1 day
                    sum_of_quanity = OrderQuantity.objects.filter(product=x,created_at__range=(from_date_obj,to_date_obj)).aggregate(Sum("quantity"))['quantity__sum']
                    
                except Exception as e:
                    print(e,"---")
                    return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                    'message':'Invalid date format date Format should year-month-date'
                                    },status=status.HTTP_400_BAD_REQUEST)
            
            
            
            y_axis.append(x.name)
            if sum_of_quanity and orders:
                average = orders/sum_of_quanity
                x_axis.append(average)
            else:
                average = 0
                x_axis.append(average)

            data.append({
                'product_id':x.id,
                'name':x.name,
                'product_item_no':x.item_no,
                'order_quanity_recieved':sum_of_quanity if sum_of_quanity else 0,
                'average': average
            })

        total_record = len(data)
        list_with_pagelimit = data[start:end]
        filter_record = len(list_with_pagelimit)

        new_data = list_with_pagelimit
        
        if request.data.get("order_quantity_recieved"):
            
            if request.data.get("order_quantity_recieved")[0] == '-':
                flag = True
            else:
                flag = False
            try:
                new_data = sorted(new_data, key=lambda k: k['order_quanity_recieved'], reverse=flag)
                response = new_data

            except:
                new_data = sorted(new_data, key=lambda k: k['order_quanity_recieved'], reverse=flag)
                response = new_data

        elif request.data.get("average"):
            if request.data.get("average")[0] == '-':
                flag = True
            else:
                flag = False

            try:
                new_data = sorted(new_data, key=lambda k: k['average'], reverse=flag)
                response = new_data
            except:
                new_data = sorted(new_data, key=lambda k: k['average'], reverse=flag)
                response = new_data


        chart = Average_sales_report.as_view(
				{'post': 'chart'})(request._request).data

        final_data = {
            'chart':chart['data'],
            'products' : new_data
        }
        response_data = {
            'status_code':status.HTTP_200_OK,
            'data': final_data,
            'total_record':total_record,
            'filter_record':filter_record,
            'message':"Successfull"
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(methods=['POST'],detail=False)
    def chart(self,request):

        From_Date = request.data.get('from_date')
        To_Date = request.data.get('to_date')
        product_id = request.data.get("product_id")
        
        month = datetime.now().month
        year = datetime.now().year
        first_day_str = str(year) +"-"+str(month)+"-1"       
        first_day_obj = datetime.strptime(first_day_str,"%Y-%m-%d")
        last_day = first_day_obj + relativedelta(day=33)
        
        orders = OrderQuantity.objects.filter(created_at__range=(first_day_obj,last_day)).aggregate(Sum("quantity"))['quantity__sum']
        if From_Date and To_Date:
            try:
                from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                d = timedelta(days=1)
                to_date_obj = to_date_obj + d #adding 1 day
                orders = OrderQuantity.objects.filter(created_at__range=(from_date_obj,to_date_obj)).aggregate(Sum("quantity"))['quantity__sum']
     
            except Exception as e:
                print(e,"---")
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid date format date Format should year-month-date'
                                },status=status.HTTP_400_BAD_REQUEST)
               
        if orders:
            orders=orders
        else:
            orders = 0

        y_axis = []  #Y Axis - Product name
        x_axis = []  #X Axis - Average sales 

        data = []

        qs = Product.objects.all()
        if product_id:
            try:
                qs = Product.objects.filter(id=product_id)
            except Exception as e:
                print(e,"---")
                return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                'message':'Invalid product!'
                                },status=status.HTTP_400_BAD_REQUEST)


        for x in qs:
            sum_of_quanity = OrderQuantity.objects.filter(product=x,created_at__range=(first_day_obj,last_day)).aggregate(Sum("quantity"))['quantity__sum']
            if From_Date and To_Date:
                try:
                    from_date_obj = datetime.strptime(From_Date,'%Y-%m-%d')
                    to_date_obj = datetime.strptime(To_Date,'%Y-%m-%d')
                    d = timedelta(days=1)
                    to_date_obj = to_date_obj + d #adding 1 day
                    sum_of_quanity = OrderQuantity.objects.filter(product=x,created_at__range=(from_date_obj,to_date_obj)).aggregate(Sum("quantity"))['quantity__sum']
        
                except Exception as e:
                    print(e,"---")
                    return Response({'status_code':status.HTTP_400_BAD_REQUEST,
                                    'message':'Invalid date format date Format should year-month-date'
                                    },status=status.HTTP_400_BAD_REQUEST)
            
            
            y_axis.append(x.name)
            if sum_of_quanity and orders:
                average = orders/sum_of_quanity
                x_axis.append(average)
            else:
                average = 0
                x_axis.append(average)

            data.append({
                'name':x.name,
                'order_quanity_recieved': sum_of_quanity,
                'average': average
            })

        data = {
            'x':x_axis,
            'y':y_axis
        }

        response = {
            'status_code':status.HTTP_200_OK,
            'data': data,
            'message':"Successfull"
        }
        return Response(response, status=status.HTTP_200_OK)

class ProductOnlyList(APIView):

    def get(self, request, format=None):
        data_qs = Product.objects.all().order_by('name')
        serializer = ProductListSerializers(data_qs, many=True)
        serializer_data = serializer.data
        response = {
            'status_code' : status.HTTP_200_OK,
            'message': 'Data fetch succesfully',
            'data':serializer_data
        }
        
        return Response(response, status=status.HTTP_200_OK)

class ScanAllproducts(APIView):
    authentication_classes = (MyCustomAuth,)
    def post(self, request, format=None):
        try:
            order_id = request.data.get('order_id')
            order_obj = Order.objects.get(id=order_id)
        except:
            response = {
                'status_code' : status.HTTP_404_NOT_FOUND,
                'message' : 'Order not found!'
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        order_quantity_qs = OrderQuantity.objects.filter(order=order_obj).exclude(remaining_scan_quantity=0.0)
        if len(order_quantity_qs) == 0:
            response = {
                        'status_code':status.HTTP_200_OK,
                        'message' : "Order Already Scanned.",
                    }
            return Response(response, status=status.HTTP_200_OK)

        for order_quantity in order_quantity_qs:
            quantity_to_scan = order_quantity.remaining_scan_quantity
            product_obj = Product.objects.filter(id=order_quantity.product.id).first()
            if quantity_to_scan <= product_obj.available_quantity:
                try:
                    order_quantity.scan_status = 'SCANNED'
                    order_quantity.scan_quantity +=  quantity_to_scan
                    product_obj.available_quantity -= quantity_to_scan 
                    order_quantity.remaining_scan_quantity -= quantity_to_scan
                    product_obj.save()
                    order_quantity.save()

                    response = {
                        'status_code':status.HTTP_200_OK,
                        'message' : "Product Scanned Successfully",
                    }

                    if product_obj.available_quantity <= product_obj.low_stock_qauntity:
                        product_obj.low_stock = True
                    
                    if product_obj.available_quantity == 0:
                        product_obj.in_stock = False

                    product_obj.save()
                    if order_quantity.scan_quantity != order_quantity.quantity:
                        order_quantity.scan_status = 'PARTIALLY_SCANNED'
                        order_quantity.save()
                        response.update({
                            'data': {
                                'remaining_quanity':'{0} Packets Scanning left'.format(order_quantity.quantity - order_quantity.scan_quantity)
                            }
                        })
                except Exception as e:
                    response = {
                        'status_code':status.HTTP_400_BAD_REQUEST,
                        'message':"Something went wrong!",
                        'error':str(e)
                        }
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

            else:
                new_scanned_quantity = product_obj.available_quantity
                order_quantity.scan_quantity += new_scanned_quantity
                order_quantity.remaining_scan_quantity -= new_scanned_quantity
                order_quantity.scan_status = 'PARTIALLY_SCANNED'
                order_quantity.save()
                product_obj.available_quantity -= new_scanned_quantity
                response = None
                
                
                if product_obj.available_quantity <= product_obj.low_stock_qauntity:
                    product_obj.low_stock = True
                    response = {
                        'status_code':status.HTTP_200_OK,
                        'message' : "Inform Admin About Low Stock",
                    }

                if product_obj.available_quantity == 0:
                    product_obj.in_stock = False
                    response = {
                        'status_code':status.HTTP_200_OK,
                        'message' : "Inform Admin About Out of Stock",
                    }
                if not response:
                    response = {
                        'status_code':status.HTTP_200_OK,
                        'message' : "Product scanned Partially",
                        }
                product_obj.save()
                response.update({
                    'data': {
                        'remaining_quanity':'{0} Packets Scanning left'.format(order_quantity.quantity - order_quantity.scan_quantity)
                    }
                })

        if order_obj.status=='OPEN':
            if OrderQuantity.objects.filter(order=order_obj).exclude(scan_status='SCANNED').exists():
                order_obj.status = 'IN_PROCESS'
            else:
                order_obj.status = 'COMPLETED'
        elif order_obj.status=='IN_PROCESS':
            order_obj.status = 'IN_PROCESS'


        order_obj.save()
        return Response(response, status=status.HTTP_200_OK)

class VerficationScanAllproducts(APIView):
    authentication_classes = (MyCustomAuth,)
    def post(self, request, format=None):
        try:
            order_id = request.data.get('order_id')
            order_obj = Order.objects.get(id=order_id)
        except:
            response = {
                'status_code' : status.HTTP_404_NOT_FOUND,
                'message' : 'Order not found!'
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        order_quantity_qs = OrderQuantity.objects.filter(order=order_obj).exclude(remaining_verfication_scan_quantity=0.0)
        if len(order_quantity_qs) == 0:
            response = {
                        'status_code':status.HTTP_200_OK,
                        'message' : "Order Already Scanned.",
                    }
            return Response(response, status=status.HTTP_200_OK)

        for order_quantity in order_quantity_qs:
            quantity_to_scan = order_quantity.remaining_verfication_scan_quantity
             
            order_quantity.verfication_scan_status = 'SCANNED'
            order_quantity.verfication_scan_quantity +=  quantity_to_scan
            order_quantity.remaining_verfication_scan_quantity -= quantity_to_scan
            order_quantity.save()

        response = {
                        'status_code':status.HTTP_200_OK,
                        'message' : "Product Scanned Successfully",
                    }
        return Response(response, status=status.HTTP_200_OK)

class SalesPDF(APIView):

    def get(self, request, id, format=None):
        try:
            order_obj = Order.objects.get(id=id)
        except:
            response = {
                'status_code' : status.HTTP_404_NOT_FOUND,
                'message' : 'Order not found!'
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        data = {
            'pdf_url':request.build_absolute_uri(order_obj.sales_pdf.url)
        }

        response = {
            'message':"PDF is retrieved successfully.", 
            'status':status.HTTP_200_OK, 
            'data': data
        }

        return Response(response, status.HTTP_200_OK)


class SalesProductList(APIView):
    authentication_classes = (MyCustomAuth,)

    def post(self, request,format=None):
    
        page = int(request.data.get('page',1))
        limit = int(request.data.get('limit',10))
        start = (page - 1) * limit
        end = start + limit
        
        search_value = request.data.get('search_value')
        
        # Data fetch - Main Condition
        product_qs = Product.objects.all().order_by('category__name',Lower('name'))
        total_record = len(product_qs)
        
        # searching data
        if search_value:
            product_qs = product_qs.filter( Q(name__icontains=search_value)|
                                        Q(category__name__icontains=search_value) |
                                        Q(item_no__icontains=search_value) )
            
            filter_record = len(product_qs)
            list_with_pagelimit = product_qs[start:end]
            serializer = SalesProductListSerializers(list_with_pagelimit, many=True)
            serializer_data = serializer.data

        else:
            list_with_pagelimit = product_qs[start:end]
            filter_record = len(list_with_pagelimit)
            serializer = SalesProductListSerializers(list_with_pagelimit, many=True)
            serializer_data = serializer.data
                
        response = {
            'status_code' : status.HTTP_200_OK,
            'message': 'Data fetch succesfully',
            'data':serializer_data,
            'total_record':total_record,
            'filter_record':filter_record,
        }
        
        return Response(response, status=status.HTTP_200_OK)                                

class CreditMemoPDF(viewsets.ViewSet):
    def create(self,request,*args,**kwargs):        
        cm_no = request.data.get('cm_no')
        data_obj = CreditMemo.objects.filter(cm_no=cm_no).first()
        
        if not data_obj:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Cm_no is Invalid",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not data_obj.credit_memo_pdf:
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"No PDF attached with this credit memo.",
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        data = {}
        data['pdf_url'] = request.build_absolute_uri(data_obj.credit_memo_pdf.url)

        response = {'message':"PDF is retrieved successfully.", 'status':status.HTTP_200_OK, 'data': data}

        return Response(response, status.HTTP_200_OK)