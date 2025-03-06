# Standard Python libraries
import base64
import calendar
import datetime
import io
import json
import os
import csv
import random
from collections import defaultdict
from datetime import timedelta
import openpyxl

import pandas as pd

# Django utilities
from django.core.files.base import ContentFile
from django.core.signing import Signer, BadSignature
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.text import Truncator  # Importar herramienta para truncar textos
from django.utils.translation import activate


# Django core libraries
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from django.db.models import Count, Q, Sum, Value, TextField, F
from django.db.models.functions import Coalesce, Substr
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlencode

# Third-party libraries
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer  
from weasyprint import HTML

# Application-specific imports
from app.forms import *
from app.models import *

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration


# Create your views here.
def login_(request):
    if request.user.is_authenticated:
        return redirect(index)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(motivationalPhrase)
        else:
            msg = 'Datos incorrectos, intente de nuevo'
            return render(request, 'auth/login.html', {'msg':msg})
    else:
        return render(request, 'auth/login.html')
        
def logout_(request):
    # Verifica si es una solicitud AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        logout(request)
        return JsonResponse({
            'status': 'success', 
            'redirect_url': '/login/'  # URL a la que redirigir después del logout
        })
    else:
        # Cierre de sesión manual tradicional
        logout(request)
        return redirect(index)
    
@login_required(login_url='/login')
def motivationalPhrase(request):
    randomInt = random.randint(1,174)
    motivation = Motivation.objects.filter(id=randomInt).first()
    context = {'motivation':motivation}
    return render (request, 'motivationalPhrase.html',context)

@login_required(login_url='/login') 
def select_client(request):

    if request.user.role == 'Admin': clients = Client.objects.all()
    else: clients = Client.objects.filter(is_active = True)
    
    return render(request, 'agents/select_client.html', {'clients':clients})

def update_type_sales(request, client_id):
    if request.method == 'POST':
        type_sales = request.POST.get('type_sales')
        route = request.POST.get('route')
        if type_sales:
            client = get_object_or_404(Client, id=client_id)
            client.type_sales = type_sales
            client.save()
            # Redirige a la URL previa con el ID del cliente
            if route == 'ACA': return redirect('formAddObama', client_id=client_id)
            elif route == 'SUPP': return redirect('formAddSupp', client_id=client_id)
            elif route == 'DEPEND': return redirect('formAddDepend', client_id=client_id)
            else: return redirect('select_client')

# Vista para crear cliente
@login_required(login_url='/login') 
def formCreateClient(request):
    if request.method == 'POST':

        date_births = request.POST.get('date_birth')
        fecha_obj = datetime.strptime(date_births, '%m/%d/%Y').date()
        fecha_formateada = fecha_obj.strftime('%Y-%m-%d')

        # Obtener la fecha actual
        hoy = datetime.today().date()
        # Calcular la edad
        edad = hoy.year - fecha_obj.year - ((hoy.month, hoy.day) < (fecha_obj.month, fecha_obj.day))

        social = request.POST.get('social_security')

        if social: formatSocial = social.replace('-','')
        else: formatSocial = None

        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.agent = request.user
            client.is_active = 1
            client.old = edad
            client.date_birth = fecha_formateada
            client.social_security = formatSocial
            client.save()

            if client.type_sales in ['ACA', 'ACA/SUPLEMENTARIO']:
                contact = ContactClient.objects.create(client=client,agent=request.user)
            
            # Responder con éxito y la URL de redirección
            return redirect('formCreatePlan', client.id)
        else:
            return render(request, 'forms/formCreateClient.html', {'error_message': form.errors})
    else:
        return render(request, 'forms/formCreateClient.html')

@login_required(login_url='/login') 
def formCreateClientMedicare(request):
    if request.method == 'POST':

        date_births = request.POST.get('date_birth')
        language = request.POST.get('language')
        fecha_obj = datetime.strptime(date_births, '%m/%d/%Y').date()
        fecha_formateada = fecha_obj.strftime('%Y-%m-%d')

        date_medicare = request.POST.get('dateMedicare')
        # Convertir a objeto datetime
        fecha_medicare = datetime.strptime(date_medicare, '%m/%d/%Y %H')
        # Asegurar compatibilidad con zona horaria
        fecha_formateada_medicare = make_aware(fecha_medicare)

        # Obtener la fecha actual
        hoy = datetime.today().date()
        # Calcular la edad
        edad = hoy.year - fecha_obj.year - ((hoy.month, hoy.day) < (fecha_obj.month, fecha_obj.day))

        social = request.POST.get('social_security')

        if social: formatSocial = social.replace('-','')
        else: formatSocial = None

        form = ClientMedicareForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.agent = request.user
            client.is_active = 1
            client.old = edad
            client.date_birth = fecha_formateada
            client.dateMedicare = fecha_formateada_medicare
            client.social_security = formatSocial
            client.save()

            contact = OptionMedicare.objects.create(client=client,agent=request.user)
            
            # Redirección a la nueva página en otra pestaña
            new_page_url = reverse('consetMedicare', args=[client.id, language])
            
            # Redirección de la página actual al index
            return render(request, 'redirect_template.html', {'new_page_url': new_page_url})
        
            
        else:
            return render(request, 'forms/formCreateClientMedicare.html', {'error_message': form.errors})
    else:
        return render(request, 'forms/formCreateClientMedicare.html')

def consetMedicare(request, client_id, language):

    medicare = Medicare.objects.get(id=client_id)
    contact = OptionMedicare.objects.filter(client = medicare.id).first()
    temporalyURL = None

    typeToken = False

    activate(language)
    # Validar si el usuario no está logueado y verificar el token
    if isinstance(request.user, AnonymousUser):
        result = validateTemporaryToken(request, typeToken)
        is_valid_token, *note = result
        if not is_valid_token:
            return HttpResponse(note)
    elif request.user.is_authenticated:
        temporalyURL = f"{request.build_absolute_uri('/consetMedicare/')}{client_id}/{language}/?token={generateTemporaryToken(medicare, typeToken)}"
        print('Usuario autenticado')
    else:
        # Si el usuario no está logueado y no hay token válido
        return HttpResponse('Acceso denegado. Por favor, inicie sesión o use un enlace válido.')
    
    if request.method == 'POST':
        
        # Usamos la nueva función para guardar los checkboxes en ContactClient
        objectContact = save_contact_medicare_checkboxes(request.POST, contact)

        return generateMedicarePdf(request, medicare ,language)


    context = {
        'medicare':medicare,
        'contact':contact,
        'company':getCompanyPerAgent(medicare.agent_usa),
        'temporalyURL': temporalyURL
    }

    return render(request, 'consent/consetMedicare.html',context)

@login_required(login_url='/login') 
def formEditClient(request, client_id):
    
    client = get_object_or_404(Client, id=client_id)        

    if request.method == 'POST':

        date_births = request.POST.get('date_birth')
        fecha_obj = datetime.strptime(date_births, '%m/%d/%Y').date()
        fecha_formateada = fecha_obj.strftime('%Y-%m-%d')

        # Obtener la fecha actual
        hoy = datetime.today().date()
        # Calcular la edad
        edad = hoy.year - fecha_obj.year - ((hoy.month, hoy.day) < (fecha_obj.month, fecha_obj.day))

        social = request.POST.get('social_security')

        if social: formatSocial = social.replace('-','')
        else: formatSocial = None
        form = ClientForm(request.POST, instance=client)
        print(form.errors)
        if form.is_valid():
            client = form.save(commit=False)
            client.is_active = 1
            client.date_birth = fecha_formateada
            client.social_security = formatSocial
            client.old = edad
            
            client.save()
            return redirect('formCreatePlan', client.id) 
        
    # Si el método es GET, mostrar el formulario con los datos del cliente
    form = ClientForm(instance=client)

    return render(request, 'forms/formEditClient.html', {'form': form, 'client': client})

# Nueva vista para verificar si el número de teléfono ya existe (usada en AJAX)
def check_phone_number(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        exists = Client.objects.filter(phone_number=phone_number).exists()
        return JsonResponse({'exists': exists})
    return JsonResponse({'exists': False})

@login_required(login_url='/login') 
def formCreatePlan(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    type_sale = request.GET.get('type_sale')
    aca_plan = ObamaCare.objects.filter(client=client).first()
    supplementary_plan = Supp.objects.filter(client=client)
    dependents = Dependent.objects.filter(client=client)
    for supp in supplementary_plan:
        supp.premium = f"{float(supp.premium):.2f}" #Esto  es para que se le ponga el premium.

    return render(request, 'forms/formCreatePlan.html', {
        'client': client,
        'aca_plan_data': aca_plan,
        'supplementary_plan_data': supplementary_plan,
        'dependents': dependents,
        'type_sale':type_sale
    })

@login_required(login_url='/login') 
def fetchAca(request, client_id):
    client = Client.objects.get(id=client_id)
    aca_plan_id = request.POST.get('acaPlanId')

    if aca_plan_id:
        # Si el ID existe, actualiza el registro
        ObamaCare.objects.filter(id=aca_plan_id).update(
            taxes=request.POST.get('taxes'),
            agent_usa=request.POST.get('agent_usa'),
            plan_name=request.POST.get('planName'),
            work=request.POST.get('work'),
            subsidy=request.POST.get('subsidy'),
            carrier=request.POST.get('carrierObama'),
            doc_income=request.POST.get('doc_income'),
            doc_migration=request.POST.get('doc_migration'),
            observation=request.POST.get('observationObama'),
            premium=request.POST.get('premium')
        )
        aca_plan = ObamaCare.objects.get(id=aca_plan_id)
        created = False
    else:
        # Si no hay ID, crea un nuevo registro
        aca_plan, created = ObamaCare.objects.update_or_create(
            client=client,
            agent=request.user,
            defaults={
                'taxes': request.POST.get('taxes'),
                'agent_usa': request.POST.get('agent_usa'),
                'plan_name': request.POST.get('planName'),
                'work': request.POST.get('work'),
                'subsidy': request.POST.get('subsidy'),
                'carrier': request.POST.get('carrierObama'),
                'observation': request.POST.get('observationObama'),
                'doc_migration': request.POST.get('doc_migration'),
                'doc_income': request.POST.get('doc_income'),
                'premium': request.POST.get('premium'),
                'status_color': 1,
                'profiling':'NO',
                'status':'IN PROGRESS'
            }
        )

        # Enviar alerta por WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'product_alerts',
            {
                'type': 'send_alert',
                'message': f'New product Obamacare added',
            }
        )

    return JsonResponse({'success': True, 'aca_plan_id': aca_plan.id})

@login_required(login_url='/login') 
def fetchSupp(request, client_id):
    client = Client.objects.get(id=client_id)
    supp_data = {}
    updated_supp_ids = []  # Lista para almacenar los IDs de los registros suplementarios

    # Filtrar solo los datos que corresponden a suplementario y organizarlos por índices
    for key, value in request.POST.items():
        if key.startswith('supplementary_plan_data'): #pregunta como inicia el string
            # Obtener índice y nombre del campo
            try:
                index = key.split('[')[1].split(']')[0]  # Extrae el índice del suplementario
                field_name = key.split('[')[2].split(']')[0]  # Extrae el nombre del campo
            except IndexError:
                continue  # Ignora las llaves que no tengan el formato esperado
            
            # Inicializar un diccionario para el suplementario si no existe
            if index not in supp_data:
                supp_data[index] = {}

            # Almacenar el valor del campo en el diccionario correspondiente
            supp_data[index][field_name] = value

    # Guardar cada dependiente en la base de datos
    for sup_data in supp_data.values():
        if 'carrierSuple' in sup_data:  # Verificar que al menos el nombre esté presente
            supp_id = sup_data.get('id')  # Obtener el id si está presente

            if supp_id:  # Si se proporciona un id, actualizar el registro existente
                Supp.objects.filter(id=supp_id).update(
                    effective_date=sup_data.get('effectiveDateSupp'),
                    agent_usa=sup_data.get('agent_usa'),
                    company=sup_data.get('carrierSuple'),
                    premium=sup_data.get('premiumSupp'),
                    policy_type=sup_data.get('policyTypeSupp'),
                    preventive=sup_data.get('preventiveSupp'),
                    coverage=sup_data.get('coverageSupp'),
                    deducible=sup_data.get('deducibleSupp'),
                    observation=sup_data.get('observationSuple'),
                )
                updated_supp_ids.append(supp_id)  # Agregar el ID actualizado a la lista
            else:  # Si no hay id, crear un nuevo registro
                new_supp = Supp.objects.create(
                    client=client,
                    status='REGISTERED',
                    agent=request.user,
                    effective_date=sup_data.get('effectiveDateSupp'),
                    agent_usa=sup_data.get('agent_usa'),
                    company=sup_data.get('carrierSuple'),
                    premium=sup_data.get('premiumSupp'),
                    policy_type=sup_data.get('policyTypeSupp'),
                    preventive=sup_data.get('preventiveSupp'),
                    coverage=sup_data.get('coverageSupp'),
                    deducible=sup_data.get('deducibleSupp'),
                    observation=sup_data.get('observationSuple'),
                    status_color = 1
                )
                updated_supp_ids.append(new_supp.id)  # Agregar el ID creado a la lista

                # Enviar alerta por WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'product_alerts',
                    {
                        'type': 'send_alert',
                        'message': f'New product Supplemental added',
                    }
                )

    return JsonResponse({'success': True,  'supp_ids': updated_supp_ids})

@login_required(login_url='/login')      
def fetchDependent(request, client_id):
    client = Client.objects.get(id=client_id)
    dependents_data = {}
    updated_dependents_ids = []

    # Procesar datos de dependientes como antes
    for key, value in request.POST.items():
        if key.startswith('dependent'):
            try:
                index = key.split('[')[1].split(']')[0]
                field_name = key.split('[')[2].split(']')[0]
            except IndexError:
                continue
            
            if index not in dependents_data:
                dependents_data[index] = {}

            dependents_data[index][field_name] = value

    # Crear lista de dependientes
    dependents_to_add = []
    for dep_data in dependents_data.values():
        if 'nameDependent' in dep_data:
            dependent_id = dep_data.get('id')

            # Procesar múltiples valores de type_police
            type_police_values = dep_data.get('typePoliceDependents', [])
            type_police = ", ".join(type_police_values.split(',') if type_police_values else [])

            # Lógica para asociar ObamaCare
            obamacare = None
            if 'ACA' in type_police:
                # Buscar un plan ObamaCare para el cliente
                obamacare = ObamaCare.objects.filter(client=client).first()

            # Crear o actualizar Dependent
            if dependent_id:
                dependent = Dependent.objects.get(id=dependent_id)
                for attr, value in {
                    'name': dep_data.get('nameDependent'),
                    'apply': dep_data.get('applyDependent'),
                    'date_birth': dep_data.get('dateBirthDependent'),
                    'migration_status': dep_data.get('migrationStatusDependent'),
                    'sex': dep_data.get('sexDependent'),
                    'kinship': dep_data.get('kinship'),
                    'type_police': type_police,
                    'obamacare': obamacare
                }.items():
                    setattr(dependent, attr, value)
                dependent.save()
            else:
                dependent = Dependent.objects.create(
                    client=client,
                    name=dep_data.get('nameDependent'),
                    apply=dep_data.get('applyDependent'),
                    date_birth=dep_data.get('dateBirthDependent'),
                    migration_status=dep_data.get('migrationStatusDependent'),
                    sex=dep_data.get('sexDependent'),
                    kinship=dep_data.get('kinship'),
                    type_police=type_police,
                    obamacare=obamacare
                )

            dependents_to_add.append(dependent)
            updated_dependents_ids.append(dependent.id)

    # Obtener todos los Supp para este cliente
    supps = Supp.objects.filter(client=client)
    
    # Agregar todos los dependientes a cada Supp
    for supp in supps:
        supp.dependents.clear()  # Limpiar relaciones existentes
        supp.dependents.add(*dependents_to_add)

    return JsonResponse({
        'success': True,
        'dependents_ids': updated_dependents_ids
    })

@login_required(login_url='/login')
def formAddObama(request,client_id):

    client = Client.objects.get(id=client_id)

    if request.method == 'POST':
        formObama = ObamaForm(request.POST)
        if formObama.is_valid():
            obama = formObama.save(commit=False)
            obama.agent = request.user
            obama.client = client
            obama.status_color = 1
            obama.is_active = True
            obama.save()

            return redirect('select_client')  # Cambia a tu página de éxito            
        
    return render(request, 'forms/formAddObama.html')

@login_required(login_url='/login')
def formAddSupp(request,client_id):

    client = Client.objects.get(id=client_id)    

    if request.method == 'POST':

        observation = request.POST.get('observation')
        effective_dates = request.POST.get('effective_date')
        fecha_obj = datetime.strptime(effective_dates, '%m/%d/%Y')
        fecha_formateada = fecha_obj.strftime('%Y-%m-%d')

        formSupp = SuppForm(request.POST)
        if formSupp.is_valid():
            supp = formSupp.save(commit=False)
            supp.agent = request.user
            supp.client = client
            supp.status_color = 1
            supp.is_active = True
            supp.effective_date = fecha_formateada
            supp.observation = observation
            supp.status = 'REGISTERED'
            supp.save()
            return redirect('select_client')  # Cambia a tu página de éxito           
        
    return render(request, 'forms/formAddSupp.html')

@login_required(login_url='/login')
def formAddDepend(request, client_id):
    lista = []
    lista2 = []
    dependents = Dependent.objects.filter(client_id=client_id)

    supp = Supp.objects.filter(client_id=client_id)
    obama = ObamaCare.objects.filter(client_id=client_id).first()

    if obama:
        lista2.append('ACA')

    for supp in supp:
        supp.policy_type = supp.policy_type.split(",")
        for i in supp.policy_type:
            lista2.append(i)

    for dependent in dependents:
        dependent.type_police = dependent.type_police.split(",")
        for i in dependent.type_police:
            lista.append(i)

    if request.method == 'POST':
       
        # Recuperar todos los dependientes enviados
        dependent_ids = request.POST.getlist('dependentId')

        # Iterar sobre cada dependiente para procesar sus datos
        for index, dependent_id in enumerate(dependent_ids):
            try:
                observations = request.POST.getlist(f'typePoliceDependents[{index}][]')
                if observations:
                    # Buscar el dependiente correspondiente
                    dependent = Dependent.objects.get(id=dependent_id)
                    
                    # Obtener los valores actuales de type_police
                    current_type_police = dependent.type_police.split(",") if dependent.type_police else []

                    # Concatenar y guardar
                    updated_type_police = list(set(current_type_police + observations))
                    dependent.type_police = ",".join(updated_type_police)
                    dependent.save()

                    # Asociar a las pólizas correspondientes
                    for observation in observations:
                        supp_instance = Supp.objects.filter(policy_type=observation, client_id=client_id).first()
                        if supp_instance:
                            supp_instance.dependents.add(dependent)

            except Exception as e:
                print(f"Error processing dependent {dependent_id}: {e}")

        return redirect('select_client')

    context = {
        'dependents': dependents,
        'lista': lista,
        'lista2': lista2,
        'client_id': client_id
    }

    return render(request, 'forms/formAddDepend.html', context)

@login_required(login_url='/login')
def addDepend(request):

    nameDependent = request.POST.get('nameDependent')
    applyDependent = request.POST.get('applyDependent')
    dateBirthDependent = request.POST.get('dateBirthDependent')
    migrationStatusDependent = request.POST.get('migrationStatusDependent')
    sexDependent = request.POST.get('sexDependent')        
    kinship = request.POST.get('kinship')  
    client_id = request.POST.get('client_id') 

    # Conversión solo si los valores no son nulos o vacíos
    if dateBirthDependent not in [None, '']:
        dateNew = datetime.strptime(dateBirthDependent, '%m/%d/%Y').date()
    else:
        dateNew = None

    # Obtenemos las polizas seleccionadas
    observations = request.POST.getlist('typePoliceDependents[]')  # Lista de valores seleccionados
    
    # Convertir las observaciones a una cadena (por ejemplo, separada por comas o saltos de línea)
    typification_text = ", ".join(observations)  # Puedes usar "\n".join(observations) si prefieres saltos de línea

    obama = ObamaCare.objects.get(client_id=client_id)
    client = Client.objects.get(id=client_id)

    if nameDependent.strip():  # Validar que el texto no esté vacío
        dependent = Dependent.objects.create(
            client=client,
            name=nameDependent,
            apply=applyDependent,
            date_birth=dateNew,
            migration_status=migrationStatusDependent,
            type_police=typification_text, # Guardamos las observaciones en el campo 'typification'
            sex=sexDependent,
            obamacare = obama,
            kinship=kinship
        )
    
    # Asociar el Dependent solo a las pólizas seleccionadas en observations
        for observation in observations:
            # Buscar la póliza correspondiente al nombre o tipo
            supp_instance = Supp.objects.filter(policy_type=observation, client=client).first()
            if supp_instance:
                supp_instance.dependents.add(dependent)

    return redirect('select_client')    

@login_required(login_url='/login')
def clientObamacare(request):
    

    borja = 'BORJA G CANTON HERRERA - NPN 20673324'
    daniel = 'DANIEL SANTIAGO LAPEIRA ACEVEDO - NPN 19904958'
    luis = 'LUIS EDUARDO LAPEIRA - NPN 20556081'
    gina = 'GINA PAOLA LAPEIRA - NPN 19944280'
    evelyn = 'EVELYN BEATRIZ HERRERA - NPN 20671818'
    danieska = 'DANIESKA LOPEZ SEQUEIRA - NPN 20134539'
    rodrigo = 'RODRIGO G CANTON - NPN 20670005'
    zohira = 'ZOHIRA RAQUEL DUARTE AGUILAR - NPN 19582295'
    vladimir = 'VLADIMIR DE LA HOZ FONTALVO - NPN 19915005'
    
    if request.user.role == 'Admin':       
        obamaCare = ObamaCare.objects.select_related('agent','client').annotate(
            truncated_agent_usa=Substr('agent_usa', 1, 8)).order_by('-created_at')
    elif request.user.username == 'zohiraDuarte':
       obamaCare = ObamaCare.objects.select_related('agent','client').annotate(
            truncated_agent_usa=Substr('agent_usa', 1, 8)).filter(is_active = True, agent_usa = zohira).order_by('-created_at') 
    elif request.user.username == 'vladimirDeLaHoz':
        obamaCare = ObamaCare.objects.select_related('agent','client').annotate(
            truncated_agent_usa=Substr('agent_usa', 1, 8)).filter(is_active = True, agent_usa = vladimir).order_by('-created_at')
    else:
        obamaCare = ObamaCare.objects.select_related('agent', 'client').annotate(
            truncated_agent_usa=Substr('agent_usa', 1, 8)).filter(is_active = True).order_by('-created_at')      


    return render(request, 'table/clientObamacare.html', {'obamacares':obamaCare})

