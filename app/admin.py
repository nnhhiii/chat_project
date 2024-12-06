from django.contrib import admin
from .models import User, ChatRoom, UserChatRoom, Message, BlockedUser

admin.site.register(User)# Đăng ký mô hình với Django Admin
admin.site.register(ChatRoom)
admin.site.register(UserChatRoom)
admin.site.register(Message)
admin.site.register(BlockedUser)
