# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.identifier = self.scope['url_route']['kwargs']['identifier']
        await self.accept()  # Accept the WebSocket connection first
        await self.switch_group(self.identifier)  # Then, assign the initial group

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')

        if command == 'switch':
            new_identifier = data.get('identifier')
            if new_identifier:
                await self.switch_group(new_identifier)
        else:
            # Gửi tin nhắn đến nhóm hiện tại
            content = data.get('content', '')
            message_type = data.get('message_type', 'text')
            message_by = data.get('message_by', 'Unknown')

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'content': content,
                    'message_type': message_type,
                    'message_by': message_by
                }
            )

    async def switch_group(self, identifier):
        # Rời khỏi nhóm hiện tại
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        # Cập nhật nhóm mới
        self.identifier = identifier
        if self.identifier.startswith("rooms_"):
            self.room_group_name = f'chat_{self.identifier.split("_")[1]}'
        elif self.identifier.startswith("users_"):
            self.room_group_name = f'user_{self.identifier.split("_")[1]}'

        # Gia nhập nhóm mới
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Thông báo cho client nhóm mới đã được thiết lập
        await self.send(text_data=json.dumps({
            'message': f'Switched to {self.room_group_name}',
            'channel': self.room_group_name
        }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'content': event['content'],
            'message_type': event.get('message_type', 'text'),
            'message_by': event.get('message_by', 'Unknown')
        }))