@login_required(login_url='/login')
def clientSupp(request):

    roleAuditar = ['S', 'C','SUPP', 'AU']
    
    if request.user.role in roleAuditar:
        supp = Supp.objects.select_related('agent','client').filter(is_active = True).exclude(status_color = 1).annotate(
            truncated_agent_usa=Substr('agent_usa', 1, 8)).order_by('-created_at')
        suppPay = Supp.objects.select_related('agent','client').filter(is_active = True, status_color = 1 )

        for item in suppPay:
            client_name = item.agent_usa if item.agent_usa else "Sin Name"    
            item.short_name = client_name.split()[0] + " ..." if " " in client_name else client_name

    elif request.user.role == 'Admin':
        supp = Supp.objects.select_related('agent','client').annotate(
            truncated_agent_usa=Substr('agent_usa', 1, 8)).order_by('-created_at')
        suppPay = False
    elif request.user.role in ['A', 'C']:
        supp = Supp.objects.select_related('agent','client').annotate(
            truncated_agent_usa=Substr('agent_usa', 1, 8)).filter(agent = request.user.id, is_active = True).order_by('-created_at')
        suppPay = False

    return render(request, 'table/clientSupp.html', {'supps':supp,'suppPay':suppPay})

def toggleObamaStatus(request, obamacare_id):
    # Obtener el cliente por su ID
    obama = get_object_or_404(ObamaCare, id=obamacare_id)
    
    # Cambiar el estado de is_active (True a False o viceversa)
    obama.is_active = not obama.is_active
    obama.save()  # Guardar los cambios en la base de datos
    
    # Redirigir de nuevo a la página actual con un parámetro de éxito
    return redirect('clientObamacare')

def toggleSuppStatus(request, supp_id):
    # Obtener el cliente por su ID
    supp = get_object_or_404(Supp, id=supp_id)
    
    # Cambiar el estado de is_active (True a False o viceversa)
    supp.is_active = not supp.is_active
    supp.save()  # Guardar los cambios en la base de datos
    
    # Redirigir de nuevo a la página actual con un parámetro de éxito
    return redirect('clientSupp')

def delete_dependent(request, dependent_id):
    if request.method == 'POST':
        try:
            # Buscar y eliminar el dependiente por ID
            dependent = Dependent.objects.get(id=dependent_id)
            dependent.delete()
            return JsonResponse({'success': True})
        except Dependent.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Dependent not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def delete_supp(request, supp_id):
    if request.method == 'POST':
        try:
            # Buscar y eliminar el dependiente por ID
            supp = Supp.objects.get(id=supp_id)
            supp.delete()
            return JsonResponse({'success': True})
        except Supp.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Dependent not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def clean_field_to_null(value):
    """
    Limpia el valor de un campo. Si el valor está vacío (cadena vacía, None o solo espacios),
    devuelve `None` para que se guarde como NULL en la base de datos.
    """
    if value == '' or value is None or value.strip() == '':
        return None
    return value

def clean_fields_to_null(request, field_names):
    """
    Limpia un conjunto de campos obtenidos desde `request.POST`, 
    convirtiendo los valores vacíos en `None` (NULL en la base de datos).
    Devuelve un diccionario con los campos limpiados.
    """
    cleaned_data = {}
    for field in field_names:
        value = request.POST.get(field)
        cleaned_data[field] = clean_field_to_null(value)
    return cleaned_data

def editClient(request,client_id):

    # Campos de Client
    client_fields = [
        'agent_usa', 'first_name', 'last_name', 'phone_number', 'email', 'address', 'zipcode',
        'city', 'state', 'county', 'sex', 'old', 'migration_status', 'apply'
    ]
    
    #formateo de fecha para guardalar como se debe en BD ya que la obtengo USA
    fecha_str = request.POST.get('date_birth')  # Formato MM/DD/YYYY
    # Conversión solo si los valores no son nulos o vacíos
    if fecha_str not in [None, '']:
        dateNew = datetime.strptime(fecha_str, '%m/%d/%Y').date()
    else:
        dateNew = None
    

    # Limpiar los campos de Client convirtiendo los vacíos en None
    cleaned_client_data = clean_fields_to_null(request, client_fields)

    # Convierte a mayúsculas los campos necesarios
    fields_to_uppercase = ['first_name', 'last_name', 'address', 'city', 'county']
    for field in fields_to_uppercase:
        if field in cleaned_client_data and cleaned_client_data[field]:
            cleaned_client_data[field] = cleaned_client_data[field].upper()


    # Actualizar Client
    client = Client.objects.filter(id=client_id).update(
        agent_usa=cleaned_client_data['agent_usa'],
        first_name=cleaned_client_data['first_name'],
        last_name=cleaned_client_data['last_name'],
        phone_number=cleaned_client_data['phone_number'],
        email=cleaned_client_data['email'],
        address=cleaned_client_data['address'],
        zipcode=cleaned_client_data['zipcode'],
        city=cleaned_client_data['city'],
        state=cleaned_client_data['state'],
        county=cleaned_client_data['county'],
        sex=cleaned_client_data['sex'],
        old=cleaned_client_data['old'],
        date_birth=dateNew,
        apply=cleaned_client_data['apply'],
        migration_status=cleaned_client_data['migration_status']
    )

    return client

@login_required(login_url='/login')
def editClientObama(request, obamacare_id):
    obamacare = ObamaCare.objects.select_related('agent', 'client').filter(id=obamacare_id).first()
    dependents = Dependent.objects.select_related('obamacare').filter(obamacare=obamacare)
    letterCard = LettersCard.objects.filter(obama = obamacare_id).first()
    apppointment = AppointmentClient.objects.select_related('obama','agent_create').filter(obama = obamacare_id)
    userCarrier = UserCarrier.objects.filter(obama = obamacare_id).first()

    if letterCard and letterCard.letters and letterCard.card: 
        newLetterCard = True
    else: 
        newLetterCard = False

    #Obtener todos los registros de meses pagados de la poliza
    monthsPaid = Payments.objects.filter(obamaCare_id=obamacare.id)

    #calculo de Status
    obamaStatus = True if obamacare.status == 'ACTIVE' else False

    #Obtener todo los meses en ingles
    monthInEnglish = [calendar.month_name[i] for i in range(1, 13)]

    newApppointment = True if apppointment else False
    
    RoleAuditar = [
        obamacare.policyNumber, 
        obamaStatus, 
        obamacare.doc_migration, 
        userCarrier,
        newLetterCard,
        newApppointment
    ]

    c = 0
    for item in RoleAuditar: 
        if item and item != 'None':
            c += 1

    percentage = int(c/6*100)

    if obamacare and obamacare.client:
        social_number = obamacare.client.social_security  # Campo real del modelo
        # Asegurarse de que social_number no sea None antes de formatear
        if social_number:
            formatted_social = f"xxx-xx-{social_number[-4:]}"  # Obtener el formato deseado
        else:
            formatted_social = "N/A"  # Valor predeterminado si no hay número disponible
    else:
        formatted_social = "N/A"
        social_number = None

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        action = request.POST.get('action')
        if action == 'validate_key':
            provided_key = request.POST.get('key')
            correct_key = 'Sseguros22@'  # Cambia por tu lógica segura

            if provided_key == correct_key and social_number:
                return JsonResponse({'status': 'success', 'social': social_number})
            else:
                return JsonResponse({'status': 'error', 'message': 'Clave incorrecta o no hay número disponible'})
    
    obsObama = ObservationAgent.objects.filter(id_obamaCare=obamacare_id)  
    users = User.objects.filter(role='C')
    list_drow = DropDownList.objects.filter(profiling_obama__isnull=False)
    obsCus = ObservationCustomer.objects.select_related('agent').filter(client_id=obamacare.client.id)
    consent = Consents.objects.filter(obamacare = obamacare_id )
    income = IncomeLetter.objects.filter(obamacare = obamacare_id)
    document = DocumentsClient.objects.filter(client = obamacare.client)
    documentObama = DocumentObama.objects.filter(obama = obamacare_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_obamacare':

            editClient(request, obamacare.client.id)
            dependents= editDepentsObama(request, obamacare_id)

            usernameCarrier(request, obamacare.id)

            # Campos de ObamaCare
            obamacare_fields = [
                'taxes', 'planName', 'carrierObama', 'profiling', 'subsidy', 'ffm', 'required_bearing',
                'doc_income', 'doc_migration', 'statusObama', 'work', 'date_effective_coverage',
                'date_effective_coverage_end', 'observationObama', 'agent_usa_obamacare','policyNumber','premium'
            ]
            
            # Limpiar los campos de ObamaCare convirtiendo los vacíos en None
            cleaned_obamacare_data = clean_fields_to_null(request, obamacare_fields)

            # Convierte a mayúsculas los campos necesarios
            fields_to_uppercase = ['planName']
            for field in fields_to_uppercase:
                if field in cleaned_obamacare_data and cleaned_obamacare_data[field]:
                    cleaned_obamacare_data[field] = cleaned_obamacare_data[field].upper()

            #formateo de fecha para guardalar como se debe en BD ya que la obtengo USA
            date_bearing = request.POST.get('date_bearing')  # Formato MM/DD/YYYY
            date_effective_coverage = request.POST.get('date_effective_coverage')  # Formato MM/DD/YYYY
            date_effective_coverage_end = request.POST.get('date_effective_coverage_end')  # Formato MM/DD/YYYY

            # Conversión solo si los valores no son nulos o vacíos
            if date_bearing not in [None, '']:
                date_bearing_new = datetime.strptime(date_bearing, '%m/%d/%Y').date()
            else:
                date_bearing_new = None

            if date_effective_coverage not in [None, '']:
                date_effective_coverage_new = datetime.strptime(date_effective_coverage, '%m/%d/%Y').date()
            else:
                date_effective_coverage_new = None

            if date_effective_coverage_end not in [None, '']:
                date_effective_coverage_end_new = datetime.strptime(date_effective_coverage_end, '%m/%d/%Y').date()
            else:
                date_effective_coverage_end_new = None

            # Recibir el valor seleccionado del formulario
            selected_profiling = request.POST.get('statusObama')

            sw = True

            # Recorrer los usuarios
            for list_drows in list_drow:
                # Comparar el valor seleccionado con el username de cada usuario
                if selected_profiling == 'ACTIVE':
                    color = 3
                    sw = False
                    break  # Si solo te interesa el primer match, puedes salir del bucle
            
            for list_drows in list_drow:
                if selected_profiling == list_drows.profiling_obama:
                    if selected_profiling != 'ACTIVE':
                        color = 2
                        sw = False
                        break
            
            
            statusRed = ['CANCELED','SALE FALL','PRICING ISSUE','OTHER AGENT','CUSTOMER CANCELED','OTHER PARTY']

            if selected_profiling in statusRed:
                sw = False
                color = 4     

            if cleaned_obamacare_data['profiling'] is not None:
                profiling_date = timezone.now().date()
                profiling = cleaned_obamacare_data['profiling']
            else:
                profiling_date = obamacare.profiling_date
                profiling = obamacare.profiling


            if selected_profiling is not None:  # Solo actualizamos profiling_date si profiling no es None                 
                statusObama = cleaned_obamacare_data['statusObama']
            else:
                statusObama = obamacare.status  # Mantener el valor anterior si profiling es None                 
                sw = False

            if sw :
                color = 1   

            # Actualizar ObamaCare
            ObamaCare.objects.filter(id=obamacare_id).update(
                taxes=cleaned_obamacare_data['taxes'],
                agent_usa=cleaned_obamacare_data['agent_usa_obamacare'],
                plan_name=cleaned_obamacare_data['planName'],
                carrier=cleaned_obamacare_data['carrierObama'],
                profiling=profiling,
                policyNumber=cleaned_obamacare_data['policyNumber'],
                profiling_date=profiling_date,  # Se actualiza solo si profiling no es None - DannyZz
                subsidy=cleaned_obamacare_data['subsidy'],
                ffm=int(cleaned_obamacare_data['ffm']) if cleaned_obamacare_data['ffm'] else None,
                required_bearing=cleaned_obamacare_data['required_bearing'],
                date_bearing=date_bearing_new,
                doc_income=cleaned_obamacare_data['doc_income'],
                status_color = color,
                doc_migration=cleaned_obamacare_data['doc_migration'],
                status=statusObama,
                work=cleaned_obamacare_data['work'],
                premium=cleaned_obamacare_data['premium'],
                date_effective_coverage=date_effective_coverage_new,
                date_effective_coverage_end=date_effective_coverage_end_new,
                observation=cleaned_obamacare_data['observationObama']
            )
           
            #obtener informacion para guardarla en modelo de cartas y tarjetas del cliente
            lettersPost = request.POST.get('letters', 'false').lower() == "true"
            cardsPost = request.POST.get('card', 'false').lower() == "true"
            idPost = request.POST.get('letterCardID') 

            if lettersPost: 
                dateLetters = letterCard.dateLetters
                letters = letterCard.letters
            else:
                dateLetters = timezone.now().date() 
                letters = request.POST.get('letters')

            if cardsPost: 
                dateCard = letterCard.dateCard
                cards = letterCard.card
            else:
                dateCard = timezone.now().date()
                cards = request.POST.get('cards')  

            if idPost:

                LettersCard.objects.filter(id = idPost).update(
                obama=obamacare,
                agent_create=request.user,
                letters=letters,
                dateLetters = dateLetters,
                card=cards,
                dateCard = dateCard )

            else:

                LettersCard.objects.create(
                obama=obamacare,
                agent_create=request.user,
                letters=letters,
                dateLetters = dateLetters,
                card=cards,
                dateCard = dateCard )


            return redirect('clientObamacare')

        elif action == 'save_observation_agent':
            
            obs = request.POST.get('obs_agent')

            if obs:
                id_client = request.POST.get('id_client')
                client = Client.objects.get(id=id_client)
                id_obama = ObamaCare.objects.get(id=obamacare_id)
                id_user = request.user

                # Crear y guardar la observación
                ObservationAgent.objects.create(
                    id_client=client,
                    id_obamaCare=id_obama,
                    id_user=id_user,
                    content=obs
                )
            
            return redirect('clientObamacare')      
        
    obamacare.subsidy = f"{float(obamacare.subsidy):.2f}"
    obamacare.premium = f"{float(obamacare.premium):.2f}"
    
    context = {
        'obamacare': obamacare,
        'formatted_social':formatted_social,
        'users': users,
        'obsObamaText': '\n'.join([obs.content for obs in obsObama]),
        'obsCustomer': obsCus,
        'list_drow': list_drow,
        'dependents' : dependents,
        'consent': consent,
        'income': income,
        'document' : document,
        'documentObama' : documentObama,
        'percentage': percentage,
        'letterCard': letterCard,
        'apppointment' : apppointment,
        'userCarrier': userCarrier,
        'c':c,
        'monthInEnglish':monthInEnglish,
        'monthsPaid':monthsPaid,
    }

    return render(request, 'edit/editClientObama.html', context)

@csrf_exempt
def fetchPaymentsMonth(request):
    form = PaymentsForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            payment = form.save(commit=False)
            payment.agent = request.user
            payment.save()
            return JsonResponse({'success': True, 'message': 'Payment creado correctamente', 'role': request.user.role})
        else:
            # Si el formulario no es válido, devolvemos los errores en formato JSON
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            obamaCare = data.get('obamaCare')
            month = data.get('month')

            # Buscar y eliminar el pago
            payment = Payments.objects.filter(obamaCare=obamaCare, month=month).first()
            if payment:
                payment.delete()
                return JsonResponse({'success': True, 'message': 'Payment eliminado correctamente'})
            else:
                return JsonResponse({'success': False, 'message': 'Payment no encontrado'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

def usernameCarrier(request, obamacare):

    obama = ObamaCare.objects.filter(id=obamacare).first()   
    id = request.POST.get('usernameCarrierID') 
    if id: userrCarrier = UserCarrier.objects.filter(id = id)
    username_carrier = request.POST.get('usernameCarrier') 
    password_carrier = request.POST.get('passwordCarrier')  

    if username_carrier is not None and password_carrier is not None:

        # Conversión solo si los valores no son nulos o vacíos
        if username_carrier is not None and password_carrier is not None:
            date = timezone.now().date()
        else:
            username_carrier = userrCarrier.username_carrier
            password_carrier = userrCarrier.password_carrier
            date = userrCarrier.dateUserCarrier

        if id:
            UserCarrier.objects.filter(id = id).update(
            obama = obama,
            agent_create=request.user,
            username_carrier=username_carrier,
            password_carrier = password_carrier,
            dateUserCarrier=date )
        
        

        else:

            UserCarrier.objects.create(
            obama=obama,
            agent_create=request.user,
            username_carrier=username_carrier,
            password_carrier = password_carrier,
            dateUserCarrier=date  )

@login_required(login_url='/login')
def editClientSupp(request, supp_id):

    supp = Supp.objects.select_related('client','agent').filter(id=supp_id).first()
    obsSupp = ObservationAgent.objects.filter(id_supp=supp_id)
    obsCus = ObservationCustomer.objects.select_related('agent').filter(client_id=supp.client.id)
    list_drow = DropDownList.objects.filter(profiling_supp__isnull=False)

    # Obtener el objeto Supp que tiene el id `supp_id`
    supp_instance = Supp.objects.get(id=supp_id)

    # Obtener todos los dependientes asociados a este Supp
    dependents = supp_instance.dependents.all()
    
    action = request.POST.get('action')

    if supp and supp.client:
        social_number = supp.client.social_security  # Campo real del modelo
        # Asegurarse de que social_number no sea None antes de formatear
        if social_number:
            formatted_social = f"xxx-xx-{social_number[-4:]}"  # Obtener el formato deseado
        else:
            formatted_social = "N/A"  # Valor predeterminado si no hay número disponible
    else:
        formatted_social = "N/A"
        social_number = None

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        action = request.POST.get('action')
        if action == 'validate_key':
            provided_key = request.POST.get('key')
            correct_key = 'Sseguros22@'  # Cambia por tu lógica segura

            if provided_key == correct_key and social_number:
                return JsonResponse({'status': 'success', 'social': social_number})
            else:
                return JsonResponse({'status': 'error', 'message': 'Clave incorrecta o no hay número disponible'})

    if request.method == 'POST':

        if action == 'save_supp':

            editClient(request, supp.client.id)
            dependents= editDepentsSupp(request, supp_id)

            #formateo de fecha para guardalar como se debe en BD ya que la obtengo USA
            date_effective_coverage = request.POST.get('date_effective_coverage')  # Formato MM/DD/YYYY
            date_effective_coverage_end = request.POST.get('date_effective_coverage_end')  # Formato MM/DD/YYYY
            effectiveDateSupp = request.POST.get('effectiveDateSupp')  # Formato MM/DD/YYYY


            # Si la fecha no viene vacia la convertimos y si viene vacia la colocamos null
            if date_effective_coverage not in [None, '']:
                date_effective_coverage_new = datetime.strptime(date_effective_coverage, '%m/%d/%Y').date()
            else:
                date_effective_coverage_new = None

            if date_effective_coverage_end not in [None, '']:
                date_effective_coverage_end_new = datetime.strptime(date_effective_coverage_end, '%m/%d/%Y').date()
            else:
                date_effective_coverage_end_new = None

            if effectiveDateSupp not in [None, '']:
                effectiveDateSupp_new = datetime.strptime(effectiveDateSupp, '%m/%d/%Y').date()
            else:
                effectiveDateSupp_new = None
            
                
            # Campos de Supp
            supp_fields = [
                'effectiveDateSupp', 'carrierSuple', 'premiumSupp', 'preventiveSupp', 'coverageSupp', 'deducibleSupp',
                'statusSupp', 'typePaymeSupp', 'observationSuple', 'agent_usa','policyNumber'
            ]
            
            # Limpiar los campos de ObamaCare convirtiendo los vacíos en None
            cleaned_supp_data = clean_fields_to_null(request, supp_fields)

            # Recibir el valor seleccionado del formulario
            selected_status= request.POST.get('statusSupp')

            color = 1         

            for list_drow in list_drow:
                if selected_status == list_drow.profiling_supp:
                    if selected_status != 'ACTIVE':
                        color = 2
                        break         
                    if selected_status == 'ACTIVE':
                        color = 3 
                        break  
            
            statusRed = ['BANK DRAFT CANCELLED - CUSTOMER REQUEST','TERM - INSURED REQUEST','TERM - LAPSE NON PAYMENT'
                         ,'AUTOMATIC TERMINATION','TERM - INSURED REQUEST (PAYMENT ERROR)','WITHDRAWN (PAYMENT ERROR)']

            if selected_status in statusRed:
                color = 4   


            # Actualizar Supp
            Supp.objects.filter(id=supp_id).update(
                effective_date=effectiveDateSupp_new,
                agent_usa=cleaned_supp_data['agent_usa'],
                company=cleaned_supp_data['carrierSuple'],
                premium=cleaned_supp_data['premiumSupp'],
                preventive=cleaned_supp_data['preventiveSupp'],
                coverage=cleaned_supp_data['coverageSupp'],
                deducible=cleaned_supp_data['deducibleSupp'],
                status=cleaned_supp_data['statusSupp'],
                policyNumber=cleaned_supp_data['policyNumber'],
                status_color=color,
                date_effective_coverage=date_effective_coverage_new,
                date_effective_coverage_end=date_effective_coverage_end_new,
                payment_type=cleaned_supp_data['typePaymeSupp'],
                observation=cleaned_supp_data['observationSuple']
            )

            return redirect('clientSupp')  
              
        elif action == 'save_supp_agent':

            obs = request.POST.get('obs_agent')

            if obs:
                id_client = request.POST.get('id_client')
                client = Client.objects.get(id=id_client)
                id_supp = Supp.objects.get(id=supp_id)
                id_user = request.user

                # Crear y guardar la observación
                ObservationAgent.objects.create(
                    id_client=client,
                    id_supp=id_supp,
                    id_user=id_user,
                    content=obs
                )
            
                return redirect('clientSupp')
            
    supp.premium = f"{float(supp.premium):.2f}"


    context = {
        'supps': supp,
        'formatted_social':formatted_social,
        'dependents': dependents,
        'obsSuppText': '\n'.join([obs.content for obs in obsSupp]),
        'obsCustomer': obsCus,
        'list_drow': list_drow
    }
    
    return render(request, 'edit/editClientSupp.html', context)

def editDepentsObama(request, obamacare_id):
    # Obtener todos los dependientes asociados al ObamaCare
    dependents = Dependent.objects.filter(obamacare=obamacare_id)    

    if request.method == "POST":
        for dependent in dependents:

            # Resetear la fecha guardarla como se debe porque la traigo en formato USA
            date_birth = request.POST.get(f'dateBirthDependent_{dependent.id}')

            # Conversión solo si los valores no son nulos o vacíos
            if date_birth not in [None, '']:
                date_birth_new = datetime.strptime(date_birth, '%m/%d/%Y').date()
            else:
                date_birth_new = None
            

            # Obtener los datos enviados por cada dependiente
            dependent_id = request.POST.get(f'dependentId_{dependent.id}')
            name = request.POST.get(f'nameDependent_{dependent.id}')
            apply = request.POST.get(f'applyDependent_{dependent.id}')
            kinship = request.POST.get(f'kinship_{dependent.id}')
            migration_status = request.POST.get(f'migrationStatusDependent_{dependent.id}')
            sex = request.POST.get(f'sexDependent_{dependent.id}')
            
            # Verificar si el ID coincide
            if dependent.id == int(dependent_id):  # Verificamos si el ID coincide
                
                # Verificamos que todos los campos tengan datos
                if name and apply and kinship and date_birth and migration_status and sex:
                    dependent.name = name
                    dependent.apply = apply
                    dependent.kinship = kinship
                    dependent.date_birth = date_birth_new
                    dependent.migration_status = migration_status
                    dependent.sex = sex

                    dependent.save()

    # Retornar todos los dependientes actualizados (o procesados)
    return dependents

def editDepentsSupp(request, supp_id):
    
    # Obtener el objeto Supp que tiene el id `supp_id`
    supp_instance = Supp.objects.get(id=supp_id)

    # Obtener todos los dependientes asociados a este Supp
    dependents = supp_instance.dependents.all()

    if request.method == "POST":
        for dependent in dependents:

            date_birth = request.POST.get(f'dateBirthDependent_{dependent.id}')
            dateNew = datetime.strptime(date_birth, '%m/%d/%Y').date()

            # Aquí obtenemos los datos enviados a través del formulario para cada dependiente
            dependent_id = request.POST.get(f'dependentId_{dependent.id}')  # Cambiar a 'dependentId_{dependent.id}'
            
            if dependent_id is None:
                continue  # Si no se encuentra el dependentId, continuamos con el siguiente dependiente
            
            # Verificamos si el dependent_id recibido coincide con el ID del dependiente actual
            if dependent.id == int(dependent_id):
                name = request.POST.get(f'nameDependent_{dependent.id}')
                apply = request.POST.get(f'applyDependent_{dependent.id}')
                kinship = request.POST.get(f'kinship_{dependent.id}')
                date_birth = request.POST.get(f'dateBirthDependent_{dependent.id}')
                migration_status = request.POST.get(f'migrationStatusDependent_{dependent.id}')
                sex = request.POST.get(f'sexDependent_{dependent.id}')
                
                
                # Verificamos si los demás campos existen y no son None
                if name and apply and kinship and date_birth and migration_status and sex:
                    # Actualizamos los campos del dependiente
                    dependent.name = name
                    dependent.apply = apply
                    dependent.kinship = kinship
                    dependent.date_birth = dateNew
                    dependent.migration_status = migration_status
                    dependent.sex = sex
                    
                    # Guardamos el objeto dependiente actualizado
                    dependent.save()
    
    # Retornar los dependientes que fueron actualizados o procesados
    return dependents

@login_required(login_url='/login') 
def formCreateAlert(request):

    if request.method == 'POST':
        formClient = ClientAlertForm(request.POST)
        if formClient.is_valid():
            alert = formClient.save(commit=False)
            alert.agent = request.user
            alert.is_active = True
            alert.save()
            return redirect('formCreateAlert')  # Cambia a tu página de éxito

    return render(request, 'forms/formCreateAlert.html')

@login_required(login_url='/login')    
def tableAlert(request):

    roleAuditar = ['S', 'C',  'AU']
    
    if request.user.role in roleAuditar:
        alert = ClientAlert.objects.select_related('agent').annotate(
            truncated_contect=Substr('content', 1, 20)).filter(is_active = True)
    elif request.user.role == 'Admin':
        alert = ClientAlert.objects.select_related('agent').annotate(
            truncated_contect=Substr('content', 1, 20))
    elif request.user.role == 'A':
        alert = ClientAlert.objects.select_related('agent').annotate(
            truncated_contect=Substr('content', 1, 20)).filter(agent = request.user.id, is_active = True)
    
    return render(request, 'table/alert.html', {'alertC':alert})

def toggleAlert(request, alertClient_id):
    # Obtener el cliente por su ID
    alert = get_object_or_404(ClientAlert, id=alertClient_id)
    
    # Cambiar el estado de is_active (True a False o viceversa)
    alert.is_active = not alert.is_active
    alert.save()  # Guardar los cambios en la base de datos
    
    # Redirigir de nuevo a la página actual con un parámetro de éxito
    return redirect('alert')

def editAlert(request, alertClient_id):

    alert = ClientAlert.objects.select_related('agent').filter(id=alertClient_id).first()

    if request.method == 'POST':

        alert_fields = ['name_client', 'phone_number', 'datetime', 'content' ]

        # Limpiar los campos 
        cleaned_alert_data = clean_fields_to_null(request, alert_fields)

        ClientAlert.objects.filter(id=alertClient_id).update(
                name_client=cleaned_alert_data['name_client'],
                phone_number=cleaned_alert_data['phone_number'],
                datetime=cleaned_alert_data['datetime'],
                content=cleaned_alert_data['content']
            )
        return redirect('alert')

    return render(request, 'edit/editAlert.html', {'editAlert':alert} )

@login_required(login_url='/login') 
def formCreateUser(request):

    users = User.objects.all()

    roles = User.ROLES_CHOICES  # Obtén las opciones dinámicamente desde el modelo

    if request.method == 'POST':
        first_name = request.POST.get('first_name').upper()
        last_name = request.POST.get('last_name').upper()
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        try:
            # Validar si el username ya existe
            if User.objects.filter(username=username).exists():
                return render(request, 'forms/formCreateUser.html', {'msg':f'El nombre de usuario "{username}" ya está en uso.','users':users, 'type':'error'})
            
            # Crear el usuario si no existe el username
            user = User.objects.create(
                username=username,
                password=make_password(password),  # Encriptar la contraseña
                last_name=last_name,
                first_name=first_name,
                role=role
            )

            context = {
                'msg':f'Usuario {user.username} creado con éxito.',
                'users':users,
                'type':'good',
                'roles': roles
            }

            return render(request, 'forms/formCreateUser.html', context)

        except Exception as e:
            return HttpResponse(str(e))
            
    return render(request, 'forms/formCreateUser.html',{'users':users,'roles': roles})

@login_required(login_url='/login') 
def editUser(request, user_id):
    # Obtener el usuario a editar o devolver un 404 si no existe
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Recuperar los datos del formulario
        first_name = request.POST.get('first_name', user.first_name)
        last_name = request.POST.get('last_name', user.last_name)
        email = request.POST.get('email', user.email)
        username = request.POST.get('username', user.username)
        password = request.POST.get('password', None)
        role = request.POST.get('role', user.role)
        is_active = request.POST.get('is_active', user.is_active)

        # Verificar si el nuevo username ya existe en otro usuario
        if username != user.username and User.objects.filter(username=username).exists():
            return JsonResponse({'error': f'El nombre de usuario "{username}" ya está en uso.'}, status=400)

        # Actualizar los datos del usuario
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = username
        user.role = role
        user.is_active = is_active

        # Actualizar la contraseña si se proporciona una nueva
        if password:
            user.password = make_password(password)

        # Guardar los cambios
        user.save()

        # Redirigir a otra vista o mostrar un mensaje de éxito
        return redirect('formCreateUser')  

    # Renderizar el formulario con los datos actuales del usuario
    context = {'users': user}
    return render(request, 'edit/editUser.html', context)

@login_required(login_url='/login') 
def toggleUser(request, user_id):
    # Obtener el cliente por su ID
    user = get_object_or_404(User, id=user_id)
    
    # Cambiar el estado de is_active (True a False o viceversa)
    user.is_active = not user.is_active
    user.save()  # Guardar los cambios en la base de datos
    
    # Redirigir de nuevo a la página actual con un parámetro de éxito
    return redirect('formCreateUser')

@login_required(login_url='/login') 
def saveCustomerObservationACA(request):
    if request.method == "POST":
        content = request.POST.get('textoIngresado')
        plan_id = request.POST.get('plan_id')
        type_plan = request.POST.get('type_plan')
        typeCall = request.POST.get('typeCall')        

        # Obtenemos las observaciones seleccionadas
        observations = request.POST.getlist('observaciones[]')  # Lista de valores seleccionados
        
        # Convertir las observaciones a una cadena (por ejemplo, separada por comas o saltos de línea)
        typification_text = ", ".join(observations)  # Puedes usar "\n".join(observations) si prefieres saltos de línea

    
        plan = ObamaCare.objects.get(id=plan_id)

        if content.strip():  # Validar que el texto no esté vacío
            ObservationCustomer.objects.create(
                client=plan.client,
                agent=request.user,
                id_plan=plan.id,
                type_police=type_plan,
                typeCall=typeCall,
                typification=typification_text, # Guardamos las observaciones en el campo 'typification'
                content=content
            )
            messages.success(request, "Observación guardada exitosamente.")
        else:
            messages.error(request, "El contenido de la observación no puede estar vacío.")

        return redirect('editClientObama', plan.id)       
        
    else:
        return HttpResponse("Método no permitido.", status=405)

@login_required(login_url='/login') 
def saveCustomerObservationSupp(request):
    if request.method == "POST":
        content = request.POST.get('textoIngresado')
        plan_id = request.POST.get('plan_id')
        type_plan = request.POST.get('type_plan')
        typeCall = request.POST.get('typeCall')        

        # Obtenemos las observaciones seleccionadas
        observations = request.POST.getlist('observaciones[]')  # Lista de valores seleccionados
        
        # Convertir las observaciones a una cadena (por ejemplo, separada por comas o saltos de línea)
        typification_text = ", ".join(observations)  # Puedes usar "\n".join(observations) si prefieres saltos de línea

        plan = Supp.objects.get(id=plan_id) 

        if content.strip():  # Validar que el texto no esté vacío
            ObservationCustomer.objects.create(
                client=plan.client,
                agent=request.user,
                id_plan=plan.id,
                type_police=type_plan,
                typeCall=typeCall,
                typification=typification_text, # Guardamos las observaciones en el campo 'typification'
                content=content
            )
            messages.success(request, "Observación guardada exitosamente.")
        else:
            messages.error(request, "El contenido de la observación no puede estar vacío.")

        return redirect('editClientSupp', plan.id)        
        
    else:
        return HttpResponse("Método no permitido.", status=405)

@login_required(login_url='/login') 
def typification(request):
        
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    agent = User.objects.filter(role__in=['A', 'C'])
    
    # Consulta base
    typification = ObservationCustomer.objects.select_related('agent', 'client').filter(is_active = True)

    # Si no se proporcionan fechas, mostrar registros del mes actual   
    # Obtener el primer día del mes actual con zona horaria
    today = timezone.now()
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Obtener el último día del mes actual
    if today.month == 12:
        # Si es diciembre, el último día será el 31
        last_day_of_month = today.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
    else:
        # Para otros meses, usar el día anterior al primer día del siguiente mes
        last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month+1) - timezone.timedelta(seconds=1))
    
    typification = typification.filter(created_at__range=[first_day_of_month, last_day_of_month])

    if request.method == 'POST':

        # Obtener parámetros de fecha del request
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')       
        nameAgent = request.POST.get('agent')
        nameTypification = request.POST.get('typification')

        # Consulta base
        typification = ObservationCustomer.objects.select_related('agent', 'client').filter(is_active = True)   
        
     
        # Convertir fechas a objetos datetime con zona horaria
        start_date = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )
        
        typification = typification.filter(
            created_at__range=[start_date, end_date],
            agent = nameAgent,
            typification__contains = nameTypification
        )

        # Ordenar por fecha de creación descendente
        typification = typification.order_by('-created_at')

        return render(request, 'table/typification.html', {
            'typification': typification,
            'start_date': start_date,
            'end_date': end_date,
            'agents' : agent
        })

    return render(request, 'table/typification.html', {
            'typification': typification,
            'start_date': start_date,
            'end_date': end_date,
            'agents' : agent
        })

