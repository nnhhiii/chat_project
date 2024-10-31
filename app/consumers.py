from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    # Kết nối WebSocket
    async def connect(self):
        self.identifier = self.scope['url_route']['kwargs']['identifier']

        # Kiểm tra nếu identifier là phòng chat hay người dùng
        if self.identifier.startswith("rooms_"):
            self.room_id = self.identifier # Lấy phần tên phòng
            self.room_group_name = f'chat_{self.room_id}'
        elif self.identifier.startswith("users_"):
            self.user_id = self.identifier  # Xem như là user_id
            self.room_group_name = f'user_{self.user_id}'

        # Gia nhập nhóm chat
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Rời nhóm chat
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    # Nhận tin nhắn từ WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json.get('content')
        message_type = text_data_json.get('message_type', 'text')  # Mặc định là 'text'
        message_by = text_data_json.get('message_by', 'Unknown')  # Giá trị mặc định nếu không có
        action = text_data_json.get('action')
        if action == 'switch':
            if self.identifier.startswith("rooms_"):
                self.room_id = self.identifier  # Lấy phần tên phòng
                self.room_group_name = f'chat_{self.room_id}'
            elif self.identifier.startswith("users_"):
                self.user_id = self.identifier  # Xem như là user_id
                self.room_group_name = f'user_{self.user_id}'

            # Gia nhập nhóm chat
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            # Rời khỏi nhóm hiện tại (nếu cần thiết)
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

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

