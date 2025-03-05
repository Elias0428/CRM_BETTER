import datetime
from django import forms
from app.models import *

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
        exclude = ['agent','date_birth','social_security','old']


class ObamaForm(forms.ModelForm):
    class Meta:
        model = ObamaCare
        fields = '__all__'
        exclude = ['client','agent','is_active','profiling','profiling_date','ffm','required_bearing','date_bearing','status','npm','date_effective_coverage','date_effective_coverage_end','password_carrier','username_carrier','policyNumber','status_color','observation']

class SuppForm(forms.ModelForm):
    class Meta:
        model = Supp
        fields = '__all__'
        exclude = ['client','agent','is_active','status','date_effective_coverage','date_effective_coverage_end','payment_type','status_color','policyNumber','observation','effective_date','dependents']

class DepentForm(forms.ModelForm):
    class Meta:
        model = Dependent
        fields = '__all__'
        exclude = ['client','obamacare','date_birth']

class ClientAlertForm(forms.ModelForm):
    class Meta:
        model = ClientAlert
        fields = '__all__'
        exclude = ['agent']


class ReporteSeleccionForm(forms.Form):
    TIPOS_DE_REPORTE = (
        ('clientes_por_agente', 'Clientes por Agente'),
        ('clientes_activos', 'Clientes Activos e Inactivos'),
        ('clientes_por_estado', 'Clientes por Estado'),
        ('planes_obamacare', 'Planes de ObamaCare por Cliente'),
        ('dependientes_cliente', 'Dependientes por Cliente'),
        ('subsidios_por_agente', 'Subsidios por Agente'),
        ('clientes_por_migracion', 'Clientes por Estado de Migración'),
        ('clientes_por_fecha_nacimiento', 'Clientes por Fecha de Nacimiento'),
        ('clientes_por_tipo_venta', 'Clientes por Tipo de Venta'),
        ('clientes_con_docs_requeridos', 'Clientes con Documentos Requeridos'),
        ('cobertura_efectiva', 'Fecha de Cobertura Efectiva de ObamaCare'),
        # Agregar más opciones de reportes según se necesite
    )

    tipo_reporte = forms.ChoiceField(choices=TIPOS_DE_REPORTE, required=True)

class ExcelUploadForm(forms.Form):
    file = forms.FileField(label="Subir archivo Excel", 
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx, .xls'  # Limita a archivos Excel
        }))

class ControlQualityForm(forms.ModelForm):
    class Meta:
        model = ControlQuality
        fields = '__all__'
        exclude = ['agent_create','observation','amount','category']

    #cambiamos formato de la fecha para guardarla como se debe en la BD ya que la obtenes en formato USA
    def clean_date(self):
        date_input = self.cleaned_data['date']
        
        # Si el input ya es un objeto de fecha, lo devolvemos tal cual
        if isinstance(date_input, datetime.date):
            return date_input

        # Si es una cadena, lo convertimos al formato adecuado
        try:
            return datetime.strptime(date_input, '%m/%d/%Y').date()
        except ValueError:
            raise forms.ValidationError('Formato de fecha inválido. Use MM/DD/YYYY.')


class ControlCallForm(forms.ModelForm):
    class Meta:
        model = ControlCall
        fields = '__all__'
        exclude = ['agent_create']

    #cambiamos formato de la fecha para guardarla como se debe en la BD ya que la obtenes en formato USA
    def clean_date(self):
        date_input = self.cleaned_data['date']
        
        # Si el input ya es un objeto de fecha, lo devolvemos tal cual
        if isinstance(date_input, datetime.date):
            return date_input

        # Si es una cadena, lo convertimos al formato adecuado
        try:
            return datetime.strptime(date_input, '%m/%d/%Y').date()
        except ValueError:
            raise forms.ValidationError('Formato de fecha inválido. Use MM/DD/YYYY.')


    