def customerPerformance(request):

    if request.method == 'POST':
        # Convertir fechas a objetos datetime con zona horaria
        start_date = timezone.make_aware(
            datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date = timezone.make_aware(
            datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )
    else:
        now = datetime.now()

        # Primer día del mes actual
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Último día del mes actual
        next_month = now.replace(day=28) + timedelta(days=4)  # Garantiza que pasamos al siguiente mes
        end_date = next_month.replace(day=1, hour=23, minute=59, second=59, microsecond=999999) - timedelta(days=1)

    obamacare = ObamaCare.objects.filter(created_at__range=(start_date, end_date), is_active=1)
    totalEnroled = obamacare.exclude(profiling='NO')
    totalNoEnroled = obamacare.filter(profiling='NO').count()
    totalOtherParty = obamacare.filter(status__in=('OTHER PARTY', 'OTHER AGENT')).count()
    enroledActiveCms = totalEnroled.filter(status='ACTIVE').count()
    totalEnroledNoActiveCms = totalEnroled.exclude(status='ACTIVE').count()
    totalActiveCms = obamacare.filter(status='ACTIVE').count()
    totalNoActiveCms = obamacare.exclude(status='ACTIVE').count()

    documents = DocumentObama.objects.select_related('agent_create').filter(created_at__range=(start_date, end_date))
    appointments = AppointmentClient.objects.select_related('agent_create').filter(created_at__range=(start_date, end_date))
    payments = Payments.objects.select_related('agent').filter(created_at__range=(start_date, end_date))

    # Obtener agentes Customer, excluyendo a Maria Tinoco y Carmen Rodriguez
    agents = User.objects.filter(role='C', is_active=1).exclude(username__in=('MariaCaTi', 'CarmenR'))
    agent_performance = {}

    for agent in agents:
        full_name = f"{agent.first_name} {agent.last_name}".strip()
        profilingAgent = obamacare.filter(profiling=full_name)
        enroledActiveCmsPerAgent = profilingAgent.filter(status='ACTIVE').count()
        enroledNoActiveCmsPerAgent = profilingAgent.exclude(status='ACTIVE').count()
        percentageEnroledActiveCms = format_decimal(
            (enroledActiveCmsPerAgent / profilingAgent.count()) * 100
        ) if profilingAgent.count() else 0

        # Inicializar la clave si no existe
        if full_name not in agent_performance:
            agent_performance[full_name] = {
                'totalEnroled': 0,
                'percentageEnroled': 0,
                'enroledActiveCms': 0,
                'percentageEnroledActiveCms': 0,
                'enroledNoActiveCms': 0,
                'percentageEnroledNoActiveCms': 0,
                'percentageTotalActiveCms': 0,
                'percentageTotalNoActiveCms': 0,
                'documents': 0,
                'appointments': 0,
                'payments': 0,
                'personalGoal': 0
            }

        # Asignar valores con validación de división por cero
        agent_performance[full_name]['totalEnroled'] = profilingAgent.count()
        agent_performance[full_name]['percentageEnroled'] = format_decimal(
            (profilingAgent.count() / obamacare.count()) * 100
        ) if obamacare.count() else 0
        agent_performance[full_name]['enroledActiveCms'] = enroledActiveCmsPerAgent
        agent_performance[full_name]['percentageEnroledActiveCms'] = percentageEnroledActiveCms
        agent_performance[full_name]['enroledNoActiveCms'] = enroledNoActiveCmsPerAgent
        agent_performance[full_name]['percentageEnroledNoActiveCms'] = format_decimal(
            (enroledNoActiveCmsPerAgent / profilingAgent.count()) * 100
        ) if profilingAgent.count() else 0
        agent_performance[full_name]['percentageTotalActiveCms'] = format_decimal(
            (enroledActiveCmsPerAgent / obamacare.count()) * 100
        ) if obamacare.count() else 0
        agent_performance[full_name]['percentageTotalNoActiveCms'] = format_decimal(
            (enroledNoActiveCmsPerAgent / obamacare.count()) * 100
        ) if obamacare.count() else 0

        agent_performance[full_name]['documents'] = documents.filter(agent_create=agent).count()
        agent_performance[full_name]['appointments'] = appointments.filter(agent_create=agent).count()
        agent_performance[full_name]['payments'] = payments.filter(agent=agent).count()

        #Meta personal
        if percentageEnroledActiveCms == 100 and percentageEnroledActiveCms == 100:
            agent_performance[full_name]['personalGoal'] = 1
        elif percentageEnroledActiveCms > 89.9 and percentageEnroledActiveCms > 89.9:
            agent_performance[full_name]['personalGoal'] = 2
        elif percentageEnroledActiveCms > 79.9 and percentageEnroledActiveCms > 79.9:
            agent_performance[full_name]['personalGoal'] = 3
        else:
            agent_performance[full_name]['personalGoal'] = 4
            


    # Evitar divisiones por cero en todos los cálculos
    obamacare_count = obamacare.count() if obamacare.exists() else 1
    totalEnroled_count = totalEnroled.count() if totalEnroled.exists() else 1

    #Verificacion de bono:
    percentageEnroled = (totalEnroled.count() / obamacare_count) * 100
    percentageEnroledActiveCms = (enroledActiveCms / totalEnroled_count) * 100
    if percentageEnroled > 89.9 and percentageEnroledActiveCms > 89.9:
        groupGoal = 1
    elif percentageEnroled > 79.9 and percentageEnroledActiveCms > 79.9:
        groupGoal = 2
    else:
        groupGoal = 3

    #Diferencia entre total
    totalAgentsPayments = 0
    for agent, details in agent_performance.items():
        totalAgentsPayments += details['payments']

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'totalObamacare': obamacare.count(),
        'totalEnroled': totalEnroled.count(),
        'percentageEnroled': format_decimal(percentageEnroled),
        'totalNoEnroled': format_decimal(totalNoEnroled),
        'percentageNoEnroled': format_decimal((totalNoEnroled / obamacare_count) * 100),
        'totalOtherParty': totalOtherParty,
        'percentageOtherParty': format_decimal((totalOtherParty / obamacare_count) * 100),
        'enroledActiveCms': enroledActiveCms,
        'percentageEnroledActiveCms': format_decimal(percentageEnroledActiveCms),
        'totalEnroledNoActiveCms': totalEnroledNoActiveCms,
        'percentageNoActiveCms': format_decimal((totalEnroledNoActiveCms / totalEnroled_count) * 100),
        'totalActiveCms': totalActiveCms,
        'percentageTotalActiveCms': format_decimal((totalActiveCms / obamacare_count) * 100),
        'totalNoActiveCms': totalNoActiveCms,
        'percentageTotalNoActiveCms': format_decimal((totalNoActiveCms / obamacare_count) * 100),
        'appointmentsTotal':appointments.count(),
        'documentsTotal': documents.count(),
        'paymentsTotal':payments.count(),
        'agentPerformance': agent_performance,

        #Messages
        'totalAgentsPayments':totalAgentsPayments,
        'groupGoal':groupGoal
    }
    return render(request, 'reports/customerPerformance.html', context)

def format_decimal(number):
    # Revisa si el numero es entero y lo devuelve entero
    if number.is_integer():
        return int(number)
    
    # Si es decimal lo devuelve con dos numeros despues del punto
    return round(number, 2)

def get_observation_detail(request, observation_id):
    try:
        # Obtener el registro específico
        observation = ObservationCustomer.objects.select_related('agent', 'client').get(id=observation_id)
        
        # Preparar los datos para el JSON
        data = {
            'agent_name': f"{observation.agent.first_name} {observation.agent.last_name}",
            'client_name': f"{observation.client.first_name} {observation.client.last_name}",
            'type_police': observation.type_police,
            'type_call': observation.typeCall,
            'created_at': observation.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'typification': observation.typification,
            'content': observation.content,
        }
        
        return JsonResponse(data)
    except ObservationCustomer.DoesNotExist:
        return JsonResponse({'error': 'Registro no encontrado'}, status=404)

def toggleTypification(request, typifications_id):
    # Obtener el cliente por su ID
    typi = get_object_or_404(ObservationCustomer, id=typifications_id)
    
    # Cambiar el estado de is_active (True a False o viceversa)
    typi.is_active = not typi.is_active
    typi.save()  # Guardar los cambios en la base de datos
    
    # Redirigir de nuevo a la página actual con un parámetro de éxito
    return redirect('typification')

@login_required(login_url='/login') 
def index(request):
    obama = countSalesObama(request)
    supp = countSalesSupp(request)
    chartOne = chartSaleIndex(request)
    tableStatusAca = tableStatusObama(request)
    tableStatusSup = tableStatusSupp(request)

    # Asegúrate de que chartOne sea un JSON válido
    chartOne_json = json.dumps(chartOne)

    context = {
        'obama':obama,
        'supp':supp,
        'chartOne':chartOne_json,
        'tableStatusObama':tableStatusAca,
        'tableStatusSup':tableStatusSup
    }      

    return render(request, 'dashboard/index.html', context)
 
