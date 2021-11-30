from django.template.loader import get_template
from django.conf import settings
from io import BytesIO
from xhtml2pdf import pisa
from datetime import date, datetime
from datetime import timedelta
from django.core.files.base import ContentFile
import requests
import json
from rest_framework.response import Response
from rest_framework import status
from django.db.models.functions import Lower

import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apps.base.models import *

def send_notification(title,body,device_tokens,extra_content=None):

    """
    This Function is used to send push notification
    """

    header = {
        "Content-Type": "application/json; charset=utf-8"
        }

    payload = {
        "app_id": settings.ONE_SIGNAL_APP_ID,
        "include_player_ids": device_tokens,
        "data": extra_content,
        "headings": {
            "en": title
            },
        "contents": {
                "en": body
                }
            }

    req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))

def update_profit(order_obj = None):
    if order_obj.delivered_status == False:
        order_pro_qs = OrderQuantity.objects.filter(order=order_obj)
        val=0
        for data in order_pro_qs:
            adjust_product_obj = AdjustProduct.objects.filter(product=data.product).last()
            if adjust_product_obj and adjust_product_obj.average_purchase_price != 0:
                purchase_price = adjust_product_obj.average_purchase_price
            else:
                purchase_price = data.product_purchase_price

            data_val = (data.net_price - purchase_price) * data.quantity

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
    

def get_order_pdfdata(order_obj,pdf_type=None):
    try:
        customer_obj = order_obj.customer
        products_data_for_pdf = []
        negative_product_data = []
        sum_of_weights=0
        sum_of_qty = 0
        for order in OrderQuantity.objects.filter(order=order_obj).order_by('product__category__name',Lower('order_product_name')):
            product_obj = order.product
            if order.quantity >= 0:
                sum_of_weights+= product_obj.weight * float(order.quantity) if product_obj.weight else 0
                sum_of_qty+=order.quantity if order.quantity else 0

                # Put net_price contition for old data
                old_data_date = datetime(2021, 9, 2).date()
                order_date = order.order.created_at.date()

                if order_date < old_data_date:
                    price_val = "%.2f" % round(order.price, 2)
                else:
                    price_val = "%.2f" % round(order.net_price, 2)

                products_data_for_pdf.append({'product_id':product_obj.id,'category':product_obj.category,
                                                    'description':order.order_product_name,'price':price_val,
                                                    'scan_qty':order.scan_quantity,
                                                    'qty':int(order.quantity) if order.quantity.is_integer() else order.quantity,
                                                    'amount':"%.2f" % round(order.product_amount, 2),
                                                    "item_no":product_obj.item_no
                                                    })
            else:
                # Put net_price contition for old data
                old_data_date = datetime(2021, 9, 2).date()
                order_date = order.order.created_at.date()

                if order_date < old_data_date:
                    price_val = "%.2f" % round(order.price, 2)
                else:
                    price_val = "%.2f" % round(order.net_price, 2)

                negative_product_data.append({'product_id':product_obj.id,'category':product_obj.category,
                                                    'description':order.order_product_name,'price':price_val,
                                                    'scan_qty':order.scan_quantity,
                                                    'qty':int(order.quantity) if order.quantity.is_integer() else order.quantity,
                                                    'amount':"%.2f" % round(order.product_amount, 2),
                                                    "item_no":product_obj.item_no
                                                    })
        
        credit_applied_pdf_data = []
        credit_applied_qs = CreditApplied.objects.filter(credit_applied_order=order_obj)

        for data in credit_applied_qs:
            dict_data = {}
            dict_data["item_no"] = data.credit_memo.cm_no
            dict_data["category"] = data.credit_memo.order.invoice_no if data.credit_memo.order else "Manual entry"
            dict_data["description"] = data.credit_memo.description if data.credit_memo.description else "-"
            dict_data["price"] =  "-" + "%.2f" % round(data.applied_amount)
            dict_data["qty"] = "-1"
            dict_data["amount"] = "-" + "%.2f" % round(data.applied_amount)

            credit_applied_pdf_data.append(dict_data)

        pdf_data = dict() 
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
       
        
        if customer_obj.phone:
            pdf_data['mobilenumber'] =  '({0}) {1}-{2}'.format(customer_obj.phone[:3],customer_obj.phone[3:6],customer_obj.phone[6:])
        else:
            pdf_data['mobilenumber'] = ''

        pdf_data['products']= products_data_for_pdf + negative_product_data + credit_applied_pdf_data
        pdf_data['weight']= "%.2f" % round(sum_of_weights, 2)
        pdf_data['total'] = "%.2f" % round(order_obj.amount, 2)
        pdf_data['due_date'] = order_obj.due_date
        pdf_data['ship_date']= order_obj.delivery_date
        pdf_data['account_num'] = customer_obj.account_num.replace("-", "") if customer_obj.account_num else '-'

        sum_of_qty =  str(sum_of_qty)
        val = sum_of_qty.find(".")
        sum_part_2 = sum_of_qty[val+1:]
        if len(sum_part_2) > 2:
            part_2 = sum_part_2[:2]
            sum_of_qty = sum_of_qty.replace(sum_part_2,part_2)

        pdf_data['total_qty']= "%.2f" % round(float(sum_of_qty), 2)
        pdf_data['terms']= order_obj.term
        pdf_data['store_name']= customer_obj.store_name
        pdf_data['customer_name']= customer_obj.full_name
        pdf_data['delivery_method'] = order_obj.delivery_method if order_obj.delivery_method else '-'
        pdf_data['rep']= '-'

        if pdf_type == 'sales_pdf':
            pdf_data['page_title']= 'SALES ORDER'
            pdf_data['date_title']= 'PO No#'
            pdf_data['invoice_no'] = order_obj.po_num
            pdf_data['po_num'] = order_obj.po_num
            pdf_data['date'] = datetime.now().date()

        else:
            pdf_data['page_title']= 'INVOICE'
            pdf_data['date_title']= 'Invoice#'
            pdf_data['po_num'] = order_obj.po_num
            pdf_data['invoice_no'] = order_obj.invoice_no
            pdf_data['date'] = order_obj.invoice_date

        if customer_obj.sales_person:
            full_name = customer_obj.sales_person.full_name
            data = full_name.split(' ')
            if len(data) != 0:
                pdf_data['rep']= data[0][0] 
                if len(data) >= 2:
                    pdf_data['rep'] = pdf_data['rep'] + data[1][0]

        num_of_row_data = len(products_data_for_pdf) + len(negative_product_data) + len(credit_applied_pdf_data)

    except Exception as e:
        print("In Exception",str(e))
        response = {
            'status_code':status.HTTP_400_BAD_REQUEST,
            'message':"Something went wrong!",
            'error': "Exception comes from get_order_pdfdata()."
            }
        return response

    response ={
        'status_code':True,
        'pdf_data': pdf_data,
        'num_of_row_data': num_of_row_data
    }
    return response

