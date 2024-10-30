from rest_framework import viewsets

from .forms import LoginForm
from .models import User, ChatRoom, Message, UserChatRoom
from .serializers import UserSerializer, ChatRoomSerializer, MessageSerializer, UserChatRoomSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.sessions.models import Session


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'], url_path='chat-users')
    def get_chat_users(self, request):
        current_user_id = request.session.get('current_user_id')  # Lấy ID người dùng hiện tại

        # Lấy tất cả những người đã gửi hoặc nhận tin nhắn từ current_user_id
        sent_messages = Message.objects.filter(message_by=current_user_id).values_list('message_to', flat=True)
        received_messages = Message.objects.filter(message_to=current_user_id).values_list('message_by', flat=True)

        # Gộp các user đã nhắn tin (bao gồm gửi và nhận), loại bỏ các giá trị trùng lặp
        chat_users_ids = set(list(sent_messages) + list(received_messages))

        # Lấy thông tin user từ các ID
        chat_users = User.objects.filter(id__in=chat_users_ids)
        serializer = UserSerializer(chat_users, many=True)

        return Response(serializer.data)


class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer


class UserChatRoomViewSet(viewsets.ModelViewSet):
    queryset = UserChatRoom.objects.all()
    serializer_class = UserChatRoomSerializer

    @action(detail=False, methods=['get'], url_path='chat-rooms')
    def get_request(self, request):
        user_id = request.query_params.get('user_id')
        room_id = request.query_params.get('room_id')
        if user_id:
            chat_rooms = UserChatRoom.objects.filter(user=user_id)
            rooms = [chat_room.room for chat_room in chat_rooms]
            serializer = ChatRoomSerializer(rooms, many=True)
        elif room_id:
            users_chat_rooms = UserChatRoom.objects.filter(room=room_id)
            users = [users_chat_room.user for users_chat_room in users_chat_rooms]
            serializer = UserSerializer(users, many=True)

        return Response(serializer.data)
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    @action(detail=False, methods=['get'], url_path='get-messages')
    def get_messages(self, request):
        current_user_id = request.session.get('current_user_id')  # Lấy người dùng hiện tại từ request
        other_user_id = request.query_params.get('user_id')  # Lấy user_id từ query parameters
        room_id = request.query_params.get('room_id')  # Lấy room_id từ query parameters (nếu có)

        if room_id:
            messages = Message.objects.filter(room=room_id).order_by('created_at')
        elif other_user_id:
            messages = Message.objects.filter(
                Q(message_by=current_user_id, message_to=other_user_id) |
                Q(message_by=other_user_id, message_to=current_user_id)
            ).order_by('created_at')

        # Sử dụng serializer để chuyển đổi dữ liệu
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Kiểm tra thông tin đăng nhập
            try:
                user = User.objects.get(email=email, password=password)
                request.session['current_user_id'] = user.id  # Lưu ID người dùng vào session
                user.is_active = True
                user.save()
                return redirect('http://127.0.0.1:8000/')

            except User.DoesNotExist:
                messages.error(request, "Sai thông tin đăng nhập.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})
def logout_view(request):
    logout(request)  # Đăng xuất và xóa session
    return redirect('login')
