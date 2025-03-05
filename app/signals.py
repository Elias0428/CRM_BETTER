from django.db.models.signals import pre_save
from django.dispatch import receiver


# Lista de modelos que quieres aplicar la transformación a mayúsculas
models_to_convert = [
    'Client', 'ObamaCare', 'Dependent', 'Supp'
]

# Función para convertir a mayúsculas los campos relevantes de cada modelo
def convert_fields_to_uppercase(instance):
    fields_to_uppercase = {
        'Client': ['first_name', 'last_name', 'city', 'state', 'county', 'migration_status', 'type_sales', 'address'],
        'ObamaCare': ['plan_name', 'carrier', 'profiling', 'status', 'work', 'apply', 'observation'],
        'Dependent': ['name', 'apply', 'sex', 'kinship', 'migration_status', 'type_police'],
        'Supp': ['company', 'policy_type', 'preventive']
    }
    
    model_name = instance.__class__.__name__
    if model_name in fields_to_uppercase:
        for field in fields_to_uppercase[model_name]:
            if hasattr(instance, field) and getattr(instance, field):
                setattr(instance, field, getattr(instance, field).upper())

@receiver(pre_save)
def apply_uppercase_conversion(sender, instance, **kwargs):
    # Aplica solo a los modelos de la lista
    if sender.__name__ in models_to_convert:
        convert_fields_to_uppercase(instance)


