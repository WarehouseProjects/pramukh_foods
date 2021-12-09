from rest_framework.routers import DefaultRouter,SimpleRouter
from django.conf.urls import include,url
from django.conf.urls.static import static
from django.urls import path

from .views import *
from .base_apiviews import *
from .sales_user_apiviews import *
from .views import *
from .admin_apiviews import *


router = DefaultRouter() 
router.register("login",LoginUser,"login")
router.register('register',RegisterUser,'register')
router.register('orderdetail',OrderDetail,'orderdetail')
router.register('dashboard',DashBoard,'dashboard')
router.register('search',Search,'Search')
router.register('vendor',VendorViewset,'vendor')
router.register('create_category',CategoryViewset,'category')
# router.register('order',Order,'order')
router.register('create_product',ProductViewset,'product')
router.register('deleteuser',UserDelete,'userdelete')
router.register('deletecustomer',CustomerDelete,'customerdelete')
router.register('order',CreateOrderNew,'createorder')
router.register('multipleproduct',AddProduct,'AddProduct')
router.register('about',About_Us,'About_us')
router.register('contact',Contact_us,'Contact_us')
router.register('privacy',Privacy,'Privacy')
router.register('terms',Terms,'terms')
router.register('pack',Add_Pack,'pack')
router.register('user',ViewUser,'alluser')
router.register('forgotpassword',ForgotPassword,'forgotpassword')
router.register('salesreports',SalesReports,'salesreports')
router.register('adjust_quantity',AdjustProductViewset,'adjust_quantity')
router.register('adjust_product_data',AdjustProductData,'adjust_product_data')
router.register('ageing_report',AegingReportViewset,'ageing_report')
router.register('sales',SalesMangement,'sales')
router.register('verifyorder',VerifyOrder,'verifyorder')
# router.register('productlisting',productlisting,'productlisting')
router.register('forceupdate',ForceUpdate,'forceupdate')
router.register('scan_order',ScanOrder,'scan_order')
router.register('packsize',PackSizeListing,'packsizes')
router.register('vendorlist',Vendorlist,'vendor list')
router.register('productlistformcatandven',ProductListFromcatandVen,'productlistfromcatandven')
router.register('VendorListingWithoutPagination',VendorListingWithoutPagination,'VendorListingWithoutPagination')
router.register('ProductPackSizesCrud',ProductPackSizesCrud,'ProductPackSizesCrud')

router.register('paymenthistory',PaymentHistoryCrud,'PaymentHistorycrud')
router.register('paymentreceived',PaymentReceived,'paymentreceivedcrud')
router.register('orderdisplay',OrderDisplayFromCustomerid,'orderdisplayfromcustomerid')

router.register('AddProductToOrder',EditOrderAdmin,'EditOrderAdmin')
router.register('clear_payment',ClearOrderPayment,'clear_payment')

router.register('product_from_category',Product_from_category,'product_from_category')
router.register('notify',Notify,'Notify')
router.register('initial_reports',Initial_Product_Quantity,'initial_reports')

router.register('notifications',Notifications,"notifications")

router.register('invoice_pdf',InvoicePDF,"invoicePDF")
router.register('invoice_pdf_url',InvoicePDF_url,"invoicePDF_url")
router.register('creditmemo_pdf_url',CreditMemoPDF,"creditmemo-pdf-url")
router.register('delivery_sheet_pdf_url',DeliverySheetPdf,"delivery-sheet-pdf-url")

router.register('average_sales_report',Average_sales_report,"average_sales_report")
router.register('average_onhand_product_report',average_onhand_product,"average-onhand-product-report")
router.register('credit_memo',CreditMemoView,"credit-memo")
router.register('customer_statement',CustomerStatementView,"customer-statement")

urlpatterns = [
    path('userlist/', UserListView.as_view(), name='user-list'),
    path('user/<int:id>/', UserGetView.as_view(), name='user-single'),

    path('customerlist/', CustomerListView.as_view(), name='customer-list'),
    path('customer/<int:id>/', CustomerGetView.as_view(), name='customer-single'),

    path('packsizeslist/', PackSizesListView.as_view(), name='packsizes-list'),
    path('packsizes/<int:id>/', PackSizesGetView.as_view(), name='packsizes-single'),

    path('categorieslist/', CategoriesListView.as_view(), name='categories-list'),
    path('categorieslistNoPagnination/', CategoriesListViewNoPagination.as_view(), name='categories-list-NP'),
    path('category/<int:id>/', CategoriesGetView.as_view(), name='categories-single'),

    path('productlist/', ProductListView.as_view(), name='product-list'),
    path('product/<int:id>/', ProductGetView.as_view(), name='product-single'),

    path('orderlist/', OrderListView.as_view(), name='order-list'),
    path('orderview/<int:id>/', OrderGetView.as_view(), name='order-single'),

    path('changepassword/', ChangePasswordView.as_view(), name='change-password'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    path('editprofile/<int:id>', EditProfile.as_view(), name='edit-profile'),

    # sales user's url(endpoint)
    path('createcustomer/', CreateCustomerView.as_view(), name='create-customer'),
    path('createcustomerapp/', CreateCustomerAppView.as_view(), name='create-customer-app'),
    path('customereditprofile/<int:id>', CustomerEditProfile.as_view(), name='customer-edit-profile'),
    path('customereditprofileapp/<int:id>', EditCustomerAppView.as_view(), name='customer-edit-profile-app'),
    
    path('productlisting/',productlisting.as_view(),name='productlisting'),
    path('sales_productlist/',SalesProductList.as_view(),name='sales_productlist'),

    path('salesuserorder/',SalesUserOrderList.as_view(),name='specificorder'),
    path('salesuserorderfilter/',SalesUserOrderListFilterAndSearch.as_view(),name='specificorder'),
    path('sales_pdf_url/<int:id>/',SalesPDF.as_view(),name='sales_pdf'),    
    path('sales_user_credits/', SalesStoreCredits.as_view(), name='sales-user-credits'),

    path('updatepaymentdetail/<int:id>/',PaymentMethodCrud.as_view(),name='updatepayment-detail'),
    path('update_order_qty/',UpdateOrderQty.as_view(),name='update-order-qty'),
    path('admin_ageing_report/',AdminAgeingReport.as_view(),name='admin-ageing-report'),
    path('new_admin_ageing_report/',NewAdminAgeingReport.as_view(),name='new-admin-ageing-report'),
    path('update_delivery_status/<int:id>/', UpdateDeliveryStatus.as_view(), name='update-delivery-status'),
    path('store_name_list/', StoreList.as_view(), name='store-name-list'),
    path('update_payment_history/', AddUpdatePaymentHistory.as_view(), name='update-payment-history'),
    path('update_check_img/', UpdateCheckImg.as_view(), name='update_check_img'),
    path('product_only_list/', ProductOnlyList.as_view(), name='product-only-list'),
    path('scan_remaining_products/', ScanAllproducts.as_view(), name='scan-remaining-products'),
    path('verification_scan_remaining_products/', VerficationScanAllproducts.as_view(), name='verification-scan-remaining-products'),
    path('invoice_no_list/', InvoiceNoList.as_view(), name='invoice-no-list'),
    path('creditmemo_no_list/', CmNoList.as_view(), name='creditmemo-no-list'),



] + router.urls + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

