from django.urls import re_path
from .consumer import UserUpdateConsumer

websocket_urlpatterns = [
    re_path(r'ws/user-update/$', UserUpdateConsumer.as_asgi()),  # Ruta para el WebSocket
]