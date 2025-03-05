import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

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