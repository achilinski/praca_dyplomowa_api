from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Send past messages to the newly connected client
        past_messages = ChatMessage.objects.filter(room_name=self.room_name).order_by('timestamp')
        for message in past_messages:
            await self.send(text_data=json.dumps({
                'username': message.username,
                'message': message.message,
                'timestamp': str(message.timestamp)
            }))

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data.get('username', 'Anonymous')

        # Save the message to the database
        ChatMessage.objects.create(room_name=self.room_name, username=username, message=message)

        # Send message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'username': username,
            'message': message,
        }))
