import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
import re

logger = logging.getLogger(__name__)
class UserUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Este método se ejecuta cuando se establece la conexión WebSocket.
        self.room_group_name = 'user_updates'

        logger.info(f'Usuario conectado: {self.channel_name}')
        # Únete al grupo de WebSocket para enviar actualizaciones de usuario
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Este método se ejecuta cuando se desconecta el WebSocket
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print('LLegó el mensaje vale.')
        # Recibe el mensaje desde el WebSocket (en este caso, el ID del usuario)
        data = json.loads(text_data)
        user_id = data.get('user_id')  # El ID del usuario enviado desde el cliente
        message = data.get('message')  # El mensaje enviado desde el servidor

        # Aquí puedes manejar los mensajes si necesitas hacer algo con ellos, 
        # como almacenar en base de datos, etc.

        # Enviar la respuesta al cliente
        await self.send(text_data=json.dumps({
            'status': 'success',
            'user_id': user_id,
            'message': message
        }))

    async def user_update(self, event):
        # Este método maneja el tipo de mensaje "user_update"
        user_id = event['user_id']
        message = event['message']
        logger.info(f'Recibido evento user_update: {event}')

        # Enviar la respuesta al WebSocket
        await self.send(text_data=json.dumps({
            'status': 'success',
            'user_id': user_id,
            'message': message
        }))


class ProductAlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        #asi estaba antes
        #self.group_name = 'product_alerts'
        #await self.channel_layer.group_add(self.group_name, self.channel_name)
        #await self.accept()

        # Obtener la dirección del host del WebSocket
        raw_host = self.scope["headers"]
        host = None
        for header in raw_host:
            if header[0] == b'host':
                host = header[1].decode("utf-8")
                break

        if not host:
            host = "default"

        # Limpiar el host para que sea un nombre de grupo válido
        safe_host = re.sub(r'[^a-zA-Z0-9_.-]', '_', host)
        self.group_name = f'product_alerts_{safe_host}'

        print(f"Conectando WebSocket al grupo: {self.group_name}")

        # Unirse al grupo
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Enviar el mensaje a todos los clientes conectados
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_alert',
                'message': message,
            }
        )

    async def send_alert(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))
