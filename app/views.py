from rest_framework import viewsets
from .forms import LoginForm, SignupForm
from .models import User, ChatRoom, Message, UserChatRoom
from .serializers import UserSerializer, ChatRoomSerializer, MessageSerializer, UserChatRoomSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import date
from django.contrib.auth.hashers import make_password, check_password
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


class UserChatRoomViewSet(viewsets.ViewSet):
    queryset = UserChatRoom.objects.all()
    serializer_class = UserChatRoomSerializer

    def list(self, request, user_id=None):
        if user_id:
            # Lấy tất cả UserChatRoom cho user_id
            user_chat_rooms = UserChatRoom.objects.filter(user_id=user_id)

            # Nếu không có phòng chat nào, trả về thông báo
            if not user_chat_rooms.exists():
                return Response({'detail': 'User has not participated in any chat rooms.'}, status=200)

            # Nếu có phòng chat, lấy danh sách phòng
            chat_rooms = [user_chat_room.room for user_chat_room in user_chat_rooms]
            serializer = ChatRoomSerializer(chat_rooms, many=True)
            return Response(serializer.data)

        return Response({'detail': 'User ID not provided.'}, status=400)
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    @action(detail=False, methods=['get'], url_path='get-messages')
    def get_messages(self, request):
        current_user_id = request.user.id  # Lấy người dùng hiện tại từ request
        other_user_id = request.query_params.get('user_id')  # Lấy user_id từ query parameters
        room_id = request.query_params.get('room_id')  # Lấy room_id từ query parameters (nếu có)

        if room_id:
            # Nếu có room_id, chỉ lấy các tin nhắn trong phòng chat đó
            messages = Message.objects.filter(room=room_id).order_by('created_at')
        elif other_user_id:
            # Nếu không có room_id, lấy các tin nhắn 1-1 giữa current_user và other_user
            messages = Message.objects.filter(
                Q(message_by=current_user_id, message_to=other_user_id) |
                Q(message_by=other_user_id, message_to=current_user_id)
            ).order_by('created_at')
        else:
            return Response({"error": "user_id hoặc room_id là bắt buộc"}, status=400)

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
                user = User.objects.get(email=email)

                # So sánh mật khẩu trực tiếp
                if user.password == password:
                    request.session['current_user_id'] = user.id  # Lưu ID người dùng vào session
                    user.is_active = True
                    user.save()
                    return redirect('http://127.0.0.1:8000/')  # Chuyển hướng đến trang chính
                # Nếu mật khẩu không khớp, sử dụng check_password
                elif check_password(password, user.password):
                    request.session['current_user_id'] = user.id  # Lưu ID người dùng vào session
                    user.is_active = True
                    user.save()
                    return redirect('http://127.0.0.1:8000/')  # Chuyển hướng đến trang chính
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
            messages.error(request, "Tên đăng nhập này đã tồn tại. Vui lòng chọn tên đăng nhập khác.")
            return redirect('signup')

        # Tạo đối tượng User mới
        user = User(
            username=username,
            email=email,
            password=make_password(password),  # Mã hóa mật khẩu
            gender=gender,
            date_of_birth=f'{year_of_birth}-{month_of_birth}-{day_of_birth}',  # Định dạng ngày
            study_at=study_at,
            working_at=working_at,
            bio=bio
        )
        user.save()  # Lưu người dùng vào cơ sở dữ liệu
        messages.success(request, "Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.")
        return redirect('login')  # Chuyển hướng đến trang đăng nhập

    # Nếu không phải là POST, trả về form đăng ký
    days = list(range(1, 32))
    months = list(range(1, 13))
    years = list(range(1900, date.today().year + 1))

    return render(request, 'signup.html', {
        'days': days,
        'months': months,
        'years': years
    })
