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

