"""
ASGI config for chat_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from channels.auth import AuthMiddlewareStack
from app import consumers  # Đảm bảo rằng đường dẫn này là chính xác

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/app/rooms/<str:room_id>/", consumers.ChatConsumer.as_asgi()),  # Sử dụng <str:room_name> để trích xuất tên phòng
            path("ws/app/users/<str:user_id>/", consumers.ChatConsumer.as_asgi()),
        ])
    ),
})