def countSalesObama(request):

    # Obtener el mes y el año actuales
    now = timezone.now()

    # Calcular el primer día del mes
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Calcular el último día del mes
    last_day = calendar.monthrange(now.year, now.month)[1]  # Obtiene el último día del mes
    end_of_month = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

    roleAuditar = ['S', 'C',  'AU', 'Admin']
    
    if request.user.role in roleAuditar:        
        all = ObamaCare.objects.filter(created_at__gte=start_of_month,created_at__lte=end_of_month,is_active = True).count()
        active = ObamaCare.objects.filter(status_color=3,created_at__gte=start_of_month,created_at__lte=end_of_month,is_active = True).count()
        process = ObamaCare.objects.filter(created_at__gte=start_of_month,created_at__lte=end_of_month,is_active = True).filter(Q(status_color=2) | Q(status_color=1)).count()
        cancell = ObamaCare.objects.filter(status_color=4,created_at__gte=start_of_month,created_at__lte=end_of_month,is_active = True).count()
    elif request.user.role in ['A','SUPP']:
        all = ObamaCare.objects.filter(created_at__gte=start_of_month,created_at__lte=end_of_month).filter(agent = request.user.id, is_active = True ).count()
        active = ObamaCare.objects.filter(status_color=3,created_at__gte=start_of_month,created_at__lte=end_of_month).filter(agent = request.user.id, is_active = True ).count()
        process = ObamaCare.objects.filter(created_at__gte=start_of_month,created_at__lte=end_of_month).filter(Q(status_color=2) | Q(status_color=1)).filter(agent = request.user.id, is_active = True ).count()
        cancell = ObamaCare.objects.filter(status_color=4,created_at__gte=start_of_month,created_at__lte=end_of_month).filter(agent = request.user.id, is_active = True ).count()
       
   
    dicts = {
        'all': all,
        'active':active,
        'process':process,
        'cancell':cancell
    }
    return dicts

def countSalesSupp(request):

    # Obtener el mes y el año actuales
    now = timezone.now()

    # Calcular el primer día del mes
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Calcular el último día del mes
    last_day = calendar.monthrange(now.year, now.month)[1]  # Obtiene el último día del mes
    end_of_month = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

    roleAuditar = ['S', 'C',  'AU', 'Admin']
    
    if request.user.role in roleAuditar:
        all = Supp.objects.filter(created_at__gte=start_of_month,created_at__lte=end_of_month,is_active = True).count()
        active = Supp.objects.filter(status_color=3,created_at__gte=start_of_month,created_at__lte=end_of_month,is_active = True).count()
        process = Supp.objects.filter(created_at__gte=start_of_month,created_at__lte=end_of_month,is_active = True).filter(Q(status_color=2) | Q(status_color=1)).count()
        cancell = Supp.objects.filter(status_color=4,created_at__gte=start_of_month,created_at__lte=end_of_month,is_active = True).count()
    elif request.user.role in ['A','SUPP']:
        all = Supp.objects.filter(created_at__gte=start_of_month,created_at__lte=end_of_month).filter(agent = request.user.id, is_active = True ).count()
        active = Supp.objects.filter(status_color=3,created_at__gte=start_of_month,created_at__lte=end_of_month).filter(agent = request.user.id, is_active = True ).count()
        process = Supp.objects.filter(created_at__gte=start_of_month,created_at__lte=end_of_month).filter(agent = request.user.id, is_active = True ).filter(Q(status_color=2) | Q(status_color=1)).count()
        cancell = Supp.objects.filter(status_color=4,created_at__gte=start_of_month,created_at__lte=end_of_month).filter(agent = request.user.id, is_active = True ).count()


    dicts = {
        'all':all,
        'active':active,
        'process':process,
        'cancell':cancell
    }
    return dicts

def chartSaleIndex(request):
    # Obtener la fecha y hora actual
    now = timezone.now()
    current_month = now.month
    current_year = now.year

    # Calcular inicio y fin del mes actual
    start_of_month = timezone.make_aware(datetime(current_year, current_month, 1), timezone.get_current_timezone())
    last_day_of_month = calendar.monthrange(current_year, current_month)[1]
    end_of_month = timezone.make_aware(
        datetime(current_year, current_month, last_day_of_month, 23, 59, 59), 
        timezone.get_current_timezone()
    )

    # Roles con acceso ampliado
    roleAuditar = ['S', 'Admin']
    excludeUsername = ['admin','Calidad01','Calidad02','mariluz','MariaCaTi','StephanieMkt']

    # Construcción de la consulta basada en el rol del usuario
    if request.user.role in roleAuditar:
        # Para roles con acceso ampliado: consultar datos de todos los usuarios
        users_data = User.objects.annotate(
            obamacare_count=Count('agent_sale_aca', filter=Q(
                agent_sale_aca__status_color=3,
                agent_sale_aca__created_at__gte=start_of_month,
                agent_sale_aca__created_at__lt=end_of_month,
                agent_sale_aca__is_active=True  
            ), distinct=True),
            obamacare_count_total=Count('agent_sale_aca', filter=Q(
                agent_sale_aca__created_at__gte=start_of_month,
                agent_sale_aca__created_at__lt=end_of_month,
                agent_sale_aca__is_active=True  
            ), distinct=True),
            supp_count=Coalesce(Count('agent_sale_supp', filter=Q(
                agent_sale_supp__status_color=3,
                agent_sale_supp__created_at__gte=start_of_month,
                agent_sale_supp__created_at__lt=end_of_month,
                agent_sale_supp__is_active=True
            ), distinct=True), 0),
            supp_count_total=Coalesce(Count('agent_sale_supp', filter=Q(
                agent_sale_supp__created_at__gte=start_of_month,
                agent_sale_supp__created_at__lt=end_of_month,
                agent_sale_supp__is_active=True
            ), distinct=True), 0)
        ).filter(is_active = True).exclude(username__in=excludeUsername).values('first_name', 'obamacare_count', 'obamacare_count_total', 'supp_count', 'supp_count_total')

    elif request.user.role not in roleAuditar:
        # Para usuarios con rol 'A': consultar datos solo para el usuario actual
        users_data = User.objects.filter(id=request.user.id).annotate(
            obamacare_count=Count('agent_sale_aca', filter=Q(
                agent_sale_aca__status_color=3,
                agent_sale_aca__created_at__gte=start_of_month,
                agent_sale_aca__created_at__lt=end_of_month,
                agent_sale_aca__agent=request.user.id,
                agent_sale_aca__is_active=True
            ), distinct=True),
            obamacare_count_total=Count('agent_sale_aca', filter=Q(
                agent_sale_aca__created_at__gte=start_of_month,
                agent_sale_aca__created_at__lt=end_of_month,
                agent_sale_aca__agent=request.user.id,
                agent_sale_aca__is_active=True
            ), distinct=True),
            supp_count=Coalesce(Count('agent_sale_supp', filter=Q(
                agent_sale_supp__status_color=3,
                agent_sale_supp__created_at__gte=start_of_month,
                agent_sale_supp__created_at__lt=end_of_month,
                agent_sale_supp__agent=request.user.id,
                agent_sale_supp__is_active=True
            ), distinct=True), 0),
            supp_count_total=Coalesce(Count('agent_sale_supp', filter=Q(
                agent_sale_supp__created_at__gte=start_of_month,
                agent_sale_supp__created_at__lt=end_of_month,
                agent_sale_supp__agent=request.user.id,
                agent_sale_supp__is_active=True
            ), distinct=True), 0)
        ).values('first_name', 'obamacare_count', 'obamacare_count_total', 'supp_count', 'supp_count_total')

    # Convertir los datos a una lista de diccionarios para su uso
    combined_data = [
        {
            'username': user['first_name'],
            'obamacare_count': user['obamacare_count'],
            'obamacare_count_total': user['obamacare_count_total'],
            'supp_count': user['supp_count'],
            'supp_count_total': user['supp_count_total'],
        }
        for user in users_data
    ]

    return combined_data

def tableStatusObama(request):

    # Obtener la fecha y hora actual
    now = timezone.now()
    current_month = now.month
    current_year = now.year

    # Obtener el primer y último día del mes actual (con zona horaria)
    start_of_month = timezone.make_aware(datetime(current_year, current_month, 1), timezone.get_current_timezone())
    end_of_month = timezone.make_aware(datetime(current_year, current_month + 1, 1), timezone.get_current_timezone()) if current_month < 12 else timezone.make_aware(datetime(current_year + 1, 1, 1), timezone.get_current_timezone())

    roleAuditar = ['S', 'C', 'AU', 'Admin']

    # Construcción de la consulta basada en el rol del usuario
    if request.user.role in roleAuditar:

        # Realizamos la consulta y agrupamos por el campo 'profiling'
        result = ObamaCare.objects.filter(created_at__gte=start_of_month, created_at__lt=end_of_month,is_active = True).values('profiling').annotate(count=Count('profiling')).order_by('profiling')
    
    elif request.user.role in ['A','SUPP']:
        
        # Realizamos la consulta y agrupamos por el campo 'profiling'
        result = ObamaCare.objects.filter(created_at__gte=start_of_month, created_at__lt=end_of_month, is_active = True).values('profiling').filter(agent=request.user.id).annotate(count=Count('profiling')).order_by('profiling')
    

    return result

def tableStatusSupp(request):

    # Obtener la fecha y hora actual
    now = timezone.now()
    current_month = now.month
    current_year = now.year

    # Obtener el primer y último día del mes actual (con zona horaria)
    start_of_month = timezone.make_aware(datetime(current_year, current_month, 1), timezone.get_current_timezone())
    end_of_month = timezone.make_aware(datetime(current_year, current_month + 1, 1), timezone.get_current_timezone()) if current_month < 12 else timezone.make_aware(datetime(current_year + 1, 1, 1), timezone.get_current_timezone())

    # Roles con acceso ampliado
    roleAuditar = ['S', 'C', 'AU', 'Admin']

    # Construcción de la consulta basada en el rol del usuario
    if request.user.role in roleAuditar:
        # Realizamos la consulta y agrupamos por el campo 'profiling'
        result = Supp.objects.filter(created_at__gte=start_of_month, created_at__lt=end_of_month,is_active = True).values('status').annotate(count=Count('status')).order_by('status')

    elif request.user.role in ['A','SUPP']:

        # Realizamos la consulta y agrupamos por el campo 'profiling'
        result = Supp.objects.filter(created_at__gte=start_of_month, created_at__lt=end_of_month, is_active = True).values('status').filter(agent=request.user.id).annotate(count=Count('status')).order_by('status')


    return result

@login_required(login_url='/login') 
def sale(request): 

    start_date = None
    end_date = None

    if request.method == 'POST':
        # Obtener los parámetros de fecha del request
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

    # Llamar a la función que procesa los datos de ventas y obtiene la información agrupada
    saleACA =  saleObamaAgent (start_date, end_date)
    saleACAUsa = saleObamaAgentUsa(start_date, end_date)
    saleSupp = saleSuppAgent(start_date, end_date)
    saleSuppUsa = saleSuppAgentUsa(start_date, end_date)
    sales_data, total_status_color_1_2_obama, total_status_color_3_obama, total_status_color_1_2_supp, total_status_color_3_supp, total_sales = salesBonusAgent(start_date, end_date)

    registered, proccessing, profiling, canceled, countRegistered,countProccsing,countProfiling,countCanceled = saleClientStatusObama(start_date, end_date)
    registeredSupp, proccessingSupp, activeSupp, canceledSupp,countRegisteredSupp,countProccsingSupp,countActiveSupp,countCanceledSupp = saleClientStatusSupp(start_date, end_date)



    # Calcular los totales por agente antes de pasar los datos a la plantilla
    for agent, data in sales_data.items():
        data['total'] = data['status_color_1_2_obama'] + data['status_color_3_obama'] + data['status_color_1_2_supp'] + data['status_color_3_supp']

    context = {
        'saleACA': saleACA,
        'saleACAUsa': saleACAUsa,
        'saleSupp': saleSupp,
        'saleSuppUsa': saleSuppUsa,
        'sales_data': sales_data,
        'total_status_color_1_obama': total_status_color_1_2_obama,
        'total_status_color_3_obama': total_status_color_3_obama,
        'total_status_color_1_supp': total_status_color_1_2_supp,
        'total_status_color_3_supp': total_status_color_3_supp,
        'total_sales': total_sales,
        'registered':registered,
        'proccessing' : proccessing,
        'profiling':profiling,
        'canceled':canceled,
        'registeredSupp': registeredSupp, 
        'proccessingSupp':proccessingSupp,
        'activeSupp':activeSupp,
        'canceledSupp':canceledSupp,
        'countRegistered':countRegistered,
        'countProccsing': countProccsing,
        'countProfiling':countProfiling,
        'countCanceled':countCanceled,
        'countRegisteredSupp':countRegisteredSupp,
        'countProccsingSupp': countProccsingSupp,
        'countActiveSupp':countActiveSupp,
        'countCanceledSupp':countCanceledSupp,
        'start_date' : start_date,
        'end_date': end_date
    }

    return render (request, 'table/sale.html', context)

def saleObamaAgent(start_date=None, end_date=None):
    # Definir la consulta base para Supp, utilizando `select_related` para obtener el nombre completo del agente (User)
    sales_query = ObamaCare.objects.select_related('agent').filter(is_active=True) \
        .values('agent__username', 'agent__first_name', 'agent__last_name', 'status_color') \
        .annotate(total_sales=Count('id')) \
        .order_by('agent', 'status_color')

    # Si no se proporcionan fechas, filtrar por el mes actual
    if not start_date and not end_date:
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if today.month == 12:
            last_day_of_month = today.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month + 1) - timezone.timedelta(seconds=1))

        sales_query = sales_query.filter(created_at__range=[first_day_of_month, last_day_of_month])

    # Si se proporcionan fechas, filtrar por el rango de fechas
    elif start_date and end_date:
        start_date = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )

        sales_query = sales_query.filter(created_at__range=[start_date, end_date])

    # Crear un diccionario para almacenar los resultados por agente y status color
    agents_sales = {}
    status_colors = [1, 2, 3, 4]

    # Procesar los resultados y organizar los totales por agente
    for entry in sales_query:
        agent_username = entry['agent__username']
        first_name = entry['agent__first_name']
        last_name = entry['agent__last_name']
        agent_full_name = f"{first_name} {last_name} "
        status_color = entry['status_color']
        total_sales = entry['total_sales']

        if agent_full_name not in agents_sales:
            agents_sales[agent_full_name] = {'status_color_1': 0, 'status_color_2': 0, 'status_color_3': 0, 'status_color_4': 0, 'total_sales': 0}

        if status_color == 1:
            agents_sales[agent_full_name]['status_color_1'] = total_sales
        elif status_color == 2:
            agents_sales[agent_full_name]['status_color_2'] = total_sales
        elif status_color == 3:
            agents_sales[agent_full_name]['status_color_3'] = total_sales
        elif status_color == 4:
            agents_sales[agent_full_name]['status_color_4'] = total_sales

        agents_sales[agent_full_name]['total_sales'] += total_sales

    # Imprimir el resultado para verificar
    #print("Sales Data:")
    #for agent, data in agents_sales.items():
    #    print(f"Agent: {agent}, Data: {data}")

    return agents_sales

def saleObamaAgentUsa(start_date=None, end_date=None):

    # Definir la consulta base para Supp, utilizando `values` para obtener el nombre del agente (agent_usa)
    sales_query = ObamaCare.objects.values('agent_usa', 'status_color').filter(is_active=True) \
        .annotate(total_sales=Count('id')) \
        .order_by('agent_usa', 'status_color')

    # Si no se proporcionan fechas, filtrar por el mes actual
    if not start_date and not end_date:
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if today.month == 12:
            last_day_of_month = today.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month + 1) - timezone.timedelta(seconds=1))

        sales_query = sales_query.filter(created_at__range=[first_day_of_month, last_day_of_month])

    # Si se proporcionan fechas, filtrar por el rango de fechas
    elif start_date and end_date:
        start_date = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )

        sales_query = sales_query.filter(created_at__range=[start_date, end_date])

    # Crear un diccionario para almacenar los resultados por agente y status color
    agents_sales = {}
    status_colors = [1, 2, 3, 4]

    # Procesar los resultados y organizar los totales por agente
    for entry in sales_query:
        agent_name = entry['agent_usa']  # Ahora tenemos el nombre del agente usando el campo `agent_usa`
        
        # Truncar el nombre del agente a un máximo de 15 caracteres
        short_name = Truncator(agent_name).chars(8)

        status_color = entry['status_color']
        total_sales = entry['total_sales']

        if short_name not in agents_sales:
            agents_sales[short_name] = {'status_color_1': 0, 'status_color_2': 0, 'status_color_3': 0, 'status_color_4': 0, 'total_sales': 0}

        if status_color == 1:
            agents_sales[short_name]['status_color_1'] = total_sales
        elif status_color == 2:
            agents_sales[short_name]['status_color_2'] = total_sales
        elif status_color == 3:
            agents_sales[short_name]['status_color_3'] = total_sales
        elif status_color == 4:
            agents_sales[short_name]['status_color_4'] = total_sales

        agents_sales[short_name]['total_sales'] += total_sales

    return agents_sales

def saleSuppAgent(start_date=None, end_date=None):
    # Definir la consulta base para Supp, utilizando `select_related` para obtener el nombre completo del agente (User)
    sales_query = Supp.objects.select_related('agent').filter(is_active=True) \
        .values('agent__username', 'agent__first_name', 'agent__last_name', 'status_color') \
        .annotate(total_sales=Count('id')) \
        .order_by('agent', 'status_color')

    # Si no se proporcionan fechas, filtrar por el mes actual
    if not start_date and not end_date:
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if today.month == 12:
            last_day_of_month = today.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month + 1) - timezone.timedelta(seconds=1))

        sales_query = sales_query.filter(created_at__range=[first_day_of_month, last_day_of_month])

    # Si se proporcionan fechas, filtrar por el rango de fechas
    elif start_date and end_date:
        start_date = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )

        sales_query = sales_query.filter(created_at__range=[start_date, end_date])

    # Crear un diccionario para almacenar los resultados por agente y status color
    agents_sales = {}
    status_colors = [1, 2, 3, 4]

    # Procesar los resultados y organizar los totales por agente
    for entry in sales_query:
        agent_username = entry['agent__username']
        first_name = entry['agent__first_name']
        last_name = entry['agent__last_name']
        agent_full_name = f"{first_name} {last_name}"
        status_color = entry['status_color']
        total_sales = entry['total_sales']

        if agent_full_name not in agents_sales:
            agents_sales[agent_full_name] = {'status_color_1': 0, 'status_color_2': 0, 'status_color_3': 0, 'status_color_4': 0, 'total_sales': 0}

        if status_color == 1:
            agents_sales[agent_full_name]['status_color_1'] = total_sales
        elif status_color == 2:
            agents_sales[agent_full_name]['status_color_2'] = total_sales
        elif status_color == 3:
            agents_sales[agent_full_name]['status_color_3'] = total_sales
        elif status_color == 4:
            agents_sales[agent_full_name]['status_color_4'] = total_sales

        agents_sales[agent_full_name]['total_sales'] += total_sales

    # Imprimir el resultado para verificar los datos
    #print("Sales Data for Supp:")
    #for agent, data in agents_sales.items():
    #    print(f"Agent: {agent}, Data: {data}")

    return agents_sales

def saleSuppAgentUsa(start_date=None, end_date=None):
    # Definir la consulta base para Supp, utilizando `values` para obtener el nombre del agente (agent_usa)
    sales_query = Supp.objects.values('agent_usa', 'status_color').filter(is_active = True) \
        .annotate(total_sales=Count('id')) \
        .order_by('agent_usa', 'status_color')

    # Si no se proporcionan fechas, filtrar por el mes actual
    if not start_date and not end_date:
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if today.month == 12:
            last_day_of_month = today.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month + 1) - timezone.timedelta(seconds=1))

        sales_query = sales_query.filter(created_at__range=[first_day_of_month, last_day_of_month])

    # Si se proporcionan fechas, filtrar por el rango de fechas
    elif start_date and end_date:
        start_date = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )

        sales_query = sales_query.filter(created_at__range=[start_date, end_date])

    # Crear un diccionario para almacenar los resultados por agente y status color
    agents_sales = {}
    status_colors = [1, 2, 3, 4]

    # Procesar los resultados y organizar los totales por agente
    for entry in sales_query:
        agent_name = entry['agent_usa']  # Ahora tenemos el nombre del agente usando el campo `agent_usa`
        status_color = entry['status_color']
        total_sales = entry['total_sales']

        # Truncar el nombre del agente a un máximo de 15 caracteres
        short_name = Truncator(agent_name).chars(8)

        if short_name not in agents_sales:
            agents_sales[short_name] = {'status_color_1': 0, 'status_color_2': 0, 'status_color_3': 0, 'status_color_4': 0, 'total_sales': 0}

        if status_color == 1:
            agents_sales[short_name]['status_color_1'] = total_sales
        elif status_color == 2:
            agents_sales[short_name]['status_color_2'] = total_sales
        elif status_color == 3:
            agents_sales[short_name]['status_color_3'] = total_sales
        elif status_color == 4:
            agents_sales[short_name]['status_color_4'] = total_sales

        agents_sales[short_name]['total_sales'] += total_sales

    return agents_sales

