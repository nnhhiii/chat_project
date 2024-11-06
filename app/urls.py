from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import *

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'chatrooms', views.ChatRoomViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'userchatrooms', views.UserChatRoomViewSet, basename='user-chat-rooms')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', signup_view, name='signup'),
    path('create_chat_room/', views.create_chat_room, name='create_chat_room'),
    path('add-user/', views.add_user, name='add_user'),
    path('search/', views.search, name='search'),
]

