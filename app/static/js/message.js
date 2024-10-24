const imgBaseUrl = '/static/img/';
function fetchChatUsers() {
    // Gọi API lấy danh sách người dùng đã chat
    $.ajax({
        url: '/api/users/chat-users/',
        method: 'GET',
        success: function(data) {
            // Xoá nội dung hiện tại
            const chatUsersList = $('.chat_users_list');
            chatUsersList.empty();

            // Nếu không có người dùng đã chat, hiển thị thông báo
            if (data.length === 0) {
                chatUsersList.append('<div>Chưa có cuộc trò chuyện nào.</div>');
                return;
            }

            // Duyệt qua từng user để hiển thị
            $.each(data, function(index, user) {
                let userHTML = `
                    <a href="#" onclick="showMessages(${user.id}, null)">
                        <div class="mess1" id="chat-user" style="position:relative" data-chat-user-id="${user.id}">
                            <div class="ava" style="background-image: url('${imgBaseUrl}${user.avatar}'); background-position: center"></div>
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

            const currentUserId = 1;
            $.ajax({
                url: `/api/user-chat-rooms/${currentUserId}/`,
                method: 'GET',
                success: function(rooms) {
                    // Nếu không có phòng chat nào, hiển thị thông báo
                    if (rooms.length === 0) {
                        chatUsersList.append('<div>Chưa tham gia phòng chat nào.</div>');
                    } else {
                        // Hiển thị các phòng chat
                        $.each(rooms, function(index, room) {
                            let roomHTML = `
                                <a href="#" onclick="showMessages(null, ${room.id})">
                                    <div class="mess1" id="chat-room" data-chat-room-id="${room.id}" style="position:relative">
                                        <div class="ava" style="background-image: url('${imgBaseUrl}${room.avatar}'   );"></div>
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
        },
        error: function(error) {
            console.error('Error fetching chat users:', error);
        }
    });
}

// Hàm lấy tin nhắn gần nhất của một user
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
            console.log(messages);
            if (messages.length > 0) {
                let latestMessage = messages[messages.length - 1];  // Lấy tin nhắn gần nhất
                let miniContent = user_id !== null ?
                    $(`[data-chat-user-id="${user_id}"] .mini_content .latest_message`) :
                    $(`[data-chat-room-id="${room_id}"] .mini_content .latest_message`);

                let timeDescription = user_id !== null ?
                    $(`[data-chat-user-id="${user_id}"] .mini_content .time_description`) :
                    $(`[data-chat-room-id="${room_id}"] .mini_content .time_description`);

                miniContent.text(latestMessage.content);  // Nội dung tin nhắn
                timeDescription.text(calculateTimeAgo(latestMessage.created_at));  // Tính toán thời gian đã qua
            }
        },
        error: function(error) {
            console.error('Error fetching latest message:', error);
        }
    });
}


