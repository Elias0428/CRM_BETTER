from django.urls import re_path
from .consumer import UserUpdateConsumer, ProductAlertConsumer

websocket_urlpatterns = [
    re_path(r'ws/user-update/$', UserUpdateConsumer.as_asgi()),  # Ruta para el WebSocket
    re_path(r'ws/alerts/$', ProductAlertConsumer.as_asgi()),
]