def salesBonusAgent(start_date=None, end_date=None):
    # Consulta para Supp
    sales_query_supp = Supp.objects.select_related('agent').filter(is_active=True) \
        .values('agent__id', 'agent__username', 'agent__first_name', 'agent__last_name', 'status_color') \
        .annotate(total_sales=Count('id'))

    # Consulta para ObamaCare
    sales_query_obamacare = ObamaCare.objects.select_related('agent').filter(is_active = True) \
        .values('agent__id', 'agent__username', 'agent__first_name', 'agent__last_name', 'status_color') \
        .annotate(total_sales=Count('id'))

    # Si no se proporcionan fechas, filtrar por el mes actual
    if not start_date and not end_date:
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if today.month == 12:
            last_day_of_month = today.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month + 1) - timezone.timedelta(seconds=1))

        sales_query_supp = sales_query_supp.filter(created_at__range=[first_day_of_month, last_day_of_month])
        sales_query_obamacare = sales_query_obamacare.filter(created_at__range=[first_day_of_month, last_day_of_month])

    # Si se proporcionan fechas, filtrar por el rango de fechas
    elif start_date and end_date:
        start_date = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )

        sales_query_supp = sales_query_supp.filter(created_at__range=[start_date, end_date])
        sales_query_obamacare = sales_query_obamacare.filter(created_at__range=[start_date, end_date])

    # Diccionario para almacenar las ventas por agente
    sales_data = {}

    # Procesar los resultados de Supp
    for entry in sales_query_supp:
        agent_id = entry['agent__id']
        username = entry['agent__username']
        first_name = entry['agent__first_name']
        last_name = entry['agent__last_name']
        agent_full_name = f"{first_name} {last_name} ({username})"
        status_color = entry['status_color']
        total_sales = entry['total_sales']

        if agent_id not in sales_data:
            sales_data[agent_id] = {
                'id': agent_id,
                'username': username,
                'full_name': agent_full_name,
                'status_color_1_2_obama': 0,
                'status_color_3_obama': 0,
                'status_color_1_2_supp': 0,
                'status_color_3_supp': 0,
                'total_sales': 0
            }

        # Sumar las ventas de status_color 1 y 2 en Supp
        if status_color in [1, 2]:
            sales_data[agent_id]['status_color_1_2_supp'] += total_sales
        elif status_color == 3:
            sales_data[agent_id]['status_color_3_supp'] += total_sales
        
        # Actualizar total_sales
        sales_data[agent_id]['total_sales'] += total_sales

    # Procesar los resultados de ObamaCare
    for entry in sales_query_obamacare:
        agent_id = entry['agent__id']
        username = entry['agent__username']
        first_name = entry['agent__first_name']
        last_name = entry['agent__last_name']
        agent_full_name = f"{first_name} {last_name} ({username})"
        status_color = entry['status_color']
        total_sales = entry['total_sales']

        if agent_id not in sales_data:
            sales_data[agent_id] = {
                'id': agent_id,
                'username': username,
                'full_name': agent_full_name,
                'status_color_1_2_obama': 0,
                'status_color_3_obama': 0,
                'status_color_1_2_supp': 0,
                'status_color_3_supp': 0,
                'total_sales': 0
            }

        # Sumar las ventas de status_color 1 y 2 en ObamaCare
        if status_color in [1, 2]:
            sales_data[agent_id]['status_color_1_2_obama'] += total_sales
        elif status_color == 3:
            sales_data[agent_id]['status_color_3_obama'] += total_sales

        # Actualizar total_sales
        sales_data[agent_id]['total_sales'] += total_sales

    # Calcular los totales generales
    total_status_color_1_2_obama = sum([data['status_color_1_2_obama'] for data in sales_data.values()])
    total_status_color_3_obama = sum([data['status_color_3_obama'] for data in sales_data.values()])

    total_status_color_1_2_supp = sum([data['status_color_1_2_supp'] for data in sales_data.values()])
    total_status_color_3_supp = sum([data['status_color_3_supp'] for data in sales_data.values()])

    # Total general
    total_sales = total_status_color_1_2_obama + total_status_color_3_obama + total_status_color_1_2_supp + total_status_color_3_supp

    return sales_data, total_status_color_1_2_obama, total_status_color_3_obama, total_status_color_1_2_supp, total_status_color_3_supp, total_sales

def saleClientStatusObama(start_date=None, end_date=None):

    # Consulta para Registered
    sales_query_registered = ObamaCare.objects.select_related('agent','client').annotate(
        truncated_agent_usa=Substr('agent_usa', 1, 8)).filter(status_color = 1, is_active = True)
    
    # Consulta para Proccessing
    sales_query_proccessing = ObamaCare.objects.select_related('agent','client').annotate(
        truncated_agent_usa=Substr('agent_usa', 1, 8)).filter(status_color = 2, is_active = True ) 

    # Consulta para Profiling
    sales_query_profiling = ObamaCare.objects.select_related('agent','client').annotate(
        truncated_agent_usa=Substr('agent_usa', 1, 8)).filter(status_color = 3, is_active = True ) 
    
    # Consulta para Canceled
    sales_query_canceled = ObamaCare.objects.select_related('agent','client').annotate(
        truncated_agent_usa=Substr('agent_usa', 1, 8)).filter(status_color = 4, is_active = True )

    # Si no se proporcionan fechas, filtrar por el mes actual
    if not start_date and not end_date:
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if today.month == 12:
            last_day_of_month = today.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month + 1) - timezone.timedelta(seconds=1))

        sales_query_registered = sales_query_registered.filter(created_at__range=[first_day_of_month, last_day_of_month])
        sales_query_proccessing = sales_query_proccessing.filter(created_at__range=[first_day_of_month, last_day_of_month])
        sales_query_profiling = sales_query_profiling.filter(created_at__range=[first_day_of_month, last_day_of_month])
        sales_query_canceled = sales_query_canceled.filter(created_at__range=[first_day_of_month, last_day_of_month])


    # Si se proporcionan fechas, filtrar por el rango de fechas
    elif start_date and end_date:
        start_date = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )

        sales_query_registered = sales_query_registered.filter(created_at__range=[start_date, end_date])
        sales_query_proccessing = sales_query_proccessing.filter(created_at__range=[start_date, end_date])
        sales_query_profiling = sales_query_profiling.filter(created_at__range=[start_date, end_date])
        sales_query_canceled = sales_query_canceled.filter(created_at__range=[start_date, end_date])

    countRegistered = sales_query_registered.count()
    countProccsing = sales_query_proccessing.count()
    countProfiling = sales_query_profiling.count()
    countCanceled = sales_query_canceled.count()
    
    return sales_query_registered,sales_query_proccessing,sales_query_profiling,sales_query_canceled,countRegistered,countProccsing,countProfiling,countCanceled

def saleClientStatusSupp(start_date=None, end_date=None):

    # Consulta para Registered
    registered_supp = Supp.objects.select_related('agent','client').annotate(
        truncated_agent_usa=Substr('agent_usa', 1, 8)).filter(status_color = 1, is_active = True)
    
    
    # Consulta para Proccessing
    proccessing_supp = Supp.objects.select_related('agent','client').annotate(
        truncated_agent_usa=Substr('agent_usa', 1, 8)).filter(status_color = 2, is_active = True ) 

    # Consulta para Active
    active_supp = Supp.objects.select_related('agent','client').annotate(
        truncated_agent_usa=Substr('agent_usa', 1, 8)).filter(status_color = 3, is_active = True ) 
    
    # Consulta para Canceled
    canceled_supp = Supp.objects.select_related('agent','client').annotate(
        truncated_agent_usa=Substr('agent_usa', 1, 8)).filter(status_color = 4, is_active = True )

    # Si no se proporcionan fechas, filtrar por el mes actual
    if not start_date and not end_date:
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if today.month == 12:
            last_day_of_month = today.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month + 1) - timezone.timedelta(seconds=1))

        registered_supp = registered_supp.filter(created_at__range=[first_day_of_month, last_day_of_month])
        proccessing_supp = proccessing_supp.filter(created_at__range=[first_day_of_month, last_day_of_month])
        active_supp = active_supp.filter(created_at__range=[first_day_of_month, last_day_of_month])
        canceled_supp = canceled_supp.filter(created_at__range=[first_day_of_month, last_day_of_month])

        countRegisteredSupp = registered_supp.count()
        countProccsingSupp = proccessing_supp.count()
        countActiveSupp = active_supp.count()
        countCanceledSupp = canceled_supp.count()

    # Si se proporcionan fechas, filtrar por el rango de fechas
    elif start_date and end_date:
        start_date = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )

        registered_supp = registered_supp.filter(created_at__range=[start_date, end_date])
        proccessing_supp = proccessing_supp.filter(created_at__range=[start_date, end_date])
        active_supp = active_supp.filter(created_at__range=[start_date, end_date])
        canceled_supp = canceled_supp.filter(created_at__range=[start_date, end_date])

        countRegisteredSupp = registered_supp.count()
        countProccsingSupp = proccessing_supp.count()
        countActiveSupp = active_supp.count()
        countCanceledSupp = canceled_supp.count()

    
    return registered_supp,proccessing_supp,active_supp,canceled_supp,countRegisteredSupp,countProccsingSupp,countActiveSupp,countCanceledSupp

def SaleModal(request, agent_id):

    start_date = request.POST.get('start_date')  # Obtiene start_date desde la URL
    end_date = request.POST.get('end_date')      # Obtiene end_date desde la URL
    print(start_date)

    if not start_date and not end_date:
        today = timezone.now()
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if today.month == 12:
            end_date = today.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            end_date = (start_date.replace(month=start_date.month + 1) - timezone.timedelta(seconds=1))

    else:
        start_date = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )

    saleModalObama = ObamaCare.objects.select_related('agent', 'client').filter(
        agent_id=agent_id, created_at__range=[start_date, end_date], is_active = True
    )
    saleModalSupp = Supp.objects.select_related('agent', 'client').filter(
        agent_id=agent_id, created_at__range=[start_date, end_date], is_active = True
    )


    # Preparar los datos en formato JSON
    data = {
        'obama_sales': [
            {
                'client_name': f'{sale.client.first_name} {sale.client.last_name}', 
                'created_at': sale.created_at.strftime('%Y-%m-%d'),
                'details': sale.profiling,  # Asegúrate de tener este campo en tu modelo
                'carrier':sale.carrier
            }
            for sale in saleModalObama
        ],
        'supp_sales': [
            {
                'client_name':  f'{sale.client.first_name} {sale.client.last_name}',
                'created_at': sale.created_at.strftime('%Y-%m-%d'),
                'details': sale.status,  # Asegúrate de tener este campo en tu modelo
                'carrier':  f'{sale.company} - {sale.policy_type}'
            }
            for sale in saleModalSupp
        ],
    }

    return JsonResponse({'success': True, 'data': data})

@login_required(login_url='/login')
def weeklyLiveView(request):
    context = {
        'weeklySales': getSalesForWeekly(),
    }
    if request.user.role == 'TV': return render(request, 'dashboard/weeklyLiveViewTV.html', context)
    else: return render(request, 'dashboard/weeklyLiveView.html', context)

def getSalesForWeekly():
    # Obtener la fecha de hoy y calcular el inicio de la semana (asumiendo que empieza el lunes)
    today = timezone.now()
    startOfWeek = today - timedelta(days=today.weekday())
    endOfWeek = startOfWeek + timedelta(days=6)

    # Inicializamos un diccionario por defecto para contar las instancias
    userCounts = defaultdict(lambda: {
        'lunes': {'obama': 0, 'obamaActive': 0 , 'supp': 0, 'suppActive':0},
        'martes': {'obama': 0, 'obamaActive': 0 , 'supp': 0, 'suppActive':0},
        'miercoles': {'obama': 0, 'obamaActive': 0 , 'supp': 0, 'suppActive':0},
        'jueves': {'obama': 0, 'obamaActive': 0 , 'supp': 0, 'suppActive':0},
        'viernes': {'obama': 0, 'obamaActive': 0 , 'supp': 0, 'suppActive':0},
        'sabado': {'obama': 0, 'obamaActive': 0 , 'supp': 0, 'suppActive':0},
    })

    # Mapeo de números a días de la semana
    daysOfWeek = {
        0: 'lunes',
        1: 'martes',
        2: 'miercoles',
        3: 'jueves',
        4: 'viernes',
        5: 'sabado'
    }

    # Contamos cuántos registros de ObamaCare tiene cada usuario por día
    userRole = ['A', 'C', 'S']

    # Filtrar por la semana actual
    obamaCounts = ObamaCare.objects.values('agent', 'created_at') \
        .filter(
            agent__role__in=userRole,
            is_active=True,
            created_at__range=[startOfWeek, endOfWeek]
        ) \
        .annotate(obamaCount=Count('id'))
        
    obamaActiveCounts = ObamaCare.objects.values('agent', 'created_at')\
        .filter(
            agent__role__in=userRole, 
            is_active=True, 
            created_at__range=[startOfWeek, endOfWeek],
            status='ACTIVE'
        )\
        .annotate(obamaProfilingCount=Count('id'))

    for obama in obamaCounts:
        # Obtener el día de la semana (0=lunes, 1=martes, ..., 6=domingo)
        dayOfWeek = obama['created_at'].weekday()
        if dayOfWeek < 6:  # Excluimos el domingo
            day = daysOfWeek[dayOfWeek]
            userCounts[obama['agent']][day]['obama'] += obama['obamaCount']

    for obamaActive in obamaActiveCounts:
        # Obtener el día de la semana (0=lunes, 1=martes, ..., 6=domingo)
        dayOfWeek = obamaActive['created_at'].weekday()
        if dayOfWeek < 6:  # Excluimos el domingo
            day = daysOfWeek[dayOfWeek]
            userCounts[obamaActive['agent']][day]['obamaActive'] += obamaActive['obamaProfilingCount']

    # Contamos cuántos registros de Supp tiene cada usuario por día
    suppCounts = Supp.objects.values('agent', 'created_at') \
        .filter(
            agent__role__in=userRole,
            is_active=True,
            created_at__range=[startOfWeek, endOfWeek]
        ) \
        .annotate(suppCount=Count('id'))

    suppActiveCounts = Supp.objects.values('agent', 'created_at') \
        .filter(
            agent__role__in=userRole,
            is_active=True,
            created_at__range=[startOfWeek, endOfWeek],
            status='ACTIVE'
        ) \
        .annotate(suppActiveCount=Count('id'))

    for supp in suppCounts:
        # Obtener el día de la semana (0=lunes, 1=martes, ..., 6=domingo)
        dayOfWeek = supp['created_at'].weekday()
        if dayOfWeek < 6:  # Excluimos el domingo
            day = daysOfWeek[dayOfWeek]
            userCounts[supp['agent']][day]['supp'] += supp['suppCount']

    for suppActive in suppActiveCounts:
        # Obtener el día de la semana (0=lunes, 1=martes, ..., 6=domingo)
        dayOfWeek = suppActive['created_at'].weekday()
        if dayOfWeek < 6:  # Excluimos el domingo
            day = daysOfWeek[dayOfWeek]
            userCounts[suppActive['agent']][day]['suppActive'] += suppActive['suppActiveCount']

    excludedUsernames = ['Calidad01', 'mariluz', 'MariaCaTi'] #Excluimos a gente que no debe aparecer en la vista

    # Aseguramos que todos los usuarios estén en el diccionario, incluso si no tienen registros
    for user in User.objects.filter(role__in=userRole, is_active=True).exclude(username__in=excludedUsernames):
        if user.id not in userCounts:
            userCounts[user.id] = {
                'lunes': {'obama': 0, 'obamaActive': 0 , 'supp': 0, 'suppActive':0},
                'martes': {'obama': 0, 'obamaActive': 0 , 'supp': 0, 'suppActive':0},
                'miercoles': {'obama': 0, 'obamaActive': 0 , 'supp': 0, 'suppActive':0},
                'jueves': {'obama': 0, 'obamaActive': 0 , 'supp': 0, 'suppActive':0},
                'viernes': {'obama': 0, 'obamaActive': 0 , 'supp': 0, 'suppActive':0},
                'sabado': {'obama': 0, 'obamaActive': 0 , 'supp': 0, 'suppActive':0}
            }

    # Convertimos los identificadores de usuario a nombres (si necesitas los nombres de los usuarios)
    userNames = {user.id: f'{user.first_name} {user.last_name}' for user in User.objects.all()}

    # Crear un diccionario con los nombres de los usuarios y los conteos por día
    finalCounts = {userNames[userId]: counts for userId, counts in userCounts.items()}

    return finalCounts

def monthLiveView(request):
    monthSales, weekRanges = getSalesForMonth()
    context = {
        'monthSales': monthSales,
        'weekRanges': weekRanges,
        'toggle': True
    }
    
    if request.user.role == 'TV': return render(request, 'dashboard/monthLiveViewTV.html', context)
    else: return render(request, 'dashboard/monthLiveView.html', context)

from django.utils.timezone import make_aware

def getSalesForMonth():
    # Obtener las fechas de inicio y fin del mes actual
    today = datetime.today()
    startDate = today.replace(day=1)  # Primer día del mes actual
    _, lastDay = calendar.monthrange(today.year, today.month)
    endDate = today.replace(day=lastDay)  # Último día del mes actual

    excludedUsernames = ['Calidad01', 'mariluz', 'MariaCaTi']  # Excluimos a gente que no debe aparecer en la vista
    userRoles = ['A', 'C', 'S']
    
    # Convertir startDate y endDate en fechas "offset-aware"
    startDate = make_aware(startDate)
    endDate = make_aware(endDate)
    
    # Número total de semanas en el mes actual
    numWeeks = (lastDay + 6) // 7  # Aproximación para incluir semanas parciales

    # Calcular los rangos de las semanas
    weekRanges = []
    for i in range(numWeeks):
        weekStart = startDate + timedelta(weeks=i)
        weekEnd = weekStart + timedelta(days=6)
        
        # Asegurarse de que la fecha final no sea después del último día del mes
        if weekEnd > endDate:
            weekEnd = endDate
        
        # Formatear las fechas en "dd/mm"
        weekRange = f"{weekStart.strftime('%d/%m')} - {weekEnd.strftime('%d/%m')}"
        weekRanges.append(weekRange)
    
    # Inicializar diccionario de ventas con todos los usuarios
    users = User.objects.filter(role__in=userRoles, is_active=True).exclude(username__in=excludedUsernames)  # Lista completa de usuarios
    salesSummary = {
        user.username: {
            f"Week{i + 1}": {"obama": 0, "activeObama": 0, "supp": 0, "activeSupp": 0}
            for i in range(numWeeks)
        } for user in users
    }
    
    # Filtrar todas las ventas realizadas en el mes actual
    obamaSales = ObamaCare.objects.filter(created_at__range=[startDate, endDate])
    suppSales = Supp.objects.filter(created_at__range=[startDate, endDate])
    
    # Iterar sobre las ventas de Obamacare y organizarlas por semanas
    for sale in obamaSales:
        agentName = sale.agent.username  # Nombre del agente
        saleWeek = (sale.created_at - startDate).days // 7 + 1
        if 1 <= saleWeek <= numWeeks:
            try:
                salesSummary[agentName][f"Week{saleWeek}"]["obama"] += 1
            except KeyError:
                pass  # Ignorar ventas de agentes que no están en el filtro de usuarios
    
    # Iterar sobre las ventas de Supp y organizarlas por semanas
    for sale in suppSales:
        agentName = sale.agent.username  # Nombre del agente
        saleWeek = (sale.created_at - startDate).days // 7 + 1
        if 1 <= saleWeek <= numWeeks:
            try:
                salesSummary[agentName][f"Week{saleWeek}"]["supp"] += 1
            except KeyError:
                pass

    # Agregar el conteo de pólizas activas por agente para Obamacare y Supp
    activeObamaPolicies = ObamaCare.objects.filter(status='Active')
    activeSuppPolicies = Supp.objects.filter(status='Active')
    
    for policy in activeObamaPolicies:
        agentName = policy.agent.username
        policyWeek = (policy.created_at - startDate).days // 7 + 1
        if 1 <= policyWeek <= numWeeks:
            try:
                salesSummary[agentName][f"Week{policyWeek}"]["activeObama"] += 1
            except KeyError:
                pass

    for policy in activeSuppPolicies:
        agentName = policy.agent.username
        policyWeek = (policy.created_at - startDate).days // 7 + 1
        if 1 <= policyWeek <= numWeeks:
            try:
                salesSummary[agentName][f"Week{policyWeek}"]["activeSupp"] += 1
            except KeyError:
                pass

    # Convertir el diccionario para usar "first_name last_name" como clave
    finalSummary = {}
    for user in users:
        fullName = f"{user.first_name} {user.last_name}".strip()
        finalSummary[fullName] = salesSummary[user.username]
    
    return finalSummary, weekRanges

#Websocket
def notify_websocket(user_id):
    """
    Función que notifica al WebSocket de un cambio, llamando a un consumidor específico.
    """
    channel_layer = get_channel_layer()

    # Llamamos al WebSocket para notificar al usuario que su plan fue agregado
    async_to_sync(channel_layer.group_send)(
        "user_updates",  # El nombre del grupo de WebSocket
        {
            "type": "user_update",  # Tipo de mensaje que enviamos
            "user_id": user_id,  # ID del usuario al que notificamos
            "message": "Nuevo plan agregado"
        }
    )

@login_required(login_url='/login')   
def formCreateControl(request):

    userRole = [ 'A' , 'C', 'SUPP']
    users = User.objects.filter(role__in = userRole)

    if request.method == 'POST':

        observation = request.POST.get('observation')
        category = request.POST.get('category')
        amount = request.POST.get('amount', 0)
        if amount == '': amount = None

        if request.POST.get('Action') == 'Quality':
            form = ControlQualityForm(request.POST)
            if form.is_valid():
                quality = form.save(commit=False)
                quality.agent_create = request.user 
                quality.is_active = True
                quality.observation = observation
                quality.category = category
                quality.amount = amount
                quality.save()
                
                # Responder con éxito y la URL de redirección
                return redirect('formCreateControl')
            
        elif request.POST.get('Action') == 'Call':
            
            form = ControlCallForm(request.POST)
            if form.is_valid():

                call = form.save(commit=False)
                call.agent_create = request.user
                call.is_active = True
                call.save()
                
                # Responder con éxito y la URL de redirección
                return redirect('formCreateControl')

    context = {'users':users}

    return render(request, 'forms/formCreateControl.html', context)

@login_required(login_url='/login')   
def tableControl(request):

    quality = ControlQuality.objects.select_related('agent','agent_create').filter(is_active = True)
    call = ControlCall.objects.select_related('agent','agent_create').filter(is_active = True)

    context = {
        'quality' : quality,
        'call' : call
    }

    return render(request, 'table/control.html', context)

@login_required(login_url='/login')   
def createQuality(request):

    userRole = [ 'A' , 'C']
    agents = User.objects.filter(is_active = True, role__in=userRole )

    if request.method == 'POST':

        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        agent = request.POST.get('agent')

        consultQuality = ControlQuality.objects.filter(date__range=(start_date, end_date), agent = agent)
        agentReport = ControlQuality.objects.select_related('agent').filter(agent = agent).first
        date = datetime.now()

        callAll = ControlCall.objects.filter(date__range=(start_date, end_date), agent = agent)
        # Sumar los valores de daily, answered y mins
        totals = callAll.aggregate(
            total_daily=Sum('daily'),
            total_answered=Sum('answered'),
            total_mins=Sum('mins')
        )

        # Acceder a los valores sumados
        total_daily = totals['total_daily']
        total_answered = totals['total_answered']
        total_mins = totals['total_mins']
        
        return generatePdfQuality(
            request, consultQuality, agentReport, start_date, end_date, date, total_daily, total_answered, total_mins
        )

    context = {
        'agents' : agents
    }

    return render (request,'pdf/createQuality.html', context)

