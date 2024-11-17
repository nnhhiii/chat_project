from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Lấy danh sách tất cả các nhóm mà người dùng tham gia từ identifier
        self.identifiers = self.scope['url_route']['kwargs']['identifier'].split(',')
        self.room_group_names = []

        # Tham gia tất cả các nhóm người dùng tham gia
        for identifier in self.identifiers:
            # Xác định tên nhóm từ identifier
            if identifier.startswith("room_"):
                room_id = identifier.split("_")[1]
                room_group_name = f'room_{room_id}'
                self.room_group_names.append(room_group_name)
            elif identifier.startswith("user_"):
                user_ids = list(map(int, identifier.split("_")[1:]))
                user_group_name = f'user_{min(user_ids)}_{max(user_ids)}'
                self.room_group_names.append(user_group_name)

        # Tham gia tất cả các nhóm
        for room_group_name in self.room_group_names:
            await self.channel_layer.group_add(
                room_group_name,
                self.channel_name
            )

        # Chấp nhận kết nối WebSocket
        await self.accept()

    async def disconnect(self, close_code):
        # Rời khỏi tất cả các nhóm
        for room_group_name in self.room_group_names:
            await self.channel_layer.group_discard(
                room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        room_id = data.get('room_id', None)
        recipient_id = data.get('message_to', None)
        content = data.get('content', None)
        message_type = data.get('message_type', 'text')
        message_by = data.get('message_by', None)
        file = data.get('file', None)
        avatar = data.get('avatar', None)
        username = data.get('username', None)

        # Nếu tin nhắn có room_id thì gửi đến group của phòng chat
        if room_id:
            room_group_name = f'room_{room_id}'
            await self.channel_layer.group_send(
                room_group_name,
                {
                    'type': 'chat_message',
                    'content': content,
                    'message_type': message_type,
                    'file': file,
                    'message_by': message_by,
                    'avatar': avatar,
                    'username': username,
                    'room_id': room_id
                }
            )
        # Nếu tin nhắn có recipient_id thì gửi đến group của người nhận
        elif recipient_id:
            user_ids = [int(message_by), int(recipient_id)]
            user_group_name = f'user_{min(user_ids)}_{max(user_ids)}'
            await self.channel_layer.group_send(
                user_group_name,
                {
                    'type': 'chat_message',
                    'content': content,
                    'message_type': message_type,
                    'message_by': message_by,
                    'file': file,
                    'avatar': avatar,
                    'username': username,
                    'message_to': recipient_id
                }
            )

    async def chat_message(self, event):
        # Gửi tin nhắn đến WebSocket của người dùng
        await self.send(text_data=json.dumps({
            'content': event['content'],
            'message_type': event.get('message_type', 'text'),
            'message_by': event.get('message_by', 'Unknown'),
            'file': event.get('file'),
            'avatar': event['avatar'],
            'username': event['username'],
            'message_to': event.get('message_to', 'Unknown'),
            'room_id': event.get('room_id')
        }))
