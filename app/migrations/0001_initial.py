# Generated by Django 5.1.2 on 2024-11-07 01:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('avatar', models.CharField(default='user1.jpg', max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('gender', models.CharField(blank=True, max_length=10, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('avatar', models.CharField(default='user.jpeg', max_length=500)),
                ('cover_picture', models.CharField(default='cover_picture.png', max_length=500)),
                ('bio', models.CharField(blank=True, max_length=200, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('last_activity', models.CharField(blank=True, max_length=100, null=True)),
                ('study_at', models.CharField(blank=True, max_length=200, null=True)),
                ('working_at', models.CharField(blank=True, max_length=200, null=True)),
                ('relationship', models.CharField(blank=True, max_length=100, null=True)),
                ('reset_token', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('message_type', models.CharField(choices=[('text', 'Text'), ('image', 'Image'), ('video', 'Video')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read_status', models.BooleanField(default=False)),
                ('is_deleted_by_user_a', models.BooleanField(default=False)),
                ('is_deleted_by_user_b', models.BooleanField(default=False)),
                ('room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.chatroom')),
                ('message_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to='app.user')),
                ('message_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to='app.user')),
            ],
        ),
        migrations.AddField(
            model_name='chatroom',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_rooms', to='app.user'),
        ),
        migrations.CreateModel(
            name='UserChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.chatroom')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.user')),
            ],
            options={
                'unique_together': {('user', 'room')},
            },
        ),
    ]