def generatePdfQuality(request, consultQuality,agentReport,start_date,end_date,date,total_daily, total_answered, total_mins):

    context = {
        'consultQuality' : consultQuality,
        'agentReport' : agentReport,
        'start_date' : start_date,
        'end_date' : end_date,
        'date' : date,
        'total_daily' : total_daily,
        'total_answered' : total_answered,
        'total_mins' : total_mins
    }

    # Renderiza la plantilla HTML a un string
    html_content = render_to_string('pdf/template.html', context)

    # Genera el PDF
    pdf_file = HTML(string=html_content).write_pdf()

    # Devuelve el PDF como respuesta HTTP
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="output.pdf"'
    return response

@login_required(login_url='/login')   
def upload_excel(request):
    headers = []  # Cabeceras del archivo Excel
    model_fields = [field.name for field in BdExcel._meta.fields if field.name not in ['id', 'agent_id', 'excel_metadata']]

    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        file_name = request.POST.get('file_name')
        description = request.POST.get('description')

        if form.is_valid() and file_name:
            excel_file = request.FILES['file']

            try:
                # Leer el archivo Excel para extraer las cabeceras
                df = pd.read_excel(excel_file, engine='openpyxl')
                headers = list(df.columns)  # Extraer las cabeceras del archivo

                # Convertir valores a tipos compatibles con JSON
                df = df.applymap(
                    lambda x: x.isoformat() if isinstance(x, pd.Timestamp) else x
                )

                # Crear un registro en ExcelFileMetadata
                excel_metadata = ExcelFileMetadata.objects.create(
                    file_name=file_name,
                    description=description,
                    uploaded_at=datetime.now()
                )

                # Guardar el DataFrame en la sesión para usarlo después
                request.session['uploaded_data'] = df.to_dict(orient='list')  # Convertir a diccionario serializable
                request.session['uploaded_headers'] = headers
                request.session['metadata_id'] = excel_metadata.id  # Guardar ID del archivo para usarlo luego

            except Exception as e:
                return render(request, 'excel/upload_excel.html', {
                    'form': form,
                    'error': f"Error al procesar el archivo: {str(e)}"
                })

            # Renderizar la página de mapeo
            return render(request, 'excel/map_headers.html', {
                'headers': headers,
                'model_fields': model_fields
            })
    else:
        form = ExcelUploadForm()

    return render(request, 'excel/upload_excel.html', {'form': form})

def process_and_save(request):
    if request.method == 'POST':
        # Obtener el mapeo entre los campos del modelo y las cabeceras del archivo
        mapping = {}
        for key, value in request.POST.items():
            if key.startswith('mapping_'):
                model_field = key.replace('mapping_', '')  # Campo del modelo
                header = value  # Cabecera del archivo seleccionada
                mapping[model_field] = header

        # Recuperar la ruta del archivo desde la sesión
        uploaded_file_path = request.session.get('uploaded_file_path')
        if not uploaded_file_path or not os.path.exists(uploaded_file_path):
            return render(request, 'excel/upload_excel.html', {'error': 'No se encontró el archivo Excel. Por favor, súbelo nuevamente.'})

        try:
            # Leer el archivo Excel desde la ruta temporal
            df = pd.read_excel(uploaded_file_path, engine='openpyxl')

            # Iterar sobre las filas del DataFrame y guardar en la BD
            for _, row in df.iterrows():
                data = {}
                for model_field, header in mapping.items():
                    if header in df.columns:  # Verificar que la cabecera esté en el archivo
                        data[model_field] = row[header]
                BdExcel.objects.create(**data)

        except Exception as e:
            return render(request, 'excel/upload_excel.html', {
                'error': f"Error al procesar el archivo: {str(e)}"
            })

        # Limpiar la sesión y eliminar el archivo temporal
        request.session.pop('uploaded_file_path', None)
        os.remove(uploaded_file_path)

        return render(request, 'excel/header_processed.html', {'mapping': mapping, 'success': True})
    else:
        return render(request, 'excel/upload_excel.html', {'form': ExcelUploadForm()})

def save_data(request):
    if request.method == 'POST':
        # Obtener el mapeo entre los campos del modelo y las cabeceras del archivo
        mapping = {}
        for key, value in request.POST.items():
            if key.startswith('mapping_'):
                model_field = key.replace('mapping_', '')
                header = value
                if header:
                    mapping[model_field] = header

        # Recuperar los datos cargados previamente desde la sesión
        uploaded_data = request.session.get('uploaded_data')
        metadata_id = request.session.get('metadata_id')
        if not uploaded_data or not metadata_id:
            return render(request, 'excel/upload_excel.html', {'error': 'No se encontraron datos para procesar.'})

        # Recuperar el registro de ExcelFileMetadata
        excel_metadata = ExcelFileMetadata.objects.get(id=metadata_id)

        # Convertir el diccionario de vuelta a un DataFrame
        df = pd.DataFrame(uploaded_data)

        # Inicializar una lista para errores
        errors = []
        valid_data = []  # Datos válidos para guardar

        # Validar cada fila
        for index, row in df.iterrows():
            row_errors = {}
            data = {}
            for model_field, header in mapping.items():
                if header in df.columns:
                    value = row[header]
                    # Validaciones por campo del modelo
                    if model_field == 'first_name' and not isinstance(value, str):
                        row_errors[model_field] = 'Debe ser una cadena de texto.'
                    elif model_field == 'last_name' and value is not None and not isinstance(value, str):
                        row_errors[model_field] = 'Debe ser una cadena de texto o nulo.'
                    elif model_field == 'phone':
                        try:
                            value = int(value)
                        except (ValueError, TypeError):
                            row_errors[model_field] = 'Debe ser un número entero.'
                    elif model_field == 'zipCode':
                        try:
                            value = int(value)
                        except (ValueError, TypeError):
                            row_errors[model_field] = 'Debe ser un número entero.'
                    elif model_field == 'agent_id' and value is not None:
                        try:
                            value = int(value)
                        except (ValueError, TypeError):
                            row_errors[model_field] = 'Debe ser un número entero o nulo.'

                    data[model_field] = value

            if row_errors:
                errors.append({'row': index + 1, 'errors': row_errors})
            else:
                # Agregar datos válidos para guardarlos más tarde
                valid_data.append(data)

        # Si hay errores, mostrarlos al usuario
        if errors:
            return render(request, 'excel/map_headers.html', {
                'headers': request.session['uploaded_headers'],
                'model_fields': [field.name for field in BdExcel._meta.fields if field.name not in ('id','agent_id' ,'excel_metadata')],
                'errors': errors
            })

        # Guardar los datos válidos
        for data in valid_data:
            BdExcel.objects.create(excel_metadata=excel_metadata, **data)

        # Limpiar los datos de la sesión
        request.session.pop('uploaded_data', None)
        request.session.pop('uploaded_headers', None)
        request.session.pop('metadata_id', None)

        return render(request, 'excel/success.html', {'message': 'Datos guardados exitosamente.'})
    else:
        return redirect('excel/upload_excel')

@login_required(login_url='/login')   
def manage_agent_assignments(request):
    if request.method == 'POST':
        # Obtener el archivo seleccionado y los agentes
        file_id = request.POST.get('file_name')
        user_ids = request.POST.getlist('users')  # Usuarios para asignar o quitar
        action = request.POST.get('action')  # Determinar si es asignar o quitar

        if not file_id:
            return render(request, 'excel/manage_agent_assignments.html', {
                'files': ExcelFileMetadata.objects.all(),
                'users': User.objects.filter(role='A',is_active=True),
                'error': 'Debes seleccionar un archivo.'
            })

        # Recuperar el archivo seleccionado
        try:
            file = ExcelFileMetadata.objects.get(id=file_id)
        except ExcelFileMetadata.DoesNotExist:
            return render(request, 'excel/manage_agent_assignments.html', {
                'files': ExcelFileMetadata.objects.all(),
                'users': User.objects.filter(role='A',is_active=True),
                'error': 'El archivo seleccionado no es válido.'
            })

        # Validar que se seleccionen usuarios
        if not user_ids:
            return render(request, 'excel/manage_agent_assignments.html', {
                'files': ExcelFileMetadata.objects.all(),
                'users': User.objects.filter(role='A',is_active=True),
                'error': 'Debes seleccionar al menos un usuario.'
            })

        if action == 'assign':
            # Asignar registros equitativamente a los agentes seleccionados
            users = User.objects.filter(id__in=user_ids, role='A')
            if not users.exists():
                return render(request, 'excel/manage_agent_assignments.html', {
                    'files': ExcelFileMetadata.objects.all(),
                    'users': User.objects.filter(role='A',is_active=True),
                    'error': 'Los usuarios seleccionados no son válidos.'
                })

            # Recuperar registros asociados al archivo
            records = BdExcel.objects.filter(excel_metadata=file)

            # Distribuir registros equitativamente
            user_count = len(users)
            user_ids = list(users.values_list('id', flat=True))
            for i, record in enumerate(records):
                record.agent_id = user_ids[i % user_count]
                record.save()

            return render(request, 'excel/manage_agent_assignments.html', {
                'files': ExcelFileMetadata.objects.all(),
                'users': User.objects.filter(role='A',is_active=True),
                'success': f'Registros de {file.file_name} distribuidos exitosamente entre los usuarios seleccionados.'
            })

        elif action == 'remove':
            # Quitar asignaciones de los usuarios seleccionados
            BdExcel.objects.filter(excel_metadata=file, agent_id__in=user_ids).update(agent_id=None)

            return render(request, 'excel/manage_agent_assignments.html', {
                'files': ExcelFileMetadata.objects.all(),
                'users': User.objects.filter(role='A',is_active=True),
                'success': f'Asignaciones eliminadas para los agentes seleccionados del archivo {file.file_name}.'
            })

        else:
            return render(request, 'excel/manage_agent_assignments.html', {
                'files': ExcelFileMetadata.objects.all(),
                'users': User.objects.filter(role='A',is_active=True),
                'error': 'Acción no válida.'
            })

    return render(request, 'excel/manage_agent_assignments.html', {
        'files': ExcelFileMetadata.objects.all(),
        'users': User.objects.filter(role='A',is_active=True)
    })

