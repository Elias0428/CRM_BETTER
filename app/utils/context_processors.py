from ..models import ClientAlert  # Ajusta esto al modelo que estés utilizando para las alertas
from datetime import date

def alert_count(request):

    # Verifica si el usuario está autenticado
    if not request.user.is_authenticated:
        return {'expiredAlerts': [], 'alertCount': 0}
    
    # Roles con acceso ampliado
    roleAuditar = ['S', 'Admin']

    # Construcción de la consulta basada en el rol del usuario
    if request.user.role in roleAuditar:

        #(ALERT) Obtener las alertas vencidas (fechas menores o iguales a la fecha actual)
        expiredAlerts = ClientAlert.objects.filter(datetime__lte=date.today(), is_active=True)

        # Contar las alertas
        alertCount = expiredAlerts.count()

    elif request.user.role not in roleAuditar:

        #(ALERT) Obtener las alertas vencidas (fechas menores o iguales a la fecha actual)
        expiredAlerts = ClientAlert.objects.filter(datetime__lte=date.today(), is_active=True, agent = request.user.id)

        # Contar las alertas
        alertCount = expiredAlerts.count()

    return {'expiredAlerts': expiredAlerts, 'alertCount': alertCount}
