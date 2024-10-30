const imgBaseUrl = '/static/img/';
const currentUserId = 1;

function fetchChatUsers() {
    $.ajax({
        url: '/api/users/chat-users/',
        method: 'GET',
        success: function(data) {
            const chatUsersList = $('.chat_users_list');
            chatUsersList.empty();

            if (data.length === 0) {
                chatUsersList.append('<div>Chưa có cuộc trò chuyện nào.</div>');
                return;
            }

            $.each(data, function(index, user) {
                let avatarUrl = user.avatar ? `${imgBaseUrl}${user.avatar}` : '/path/to/default/user1.jpg';
                let userHTML = `
                    <a href="#" onclick="showMessages(${user.id}, null)">
                        <div class="mess1" style="position:relative" data-chat-user-id="${user.id}">
                            <div class="ava" style="background-image: url('${avatarUrl}'); background-position: center"></div>
                            <div class="username">${user.username}</div>
                            <br><br>
                            <div class="mini_content" style="max-width:200px;">
                                <span class="latest_message">Đang tải...</span>
                                <div style="font-size:12px;position:absolute;right:20px;bottom:20px;" class="time_description">Đang tải...</div>
                            </div>
                        </div>
                    </a>`;
                chatUsersList.append(userHTML);
                fetchLatestMessage(user.id, null);
            });

            fetchChatRooms();
        },
        error: function(error) {
            console.error('Error fetching chat users:', error);
        }
    });
}

function fetchChatRooms() {
    $.ajax({
        url: `/api/user-chat-rooms/${currentUserId}/`,
        method: 'GET',
        success: function(rooms) {
            const chatUsersList = $('.chat_users_list');

            if (rooms.length === 0) {
                chatUsersList.append('<div>Chưa tham gia phòng chat nào.</div>');
            } else {
                $.each(rooms, function(index, room) {
                    let roomHTML = `
                        <a href="#" onclick="showMessages(null, ${room.id})">
                            <div class="mess1" data-chat-room-id="${room.id}" style="position:relative">
                                <div class="ava" style="background-image: url('${imgBaseUrl}${room.avatar}');"></div>
                                <div class="username">${room.room_name}</div>
                                <br><br>
                                <div class="mini_content" style="max-width:200px;">
                                    <span class="latest_message">Đang tải...</span>
                                    <div style="font-size:12px;position:absolute;right:20px;bottom:20px;" class="time_description">Đang tải...</div>
                                </div>
                            </div>
                        </a>`;
                    chatUsersList.append(roomHTML);
                    fetchLatestMessage(null, room.id);
                });
            }
        },
        error: function(error) {
            console.error('Error fetching chat rooms:', error);
        }
    });
}

function fetchLatestMessage(user_id, room_id) {
    if (user_id === null && room_id === null) return;

    let url = `/api/messages/get-messages`;
    if (user_id) {
        url += `?user_id=${user_id}`;
    } else if (room_id) {
        url += `?room_id=${room_id}`;
    }

    $.ajax({
        url: url,
        method: 'GET',
        success: function(messages) {
            if (messages.length > 0) {
                let latestMessage = messages[messages.length - 1];
                let miniContent = user_id !== null ?
                    $(`[data-chat-user-id="${user_id}"] .mini_content .latest_message`) :
                    $(`[data-chat-room-id="${room_id}"] .mini_content .latest_message`);

                let timeDescription = user_id !== null ?
                    $(`[data-chat-user-id="${user_id}"] .mini_content .time_description`) :
                    $(`[data-chat-room-id="${room_id}"] .mini_content .time_description`);

                miniContent.text(latestMessage.content);
                timeDescription.text(calculateTimeAgo(latestMessage.created_at));
            }
        },
        error: function(error) {
            console.error('Error fetching latest message:', error);
        }
    });
}

function calculateTimeAgo(timestamp) {
    let timeAgo = new Date(timestamp);
    let now = new Date();
    let difference = Math.floor((now - timeAgo) / 1000);

    if (difference < 60) {
        return `${difference} giây trước`;
    } else if (difference < 3600) {
        return `${Math.floor(difference / 60)} phút trước`;
    } else if (difference < 86400) {
        return `${Math.floor(difference / 3600)} giờ trước`;
    } else {
        return `${Math.floor(difference / 86400)} ngày trước`;
    }
}

function showMessages(user_id = null, room_id = null) {
    $('.content').html('');

    if (room_id) {
        setupWebSocket(room_id, null, currentUserId);
        loadMessage(room_id, null, currentUserId);
    } else if (user_id) {
        setupWebSocket(null, user_id, currentUserId);
        loadMessage(null, user_id, currentUserId);
    } else {
        console.error('Cần cung cấp user_id hoặc room_id.');
    }
}

$('#create-group-btn').click(function() {
    const groupName = $('#group-name-input').val();
    const groupAvatar = $('#group-avatar-input')[0].files[0];

    const formData = new FormData();
    formData.append('name', groupName);
    if (groupAvatar) {
        formData.append('avatar', groupAvatar);
    }

    $.ajax({
        url: '/api/chat-rooms/',
        method: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function(data) {
            console.log('Nhóm chat đã được tạo:', data);
            fetchChatRooms();
        },
        error: function(error) {
            console.error('Lỗi khi tạo nhóm chat:', error);
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    fetchChatUsers();
});

document.querySelector('.btn-add-user').addEventListener('click', function() {
    $('#addUserModal').modal('show');
});

fetch('http://localhost:8000/api/userchatrooms/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        user_id: 1,
        chat_room_id: 2,
    }),
})
.then(response => response.json())
.then(data => console.log(data))
.catch((error) => console.error('Error:', error));
