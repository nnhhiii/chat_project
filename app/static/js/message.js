const imgBaseUrl = '/static/img/';

document.addEventListener('DOMContentLoaded', function () {
    fetchChatUsers();
});

// Hàm lấy danh sách người dùng đã chat
function fetchChatUsers() {
    $.ajax({
        url: '/api/users/chat-users/',
        method: 'GET',
        success: function(data) {
            const chatUsersList = $('.chat_users_list');
            chatUsersList.empty();

            // Hiển thị thông báo nếu không có người dùng đã chat
            if (data.length === 0) {
                chatUsersList.append('<div>Chưa có cuộc trò chuyện nào.</div>');
                return;
            }

            // Duyệt qua từng user và hiển thị
            data.forEach(user => {
                let userHTML = `
                    <a href="#" onclick="showMessages(${user.id}, null)">
                        <div class="mess1" id="chat-user" style="position:relative" data-chat-user-id="${user.id}">
                            <div class="ava" style="background-image: url('${imgBaseUrl}${user.avatar}'); background-position: center"></div>
                            <div class="username">${user.username}</div>
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

// Hàm lấy danh sách phòng chat
function fetchChatRooms() {
    const currentUserId = 1; // Thay bằng ID người dùng hiện tại

    $.ajax({
        url: `/api/user-chat-rooms/${currentUserId}`,
        method: 'GET',
        success: function(rooms) {
            const chatUsersList = $('.chat_users_list');

            // Hiển thị thông báo nếu không có phòng chat nào
            if (rooms.length === 0) {
                chatUsersList.append('<div>Chưa tham gia phòng chat nào.</div>');
            } else {
                rooms.forEach(room => {
                    let roomHTML = `
                        <a href="#" onclick="showMessages(null, ${room.id})">
                            <div class="mess1" id="chat-room" data-chat-room-id="${room.id}" style="position:relative">
                                <div class="ava" style="background-image: url('${imgBaseUrl}${room.avatar}');"></div>
                                <div class="username">${room.room_name}</div>
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

// Hàm lấy tin nhắn gần nhất của người dùng hoặc phòng chat
function fetchLatestMessage(user_id, room_id) {
    if (!user_id && !room_id) return;

    let url = `/api/messages/get-messages?`;
    url += user_id ? `user_id=${user_id}` : `room_id=${room_id}`;

    $.ajax({
        url: url,
        method: 'GET',
        success: function(messages) {
            if (messages.length > 0) {
                let latestMessage = messages[messages.length - 1];
                let selector = user_id ? `[data-chat-user-id="${user_id}"]` : `[data-chat-room-id="${room_id}"]`;
                $(`${selector} .latest_message`).text(latestMessage.content);
                $(`${selector} .time_description`).text(calculateTimeAgo(latestMessage.created_at));
            }
        },
        error: function(error) {
            console.error('Error fetching latest message:', error);
        }
    });
}

// Hàm tính toán thời gian đã qua
function calculateTimeAgo(timestamp) {
    let timeAgo = new Date(timestamp);
    let now = new Date();
    let difference = Math.floor((now - timeAgo) / 1000);

    if (difference < 60) return `${difference} giây trước`;
    else if (difference < 3600) return `${Math.floor(difference / 60)} phút trước`;
    else if (difference < 86400) return `${Math.floor(difference / 3600)} giờ trước`;
    return `${Math.floor(difference / 86400)} ngày trước`;
}

// Hàm hiển thị tin nhắn khi nhấn vào user hoặc phòng chat
function showMessages(user_id = null, room_id = null) {
    const currentUserId = 1;
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

// Hàm cấu hình WebSocket
function setupWebSocket(roomId = null, recipientId = null, currentUserId = null) {
    let ws_url = `ws://${window.location.host}/ws/app/`;
    ws_url += roomId ? `rooms/${roomId}/` : `users/${recipientId}/`;

    const chatSocket = new WebSocket(ws_url);

    $('#messageForm').on('submit', function (event) {
        event.preventDefault();
        const message = $('textarea[name="content"]').val().trim();
        if (message) {
            chatSocket.send(JSON.stringify({'message': message}));
            addMessage({ content: message, message_by: currentUserId, message_type: 'text', room: roomId, message_to: recipientId });
            $('textarea[name="content"]').val('');
        }
    });

    chatSocket.onopen = function () {
        console.log('WebSocket kết nối thành công');
        loadMessage(roomId, recipientId, currentUserId);
    };

    chatSocket.onclose = function () {
        console.error('WebSocket bị đóng. Đang thử kết nối lại...');
        reconnectWebSocket();
    };
}

// Hàm thêm tin nhắn vào API
function addMessage(payload) {
    $.ajax({
        url: '/api/messages/',
        type: 'POST',
        contentType: 'application/json',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        data: JSON.stringify(payload),
        success: function (data) {
            displayMessage(data, payload.message_by);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.error('Lỗi khi lưu tin nhắn:', textStatus, errorThrown);
        }
    });
}

// Hàm hiển thị tin nhắn
function displayMessage(data, currentUserId) {
    let messageClass = data.message_by === currentUserId ? 'sent-message' : 'received-message';
    let messageHtml;

    switch (data.message_type) {
        case 'text':
            messageHtml = `<div class="content-message"><div class="text-message ${messageClass}">${data.content}</div></div>`;
            break;
        case 'image':
            messageHtml = `<div class="content-message"><div class="image-message ${messageClass}"><img src="${data.content}" alt="Image" /></div></div>`;
            break;
        case 'video':
            messageHtml = `<div class="content-message"><div class="image-message ${messageClass}"><video controls><source src="${data.content}" type="video/mp4">Trình duyệt của bạn không hỗ trợ video.</video></div></div>`;
            break;
        case 'link':
            messageHtml = `<div class="content-message"><div class="link-message ${messageClass}"><a href="${data.content}" target="_blank">${data.content}</a></div></div>`;
            break;
        default:
            messageHtml = `<div class="content-message"><div class="unknown-message">Tin nhắn không xác định.</div></div>`;
    }

    $('.content').append(messageHtml).scrollTop($('.content')[0].scrollHeight);
}

// Hàm lấy CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(cookie => {
            cookie = cookie.trim();
            if (cookie.substring(0, name.length + 1) === `${name}=`) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            }
        });
    }
    return cookieValue;
}

// Thử kết nối lại WebSocket
function reconnectWebSocket() {
    setTimeout(() => location.reload(), 5000);
}