def create_pdf(**kwagrs):
    try:
        # Params which requried to call this function
        try:
            request = kwagrs["request"]
            pdf_type = kwagrs["pdf_type"]
            pdf_data = kwagrs["pdf_data"]
            filename = kwagrs["filename"]
            order_obj = kwagrs["order_obj"]
            num_of_row_data = kwagrs["num_of_row_data"]

        except KeyError as e:
            print("In Exception",str(e))
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Something went wrong!",
                'error': "create_pdf : Requried parameters are missing."
                }
            return response

        # check if file already exist
        pdf_filename = filename 
        pdf_path = settings.MEDIA_ROOT + "/pdf"
        fullname = os.path.join(pdf_path, pdf_filename)
        if os.path.exists(fullname):
            os.remove(fullname)

        # Getting extra row needs to add in last page of PDF 
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
        
        # Process of Creating PDF
        template=get_template(settings.BASE_DIR +'/templates/invoice_pdf.html')
        result = BytesIO()
        html = template.render(pdf_data)
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result,encoding='UTF-8')
        f = open(filename,"wb")
        f.write(result.getvalue())
        f.close()
        myfile = ContentFile(result.getvalue())

        if pdf_type == "sales_pdf":
            print("new..")
            order_obj.sales_pdf.save(filename, myfile)
            pdf_url = request.build_absolute_uri(order_obj.sales_pdf.url)
        elif pdf_type == "invoice_pdf" :
            order_obj.invoice_pdf.save(filename, myfile)
            pdf_url = request.build_absolute_uri(order_obj.invoice_pdf.url)
        elif pdf_type == "credit_memo_pdf" :
            extra_rows = 26
            pdf_data['loop_times'] = range(1, extra_rows+1)
            # Process of Creating PDF
            template=get_template(settings.BASE_DIR +'/templates/credit_memo_pdf.html')
            result = BytesIO()
            html = template.render(pdf_data)
            pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result,encoding='UTF-8')
            f = open(filename,"wb")
            f.write(result.getvalue())
            f.close()
            myfile = ContentFile(result.getvalue())
            credit_obj = order_obj
            credit_obj.credit_memo_pdf.save(filename, myfile)
            pdf_url = request.build_absolute_uri(credit_obj.credit_memo_pdf.url)

            base_pdf_path = settings.BASE_DIR
            fullname = os.path.join(base_pdf_path, pdf_filename)

            if os.path.exists(fullname):
                os.remove(fullname)

        response = {
            'status_code': True,
            'pdf_url':pdf_url,
            'filename': filename
        }

    except Exception as e:
        print("In Exception create_pdf",str(e))
        response = {
            'status_code':status.HTTP_400_BAD_REQUEST,
            'message':"Something went wrong!",
            'error': "Exception comes from create_pdf()."
            }
        return response

    return response