@login_required(login_url='/login')
def commentDB(request):

    roleAuditar = ['S', 'Admin']

    # Obtén las opciones para el select desde el modelo DropDownList
    optionBd = DropDownList.objects.values_list('status_bd', flat=True).exclude(status_bd__isnull=True)
    comenntAgent = CommentBD.objects.all()

    # Filtra los registros dependiendo del rol del usuario
    if request.user.role in roleAuditar:
        bd = BdExcel.objects.all()
    else:
        bd = BdExcel.objects.filter(agent_id=request.user.id, is_sold = False)

    # Si es una solicitud POST, procesamos la observación
    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        observation = request.POST.get('observation')

        # Validar que se envíen los datos necesarios
        if not record_id or not observation:
            messages.error(request, "Please select a valid option.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        try:
            # Obtener el objeto BdExcel correspondiente al record_id
            bd_excel_record = BdExcel.objects.get(id=record_id)

            # Crear un nuevo comentario en la tabla CommentBD
            CommentBD.objects.create(
                bd_excel=bd_excel_record,  # Relacionar con el objeto BdExcel
                agent_create=request.user,  # Relacionar con el usuario actual
                content=observation,  # Guardar el comentario
                excel_metadata=bd_excel_record.excel_metadata
            )

            # Verificar si la opción seleccionada es "sold"
            if observation == 'SOLD':
                # Actualizar el campo is_sold en BdExcel
                bd_excel_record.is_sold = True
                bd_excel_record.save()

            messages.success(request, "Observation saved successfully.")
        except BdExcel.DoesNotExist:
            messages.error(request, "Record not found.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        # Redirige a la página previa después de guardar
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Si es una solicitud GET, simplemente renderizamos la vista con los datos
    context = {
        'optionBd': optionBd,
        'bd': bd,
        'comenntAgent':comenntAgent
    }

    return render(request, 'table/bd.html', context)

def generar_reporte(request):
    form = ReporteSeleccionForm(request.GET)
    reporte_datos = None
    return render(request, 'generar_reporte.html', {'form': form, 'reporte_datos': reporte_datos})

def consent(request, obamacare_id):
    obamacare = ObamaCare.objects.select_related('client').get(id=obamacare_id)
    temporalyURL = None

    typeToken = True
   
    language = request.GET.get('lenguaje', 'es')  # Idioma predeterminado si no se pasa
    activate(language)
    # Validar si el usuario no está logueado y verificar el token
    if isinstance(request.user, AnonymousUser):
        result = validateTemporaryToken(request, typeToken)
        is_valid_token, *note = result
        if not is_valid_token:
            return HttpResponse(note)
    elif request.user.is_authenticated:
        temporalyURL = f"{request.build_absolute_uri('/viewConsent/')}{obamacare_id}?token={generateTemporaryToken(obamacare.client , typeToken)}&lenguaje={language}"
        print('Usuario autenticado')
    else:
        # Si el usuario no está logueado y no hay token válido
        return HttpResponse('Acceso denegado. Por favor, inicie sesión o use un enlace válido.')
    
    dependents = Dependent.objects.filter(client=obamacare.client)
    supps = Supp.objects.filter(client_id=obamacare.client.id)
    consent = Consents.objects.select_related('obamacare').filter(obamacare = obamacare_id ).last()
    contact = ContactClient.objects.filter(client = obamacare.client.id).first()


    if request.method == 'POST':
        documents = request.FILES.getlist('documents')  # Lista de archivos subidos

        language = request.GET.get('lenguaje', 'es')  # Idioma predeterminado si no se pasa

        objectClient = save_data_from_request(Client, request.POST, ['agent'],obamacare.client)
        objectObamacare = save_data_from_request(ObamaCare, request.POST, ['signature'], obamacare)
        
        # Usamos la nueva función para guardar los checkboxes en ContactClient
        objectContact = save_contact_client_checkboxes(request.POST, contact)

        for document in documents:
            photo = DocumentsClient(
                file=document,
                client=obamacare.client)  # Crear una nueva instancia de Foto
            photo.save()  # Guardar el archivo en la base de datos
        return generateConsentPdf(request, objectObamacare, dependents, supps, language)

    context = {
        'valid_migration_statuses': ['PERMANENT_RESIDENT', 'US_CITIZEN', 'EMPLOYMENT_AUTHORIZATION'],
        'obamacare':obamacare,
        'dependents':dependents,
        'consent':consent,
        'contact':contact,
        'company':getCompanyPerAgent(obamacare.agent_usa),
        'temporalyURL': temporalyURL,
        'supps': supps
    }
    return render(request, 'consent/consent1.html', context)

def incomeLetter(request, obamacare_id):
    # Validar si el usuario no está logueado y verificar el token
    if isinstance(request.user, AnonymousUser):
        typeToken = True #Aqui le indico si buscar el token temporal por el medicare o client_id
        result = validateTemporaryToken(request, typeToken)
        is_valid_token, *note = result
        if not is_valid_token:
            return HttpResponse(note)
    elif request.user.is_authenticated:
        print('Usuario autenticado')
    else:
        # Si el usuario no está logueado y no hay token válido
        return HttpResponse('Acceso denegado. Por favor, inicie sesión o use un enlace válido.')
    obamacare = ObamaCare.objects.select_related('client').get(id=obamacare_id)
    signed = IncomeLetter.objects.filter(obamacare = obamacare_id).first()

    language = request.GET.get('lenguaje', 'es')  # Idioma predeterminado si no se pasa
    activate(language)
    
  
    context = {
        'obamacare': obamacare,
        'signed' : signed,
    }
    if request.method == 'POST':
        objectClient = save_data_from_request(Client, request.POST, ['agent'],obamacare.client)
        objectObamacare = save_data_from_request(ObamaCare, request.POST, ['signature'], obamacare)
        generateIncomeLetterPDF(request, objectObamacare, language)
        deactivateTemporaryToken(request)
        return render(request, 'consent/endView.html')
    
        

    return render(request, 'consent/incomeLetter.html', context)

def generateConsentPdf(request, obamacare, dependents, supps, language):
    token = request.GET.get('token')

    current_date = datetime.now().strftime("%A, %B %d, %Y %I:%M")
    date_more_3_months = (datetime.now() + timedelta(days=360)).strftime("%A, %B %d, %Y %I:%M")

    contact = ContactClient.objects.filter(client = obamacare.client).first()

    # Obtener los campos con valor True
    true_fields = []

    if contact.sms: true_fields.append('sms')
    if contact.phone: true_fields.append('phone')
    if contact.email: true_fields.append('email')
    if contact.whatsapp: true_fields.append('whatsapp')

    # Variable con los nombres de los campos
    var = ", ".join(true_fields)
    

    consent = Consents.objects.create(
        obamacare=obamacare,
    )

    signature_data = request.POST.get('signature')
    format, imgstr = signature_data.split(';base64,')
    ext = format.split('/')[-1]
    image = ContentFile(base64.b64decode(imgstr), name=f'firma.{ext}')

    consent.signature = image
    consent.save()

    context = {
        'obamacare':obamacare,
        'dependents':dependents,
        'supps':supps,
        'consent':consent,
        'company':getCompanyPerAgent(obamacare.agent_usa),
        'social_security':request.POST.get('socialSecurity'),
        'current_date':current_date,
        'date_more_3_months':date_more_3_months,
        'ip':getIPClient(request),
        'var':var
    }

    activate(language)
    # Renderiza la plantilla HTML a un string
    html_content = render_to_string('consent/templatePdfConsent.html', context)

    # Genera el PDF
    pdf_file = HTML(string=html_content).write_pdf()

    # Usa BytesIO para convertir el PDF en un archivo
    pdf_io = io.BytesIO(pdf_file)
    pdf_io.seek(0)  # Asegúrate de que el cursor esté al principio del archivo

    # Guarda el PDF en el modelo usando un ContentFile
    pdf_name = f'Consent{obamacare.client.first_name}_{obamacare.client.last_name}#{obamacare.client.phone_number} {datetime.now().strftime("%m-%d-%Y-%H:%M")}.pdf'  # Nombre del archivo

    consent.pdf.save(pdf_name, ContentFile(pdf_io.read()), save=True)

    base_url = reverse('incomeLetter', args=[obamacare.id])
    query_params = urlencode({'token': token,'lenguaje': language})
    url = f'{base_url}?{query_params}'

    return redirect(url)

def generateMedicarePdf(request, medicare ,language):
    token = request.GET.get('token')

    current_date = datetime.now().strftime("%A, %B %d, %Y %I:%M")

    contact = OptionMedicare.objects.filter(client = medicare.id).first()

    # Obtener los campos con valor True
    true_fields = []

    if contact.prescripcion: true_fields.append('Planes de Prescripción de Medicare Parte D')
    if contact.advantage: true_fields.append('Planes de Medicare Advantage (Parte C) y Planes de Costo')
    if contact.dental: true_fields.append('Productos Dental-Visión-Oescucha')
    if contact.complementarios: true_fields.append('Productos de Complementarios de Hospitalización')
    if contact.suplementarios: true_fields.append('Planes Suplementarios de Medicare (Medigap)')

    # Variable con los nombres de los campos
    var = ", ".join(true_fields)    

    consent = Consents.objects.create(
        medicare=medicare,
    )

    signature_data = request.POST.get('signature')
    format, imgstr = signature_data.split(';base64,')
    ext = format.split('/')[-1]
    image = ContentFile(base64.b64decode(imgstr), name=f'firma.{ext}')

    consent.signature = image
    consent.save()

    context = {
        'medicare':medicare,
        'consent':consent,
        'company':getCompanyPerAgent(medicare.agent_usa),
        'ip':getIPClient(request),
        'current_date':current_date,
        'var':var
    }

    activate(language)
    # Renderiza la plantilla HTML a un string
    html_content = render_to_string('consent/templatePdfConsentMedicare.html', context)

    # Genera el PDF
    pdf_file = HTML(string=html_content).write_pdf()

    # Usa BytesIO para convertir el PDF en un archivo
    pdf_io = io.BytesIO(pdf_file)
    pdf_io.seek(0)  # Asegúrate de que el cursor esté al principio del archivo

    # Guarda el PDF en el modelo usando un ContentFile
    pdf_name = f'Consent-medicare{medicare.first_name}_{medicare.last_name}#{medicare.phone_number} {datetime.now().strftime("%m-%d-%Y-%H:%M")}.pdf'  # Nombre del archivo

    consent.pdf.save(pdf_name, ContentFile(pdf_io.read()), save=True)



    return render(request, 'consent/endView.html')

def generateIncomeLetterPDF(request, obamacare, language):
    current_date = datetime.now().strftime("%A, %B %d, %Y %I:%M")

    incomeLetter = IncomeLetter.objects.create(
        obamacare=obamacare,
    )
    signature_data = request.POST.get('signature')
    format, imgstr = signature_data.split(';base64,')
    ext = format.split('/')[-1]
    image = ContentFile(base64.b64decode(imgstr), name=f'firma.{ext}')
    incomeLetter.signature = image
    incomeLetter.save()

    context = {
        'obamacare':obamacare,
        'current_date':current_date,
        'ip':getIPClient(request),
        'incomeLetter':incomeLetter
    }

    activate(language)

    # Renderiza la plantilla HTML a un string
    html_content = render_to_string('consent/templatePdfIncomeLetter.html', context)

    # Genera el PDF
    pdf_file = HTML(string=html_content).write_pdf()

    # Usa BytesIO para convertir el PDF en un archivo
    pdf_io = io.BytesIO(pdf_file)
    pdf_io.seek(0)  # Asegúrate de que el cursor esté al principio del archivo

    # Guarda el PDF en el modelo usando un ContentFile
    pdf_name = f'IncomeOfLetter{obamacare.client.first_name}_{obamacare.client.last_name}#{obamacare.client.phone_number} {datetime.now().strftime("%A, %B %d, %Y %I:%M")}.pdf'  # Nombre del archivo

    incomeLetter.pdf.save(pdf_name, ContentFile(pdf_io.read()), save=True)

def save_data_from_request(model_class, post_data, exempted_fields, instance=None):
    """
    Guarda o actualiza los datos de un request.POST en la base de datos utilizando un modelo específico.

    Args:
        model_class (models.Model): Modelo de Django al que se guardarán los datos.
        post_data (QueryDict): Datos enviados en el request.POST.
        instance (models.Model, optional): Instancia existente del modelo para actualizar.
                                        Si es None, se creará un nuevo registro.

    Returns:
        models.Model: Instancia del modelo guardada o actualizada.
        False: Si ocurre algún error durante el proceso.
    """
    try:
        # Crear un diccionario con las columnas del modelo y sus valores correspondientes
        model_fields = [field.name for field in model_class._meta.fields]
        data_to_save = {}

        for field in model_fields:
            if field in exempted_fields:
                continue
            if field in post_data:
                data_to_save[field] = post_data[field]

        if instance:
            # Si se proporciona una instancia, actualizamos sus campos
            for field, value in data_to_save.items():
                setattr(instance, field, value)
            instance.save()
            return instance
        else:
            # Si no hay instancia, creamos una nueva
            instance = model_class(**data_to_save)
            instance.save()
            return instance

    except Exception as e:
        return False

def save_contact_client_checkboxes(post_data, contact_instance):
    """
    Guarda o actualiza los campos de tipo checkbox en ContactClient (phone, email, sms, whatsapp).
    
    Args:
        post_data (QueryDict): Datos enviados en el request.POST.
        contact_instance (ContactClient): Instancia de ContactClient a actualizar.

    Returns:
        ContactClient: Instancia de ContactClient actualizada.
    """
    checkbox_fields = ['phone', 'email', 'sms', 'whatsapp']
    
    # Asegúrate de que solo los campos seleccionados se marquen como True
    for field in checkbox_fields:
        # Si el checkbox está marcado (enviará 'on'), lo asignamos como True
        if post_data.get(field) == 'on':
            setattr(contact_instance, field, True)
        else:
            setattr(contact_instance, field, False)
    
    contact_instance.save()  # Guardar la instancia actualizada
    return contact_instance

def save_contact_medicare_checkboxes(post_data, contact_instance):
    """
    Guarda o actualiza los campos de tipo checkbox en ContactClient (phone, email, sms, whatsapp).
    
    Args:
        post_data (QueryDict): Datos enviados en el request.POST.
        contact_instance (ContactClient): Instancia de ContactClient a actualizar.

    Returns:
        ContactClient: Instancia de ContactClient actualizada.
    """
    checkbox_fields = ['prescripcion', 'advantage', 'dental', 'complementarios','suplementarios']
    
    # Asegúrate de que solo los campos seleccionados se marquen como True
    for field in checkbox_fields:
        # Si el checkbox está marcado (enviará 'on'), lo asignamos como True
        if post_data.get(field) == 'on':
            setattr(contact_instance, field, True)
        else:
            setattr(contact_instance, field, False)
    
    contact_instance.save()  # Guardar la instancia actualizada
    return contact_instance

def getCompanyPerAgent(agent):
    agent_upper = agent.upper()

    if "GINA" in agent_upper or "LUIS" in agent_upper:
        company = "TRUINSURANCE GROUP LLC"
    elif any(substring in agent_upper for substring in ["DANIEL", "ZOHIRA", "DANIESKA", "VLADIMIR", "FRANK"]):
        company = "LAPEIRA & ASSOCIATES LLC"
    elif any(substring in agent_upper for substring in ["BORJA", "RODRIGO", "EVELYN"]):
        company = "SECUREPLUS INSURANCE LLC"
    else:
        company = ""  # Valor predeterminado si no hay coincidencia
    return company

def getIPClient(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # Puede haber múltiples IPs separadas por comas
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required(login_url='/login')
def salesPerformance(request):
    # Obtener la fecha actual
    now = timezone.now()

    # Si se proporcionan fechas, filtrar por el rango de fechas
    if request.method == 'POST':
        startDatePost = request.POST['start_date']
        endDatePost = request.POST['end_date']
        startDate = timezone.make_aware(
            datetime.strptime(startDatePost, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        endDate = timezone.make_aware(
            datetime.strptime(endDatePost, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )
    else:
        startDate = timezone.make_aware(
            datetime(now.year, now.month, 1, 0, 0, 0, 0)
        )
        endDate = timezone.make_aware(
            datetime(now.year, now.month + 1, 1, 0, 0, 0, 0) - timezone.timedelta(microseconds=1)
        )


    salesData = get_agent_sales(startDate, endDate)

    # Preparar datos para la gráfica con nombres completos
    agents = list(salesData.keys())
    obamacareSales = [salesData[agent]['obamas'] for agent in agents]
    suppSales = [salesData[agent]['supp'] for agent in agents]

    users = User.objects.all()
    for user in users:
        print(f'{user.username} {get_weekly_counts(user)}')

    context = {
        'agents': agents,
        'obamacareSales': obamacareSales,
        'suppSales': suppSales,
        'startDate':startDate,
        'endDate':endDate,
    }

    # Renderizar la respuesta
    return render(request, 'chart/averageSales.html', context)

def get_weekly_counts(user):
    # Obtener la fecha actual
    noww = timezone.now()

    # Primer día del mes anterior
    now = noww.replace(day=1) - relativedelta(months=1)
    
    # Obtener el primer día del mes actual
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Obtener el último día del mes actual
    if now.month == 12:
        next_month = now.replace(year=now.year + 1, month=1, day=1)
    else:
        next_month = now.replace(month=now.month + 1, day=1)
    last_day_of_month = next_month - timedelta(days=1)
    
    # Calcular las fechas de inicio de cada semana
    week1_start = first_day_of_month
    week2_start = week1_start + timedelta(days=7)
    week3_start = week2_start + timedelta(days=7)
    week4_start = week3_start + timedelta(days=7)
    
    # Inicializar el diccionario de resultados
    result = {
        "week1obama": 0,
        "week2obama": 0,
        "week3obama": 0,
        "week4obama": 0,
        "week1supp": 0,
        "week2supp": 0,
        "week3supp": 0,
        "week4supp": 0,
    }
    
    # Conteo de ObamaCare
    obamacare_counts = ObamaCare.objects.filter(agent=user, created_at__range=(first_day_of_month, last_day_of_month))
    for obamacare in obamacare_counts:
        if week1_start <= obamacare.created_at < week2_start:
            result["week1obama"] += 1
        elif week2_start <= obamacare.created_at < week3_start:
            result["week2obama"] += 1
        elif week3_start <= obamacare.created_at < week4_start:
            result["week3obama"] += 1
        elif week4_start <= obamacare.created_at <= last_day_of_month:
            result["week4obama"] += 1
    
    # Conteo de Supp
    supp_counts = Supp.objects.filter(agent=user, created_at__range=(first_day_of_month, last_day_of_month))
    for supp in supp_counts:
        if week1_start <= supp.created_at < week2_start:
            result["week1supp"] += 1
        elif week2_start <= supp.created_at < week3_start:
            result["week2supp"] += 1
        elif week3_start <= supp.created_at < week4_start:
            result["week3supp"] += 1
        elif week4_start <= supp.created_at <= last_day_of_month:
            result["week4supp"] += 1
    
    return result

def get_agent_sales(start_date, end_date):
    """
    Obtiene el conteo de ObamaCare y Supp vendidos por cada agente en un rango de fechas.
    
    Parámetros:
        start_date (date): Fecha de inicio del rango.
        end_date (date): Fecha de fin del rango.
    
    Retorna:
        dict: Un diccionario con el conteo de ventas por agente (nombre completo).
    """

    userExcludes = ['CarmenR', 'MariaCaTi']

    # Obtener todos los agentes activos con roles 'A' y 'C'
    allAgents = User.objects.filter(is_active=True, role__in=['A', 'C']).exclude(username__in=userExcludes).values('username', 'first_name', 'last_name')

    # Crear un diccionario para mapear username a nombre completo
    agentNameMap = {agent['username']: f"{agent['first_name']} {agent['last_name']}".strip() for agent in allAgents}

    # Obtener todos los agentes que tienen ventas
    obamaCareAgents = set(ObamaCare.objects.filter(
        created_at__range=[start_date, end_date],
        is_active=True
    ).values_list('agent__username', flat=True))

    suppAgents = set(Supp.objects.filter(
        created_at__range=[start_date, end_date],
        is_active=True
    ).values_list('agent__username', flat=True))

    # Unir todos los agentes que tienen ventas con los agentes filtrados inicialmente
    allUsernames = set(agentNameMap.keys())
    allUsernames.update(obamaCareAgents)
    allUsernames.update(suppAgents)

    # Obtener el conteo de ObamaCare dentro del rango de fechas
    obamaCareCount = ObamaCare.objects.filter(
        created_at__range=[start_date, end_date],
        is_active=True
    ).values('agent__username').annotate(obama_count=Count('id'))

    # Obtener el conteo de Supp dentro del rango de fechas
    suppCount = Supp.objects.filter(
        created_at__range=[start_date, end_date],
        is_active=True
    ).values('agent__username').annotate(supp_count=Count('id'))

    # Diccionario para almacenar los resultados con nombres completos
    agentSales = {}

    # Incluir a todos los agentes de allAgents, incluso si no tienen ventas
    for agent in allAgents:
        fullName = f"{agent['first_name']} {agent['last_name']}".strip()
        agentSales[fullName] = {'obamas': 0, 'supp': 0}

    # Agregar conteos de ObamaCare
    for entry in obamaCareCount:
        username = entry['agent__username']
        if username not in agentNameMap:
            # Si el agente no está en agentNameMap, obtener su nombre completo directamente
            agent = User.objects.filter(username=username).values('first_name', 'last_name').first()
            if agent:
                fullName = f"{agent['first_name']} {agent['last_name']}".strip()
            else:
                fullName = username
        else:
            fullName = agentNameMap[username]
        
        if fullName not in agentSales:
            agentSales[fullName] = {'obamas': 0, 'supp': 0}
        agentSales[fullName]['obamas'] = entry['obama_count']

    # Agregar conteos de Supp
    for entry in suppCount:
        username = entry['agent__username']
        if username not in agentNameMap:
            # Si el agente no está en agentNameMap, obtener su nombre completo directamente
            agent = User.objects.filter(username=username).values('first_name', 'last_name').first()
            if agent:
                fullName = f"{agent['first_name']} {agent['last_name']}".strip()
            else:
                fullName = username
        else:
            fullName = agentNameMap[username]
        
        if fullName not in agentSales:
            agentSales[fullName] = {'obamas': 0, 'supp': 0}
        agentSales[fullName]['supp'] = entry['supp_count']

    return agentSales

# View para generar solo el token
def generateTemporaryToken(client, typeToken):
    signer = Signer()

    expiration_time = timezone.now() + timedelta(minutes=90)

    # Crear el token con la fecha de expiración usando JSON
    data = {
        'client_id': client.id,
        'expiration': expiration_time.isoformat(),
    }
    signed_data = signer.sign(json.dumps(data))  # Firmar los datos serializados
    token = urlsafe_base64_encode(force_bytes(signed_data))  # Codificar seguro para URL

    # Guardar solo el token en la base de datos
    if typeToken:
        TemporaryToken.objects.create(
            client=client,
            token=token,
            expiration=expiration_time
        )
    else:
        TemporaryToken.objects.create(
            medicare = client,
            token=token,
            expiration=expiration_time
        )

    # Retornar solo el token (no se genera ni guarda la URL temporal)
    return token

# Vista para verificar y procesar la URL temporal
def validateTemporaryToken(request, typeToken):
    token = request.POST.get('token') or request.GET.get('token')

    if not token:
        return False, 'Token no proporcionado. Not found token.'

    signer = Signer()
    
    try:
        signed_data = force_str(urlsafe_base64_decode(token))
        data = json.loads(signer.unsign(signed_data))

        if typeToken:
            client_id = data.get('client_id')
            expiration_time = timezone.datetime.fromisoformat(data['expiration'])
            # Verificar si el token está activo y no ha expirado
            tempToken = TemporaryToken.objects.get(token=token, client_id=client_id)
        else:
            medicare_id = data.get('client_id')
            expiration_time = timezone.datetime.fromisoformat(data['expiration'])
            # Verificar si el token está activo y no ha expirado
            tempToken = TemporaryToken.objects.get(token=token, medicare_id=medicare_id)

        if not tempToken.is_active:
            return False, 'Enlace desactivado. Link deactivated.'

        if tempToken.is_expired():
            return False, 'Enlace ha expirado. Link expired.'

        
        return True, 'Success'
    
    except (BadSignature, ValueError, KeyError):
        return False, 'Token inválido o alterado. Invalid token.'

def deactivateTemporaryToken(request):
    token = request.POST.get('token') or request.GET.get('token')
    print(f'Cogi el token {token}')
    if not token:
        return False, 'Token no proporcionado. Not found token.'
    
    tempToken = TemporaryToken.objects.get(token=token)
    print(f'Encontre al token {tempToken}')
    tempToken.is_active = False
    tempToken.save()
    print(f'Desactive al token mmgv')

@login_required(login_url='/login')
def reportBd(request):
    BD = ExcelFileMetadata.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")  # Identificar qué formulario se está enviando

        if action == "show":
            # Procesar formulario de listar
            filterBd = request.POST.get("bd")
            if not filterBd:
                return render(request, 'table/reportBd.html', {'BDS': BD, 'error': 'Please select a BD'})

            filterBd = int(filterBd)
            nameBd = ExcelFileMetadata.objects.filter(id=filterBd).first()

            # Generar datos para mostrar en la tabla
            comment_with_content = (
                CommentBD.objects
                .filter(excel_metadata=filterBd)
                .exclude(content__isnull=True, content__exact='')
                .values(content_label=Coalesce('content', Value('PENDING', output_field=TextField())))
                .annotate(amount=Count('content'))
            )

            pending_count = (
                BdExcel.objects
                .filter(excel_metadata_id=filterBd)
                .exclude(id__in=CommentBD.objects.filter(excel_metadata=filterBd).values_list('bd_excel', flat=True))
                .count()
            )

            all_comments = list(comment_with_content)
            if pending_count > 0:
                all_comments.append({'content_label': 'PENDING', 'amount': pending_count})

            context = {
                'BDS': BD,
                'all_comments': all_comments,
                'nameBd': nameBd,
                'filterBd': filterBd,  # Pasamos el BD seleccionado al contexto
            }

            return render(request, 'table/reportBd.html', context)

        elif action == "download":
            # Procesar formulario de descargar
            filterBd = request.POST.get("filterBd")  # Recibimos el BD ya seleccionado
            content_label = request.POST.get("content_label")
            if not filterBd or not content_label:
                return render(request, 'table/reportBd.html', {'BDS': BD, 'error': 'Please select a category'})

            # Llamar a la función de descarga
            return downloadBdExcelByCategory(int(filterBd), content_label)

    return render(request, 'table/reportBd.html', {'BDS': BD})

def downloadBdExcelByCategory(filterBd, content_label):
    if content_label == "PENDING":
        # Obtener registros sin comentarios
        bd_excel_data = BdExcel.objects.filter(
            excel_metadata_id=filterBd
        ).exclude(
            id__in=CommentBD.objects.filter(excel_metadata=filterBd).values_list('bd_excel', flat=True)
        )
    else:
        # Obtener registros relacionados con la categoría
        bd_excel_data = BdExcel.objects.filter(
            excel_metadata_id=filterBd,
            commentbd__content=content_label
        ).distinct()

    # Crear el archivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="Excel_{content_label}.csv"'

    writer = csv.writer(response)
    writer.writerow(['First Name', 'Last Name', 'Phone', 'Address', 'City', 'State', 'Zip Code', 'Agent ID', 'Is Sold'])

    for item in bd_excel_data:
        writer.writerow([
            item.first_name,
            item.last_name or '',
            item.phone,
            item.address or '',
            item.city or '',
            item.state or '',
            item.zipCode or '',
            item.agent_id or '',
            'Yes' if item.is_sold else 'No'
        ])

    return response

@login_required(login_url='/login')
def averageCustomer(request):

    data = list(ObservationCustomer.objects.filter(
        typification__icontains="EFFECTIVE MANAGEMENT"
    ).values('agent__first_name', 'agent__last_name').annotate(total_llamadas=Count('id')).order_by('-total_llamadas'))

    context = {
        'data': json.dumps(data)  # Convertir los datos a JSON válido
    }

    # Si se proporcionan fechas, filtrar por el rango de fechas
    if request.method == 'POST':

        # Obtener parámetros de fecha del request
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        start_date_new = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date_new = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )

        data = list(ObservationCustomer.objects.filter(created_at__range=[start_date_new, end_date_new],
            typification__icontains="EFFECTIVE MANAGEMENT" ).values('agent__first_name', 'agent__last_name')
            .annotate(total_llamadas=Count('id')).order_by('-total_llamadas'))

        context = {
            'data': json.dumps(data),  # Convertir los datos a JSON válido
            'start_date': start_date,
            'end_date': end_date
        }    

    return render(request, 'chart/averageCustomer.html', context)

@login_required(login_url='/login')
def customerTypification(request) :

    # Obtener la fecha actual
    now = timezone.now()

    # Si se proporcionan fechas, filtrar por el rango de fechas
    if request.method == 'POST':
        startDatePost = request.POST['start_date']
        endDatePost = request.POST['end_date']
        startDate = timezone.make_aware(
            datetime.strptime(startDatePost, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        endDate = timezone.make_aware(
            datetime.strptime(endDatePost, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )
    else:
        startDate = timezone.make_aware(
            datetime(now.year, now.month, 1, 0, 0, 0, 0)
        )
        endDate = timezone.make_aware(
            datetime(now.year, now.month + 1, 1, 0, 0, 0, 0) - timezone.timedelta(microseconds=1)
        )
            
    agents = ObservationCustomer.objects.values('agent__username', 'agent__first_name', 'agent__last_name').distinct().filter(created_at__range=[startDate, endDate],is_active = True)
    agent_data = []

    for agent in agents:
        username = agent['agent__username']
        full_name = f"{agent['agent__first_name']} {agent['agent__last_name']}"
        
        typifications = ObservationCustomer.objects.filter(
            agent__username=username
        ).annotate(
            individual_types=F('typification')
        ).values('individual_types').filter(is_active = True)
        
        type_count = {}
        total = 0
        for t in typifications:
            types = [typ.strip() for typ in t['individual_types'].split(',')]
            for typ in types:
                type_count[typ] = type_count.get(typ, 0) + 1
                total += 1

        agent_data.append({
            'username': username,
            'full_name': full_name,
            'typifications': type_count,
            'total': total
        })

    context = {
        'agent_data':agent_data,
        'startDate':startDate,
        'endDate':endDate
    }   
    
    
    return render(request, 'table/customerTypification.html', context)

def redirect_with_token(request, view_name, *args, **kwargs):
    token = request.GET.get('token')
    url = reverse(view_name, args=args, kwargs=kwargs)
    query_params = urlencode({'token': token})
    return redirect(f'{url}?{query_params}')

def table6Week():

    # Obtener la fecha actual
    today = datetime.today()

    # Calcular el domingo anterior (inicio de la semana actual)
    startOfCurrentWeek = today - timedelta(days=today.weekday() + 1)

    # Calcular el domingo siguiente (fin de la semana actual)
    endOfCurrentWeek = startOfCurrentWeek + timedelta(days=6)

    # Calcular el inicio de las 6 semanas (domingo anterior a 6 semanas atrás)
    startDate = startOfCurrentWeek - timedelta(weeks=5)  # 5 semanas atrás desde el inicio de la semana actual

    # Convertir las fechas a "offset-aware"
    startDate = make_aware(startDate)
    endOfCurrentWeek = make_aware(endOfCurrentWeek)

    # Número total de semanas (6 semanas, incluyendo la semana actual)
    numWeeks = 6

    # Calcular los rangos de las semanas
    weekRanges = []
    for i in range(numWeeks):
        weekStart = startDate + timedelta(weeks=i)
        weekEnd = weekStart + timedelta(days=6)
        weekRange = f"{weekStart.strftime('%d/%m')} - {weekEnd.strftime('%d/%m')}"
        weekRanges.append(weekRange)

    # Inicializar diccionario de ventas para las últimas 6 semanas
    excludedUsernames = ['Calidad01', 'mariluz', 'MariaCaTi','StephanieMkt','CarmenR']  # Excluimos a gente que no debe aparecer en la vista
    userRoles = ['A', 'C', 'S']

    users = User.objects.filter(role__in=userRoles, is_active=True).exclude(username__in=excludedUsernames)

    salesSummary = {
        user.username: {
            f"Week{i + 1}": {
                "obama": 0, 
                "activeObama": 0, 
                "totalObama": 0,  # Total Obama = obama + activeObama
                "supp": 0, 
                "activeSupp": 0, 
                "totalSupp": 0,   # Total Supp = supp + activeSupp
                "total": 0        # Total General = totalObama + totalSupp
            }
            for i in range(numWeeks)
        } for user in users
    }

    # Filtrar todas las ventas realizadas en las últimas 6 semanas
    obamaSales = ObamaCare.objects.filter(created_at__range=[startDate, endOfCurrentWeek])
    suppSales = Supp.objects.filter(created_at__range=[startDate, endOfCurrentWeek])

    # Procesar las ventas de Obamacare y Supp para las últimas 6 semanas
    for sale in obamaSales:
        agentName = sale.agent.username
        if sale.agent.is_active:
            if agentName not in excludedUsernames:
                saleWeek = (sale.created_at - startDate).days // 7  # Calcular la semana (0 a 5)
                if 0 <= saleWeek < numWeeks:
                    try:
                        salesSummary[agentName][f"Week{saleWeek + 1}"]["obama"] += 1
                        salesSummary[agentName][f"Week{saleWeek + 1}"]["totalObama"] += 1
                        salesSummary[agentName][f"Week{saleWeek + 1}"]["total"] += 1
                    except KeyError:
                        pass

    for sale in suppSales:
        agentName = sale.agent.username
        if sale.agent.is_active:
            if agentName not in excludedUsernames:
                saleWeek = (sale.created_at - startDate).days // 7  # Calcular la semana (0 a 5)
                if 0 <= saleWeek < numWeeks:
                    try:
                        salesSummary[agentName][f"Week{saleWeek + 1}"]["supp"] += 1
                        salesSummary[agentName][f"Week{saleWeek + 1}"]["totalSupp"] += 1
                        salesSummary[agentName][f"Week{saleWeek + 1}"]["total"] += 1
                    except KeyError:
                        pass

    # Agregar el conteo de pólizas activas para las últimas 6 semanas
    activeObamaPolicies = ObamaCare.objects.filter(status='Active', created_at__range=[startDate, endOfCurrentWeek],is_active = True)
    activeSuppPolicies = Supp.objects.filter(status='Active', created_at__range=[startDate, endOfCurrentWeek], is_active = True)

    for policy in activeObamaPolicies:
        agentName = policy.agent.username
        if policy.agent.is_active:
            if agentName not in excludedUsernames:
                policyWeek = (policy.created_at - startDate).days // 7  # Calcular la semana (0 a 5)
                if 0 <= policyWeek < numWeeks:
                    try:
                        salesSummary[agentName][f"Week{policyWeek + 1}"]["activeObama"] += 1
                        salesSummary[agentName][f"Week{policyWeek + 1}"]["totalObama"] += 1
                        salesSummary[agentName][f"Week{policyWeek + 1}"]["total"] += 1
                    except KeyError:
                        pass

    for policy in activeSuppPolicies:
        agentName = policy.agent.username
        if policy.agent.is_active:
            if agentName not in excludedUsernames:
                policyWeek = (policy.created_at - startDate).days // 7  # Calcular la semana (0 a 5)
                if 0 <= policyWeek < numWeeks:
                    try:
                        salesSummary[agentName][f"Week{policyWeek + 1}"]["activeSupp"] += 1
                        salesSummary[agentName][f"Week{policyWeek + 1}"]["totalSupp"] += 1
                        salesSummary[agentName][f"Week{policyWeek + 1}"]["total"] += 1
                    except KeyError:
                        pass

    # Convertir el diccionario para usar "first_name last_name" como clave
    finalSummary = {}

    for user in users:
        fullName = f"{user.first_name} {user.last_name}".strip()
        finalSummary[fullName] = salesSummary[user.username]

    return finalSummary, weekRanges

def chart6WeekSale():

    # Obtener la fecha actual
    today = datetime.today()

    # Calcular el domingo anterior (inicio de la semana actual)
    startOfCurrentWeek = today - timedelta(days=today.weekday() + 1)

    # Calcular el inicio de las 6 semanas (domingo anterior a 6 semanas atrás)
    startDate = startOfCurrentWeek - timedelta(weeks=5)  # 5 semanas atrás desde el inicio de la semana actual

    # Convertir las fechas a "offset-aware"
    startDate = make_aware(startDate)
    endOfCurrentWeek = make_aware(startOfCurrentWeek + timedelta(days=6))

    # Número total de semanas (6 semanas, incluyendo la semana actual)
    numWeeks = 6

    # Calcular los rangos de las semanas
    weekRanges = []
    for i in range(numWeeks):
        weekStart = startDate + timedelta(weeks=i)
        weekEnd = weekStart + timedelta(days=6)
        weekRange = f"{weekStart.strftime('%d/%m')} - {weekEnd.strftime('%d/%m')}"
        weekRanges.append(weekRange)

    # Obtener los datos de pólizas activas para las últimas 6 semanas
    activeObamaPolicies = ObamaCare.objects.filter(status='Active', created_at__range=[startDate, endOfCurrentWeek],is_active = True)
    activeSuppPolicies = Supp.objects.filter(status='Active', created_at__range=[startDate, endOfCurrentWeek], is_active= True)

    # Inicializar diccionario de ventas para las últimas 6 semanas
    excludedUsernames = ['Calidad01', 'mariluz', 'MariaCaTi','StephanieMkt','CarmenR']  # Excluimos a gente que no debe aparecer en la vista

    # Inicializar diccionario para almacenar los datos de la gráfica por agente
    chart_data = {
        "labels": weekRanges,  # Etiquetas de las semanas
        "series": {}  # Diccionario para almacenar series por agente
    }

    # Procesar las pólizas activas de ObamaCare
    for policy in activeObamaPolicies:
        agentName = policy.agent.username
        if policy.agent.is_active:
            if agentName not in excludedUsernames:
                agentName = f"{policy.agent.first_name} {policy.agent.last_name}".strip()        
                policyWeek = (policy.created_at - startDate).days // 7  # Calcular la semana (0 a 5)
                if 0 <= policyWeek < numWeeks:
                    if agentName not in chart_data["series"]:
                        chart_data["series"][agentName] = {
                            "activeObama": [0] * numWeeks,
                            "activeSupp": [0] * numWeeks
                        }
                    chart_data["series"][agentName]["activeObama"][policyWeek] += 1

    # Procesar las pólizas activas de Supp
    for policy in activeSuppPolicies:
        agentName = policy.agent.username
        if policy.agent.is_active:
            if agentName not in excludedUsernames:
                agentName = f"{policy.agent.first_name} {policy.agent.last_name}".strip()        
                policyWeek = (policy.created_at - startDate).days // 7  # Calcular la semana (0 a 5)
                if 0 <= policyWeek < numWeeks:
                    if agentName not in chart_data["series"]:
                        chart_data["series"][agentName] = {
                            "activeObama": [0] * numWeeks,
                            "activeSupp": [0] * numWeeks
                        }
                    chart_data["series"][agentName]["activeSupp"][policyWeek] += 1

    return chart_data

@login_required(login_url='/login')
def sales6WeekReport(request):
    # Obtener el resumen de ventas para las últimas 6 semanas
    finalSummary, weekRanges = table6Week()

    # Obtener los datos para la gráfica
    chart_data = chart6WeekSale()

    # Pasar los datos a la plantilla
    context = {
        'finalSummary': finalSummary,  # Resumen de ventas de las últimas 6 semanas
        'weekRanges': weekRanges,      # Rangos de fechas de las últimas 6 semanas
        'chart_data': chart_data,      # Datos para la gráfica
    }

    # Renderizar la plantilla con los datos
    return render(request, 'table/sale6Week.html', context)

@login_required(login_url='/login')
def chart6Week(request):

    # Obtener los datos para la gráfica
    chart_data = chart6WeekSale()

    # Pasar los datos a la plantilla
    context = {
        'chart_data': chart_data   # Datos para la gráfica
    }

    # Renderizar la plantilla con los datos
    return render(request, 'chart/chart6Week.html', context)

def weekSalesSummary(week_number):
    # Obtener el año actual
    current_year = datetime.today().year

    # Calcular el lunes de la semana seleccionada
    startOfWeek = datetime.fromisocalendar(current_year, week_number, 1)  # 1 = Lunes
    # Calcular el sábado de la semana seleccionada
    endOfWeek = startOfWeek + timedelta(days=5)  # Lunes + 5 días = Sábado

    # Convertir las fechas a "offset-aware" (si es necesario)
    startOfWeek = make_aware(startOfWeek)
    endOfWeek = make_aware(endOfWeek)

    # Inicializar variables de totales generales
    total_aca = 0
    total_supp = 0
    totalActiveAca = 0
    totalActiveSupp = 0

    # Inicializar diccionario de ventas para la semana seleccionada
    excludedUsernames = ['Calidad01', 'mariluz', 'MariaCaTi', 'StephanieMkt', 'CarmenR','admin','tv','zohiraDuarte']  # Excluimos a gente que no debe aparecer en la vista
    userRoles = ['A', 'C', 'S','SUPP']

    users = User.objects.exclude(username__in=excludedUsernames).filter(role__in=userRoles, is_active=True)

    salesSummary = {
        user.username: {
            "obama": 0,
            "activeObama": 0,
            "supp": 0,
            "activeSupp": 0,
            "total": 0,       # Total General = totalObama + totalSupp
            "clientes_obama": [],  # Lista de clientes de ObamaCare
            "clientes_supp": []    # Lista de clientes de Supp
        } for user in users
    }

    # Filtrar todas las ventas realizadas en la semana seleccionada
    obamaSales = ObamaCare.objects.filter(created_at__range=[startOfWeek, endOfWeek])
    suppSales = Supp.objects.filter(created_at__range=[startOfWeek, endOfWeek])

    # Procesar las ventas de Obamacare para la semana seleccionada
    for sale in obamaSales:
        agentName = sale.agent.username
        if sale.agent.is_active and agentName not in excludedUsernames:
            salesSummary[agentName]["obama"] += 1
            salesSummary[agentName]["total"] += 1
            total_aca += 1  # Incrementar total general de ACA

            # Agregar detalles del cliente
            cliente_info = {
                "nombre": f"{sale.client.first_name} {sale.client.last_name}",
                "fecha_poliza": sale.created_at.strftime('%d/%m/%Y'),
                "estatus": sale.status,
                "estatus_color": sale.status_color
            }
            salesSummary[agentName]["clientes_obama"].append(cliente_info)

    # Procesar las ventas de Supp para la semana seleccionada
    for sale in suppSales:
        agentName = sale.agent.username
        if sale.agent.is_active and agentName not in excludedUsernames:
            salesSummary[agentName]["supp"] += 1
            salesSummary[agentName]["total"] += 1
            total_supp += 1  # Incrementar total general de SUPP

            # Agregar detalles del cliente
            cliente_info = {
                "nombre": f"{sale.client.first_name} {sale.client.last_name}",
                "fecha_poliza": sale.created_at.strftime('%d/%m/%Y'),
                "estatus": sale.status,
                "estatus_color": sale.status_color
            }
            salesSummary[agentName]["clientes_supp"].append(cliente_info)

    # Agregar el conteo de pólizas activas para la semana seleccionada
    activeObamaPolicies = ObamaCare.objects.filter(status='Active', created_at__range=[startOfWeek, endOfWeek], is_active=True)
    activeSuppPolicies = Supp.objects.filter(status='Active', created_at__range=[startOfWeek, endOfWeek], is_active=True)

    for policy in activeObamaPolicies:
        agentName = policy.agent.username
        if policy.agent.is_active and agentName not in excludedUsernames:
            salesSummary[agentName]["activeObama"] += 1
            totalActiveAca += 1  # Incrementar total general de ACA

    for policy in activeSuppPolicies:
        agentName = policy.agent.username
        if policy.agent.is_active and agentName not in excludedUsernames:
            salesSummary[agentName]["activeSupp"] += 1
            totalActiveSupp += 1  # Incrementar total general de SUPP

    # Convertir el diccionario para usar "first_name last_name" como clave
    finalSummary = {}
    for user in users:
        fullName = f"{user.first_name} {user.last_name}".strip()
        finalSummary[fullName] = salesSummary[user.username]

    # Agregar los totales generales al resumen
    finalSummary["TOTAL_GENERAL"] = {
        "total_aca": total_aca,
        "total_supp": total_supp,
        "totalActiveAca": totalActiveAca,
        "totalActiveSupp": totalActiveSupp,
        "total_general": total_aca + total_supp
    }

    # Rango de fechas de la semana seleccionada
    weekRange = f"{startOfWeek.strftime('%d/%m')} - {endOfWeek.strftime('%d/%m')}"

    return finalSummary, weekRange

def downloadPdf(request, week_number):
    # Obtener el resumen de la semana seleccionada
    resumen_semana, rango_fechas = weekSalesSummary(week_number)

    # Renderizar la plantilla específica para el PDF
    html_string = render_to_string('pdf/reportePdf.html', {
        'resumen_semana': resumen_semana,
        'rango_fechas': rango_fechas,
        'week_number': week_number
    })

    # Crear un objeto HTML de WeasyPrint
    font_config = FontConfiguration()
    html = HTML(string=html_string)
    
    # Generar el PDF
    pdf = html.write_pdf(font_config=font_config)

    # Crear una respuesta HTTP con el PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_semana_{week_number}.pdf"'
    return response

@login_required(login_url='/login')
def weekSalesWiew(request):
    if request.method == 'POST':
        # Obtener el número de la semana del formulario
        week_number = int(request.POST.get('week_number'))

        # Llamar a la función de lógica para obtener el resumen
        resumen_semana, rango_fechas = weekSalesSummary(week_number)

        # Renderizar la plantilla con los resultados
        return render(request, 'table/weekSalesWiew.html', {
            'resumen_semana': resumen_semana,
            'rango_fechas': rango_fechas,
            'week_number': week_number
        })

    # Si no es POST, mostrar el formulario vacío
    return render(request, 'table/weekSalesWiew.html')

@login_required(login_url='/login')
def clientMedicare(request):
    
    roleAuditor = ['S','AU']
    
    if request.user.role == 'Admin':       
        medicare = Medicare.objects.select_related('agent').annotate(
            truncated_agent_usa=Substr('agent_usa', 1, 8)).order_by('-created_at')
    elif request.user.role in roleAuditor:
        medicare = Medicare.objects.select_related('agent').annotate(
            truncated_agent_usa=Substr('agent_usa', 1, 8)).filter(is_active = True).order_by('-created_at')   
    else:
        medicare = Medicare.objects.select_related('agent').annotate(
            truncated_agent_usa=Substr('agent_usa', 1, 8)).filter(is_active = True, agent_id = request.user.id).order_by('-created_at')   


    return render(request, 'table/clientMedicare.html', {'medicares':medicare})

@login_required(login_url='/login')
def editClientMedicare(request, medicare_id):
    
    medicare = Medicare.objects.select_related('agent').filter(id=medicare_id).first()

    if medicare and medicare:
        social_number = medicare.social_security  # Campo real del modelo
        # Asegurarse de que social_number no sea None antes de formatear
        if social_number:
            formatted_social = f"xxx-xx-{social_number[-4:]}"  # Obtener el formato deseado
        else:
            formatted_social = "N/A"  # Valor predeterminado si no hay número disponible
    else:
        formatted_social = "N/A"
        social_number = None

    obsCus = ObservationCustomerMedicare.objects.select_related('agent').filter(medicare=medicare.id)
    list_drow = DropDownList.objects.filter(profiling_supp__isnull=False)

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        action = request.POST.get('action')
        if action == 'validate_key':
            provided_key = request.POST.get('key')
            correct_key = 'Sseguros22@'  # Cambia por tu lógica segura

            if provided_key == correct_key and social_number:
                return JsonResponse({'status': 'success', 'social': social_number})
            else:
                return JsonResponse({'status': 'error', 'message': 'Clave incorrecta o no hay número disponible'})
    

    consent = Consents.objects.filter(medicare = medicare_id )

    if request.method == 'POST':
        action = request.POST.get('action')

        # Campos de Client
        client_fields = [
            'agent_usa', 'first_name', 'last_name', 'phone_number', 'email', 'address', 'zipcode',
            'city', 'state', 'county', 'sex', 'migration_status', 'statusMedicare'
        ]        
        
        #formateo de fecha para guardalar como se debe en BD ya que la obtengo USA
        fecha_str = request.POST.get('date_birth')  # Formato MM/DD/YYYY
        # Conversión solo si los valores no son nulos o vacíos
        if fecha_str not in [None, '']:
            dateNew = datetime.strptime(fecha_str, '%m/%d/%Y').date()
        else:
            dateNew = None
        

        # Limpiar los campos de Client convirtiendo los vacíos en None
        cleaned_client_data = clean_fields_to_null(request, client_fields)

        # Convierte a mayúsculas los campos necesarios
        fields_to_uppercase = ['first_name', 'last_name', 'address', 'city', 'county']
        for field in fields_to_uppercase:
            if field in cleaned_client_data and cleaned_client_data[field]:
                cleaned_client_data[field] = cleaned_client_data[field].upper()

        # Actualizar Client
        client = Medicare.objects.filter(id=medicare_id).update(
            agent_usa=cleaned_client_data['agent_usa'],
            first_name=cleaned_client_data['first_name'],
            last_name=cleaned_client_data['last_name'],
            phone_number=cleaned_client_data['phone_number'],
            email=cleaned_client_data['email'],
            address=cleaned_client_data['address'],
            zipcode=cleaned_client_data['zipcode'],
            city=cleaned_client_data['city'],
            state=cleaned_client_data['state'],
            county=cleaned_client_data['county'],
            sex=cleaned_client_data['sex'],
            date_birth=dateNew,
            migration_status=cleaned_client_data['migration_status'],
            status=cleaned_client_data['statusMedicare']
        )

        return redirect('clientMedicare')   

    context = {
        'medicare': medicare,
        'formatted_social':formatted_social,
        'consent': consent,
        'obsCustomer': obsCus,
        'list_drow': list_drow,

    }

    return render(request, 'edit/editClientMedicare.html', context)

@login_required(login_url='/login') 
def saveCustomerObservationMedicare(request):
    if request.method == "POST":
        content = request.POST.get('textoIngresado')
        medicare_id = request.POST.get('plan_id')
        typeCall = request.POST.get('typeCall')        

        # Obtenemos las observaciones seleccionadas
        observations = request.POST.getlist('observaciones[]')  # Lista de valores seleccionados
        
        # Convertir las observaciones a una cadena (por ejemplo, separada por comas o saltos de línea)
        typification_text = ", ".join(observations)  # Puedes usar "\n".join(observations) si prefieres saltos de línea

        medicare = Medicare.objects.filter(id = medicare_id).first()

        if content.strip():  # Validar que el texto no esté vacío
            ObservationCustomerMedicare.objects.create(
                medicare=medicare,
                agent=request.user,
                typeCall=typeCall,
                typification=typification_text, # Guardamos las observaciones en el campo 'typification'
                content=content
            )
            messages.success(request, "Observación guardada exitosamente.")
        else:
            messages.error(request, "El contenido de la observación no puede estar vacío.")

        return redirect('editClientMedicare', medicare_id)       
        
    else:
        return HttpResponse("Método no permitido.", status=405)

def desactiveMedicare(request, medicare_id):
    # Obtener el cliente por su ID
    medicare = get_object_or_404(Medicare, id=medicare_id)
    
    # Cambiar el estado de is_active (True a False o viceversa)
    medicare.is_active = not medicare.is_active
    medicare.save()  # Guardar los cambios en la base de datos
    
    # Redirigir de nuevo a la página actual con un parámetro de éxito
    return redirect('clientMedicare')
 
def validarCita(request):
    fecha_str = request.GET.get('fecha')
    agente = request.GET.get('agente')

    try:
        # Convertir la fecha recibida en un objeto datetime
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
        fecha = make_aware(fecha)  # Asegurar que tenga zona horaria

        # Verificar si ya hay una cita en esa fecha y hora para el mismo agente
        cita_existente = Medicare.objects.filter(dateMedicare=fecha, agent_usa=agente).exists()

        return JsonResponse({"ocupado": cita_existente})
    
    except ValueError:
        return JsonResponse({"error": "Fecha no válida"}, status=400)

@login_required(login_url='/login')
def saveDocumentClient(request, obamacare_id):
    if request.method == "POST":
        obama = get_object_or_404(ObamaCare, id=obamacare_id)
        documents = request.FILES.getlist("documents")  # 📌 Recibe la lista de archivos
        filenames = request.POST.getlist("filenames")  # 📌 Recibe la lista de nombres

        if not documents:
            return JsonResponse({"success": False, "message": "No se han subido archivos."})

        for index, document in enumerate(documents):
            # ✅ Usa el nombre si existe, si no, asigna "Documento sin nombre"
            document_name = filenames[index].strip() if index < len(filenames) and filenames[index].strip() else document.name

            # ✅ Guarda el documento con el nombre en la BD
            DocumentObama.objects.create(
                file=document,
                name=document_name,  # ✅ Guardar nombre del documento
                obama=obama,
                agent_create=request.user
            )

        messages.success(request, "Archivos subidos correctamente.")
        return JsonResponse({"success": True, "message": "Archivos subidos correctamente.", "redirect_url": f"/editClientObama/{obamacare_id}/"})
    
    return JsonResponse({"success": False, "message": "Método no permitido."}, status=405)

@login_required(login_url='/login')
def saveAppointment(request, obamacare_id):
    
    obama = ObamaCare.objects.get(id = obamacare_id)
    appointment = request.POST.get('appointment') 
    dateAppointment = request.POST.get('dateAppointment') 
    timeAppointment = request.POST.get('timeAppointment') 

    # Conversión de date a la BD requerido
    dateAppointmentNew = datetime.strptime(dateAppointment, '%m/%d/%Y').date()          

    AppointmentClient.objects.create(
        obama=obama,
        agent_create=request.user,
        appointment=appointment,
        dateAppointment = dateAppointmentNew,
        timeAppointment=timeAppointment,
    )

    return redirect('editClientObama', obamacare_id)   

@login_required(login_url='/login')
def paymentClients(request):

    payments = Payments.objects.values('month').annotate(total=Count('id')).order_by('month')

    if request.method == "POST":       

        months = request.POST.getlist("months")  # Capturar lista de meses seleccionados
        # Obtener pagos que correspondan a los meses seleccionados
        clients = Payments.objects.select_related("obamaCare").filter(month__in=months)

        # ✅ Crear un nuevo archivo Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Clientes"

        # ✅ Encabezados
        headers = ["First Name", "Last Name", "Plan", "Carrier", "Profiling", "Date-Profiling", "Status", "Created At","Month","Date payment was marked"]
        ws.append(headers)

        # ✅ Agregar datos al archivo Excel
        for client in clients:
            if client.obamaCare.is_active:
                ws.append([
                    client.obamaCare.client.first_name,
                    client.obamaCare.client.last_name,
                    client.obamaCare.plan_name,
                    client.obamaCare.carrier,
                    client.obamaCare.profiling,
                    client.obamaCare.profiling_date.strftime("%m-%d-%Y") if client.obamaCare.profiling_date else '',
                    client.obamaCare.status,
                    client.obamaCare.created_at.strftime("%m-%d-%Y") if client.obamaCare.created_at else '',  # Convertir fecha a string legible
                    client.month,
                    client.created_at.strftime("%m-%d-%Y")
                ])

        # ✅ Preparar la respuesta HTTP
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename="clientes.xlsx"'
        wb.save(response)

        return response 

    context = {'payments' : payments }

    return render(request, 'table/paymentClients.html',context)