// Hàm tính toán thời gian đã qua (ví dụ: 1 phút trước, 2 giờ trước)
function calculateTimeAgo(timestamp) {
    let timeAgo = new Date(timestamp);
    let now = new Date();
    let difference = Math.floor((now - timeAgo) / 1000);  // Tính sự chênh lệch theo giây

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

// Hàm để hiển thị tin nhắn khi nhấn vào user
function showMessages(user_id = null, room_id = null) {
    const currentUserId = 1;  // Thay bằng logic để lấy ID user hiện tại

    // Xóa nội dung hiện tại trong div chứa tin nhắn
    $('.content').html('');

    if (room_id) {
        setupWebSocket(room_id, null, currentUserId);
        // Tải tin nhắn cho phòng chat
        loadMessage(room_id, null, currentUserId);
    } else if (user_id) {
        // Kết nối WebSocket cho 1-1 chat
        setupWebSocket(null, user_id, currentUserId);  // room_id = null khi là 1-1 chat
        // Tải tin nhắn cho cuộc trò chuyện 1-1
        loadMessage(null, user_id, currentUserId);  // room_id = null khi là 1-1 chat
    } else {
        console.error('Cần cung cấp user_id hoặc room_id.');
    }
}


document.addEventListener('DOMContentLoaded', function () {
    fetchChatUsers();  // Gọi API khi trang được tải
});

function setupWebSocket(roomId = null, recipientId = null, currentUserId = null) {
    let ws_url = 'ws://' + window.location.host + '/ws/app/';

    if (roomId) {
        ws_url += `rooms/${roomId}/`;  // WebSocket kết nối theo phòng
    } else if (recipientId) {
        ws_url += `users/${recipientId}/`;  // WebSocket kết nối theo người dùng
    } else {
        console.error('roomId hoặc recipientId phải được cung cấp.');
        return;
    }

    const chatSocket = new WebSocket(ws_url);


    // Gửi tin nhắn qua WebSocket và API khi form được submit
    $('#messageForm').on('submit', function (event) {
        event.preventDefault();
        const message = $('textarea[name="content"]').val();
        if (message.trim() !== "") {
            // Gửi tin nhắn qua WebSocket
            chatSocket.send(JSON.stringify({'message': message}));

            // Dữ liệu để gửi qua API
            const payload = {
                'content': message,
                'message_by': currentUserId,
                'message_type': 'text'
            };

            if (roomId) {
                payload['room'] = roomId;
                payload['message_to'] = null;
            } else if (recipientId) {
                payload['room'] = null;
                payload['message_to'] = recipientId;
            }

            // Gửi tin nhắn đến API để lưu vào DB
            addMessage(payload);

            // Xóa nội dung sau khi gửi
            $('textarea[name="content"]').val('');
        }
    });

    // Kết nối WebSocket thành công, tải tin nhắn cũ
    chatSocket.onopen = function () {
        console.log('WebSocket kết nối thành công');
        loadMessage(roomId, recipientId, currentUserId);
    };

    // Xử lý khi WebSocket bị ngắt
    chatSocket.onclose = function () {
        console.error('WebSocket kết nối bị đóng. Đang thử kết nối lại...');
        reconnectWebSocket();
    };
}

// Hàm thêm tin nhắn vào API
function addMessage(payload) {
    $.ajax({
        url: '/api/messages/',
        type: 'POST',
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        data: JSON.stringify(payload),
        success: function (data) {
            console.log('Tin nhắn đã được thêm vào cơ sở dữ liệu:', data);
            displayMessage(data, payload.message_by);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.error('Lỗi khi lưu tin nhắn:', textStatus, errorThrown);
        }
    });
}

// Lấy các tin nhắn cũ qua API
function loadMessage(roomId = null, recipientId = null, currentUserId) {
    let apiUrl = '/api/messages/get-messages';

    if (roomId) {
        apiUrl += `?room_id=${roomId}`;  // Lấy tin nhắn theo phòng
    } else if (recipientId) {
        apiUrl += `?user_id=${recipientId}`;  // Lấy tin nhắn 1-1
    } else {
        console.error('roomId hoặc userId phải được cung cấp.');
        return;
    }

    // Gọi API để lấy các tin nhắn cũ
    $.ajax({
        url: apiUrl,
        type: 'GET',
        success: function (data) {
            data.forEach(message => {
                displayMessage(message, currentUserId);
            });
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.error('Lỗi khi tải tin nhắn cũ:', textStatus, errorThrown);
        }
    });
}

function displayMessage(data, currentUserId) {
    let messageHtml;
    let messageClass;
    console.log('message_type:', data.message_type);

    if (data.message_by === currentUserId) {
        messageClass = 'sent-message';
    } else {
        messageClass = 'received-message';
    }

    switch (data.message_type) {
        case 'text':
            messageHtml = '<div class="content-message"><div class=" text-message ' + messageClass + '">' + data.content + '</div></div>';
            break;
        case 'image':
            messageHtml = '<div class="content-message"><div class=" image-message ' + messageClass + '"><img src="' + data.content + '" alt="Image" /></div></div>';
            break;
        case 'video':
            messageHtml = '<div class="content-message"><div class=" image-message ' + messageClass + '"><video controls><source src="' + data.content + '" type="video/mp4">Trình duyệt của bạn không hỗ trợ video.</video></div></div>';
            break;
        case 'link':
            messageHtml = '<div class="content-message"><div class=" link-message ' + messageClass + '"><a href="' + data.content + '" target="_blank">' + data.content + '</a></div></div>';
            break;
        default:
            messageHtml = '<div class="content-message"><div class="unknown-message">Tin nhắn không xác định.</div></div>';
    }

    $('.content').append(messageHtml);
    $('.content').scrollTop($('.content')[0].scrollHeight);
}

// Hàm lấy giá trị CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Thử kết nối lại WebSocket
function reconnectWebSocket() {
    setTimeout(function () {
        location.reload();
    }, 5000);
}





