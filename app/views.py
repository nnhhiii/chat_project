import cloudinary
from cloudinary.uploader import upload
from rest_framework import viewsets, status
from .forms import LoginForm, SignupForm
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import date
from django.contrib.auth.hashers import make_password, check_password

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

        # Lọc bỏ những người đã bị block
        blocked_users_ids = BlockedUser.objects.filter(blocker=current_user_id).values_list('blocked', flat=True)
        chat_users_ids = chat_users_ids - set(blocked_users_ids)

        # Lấy thông tin những người dùng không bị block
        chat_users = User.objects.filter(id__in=chat_users_ids)
        serializer = UserSerializer(chat_users, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='update-avatar')
    def update_avatar(self, request):
        user = request.session.get('current_user_id')
        file = request.FILES.get('avatar')

        cloudinary_response = cloudinary.uploader.upload(file)
        avatar_url = cloudinary_response.get('secure_url')

        user = User.objects.get(id=user)
        user.avatar = avatar_url
        user.save()

        return Response({
            "message": "Đổi ảnh thành công.",
            "avatar_url": avatar_url
        }, status=status.HTTP_200_OK)

class BlockedUserViewSet(viewsets.ModelViewSet):
    queryset = BlockedUser.objects.all()
    serializer_class = BlockedUserSerializer

    @action(detail=False, methods=['get'], url_path='get-blocked-users')
    def get_blocked_users(self, request):
        current_user_id = request.session.get('current_user_id')
        blocked_users = BlockedUser.objects.filter(blocker_id=current_user_id)
        # Lấy thông tin người dùng bị block
        blocked_user_ids = [blocked_user.blocked.id for blocked_user in blocked_users]

        # Lấy thông tin chi tiết của các người dùng bị block
        blocked_users_info = User.objects.filter(id__in=blocked_user_ids)
        serializer = UserSerializer(blocked_users_info, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='block')
    def block(self, request):
        blocker_id = request.data.get('blocker_id')
        blocked_id = request.data.get('blocked_id')

        blocker = User.objects.get(id=blocker_id)
        blocked = User.objects.get(id=blocked_id)

        # Kiểm tra nếu người dùng đã bị chặn
        if BlockedUser.objects.filter(blocker=blocker, blocked=blocked).exists():
            return Response({'message': 'Người dùng đã bị chặn.'}, status=status.HTTP_400_BAD_REQUEST)

        # Lưu db
        BlockedUser.objects.create(blocker=blocker, blocked=blocked)

        return Response({'message': 'Chặn người dùng thành công!'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='unblock')
    def unblock(self, request):
        blocker_id = request.data.get('blocker_id')
        blocked_id = request.data.get('blocked_id')

        blocker = User.objects.get(id=blocker_id)
        blocked = User.objects.get(id=blocked_id)

        # Kiểm tra nếu người dùng đã bị chặn
        blocked_user = BlockedUser.objects.filter(blocker=blocker, blocked=blocked).first()
        if not blocked_user:
            return Response({'message': 'Người dùng không bị chặn.'}, status=status.HTTP_400_BAD_REQUEST)

        # Xóa bản ghi chặn
        blocked_user.delete()

        return Response({'message': 'Bỏ chặn người dùng thành công!'}, status=status.HTTP_200_OK)


class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer

    @action(detail=False, methods=['post'], url_path='create-room')
    def create_chat_room(self, request):
        name = request.data.get('name')
        avatar = request.data.get('avatar')
        creator_id = request.data.get('creator')
        user_ids = request.data.get('users', [])
        content = request.data.get('content')

        # Tạo phòng chat
        creator = User.objects.get(id=creator_id)
        chat_room = ChatRoom.objects.create(name=name, avatar=avatar, creator=creator)

        # Thêm creator vào phòng chat
        UserChatRoom.objects.create(user=creator, room=chat_room)

        # Thêm các người dùng vào phòng chat
        for user_id in user_ids:
            user = User.objects.get(id=user_id)
            UserChatRoom.objects.get_or_create(user=user, room=chat_room)

        # Tạo tin nhắn đầu tiên cho phòng chat
        Message.objects.create(
            room=chat_room,
            message_by=creator,
            content=content,
            message_type='text'
        )
        # Trả về dữ liệu phòng chat mới
        serializer = ChatRoomSerializer(chat_room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='update-avatar')
    def update_avatar(self, request):
        room_id = request.data.get('room_id')
        file = request.FILES.get('avatar')

        cloudinary_response = cloudinary.uploader.upload(file)
        avatar_url = cloudinary_response.get('secure_url')

        room = ChatRoom.objects.get(id=room_id)
        room.avatar = avatar_url
        room.save()

        return Response({
            "message": "Đổi ảnh thành công.",
            "avatar_url": avatar_url
        }, status=status.HTTP_200_OK)


class UserChatRoomViewSet(viewsets.ModelViewSet):
    queryset = UserChatRoom.objects.all()
    serializer_class = UserChatRoomSerializer

    @action(detail=False, methods=['get'], url_path='chat-rooms')
    def room_or_user_info(self, request):
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

            # Lấy thông tin của phòng chat (bao gồm creator)
            chat_room = ChatRoom.objects.get(id=room_id)
            creator_id = chat_room.creator.id  # ID của người tạo phòng

            # Trả về danh sách người dùng và ID của người tạo phòng
            return Response({
                'users': serializer.data,
                'room_creator_id': creator_id
            })

        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='add-users')
    def add_users_to_room(self, request):
        room_id = request.data.get('room_id')
        user_ids = request.data.get('user_ids', [])

        chat_room = ChatRoom.objects.get(id=room_id)

        for user_id in user_ids:
            user = User.objects.get(id=user_id)
            UserChatRoom.objects.get_or_create(user=user, room=chat_room)

        return Response({
            "message": "Thêm thành viên thành công!",
            "room_id": room_id,
            "user_ids": user_ids
            }, status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'], url_path='delete-user-from-room')
    def delete_user_from_room(self, request):
        user_id = request.data.get('user_id')
        room_id = request.data.get('room_id')

        # Kiểm tra xem người dùng có tồn tại trong phòng không
        user_chat_room = UserChatRoom.objects.filter(user_id=user_id, room_id=room_id).first()

        if user_chat_room:
            user_chat_room.delete()  # Xóa người dùng khỏi phòng
            return Response({
                "message": "Xóa thành công!",
                "room_id": room_id,
                "user_id": user_id
            }, status=status.HTTP_200_OK)

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

    @action(detail=False, methods=['post'])
    def send_message(self, request):
        content = request.data.get('content')
        file = request.FILES.get('file')
        message_by = User.objects.get(id=request.session['current_user_id'])

        if file:
            if file.content_type.startswith('video'):
                cloudinary_response = cloudinary.uploader.upload(file, resource_type="video")
                message_type = 'video'
            else:
                cloudinary_response = cloudinary.uploader.upload(file)
                message_type = 'image'
            file_url = cloudinary_response.get('secure_url')
        else :
            file_url=None
            message_type = 'text'

        # Kiểm tra room_id và message_to
        room_id = request.data.get('room_id')
        message_to_id = request.data.get('message_to')

        if room_id:
            message_to = None
        else:
            message_to = User.objects.get(id=message_to_id)  # Lấy User nếu có message_to
            room_id = None

        # Lưu tin nhắn vào cơ sở dữ liệu
        message = Message.objects.create(
            content=content,
            message_by=message_by,
            message_type=message_type,
            message_to=message_to,
            room_id=room_id,
            file=file_url
        )
        return Response({
            'content': message.content,
            'message_type': message.message_type,
            'file': message.file,
            'message_by': message.message_by.username,
            'message_to': message.message_to.username if message.message_to else None,
            'room_id': message.room_id
        })


def home(request):
    return render(request, 'home.html')
def blocked_list(request):
    return render(request, 'blocked.html')
def my_profile(request):
    return render(request, 'my_pro5.html')
def profile(request, userid):
    return render(request, 'user_pro5.html', {'userid': userid})

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
