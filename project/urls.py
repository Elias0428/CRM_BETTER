"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_, name='login'),
    path('logout/', views.logout_, name='logout'),

    path('admin/', admin.site.urls),

    path('weeklyLiveView/',views.weeklyLiveView,name='weeklyLiveView'),
    path('monthLiveView/',views.monthLiveView,name='monthLiveView'),

    path('weeklyLiveViewTV/',views.weeklyLiveView,name='weeklyLiveViewTV'),
    path('monthLiveViewTV/',views.monthLiveView,name='monthLiveViewTV'),

    path('formCreateClient/', views.formCreateClient, name='formCreateClient'),
    path('formEditClient/<client_id>/', views.formEditClient, name='formEditClient'),

    path('check-phone-number/', views.check_phone_number, name = 'check_phone_number'),
    path('motivationalPhrase/', views.motivationalPhrase, name='motivationalPhrase'),

    path('select_client/', views.select_client, name='select_client'),
    path('update-type-sales/<int:client_id>/', views.update_type_sales, name='update_type_sales'),

    path('clientObamacare/', views.clientObamacare, name='clientObamacare'),
    path('clientSupp/', views.clientSupp, name='clientSupp'),
    
    path('toggleObamaStatus/<obamacare_id>/', views.toggleObamaStatus, name='toggleObamaStatus'),
    path('toggleSuppStatus/<supp_id>/', views.toggleSuppStatus, name='toggleSuppStatus'),

    path('save-customer-observation-aca/', views.saveCustomerObservationACA, name='saveCustomerObservationACA'),
    path('save-customer-observation-supp/', views.saveCustomerObservationSupp, name='saveCustomerObservationSupp'),

    path('typification/', views.typification, name='typification'),
    path('customerPerformance/', views.customerPerformance, name='customerPerformance'),
    path('get-observation-detail/<observation_id>/', views.get_observation_detail, name='get_observation_detail'),
    path('toggleTypification/<typifications_id>/', views.toggleTypification, name='toggleTypification'),

    path('sale/', views.sale, name='sale'),

    path('editClientObama/<obamacare_id>/', views.editClientObama, name='editClientObama'),
    path('saveDocumentClient/<int:obamacare_id>/', views.saveDocumentClient, name='saveDocumentClient'),
    path('saveAppointment/<int:obamacare_id>/', views.saveAppointment, name='saveAppointment'),
    path('editClientSupp/<supp_id>/', views.editClientSupp, name='editClientSupp'),
    
    path('formCreateAlert/', views.formCreateAlert, name='formCreateAlert'),
    path('alert/', views.tableAlert, name='alert'),
    path('toggleAlert/<alertClient_id>/', views.toggleAlert, name='toggleAlert'),
    path('editAlert/<alertClient_id>/', views.editAlert, name='editAlert'),

    path('formCreateUser/', views.formCreateUser, name='formCreateUser'),
    path('editUser/<user_id>', views.editUser, name='editUser'),
    path('toggleUser/<user_id>/', views.toggleUser, name='toggleUser'),

    # Json
    path('formCreatePlan/<client_id>/', views.formCreatePlan, name='formCreatePlan'),
    path('fetchAca/<client_id>/', views.fetchAca, name='fetchAca'),
    path('fetchSupp/<client_id>/', views.fetchSupp, name='fetchSupp'),
    path('fetchDependent/<client_id>/', views.fetchDependent, name='fetchDependent'),

    path('fetchPaymentsMonth/', views.fetchPaymentsMonth, name='fetchPaymentsMonth'),

    path('formCreatePlan/deleteDependent/<int:dependent_id>/', views.delete_dependent, name='delete_dependent'),
    path('formCreatePlan/deleteSupp/<int:supp_id>/', views.delete_supp, name='delete_supp'),

    path('upload_excel/', views.upload_excel, name='upload_excel'),    
    path('process_and_save/', views.process_and_save, name='process_and_save'),
    path('save_data/', views.save_data, name='save_data'),
    path('manage_agent_assignments/', views.manage_agent_assignments, name='manage_agent_assignments'),
    path('bd/', views.commentDB, name='bd'),
    path('reportBd/', views.reportBd, name='reportBd'),

    path('formCreateControl/', views.formCreateControl, name='formCreateControl'),
    path('control/', views.tableControl, name='control'),
    path('createQuality/', views.createQuality, name='createQuality'),

    path('salesPerformance/', views.salesPerformance, name='salesPerformance'),

    path('viewConsent/<obamacare_id>/', views.consent, name='viewConsent'),
    path('viewIncomeLetter/<obamacare_id>/', views.incomeLetter, name='incomeLetter'),

    path('averageCustomer', views.averageCustomer, name='averageCustomer'),
    path('customerTypification', views.customerTypification, name='customerTypification'),

    path('formAddObama/<client_id>', views.formAddObama, name='formAddObama'),
    path('formAddSupp/<client_id>', views.formAddSupp, name='formAddSupp'),
    path('formAddDepend/<client_id>', views.formAddDepend, name='formAddDepend'),
    path('addDepend/', views.addDepend, name='addDepend'),
    
    path('detalle-agente/<agent_id>/', views.SaleModal, name='detalle_agente'),  

    path('sale6Week/', views.sales6WeekReport, name='sale6Week'),  
    path('chart6Week/', views.chart6Week, name='chart6Week'), 

    path('weekSalesWiew/',views.weekSalesWiew, name='weekSalesWiew'),
    path('descargarPdf/<int:week_number>/', views.downloadPdf, name='downloadPdf'),

    path('formCreateClientMedicare/', views.formCreateClientMedicare, name='formCreateClientMedicare'),
    path('consetMedicare/<client_id>/<language>/', views.consetMedicare, name='consetMedicare'),
    path('clientMedicare/', views.clientMedicare, name='clientMedicare'),
    path('editClientMedicare/<medicare_id>/', views.editClientMedicare, name='editClientMedicare'),
    path('save-customer-observation-medicare/', views.saveCustomerObservationMedicare, name='saveCustomerObservationMedicare'),
    path('desactiveMedicare/<medicare_id>/', views.desactiveMedicare, name='desactiveMedicare'),
    path('validarCita/', views.validarCita, name='validarCita'),

    path('paymentClients/', views.paymentClients, name='paymentClients'),

    ##path('exportUsers/', views.exportUsers, name='exportUsers'),
    ##path('testImportDb/', views.testExportDB, name='testExportDB'),
]