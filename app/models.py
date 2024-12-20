from cloudinary.models import CloudinaryField
from django.db import models
from django.contrib.auth.models import User

class User(models.Model):
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    avatar = models.TextField('file', null=True, blank=True)
    cover_picture = models.CharField(max_length=500, default='cover_picture.png')
    bio = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_activity = models.CharField(max_length=100, blank=True, null=True)
    study_at = models.CharField(max_length=200, blank=True, null=True)
    working_at = models.CharField(max_length=200, blank=True, null=True)
    relationship = models.CharField(max_length=100, blank=True, null=True)
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username}"

class BlockedUser(models.Model):
    blocker = models.ForeignKey(User, related_name='blocked_by', on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name='blocked_users', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f"{self.blocker.username} chặn {self.blocked.username}"

class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    avatar = models.TextField('file', null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

class UserChatRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'room')

    def __str__(self):
        return f"{self.user.username} in {self.room.name}"


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, blank=True, null=True)
    message_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True)
    content = models.TextField(null=True, blank=True)
    message_type = models.CharField(max_length=10, choices=[('text', 'Text'), ('image', 'Image'), ('video', 'Video')])
    file = models.TextField('file', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_status = models.BooleanField(default=False)
    is_deleted_by_user_a = models.BooleanField(default=False)  # Đánh dấu tin nhắn đã bị ẩn đối với người dùng A
    is_deleted_by_user_b = models.BooleanField(default=False)  # Đánh dấu tin nhắn đã bị ẩn đối với người dùng B


    def delete_message(self, user):
        """Đánh dấu tin nhắn là đã xóa đối với người dùng."""
        if self.message_by == user:
            self.is_deleted_by_user_a = True
        elif self.message_to == user:
            self.is_deleted_by_user_b = True
        self.save()
    def __str__(self):
        return f"{self.message_by.username}: {self.content[:20]}"