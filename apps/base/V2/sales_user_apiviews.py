from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.decorators import permission_classes,authentication_classes

from apps.base.models import *
from apps.base.authentication import *
from .base_apiviews import CustomerGetView
from .serializers import *


# @authentication_classes([])
class CreateCustomerView(APIView):
    authentication_classes = (MyCustomAuth,)

    def post(self, request, format=None):
        store_name = request.data.get('store_name')
        fullname = request.data.get('fullname')
        phone_no = request.data.get('phone_no')
        email = request.data.get('email')
        sales_person = request.data.get('sales_person')

        billing_address = request.data.get('billing_address')
        billing_city = request.data.get('billing_city')
        billing_state = request.data.get('billing_state')
        billing_country = request.data.get('billing_country')
        billing_zipcode = request.data.get('billing_zipcode')

        shipping_address_same = request.data.get('shipping_address_same',"True")

        shipping_address = request.data.get('shipping_address')
        shipping_city = request.data.get('shipping_city')
        shipping_state = request.data.get('shipping_state')
        shipping_country = request.data.get('shipping_country')
        shipping_zipcode = request.data.get('shipping_zipcode')

        minumum_threshold = request.data.get('minumum_threshold')
        maximum_threshold = request.data.get('maximum_threshold')

        sales_tax_id = request.data.get('sales_tax_id')
        sales_tax_image = request.data.get('sales_tax_image')
        agree_terms_and_condition = request.data.get('terms_and_condition')

        if not store_name:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Store name is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not fullname:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Fullname is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not phone_no:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Phone number is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not email:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Email is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not sales_person:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Sales person is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                user_obj =  User.objects.get(user_type="SALESPERSON",id=sales_person)
            except Exception as e:
                response = {
                    "status_code" : status.HTTP_400_BAD_REQUEST,
                    'message' : 'Sales person does not exist!'
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)


        if not billing_address:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Billing address is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


        if not minumum_threshold:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : "Minimum threshold is required!"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not maximum_threshold:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : "Maximum threshold is required!"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


        if shipping_address_same == 'True':
            billing_address_obj = Billing_Address.objects.create(address=billing_address, city=billing_city, state=billing_state, country=billing_country, zipcode=billing_zipcode)
            shipping_address_obj = ShippingAddress.objects.create(address=billing_address, city=billing_city, state=billing_state, country=billing_country, zipcode=billing_zipcode)
        
        elif shipping_address_same == 'False':
            billing_address_obj = Billing_Address.objects.create(address=billing_address, city=billing_city, state=billing_state, country=billing_country, zipcode=billing_zipcode)
            shipping_address_obj = ShippingAddress.objects.create(address=shipping_address, city=shipping_city, state=shipping_state, country=shipping_country, zipcode=shipping_zipcode)


        account_num = phone_no[-7:]
        customer_obj = Customer.objects.create(store_name=store_name, shipping_address=shipping_address_obj, 
                                billing_address=billing_address_obj, both_address_same=shipping_address_same,
                                min_threshold=minumum_threshold, max_threshold=maximum_threshold,
                                sales_tax_id=sales_tax_id, sales_tax_image=sales_tax_image, terms=agree_terms_and_condition, 
                                full_name=fullname, email=email, phone=phone_no,sales_person=user_obj,account_num=account_num)
        
        serializer = CustomerSerializers(customer_obj)
        response = {
                "status_code" : status.HTTP_200_OK,
                'message' : "Customer created!",
                
            }
        return Response(response, status=status.HTTP_200_OK)

