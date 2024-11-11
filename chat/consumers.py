from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import ChatMessage
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('Client connected')
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Retrieve past messages asynchronously
        past_messages = await sync_to_async(
            lambda: list(ChatMessage.objects.filter(room_name=self.room_name).order_by('timestamp'))
        )()

        for message in past_messages:
            await self.send(text_data=json.dumps({
                'username': message.username,
                'message': message.message,
                'timestamp': message.timestamp.isoformat(),  # Convert to ISO format string
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
        timestamp = datetime.now()

        print('Message received')
        print(data['message'])
        # Save the message to the database asynchronously
        await sync_to_async(ChatMessage.objects.create)(
            room_name=self.room_name,
            username=username,
            message=message,
            timestamp=timestamp  # This should be saved as a datetime object in the database
        )

        # Send the message to the group with a serialized timestamp
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'timestamp': timestamp.isoformat()  # Convert to ISO format string
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        timestamp = event['timestamp']  # This is already serialized as a string

        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'username': username,
            'message': message,
            'timestamp': timestamp,  # No need for further conversion
        }))
