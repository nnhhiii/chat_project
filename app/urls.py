from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

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
    path('signup/', views.signup_view, name='signup'),
    path('myprofile/', views.my_profile, name='my_profile'),
    path('profile/<int:userid>', views.profile, name='profile'),
    path('create_chat_room/', views.create_chat_room, name='create_chat_room'),
    path('add-user/', views.add_user, name='add_user'),

]
