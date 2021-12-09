
from django.utils import timezone
import datetime
from django.conf import settings
import os
import pandas as pd
from django.core.files import File
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

## run cron script in local 
# import os, sys, django
# sys.path.append('/home/agile/DevangiRami/projects/inventory/Python_Akshar_App/')
# os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.settings'
# django.setup()

from apps.base.models import Product,InventoryMonthlyData
from apps.base.V1.serializers import ProductExcelSerializers

import logging
logger = logging.getLogger('django')



def run():
    try:
        date_today = datetime.date.today()
        today = str(datetime.date.strftime(date_today, "%m-%d-%Y"))
        file_name = "inventory_report_" + today.replace('-','_') + ".xlsx"
        
        #Fetching the data
        product_qs = Product.objects.all().order_by('name')
        serializer = ProductExcelSerializers(product_qs, many=True)
        serializer_data = serializer.data
        
        # Creating xlsx file
        new_data = InventoryMonthlyData.objects.create()
        df = pd.DataFrame(serializer_data)
        df.columns = ['Item No', 'Category', 'Item Name', 'Available qty', 'Purchase Price', 'Selling Price', 'Purchase Price * Qty', 'Selling Price * Qty']
        df.to_excel(file_name,index=False)

        # Saving to DB
        with open(file_name, 'rb') as excel:
            new_data.inventory_excel_file.save(file_name, File(excel))
            new_data.save()

        # Sending the email        
        email_body = "PFA inventory statement as of " + today
        message = MIMEMultipart()
        message['subject'] =  "Inventory Statement as of " + today
        message.attach(MIMEText(email_body, "plain"))
        xlsx_file = open(file_name, 'rb')

        payload = MIMEBase('application', 'octate-stream', Name=file_name + '.xlsx')
        payload.set_payload((xlsx_file).read())
        encoders.encode_base64(payload)
        payload.add_header('Content-Decomposition', 'attachment', filename=file_name)
        message.attach(payload)
        text = message.as_string()

        # Log in to server using secure context and send email
        email_form =  settings.EMAIL_HOST_USER
        password = settings.EMAIL_HOST_PASSWORD
        recipient_list = 'krishivfoods2019@gmail.com'
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_form, password)
            server.sendmail(email_form, recipient_list, text)
        
        ## Remove Temp file
        fullname = os.path.join(settings.BASE_DIR, file_name)
        if os.path.exists(fullname):
            os.remove(fullname)

        logger.error("successfully Sent:{0}".format(file_name))
    except Exception as e:
        logger.error(str(timezone.now()) + " Exception: " + str(e))

# run()