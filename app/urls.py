from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views
from .views import *

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'chatrooms', views.ChatRoomViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'userchatrooms', views.UserChatRoomViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.home),
    path('api/user-chat-rooms/<int:user_id>/', UserChatRoomViewSet.as_view({'get': 'list'}), name='get-user-chat-rooms'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_view, name='signup'),

]