class CreateCustomerAppView(APIView):
    authentication_classes = (MyCustomAuth,)

    def post(self, request, format=None):
        store_name = request.data.get('store_name')
        fullname = request.data.get('fullname')
        phone_no = request.data.get('phone_no')
        email = request.data.get('email')

        billing_address = request.data.get('billing_address')
        billing_city = request.data.get('billing_city')
        billing_state = request.data.get('billing_state')
        billing_country = request.data.get('billing_country')
        billing_zipcode = request.data.get('billing_zipcode')

        shipping_address_same = request.data.get('shipping_address_same','True')
        shipping_address = request.data.get('shipping_address')
        shipping_city = request.data.get('shipping_city')
        shipping_state = request.data.get('shipping_state')
        shipping_country = request.data.get('shipping_country')
        shipping_zipcode = request.data.get('shipping_zipcode')

        minumum_threshold = request.data.get('minumum_threshold',0)
        if minumum_threshold == "":
            minumum_threshold = 0
        
        maximum_threshold = request.data.get('maximum_threshold',0)
        if maximum_threshold == "":
            maximum_threshold = 0
            
        sales_tax_id = request.data.get('sales_tax_id')
        sales_tax_image = request.data.get('sales_tax_image')
        if sales_tax_image == 'null':
            sales_tax_image = None
            
        agree_terms_and_condition = request.data.get('terms_and_condition')


        if not fullname:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Fullname is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not phone_no:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Phone number is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not email:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Email is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not billing_address:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Billing address is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


        if request.user.user_type != 'SALESPERSON':
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'User is not sales person!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if shipping_address_same == "True":
            billing_address_obj = Billing_Address.objects.create(address=billing_address, city=billing_city, state=billing_state, country=billing_country, zipcode=billing_zipcode)
            shipping_address_obj = ShippingAddress.objects.create(address=billing_address, city=billing_city, state=billing_state, country=billing_country, zipcode=billing_zipcode)
        
        else:
            billing_address_obj = Billing_Address.objects.create(address=billing_address, city=billing_city, state=billing_state, country=billing_country, zipcode=billing_zipcode)
            shipping_address_obj = ShippingAddress.objects.create(address=shipping_address, city=shipping_city, state=shipping_state, country=shipping_country, zipcode=shipping_zipcode)
            if not shipping_address:
                response = {
                    "status_code" : status.HTTP_400_BAD_REQUEST,
                    'message' : 'Shipping address is required!'
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        

            if not shipping_state:
                response = {
                    "status_code" : status.HTTP_400_BAD_REQUEST,
                    'message' : 'Shipping state is required!'
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            if not shipping_country:
                response = {
                    "status_code" : status.HTTP_400_BAD_REQUEST,
                    'message' : 'Shipping country is required!'
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)


        account_num = phone_no[-7:]
        sales_person= request.user
        customer_obj = Customer.objects.create(store_name=store_name, shipping_address=shipping_address_obj, 
                                billing_address=billing_address_obj, both_address_same=shipping_address_same,
                                min_threshold=minumum_threshold, max_threshold=maximum_threshold,
                                sales_tax_id=sales_tax_id, sales_tax_image=sales_tax_image, terms=agree_terms_and_condition, 
                                full_name=fullname, email=email, phone=phone_no,account_num=account_num,sales_person=sales_person)
        
        serializer = CustomerSerializers(customer_obj)
        response = {
                "status_code" : status.HTTP_200_OK,
                'message' : "Customer created!",
                
            }
        return Response(response, status=status.HTTP_200_OK)

class EditCustomerAppView(APIView):
    authentication_classes = (MyCustomAuth,)

    def put(self, request,id=None, format=None):
        store_name = request.data.get('store_name')
        fullname = request.data.get('full_name')
        phone_no = request.data.get('phone_no')
        email = request.data.get('email')

        billing_address = request.data.get('billing_address')
        billing_city = request.data.get('billing_city')
        billing_state = request.data.get('billing_state')
        billing_country = request.data.get('billing_country')
        billing_zipcode = request.data.get('billing_zipcode')

        shipping_address_same = request.data.get('shipping_address_same',True)
        shipping_address = request.data.get('shipping_address')
        shipping_city = request.data.get('shipping_city')
        shipping_state = request.data.get('shipping_state')
        shipping_country = request.data.get('shipping_country')
        shipping_zipcode = request.data.get('shipping_zipcode')

        minumum_threshold = request.data.get('minumum_threshold',0)
        maximum_threshold = request.data.get('maximum_threshold',0)

        sales_tax_id = request.data.get('sales_tax_id')
        sales_tax_image = request.data.get('sales_tax_image')
        agree_terms_and_condition = request.data.get('terms_and_condition')

        customer_obj = Customer.objects.filter(id=id).first()
        if not customer_obj:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Invalid CustomerID'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not fullname:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Fullname is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not phone_no:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Phone number is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not email:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Email is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if not billing_address:
            response = {
                "status_code" : status.HTTP_400_BAD_REQUEST,
                'message' : 'Billing address is required!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        new_data = request.data.copy()
        new_data.pop('shipping_address')
        new_data.pop('billing_address')

        if shipping_address_same:
            if customer_obj.billing_address:
                customer_obj.billing_address.address=billing_address
                customer_obj.billing_address.city=billing_city
                customer_obj.billing_address.state=billing_state
                customer_obj.billing_address.country=billing_country
                customer_obj.billing_address.zipcode=billing_zipcode
                customer_obj.billing_address.save()
            else:
                billing_obj = Billing_Address.objects.create(address=billing_address, city=billing_city, state=billing_state, country=billing_country, zipcode=billing_zipcode)
                customer_obj.billing_address = billing_obj
                customer_obj.save()

            if customer_obj.shipping_address:
                customer_obj.shipping_address.address=billing_address
                customer_obj.shipping_address.city=billing_city
                customer_obj.shipping_address.state=billing_state
                customer_obj.shipping_address.country=billing_country
                customer_obj.shipping_address.zipcode=billing_zipcode
                customer_obj.shipping_address.save()
            else:
                shipping_address_obj = ShippingAddress.objects.create(address=billing_address, city=billing_city, state=billing_state, country=billing_country, zipcode=billing_zipcode)
                customer_obj.shipping_address = shipping_address_obj
                customer_obj.save()
                
        else:
            if not shipping_address:
                response = {
                    "status_code" : status.HTTP_400_BAD_REQUEST,
                    'message' : 'Shipping address is required!'
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
            if customer_obj.billing_address:
                customer_obj.billing_address.address=billing_address
                customer_obj.billing_address.city=billing_city
                customer_obj.billing_address.state=billing_state
                customer_obj.billing_address.country=billing_country
                customer_obj.billing_address.zipcode=billing_zipcode
                customer_obj.billing_address.save()
            else:
                billing_obj = Billing_Address.objects.create(address=billing_address, city=billing_city, state=billing_state, country=billing_country, zipcode=billing_zipcode)
                customer_obj.billing_address = billing_obj
                customer_obj.save()

            if customer_obj.shipping_address:
                customer_obj.shipping_address.address=shipping_address
                customer_obj.shipping_address.city=shipping_city
                customer_obj.shipping_address.state=shipping_state
                customer_obj.shipping_address.country=shipping_country
                customer_obj.shipping_address.zipcode=shipping_zipcode
                customer_obj.shipping_address.save()
            else:
                shipping_address_obj = ShippingAddress.objects.create(address=shipping_address, city=shipping_city, state=shipping_state, country=shipping_country, zipcode=shipping_zipcode)
                customer_obj.shipping_address = shipping_address_obj
                customer_obj.save()
            
        serializer = CustomerSerializers(customer_obj,data=new_data,partial=True)
        if serializer.is_valid(raise_exception=True):
            response = {
                    "status_code" : status.HTTP_200_OK,
                    'message' : "Customer Updated!",
                    
                }
            return Response(response, status=status.HTTP_200_OK)

# salesuser manageaccount(edit profile api)
# @authentication_classes([])
class CustomerEditProfile(APIView):
    authentication_classes = (MyCustomAuth,)
    
    def put(self, request, id, format=None):
        try:
            customer_obj = Customer.objects.get(id=id)
        except:
            response = {
                "status_code" : status.HTTP_404_NOT_FOUND,
                'message' : 'Customer not found!'
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        
        storename = request.data.get("storename")
        fullname = request.data.get("full_name")
        phone_no = request.data.get('phone')
        email = request.data.get('email')
        billing_address = request.data.get("billing_address")
        billing_city = request.data.get("billing_city")
        billing_state = request.data.get("billing_state")
        billing_country = request.data.get("billing_country")
        billing_zipcode = request.data.get("billing_zipcode")
        shipping_address = request.data.get("shipping_address")
        shipping_city = request.data.get("shipping_city")
        shipping_state = request.data.get("shipping_state")
        shipping_country = request.data.get("shipping_country")
        shipping_zipcode = request.data.get("shipping_zipcode")
        sales_tax_id = request.data.get("sales_tax_id")
        sales_tax_image = request.data.get("sales_tax_image")
        minumum_threshold = request.data.get('minumum_threshold')
        maximum_threshold = request.data.get('maximum_threshold')
        terms_and_condition_doc = request.data.get('terms&condition_doc')
        sales_person = request.data.get('sales_person')

        new_data = request.data.copy()
        if 'sales_person' in new_data:
            new_data.pop('sales_person')
        # new_data.pop('billing_address')
        # new_data.pop('shipping_address')
        serializer = CustomerSerializers(customer_obj, data=new_data,partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if sales_person:
            if not sales_person in [None,"Null","null"]:
                try:
                    user_obj =  User.objects.get(user_type="SALESPERSON",id=sales_person)
                except Exception as e:
                    response = {
                        "status_code" : status.HTTP_400_BAD_REQUEST,
                        'message' : 'Sales person does not exist!'
                    }
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

                customer_obj.sales_person = user_obj
                customer_obj.save()

        if billing_address:
            customer_obj.billing_address.address = billing_address
            customer_obj.billing_address.save()
        if billing_city:
            customer_obj.billing_address.city = billing_city
            customer_obj.billing_address.save()
        if billing_state:
            customer_obj.billing_address.state = billing_state
            customer_obj.billing_address.save()
        if billing_country:
            customer_obj.billing_address.country = billing_country
            customer_obj.billing_address.save()
        if billing_zipcode:
            customer_obj.billing_address.zipcode = billing_zipcode
            customer_obj.billing_address.save()
        if shipping_address:
            customer_obj.shipping_address.address = shipping_address
            customer_obj.shipping_address.save()
        if shipping_city:
            customer_obj.shipping_address.city= shipping_city
            customer_obj.shipping_address.save()
        if shipping_state:
            customer_obj.shipping_address.state = shipping_state
            customer_obj.shipping_address.save()
        if shipping_country:
            customer_obj.shipping_address.country = shipping_country
            customer_obj.shipping_address.save()
        if shipping_zipcode:
            customer_obj.shipping_address.zipcode = shipping_zipcode 
            customer_obj.shipping_address.save()
        customer_obj.save()

            
        response = {
            "status_code" : status.HTTP_200_OK,
            'message' : "Customer details updated!"
                }
        return Response(response, status=status.HTTP_200_OK)

        