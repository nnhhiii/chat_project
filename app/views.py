from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from .forms import LoginForm, SignupForm
from .models import User, ChatRoom, Message, UserChatRoom
from .serializers import UserSerializer, ChatRoomSerializer, MessageSerializer, UserChatRoomSerializer
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import date
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.sessions.models import Session
from rest_framework.decorators import api_view

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'], url_path='chat-users')
    def get_chat_users(self, request):
        current_user_id = request.session.get('current_user_id')

        # Lấy tất cả những người đã gửi hoặc nhận tin nhắn
        sent_messages = Message.objects.filter(message_by=current_user_id).values_list('message_to', flat=True)
        received_messages = Message.objects.filter(message_to=current_user_id).values_list('message_by', flat=True)
        chat_users_ids = set(list(sent_messages) + list(received_messages))
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

    @action(detail=False, methods=['post'])
    def add_user_to_chat_room(self, request):
        user_id = request.data.get('user_id')
        chat_room_id = request.data.get('chat_room_id')

        if not user_id or not chat_room_id:
            return Response({'error': 'user_id và chat_room_id là bắt buộc.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            chat_room = ChatRoom.objects.get(id=chat_room_id)
            user_chat_room, created = UserChatRoom.objects.get_or_create(user=user, chat_room=chat_room)

            if created:
                return Response({'message': 'User added to chat room successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'User already in this chat room.'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except ChatRoom.DoesNotExist:
            return Response({'error': 'Chat room not found.'}, status=status.HTTP_404_NOT_FOUND)

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

        # Lọc tin nhắn theo trường is_deleted_by_user_a hoặc is_deleted_by_user_b
        messages = messages.exclude(
            Q(is_deleted_by_user_a=True, message_by=current_user_id) |
            Q(is_deleted_by_user_b=True, message_to=current_user_id)
        )

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

def home(request):
    return render(request, 'home.html')

def login_view(request):
    host_url = request.build_absolute_uri('/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Kiểm tra thông tin đăng nhập
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                request.session['current_user_id'] = user.id
                return redirect(host_url)
            else:
                try:
                    user = User.objects.get(email=email)

                    # So sánh mật khẩu trực tiếp
                    if user.password == password:
                        request.session['current_user_id'] = user.id  # Lưu ID người dùng vào session
                        user.is_active = True
                        user.save()
                        return redirect(host_url)  # Chuyển hướng đến trang chính
                    # Nếu mật khẩu không khớp, sử dụng check_password
                    elif check_password(password, user.password):
                        request.session['current_user_id'] = user.id  # Lưu ID người dùng vào session
                        user.is_active = True
                        user.save()
                        return redirect(host_url)  # Chuyển hướng đến trang chính
                    else:
                        messages.error(request, "Sai thông tin đăng nhập.")
                except User.DoesNotExist:
                    messages.error(request, "Sai thông tin đăng nhập.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)  # Đăng xuất và xóa session
    return redirect('login')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_chat_room(request):
    serializer = ChatRoomSerializer(data=request.data)

    if serializer.is_valid():
        chat_room = serializer.save(creator=request.user)
        UserChatRoom.objects.create(user=request.user, room=chat_room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def user_chat_room_list(request):
    return Response({"message": "User chat rooms here"})

def add_user_to_chat(request):
    if request.method == 'POST':
        user_ids = request.POST.getlist('user_ids[]')
        chat_room_id = request.POST.get('chat_room_id')  # Thêm cách lấy chat_room_id từ request
        chat_room = UserChatRoom.objects.get(id=chat_room_id)

        for user_id in user_ids:
            user = User.objects.get(id=user_id)
            chat_room.users.add(user)  # Thêm người dùng vào phòng chat

        return redirect('chat_room_detail', chat_room_id=chat_room_id)  # Chuyển hướng về chi tiết phòng chat
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@require_POST
def add_user(request):
    if request.method == 'POST':
        user_ids = request.POST.getlist('user_ids')  # Lấy danh sách ID người dùng đã chọn
        # Thực hiện logic để thêm người dùng vào nhóm
        for user_id in user_ids:
            # Thêm logic để thêm người dùng vào nhóm, ví dụ:
            # UserChatRoom.objects.create(user_id=user_id, group=group)
            pass
        return redirect('chatrooms')  # Chuyển hướng sau khi thêm

    return render(request, 'home.html')  # Nếu không phải POST, render lại trang

def signup_view(request):
    if request.method == 'POST':
        # Nhận dữ liệu từ form
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        day_of_birth = request.POST.get('day_of_birth')
        month_of_birth = request.POST.get('month_of_birth')
        year_of_birth = request.POST.get('year_of_birth')
        gender = request.POST.get('gender')
        study_at = request.POST.get('study_at')
        working_at = request.POST.get('working_at')
        bio = request.POST.get('bio')

        # Kiểm tra nếu email hoặc username đã tồn tại
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email này đã được sử dụng. Vui lòng nhập email khác.")
            return redirect('signup')
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Tên người dùng này đã được sử dụng. Vui lòng nhập tên khác.")
            return redirect('signup')

        # Tạo đối tượng người dùng mới
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),  # Mã hóa mật khẩu
            gender=gender,
            date_of_birth=date(year=int(year_of_birth), month=int(month_of_birth), day=int(day_of_birth)),
            study_at=study_at,
            working_at=working_at,
            bio=bio,
            is_active=True
        )
        user.save()

        messages.success(request, "Đăng ký thành công. Bạn có thể đăng nhập ngay bây giờ.")
        return redirect('login')

    return render(request, 'signup.html')


def search(request):
    query = request.POST.get('timkiem', '')
    user_results = []
    chat_results = []

    if query:
        # Tìm kiếm người dùng theo username
        user_results = User.objects.filter(Q(username__icontains=query))  # Tìm kiếm người dùng có tên chứa từ khóa

        # Tìm kiếm nhóm chat theo name (tên nhóm chat)
        chat_results = ChatRoom.objects.filter(Q(name__icontains=query))  # Tìm kiếm nhóm chat có tên chứa từ khóa

    return render(request, 'home.html', {
        'user_results': user_results,
        'chat_results': chat_results,
        'query': query,
    })