def send_pdf_mail(**kwagrs):
    # Params which requried to call this function
    try:
        try:
            email_subject = kwagrs["email_subject"]
            email_body = kwagrs["email_body"]
            filename = kwagrs["filename"]
            recipient_list = kwagrs["recipient_list"]

        except KeyError as e:
            print("In Exception",str(e))
            response = {
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':"Something went wrong!",
                'error': "send_pdf_mail : Requried parameters are missing."
                }
            return response

        # Process of Email  
        message = MIMEMultipart()
        message['subject'] = email_subject
        message.attach(MIMEText(email_body, "plain"))
        binary_pdf = open(filename, 'rb')

        payload = MIMEBase('application/pdf', 'octate-stream', Name=filename + '.pdf')
        payload.set_payload((binary_pdf).read())
        encoders.encode_base64(payload)
        payload.add_header('Content-Decomposition', 'attachment', filename=filename)
        message.attach(payload)
        text = message.as_string()

        # Log in to server using secure context and send email
        email_form = settings.EMAIL_HOST_USER
        password = settings.EMAIL_HOST_PASSWORD
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_form, password)
            server.sendmail(email_form, recipient_list, text)

        pdf_filename = filename 
        pdf_path = settings.BASE_DIR
        fullname = os.path.join(pdf_path, pdf_filename)
        if os.path.exists(fullname):
            os.remove(fullname)

    except Exception as e:
        print("In Exception",str(e))
        response = {
            'status_code':status.HTTP_400_BAD_REQUEST,
            'message':"Something went wrong!",
            'error': "Exception comes from send_pdf_mail()."
            }
        return response

    response = {'status_code': True }
    return response

def get_creditmemo_pdfdata(creditmemo_obj=None):
    try:
        data_for_pdf = []
        customer_obj = creditmemo_obj.customer
        data_obj = creditmemo_obj
       
        # Put net_price contition for old data
        if data_obj.order:
            data_for_pdf.append({'order_number':data_obj.order.invoice_no,
                                    'description':data_obj.description,
                                    'amount':"%.2f" % round(float(data_obj.updated_credit_amount), 2)
                                })
        else:
            data_for_pdf.append({'order_number':"Manual Entry",
                                'description':data_obj.description,
                                'amount': "%.2f" % round(float(data_obj.updated_credit_amount), 2)
                                })

        pdf_data = dict() 
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
       
        
        if customer_obj.phone:
            pdf_data['mobilenumber'] =  '({0}) {1}-{2}'.format(customer_obj.phone[:3],customer_obj.phone[3:6],customer_obj.phone[6:])
        else:
            pdf_data['mobilenumber'] = ''

        pdf_data['row_data']= data_for_pdf 
        pdf_data['total'] = "%.2f" % round(float(data_obj.updated_credit_amount), 2)
        # pdf_data['due_date'] = order_obj.due_date
        # pdf_data['ship_date']= order_obj.delivery_date
        pdf_data['account_num'] = customer_obj.account_num.replace("-", "") if customer_obj.account_num else '-'

        # pdf_data['terms']= order_obj.term
        pdf_data['store_name']= customer_obj.store_name
        pdf_data['customer_name']= customer_obj.full_name
        # pdf_data['delivery_method'] = order_obj.delivery_method if order_obj.delivery_method else '-'
        pdf_data['rep']= '-'

        
        pdf_data['page_title']= 'CREDIT MEMO'
        pdf_data['date_title']= 'CM#'
        pdf_data['cm_no'] = data_obj.cm_no
        pdf_data['date'] = datetime.now().date()

        if customer_obj.sales_person:
            full_name = customer_obj.sales_person.full_name
            data = full_name.split(' ')
            if len(data) != 0:
                pdf_data['rep']= data[0][0] 
                if len(data) >= 2:
                    pdf_data['rep'] = pdf_data['rep'] + data[1][0]

        num_of_row_data = 24

    except Exception as e:
        print("In Exception get_creditmemo_pdfdata",str(e))
        response = {
            'status_code':status.HTTP_400_BAD_REQUEST,
            'message':"Something went wrong!",
            'error': "Exception comes from get_creditmemo_pdfdata()."
            }
        return response

    response ={
        'status_code':True,
        'pdf_data': pdf_data,
        'num_of_row_data': num_of_row_data
    }
    return response
