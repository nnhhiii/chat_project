from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'chatrooms', views.ChatRoomViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'user-chat-rooms', views.UserChatRoomViewSet, basename='user-chat-rooms')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create_chat_room/', views.create_chat_room, name='create_chat_room'),
    path('api/user-chat-rooms/<int:user_id>/', views.UserChatRoomViewSet.as_view({'get': 'list'}), name='user-chat-rooms-list'),
    path('add-user/', views.add_user, name='add_user'),
]
