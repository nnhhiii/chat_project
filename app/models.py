from django.db import models
from django.contrib.auth.models import User

class User(models.Model):
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    avatar = models.CharField(max_length=500, default='user.jpeg')
    bio = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_activity = models.CharField(max_length=100, blank=True, null=True)
    study_at = models.CharField(max_length=200, blank=True, null=True)
    working_at = models.CharField(max_length=200, blank=True, null=True)
    relationship = models.CharField(max_length=100, blank=True, null=True)
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    avatar = models.CharField(default='user1.jpg', max_length=500)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    # members = models.ManyToManyField(User, through='UserChatRoom', related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserChatRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'room')

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, blank=True, null=True)
    message_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True)
    content = models.TextField()
    message_type = models.CharField(max_length=10, choices=[('text', 'Text'), ('image', 'Image'), ('video', 'Video')])
    created_at = models.DateTimeField(auto_now_add=True)
    read_status = models.BooleanField(default=False)


    def __str__(self):
        return self.name