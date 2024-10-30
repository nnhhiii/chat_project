from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    # Kết nối WebSocket
    async def connect(self):
        # Lấy user_id từ URL
        self.user_id = self.scope['url_route']['kwargs'].get('user_id', None)
        self.room_id = self.scope['url_route']['kwargs'].get('room_id', None)

        # Tham gia phòng hoặc kết nối người dùng
        if self.room_id:
            self.room_group_name = f'chat_{self.room_id}'
        else:
            self.room_group_name = f'chat_{self.user_id}'

        # Tham gia group chat
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Rời nhóm
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Nhận tin nhắn từ WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json.get('content')
        message_type = text_data_json.get('message_type', 'text')  # Mặc định là 'text'
        message_by = text_data_json.get('message_by', 'Unknown')  # Giá trị mặc định nếu không có

        # Gửi tin nhắn tới nhóm WebSocket
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'content': content,
                'message_type': message_type,
                'message_by': message_by
            }
        )
        print(f"Sent message: {content} to group: {self.room_group_name}")

    # Gửi tin nhắn tới WebSocket client
    async def chat_message(self, event):
        # Nhận tất cả thông tin từ event
        content = event['content']
        message_type = event.get('message_type', 'text')
        message_by = event.get('message_by', 'Unknown')

        # Gửi tin nhắn lại cho client
        await self.send(text_data=json.dumps({
            'content': content,
            'message_type': message_type,
            'message_by': message_by
        }))

