from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from storages.backends.s3boto3 import S3Boto3Storage

class User(AbstractUser):

    ROLES_CHOICES = (
        ('A', 'Agent'),
        ('S', 'Supervisor'),
        ('C', 'Customer'),
        ('SUPP', 'Supplementary'),
        ('AU', 'Auditor'),
        ('TV', 'Tv'),
        ('Admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLES_CHOICES)
    # Sobrescribimos solo el campo email
    email = models.EmailField(
        blank=True, 
        null=True,
        unique=False
    )
    
    class Meta:
        db_table = 'users'
        
    def _str_(self):
        return self.username

class Client(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    agent_usa = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.BigIntegerField()
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)    
    address = models.CharField(max_length=255)
    zipcode = models.IntegerField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    county = models.CharField(max_length=100)
    sex = models.CharField(max_length=1)
    old = models.IntegerField()    
    date_birth = models.DateField()
    migration_status = models.CharField(max_length=100)
    social_security = models.CharField(max_length=9,null=True)
    type_sales = models.CharField(max_length=100)    
    is_active = models.BooleanField(default=True)  
    apply = models.BooleanField()

    class Meta:
        db_table = 'clients'

class Medicare(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    agent_usa = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.BigIntegerField()
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)    
    address = models.CharField(max_length=255)
    zipcode = models.IntegerField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    county = models.CharField(max_length=100)
    sex = models.CharField(max_length=1)
    old = models.IntegerField()    
    date_birth = models.DateField()
    dateMedicare = models.DateTimeField()
    migration_status = models.CharField(max_length=100)
    social_security = models.CharField(max_length=9,null=True) 
    nameAutorized = models.CharField(max_length=100, null= True)
    relationship = models.CharField(max_length=100, null= True) 
    status = models.CharField(max_length=100, null=True) 
    status_color = models.IntegerField(null = True)    
    is_active = models.BooleanField(default=True)  

    class Meta:
        db_table = 'medicare'

class ContactClient(models.Model):

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.BooleanField(default=True) 
    email = models.BooleanField(default=True) 
    sms = models.BooleanField(default=True)  
    whatsapp = models.BooleanField(default=True) 

    class Meta:
        db_table = 'ContactClient'

class OptionMedicare(models.Model):

    client = models.ForeignKey(Medicare, on_delete=models.CASCADE)
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    prescripcion  = models.BooleanField(default=True) 
    advantage = models.BooleanField(default=True) 
    dental = models.BooleanField(default=True) 
    complementarios  = models.BooleanField(default=True)  
    suplementarios = models.BooleanField(default=True)     

    class Meta:
        db_table = 'OptionMedicare'

class Call(models.Model):
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE)
    id_agent = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    create_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'calls'

class Typification(models.Model):
    id_call = models.ForeignKey(Call, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'typifications'

class ObamaCare(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE,related_name='agent_sale_aca')
    client = models.OneToOneField(Client, on_delete=models.CASCADE,null=True)
    agent_usa = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)  
    taxes = models.IntegerField()
    plan_name = models.CharField(max_length=200)
    carrier = models.CharField(max_length=200)
    premium = models.DecimalField(max_digits=10, decimal_places=2)
    profiling = models.CharField(max_length=200,default='NO')
    profiling_date = models.DateField(null=True)
    subsidy = models.DecimalField(max_digits=10, decimal_places=2,)
    ffm = models.BigIntegerField(null=True)
    required_bearing = models.BooleanField(default=False,null=True)
    date_bearing = models.DateField(null=True)
    doc_income = models.BooleanField(default=False,null=True)
    doc_migration = models.BooleanField(default=False,null=True)
    status = models.CharField(max_length=50,null=True)
    status_color = models.IntegerField(null = True)    
    policyNumber = models.CharField(max_length=200, null=True)
    work = models.CharField(max_length=50)
    date_effective_coverage = models.DateField(null=True)
    date_effective_coverage_end = models.DateField(null=True)
    date_username = models.DateField(null=True)
    observation = models.TextField(null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'obamacare'

class Dependent(models.Model):  
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    obamacare = models.ForeignKey(ObamaCare, on_delete=models.CASCADE, null=True)  # Relación de muchos a uno
    name = models.CharField(max_length=200)
    apply = models.CharField(max_length=200)
    sex = models.CharField(max_length=1)
    kinship = models.CharField(max_length=100,null=True)
    date_birth = models.DateField(null=True)
    migration_status = models.CharField(max_length=50)
    type_police = models.TextField()

    class Meta:
        db_table = 'dependents'

class Supp(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_sale_supp')
    agent_usa = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)  
    effective_date = models.DateField()
    company = models.CharField(max_length=200)
    policy_type = models.CharField(max_length=100)
    premium = models.DecimalField(max_digits=10, decimal_places=2,)
    preventive = models.CharField(max_length=100)
    coverage = models.CharField(max_length=100)
    policyNumber = models.CharField(max_length=200, null=True)
    deducible = models.CharField(max_length=100)
    status = models.CharField(max_length=50,null=True)
    status_color = models.IntegerField(null = True)
    date_effective_coverage = models.DateField(null=True)
    date_effective_coverage_end = models.DateField(null=True)
    payment_type = models.CharField(max_length=50,null=True)
    observation = models.TextField(null=True)
    is_active = models.BooleanField(default=True)
    dependents = models.ManyToManyField(Dependent, related_name='SuppDependents')

    class Meta:
        db_table = 'supp'

class Payments(models.Model):
    obamaCare = models.ForeignKey(ObamaCare, on_delete=models.CASCADE)
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    # amount = models.DecimalField(max_digits=6, decimal_places=2) esto lo guardo aqui para un futuro

    class Meta:
        db_table = 'payments'

class ObservationAgent(models.Model):
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE)
    id_obamaCare = models.ForeignKey(ObamaCare, on_delete=models.CASCADE, null=True, blank=True)
    id_supp = models.ForeignKey(Supp, on_delete=models.CASCADE, null=True, blank=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        db_table = 'observations_agents'

class ObservationCustomer(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    agent = models.ForeignKey(User, on_delete=models.CASCADE)  
    type_police = models.CharField(max_length=20) 
    typeCall = models.CharField(max_length=20)   
    id_plan = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True) 
    typification = models.TextField()
    content = models.TextField()
    is_active = models.BooleanField(default=True) 

    class Meta:
        db_table = 'observations_customers'

class ObservationCustomerMedicare(models.Model):
    medicare = models.ForeignKey(Medicare, on_delete=models.CASCADE)
    agent = models.ForeignKey(User, on_delete=models.CASCADE)  
    typeCall = models.CharField(max_length=20, null=True)   
    created_at = models.DateTimeField(auto_now_add=True) 
    typification = models.TextField(null=True)
    content = models.TextField()

    class Meta:
        db_table = 'observations_customers_medicare'

class CustomerTracking(models.Model):
    id_obama = models.ForeignKey(ObamaCare, on_delete=models.CASCADE, null=True)
    id_supp = models.ForeignKey(Supp, on_delete=models.CASCADE, null=True)
    cs4h = models.BooleanField(default=False)
    cs8d = models.BooleanField(default=False)
    cs3w = models.BooleanField(default=False)
    cs5w = models.BooleanField(default=False)
    activo = models.BooleanField(default=False)
    gossip = models.BooleanField(default=False)

    class Meta:
        db_table = 'customer_tracking'

class Log(models.Model):
    id_agent = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=255)

    class Meta:
        db_table = 'logs'

class Motivation(models.Model):
    content = models.TextField()

    class Meta:
        db_table = 'motivation'

class ClientAlert(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    name_client = models.CharField(max_length=255)
    phone_number = models.BigIntegerField()
    datetime = models.DateField()
    content = models.TextField()
    is_active = models.BooleanField(default=True)  

    class Meta:
        db_table = 'client_alert'

class DropDownList(models.Model):
    profiling_obama = models.CharField(max_length=255,null=True)
    profiling_supp = models.CharField(max_length=255,null=True)
    status_bd = models.CharField(max_length=255,null=True)

    class Meta:
        db_table = 'drop_down_list'

class ExcelFileMetadata(models.Model):
    file_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ExcelFileMetadata'

class BdExcel(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255,null=True)
    phone = models.BigIntegerField()
    address = models.CharField(max_length=255,null=True)
    city = models.CharField(max_length=200,null=True)
    state = models.CharField(max_length=200,null=True)
    zipCode = models.IntegerField(null=True)
    agent_id = models.IntegerField(null=True)
    excel_metadata = models.ForeignKey('ExcelFileMetadata',on_delete=models.CASCADE,related_name='records')
    is_sold = models.BooleanField(default=False)  # Campo booleano para indicar si está "sold"
    
    class Meta:
        db_table = 'bd_excel'

class ControlQuality(models.Model):
    agent_create = models.ForeignKey(User,on_delete=models.CASCADE, related_name='created_controls' )
    agent = models.ForeignKey(User,on_delete=models.CASCADE, related_name='assigned_controls')
    category = models.CharField(max_length=200, null=True)
    amount = models.BigIntegerField(null= True)
    date = models.DateField()
    findings = models.TextField(null= True)
    observation = models.TextField(null= True)
    create_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  

    class Meta:
        db_table = 'ControlQuality'

class ControlCall(models.Model):
    agent_create = models.ForeignKey(User,on_delete=models.CASCADE, related_name='created_controls_call' )
    agent = models.ForeignKey(User,on_delete=models.CASCADE, related_name='assigned_controls_call',)
    daily = models.BigIntegerField()
    answered = models.BigIntegerField()
    mins = models.BigIntegerField()
    date = models.DateField()
    create_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'ControlCall'

class CommentBD(models.Model):
    bd_excel = models.ForeignKey(BdExcel, on_delete=models.CASCADE)
    agent_create = models.ForeignKey(User,on_delete=models.CASCADE )
    excel_metadata = models.ForeignKey(ExcelFileMetadata,on_delete=models.CASCADE)
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CommentBD'

class DocumentsClient(models.Model):
    file = models.FileField(
        upload_to='consents',
        storage=S3Boto3Storage(),
        null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    class Meta:
        db_table = 'DocumentsClient'

class Consents(models.Model):
    pdf = models.FileField(
        upload_to='DocumentsClient',
        storage=S3Boto3Storage(),
        null=True)
    obamacare = models.ForeignKey(ObamaCare, on_delete=models.CASCADE, null = True)
    medicare = models.ForeignKey(Medicare, on_delete=models.CASCADE, null = True)
    signature = models.FileField(
        upload_to='SignatureConsents',
        storage=S3Boto3Storage(),
        null=True)

    class Meta:
        db_table = 'Consents'


class IncomeLetter(models.Model):
    pdf = models.FileField(
        upload_to='incomeLetter',
        storage=S3Boto3Storage(),
        null=True)
    signature = models.FileField(
        upload_to='SignatureLetterIncome',
        storage=S3Boto3Storage(),
        null=True)
    obamacare = models.ForeignKey(ObamaCare, on_delete=models.CASCADE)

    class Meta:
        db_table = 'IncomeLetter'

class TemporaryToken(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null = True)
    medicare = models.ForeignKey(Medicare, on_delete=models.CASCADE, null = True)
    token = models.TextField()  # Guardar el token firmado
    expiration = models.DateTimeField()
    is_active = models.BooleanField(default=True)  # Para invalidar manualmente

    def is_expired(self):
        return timezone.now() > self.expiration

    def __str__(self):
        return f"Temporary URL for {self.client.first_name} (Active: {self.is_active})"

    class Meta:
        db_table = 'TemporaryToken'

class DocumentObama(models.Model):
    file = models.FileField(
        upload_to='DocumentObama',
        storage=S3Boto3Storage())
    obama = models.ForeignKey(ObamaCare, on_delete=models.CASCADE)
    agent_create = models.ForeignKey(User,on_delete=models.CASCADE )   
    name =  models.CharField(max_length=255, default="Unnamed Document")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'DocumentObama'

class LettersCard(models.Model):
    obama = models.ForeignKey(ObamaCare, on_delete=models.CASCADE)
    agent_create = models.ForeignKey(User,on_delete=models.CASCADE )    
    letters = models.BooleanField(default=False) 
    dateLetters = models.DateField(null=True)
    card = models.BooleanField(default=False) 
    dateCard = models.DateField(null=True)

    class Meta:
        db_table = 'LettersCard'

class AppointmentClient(models.Model):
    obama = models.ForeignKey(ObamaCare, on_delete=models.CASCADE)
    agent_create = models.ForeignKey(User,on_delete=models.CASCADE )    
    appointment = models.TextField() 
    dateAppointment = models.DateField()
    timeAppointment = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'AppointmentClient'

class UserCarrier(models.Model):
    obama = models.ForeignKey(ObamaCare, on_delete=models.CASCADE)
    agent_create = models.ForeignKey(User,on_delete=models.CASCADE)    
    username_carrier = models.CharField(max_length=200,null=True)
    password_carrier = models.CharField(max_length=200,null=True)
    dateUserCarrier = models.DateField(null=True)

    class Meta:
        db_table = 'UserCarrier'