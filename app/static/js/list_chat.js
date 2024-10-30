const imgBaseUrl = '/static/img/';
let latestMessages = [];  // Mảng lưu trữ thông tin tin nhắn gần nhất

function fetchChatUsers() {
    $.ajax({
        url: '/api/users/chat-users/',
        method: 'GET',
        success: function(users) {
            if (users.length > 0) {
                $.each(users, function (index, user) {
                    // Gọi hàm lấy tin nhắn gần nhất cho từng user
                    fetchLatestMessage(user.id, null, function(latestMessage) {
                        latestMessages.push({
                            id: user.id,
                            username: user.username,
                            avatar: user.avatar,
                            type: 'user',
                            latestMessage: latestMessage
                        });
                        // Cập nhật giao diện sau khi có tất cả thông tin
                        updateChatListDisplay();
                    });
                });
            }
        },
        error: function(error) {
            console.error('Error fetching chat users:', error);
        }
    });
}

function fetchChatRooms() {
    $.ajax({
        url: `/api/userchatrooms/chat-rooms/?user_id=${currentUserId}`,
        method: 'GET',
        success: function (rooms) {
            if (rooms.length > 0) {
                $.each(rooms, function (index, room) {
                    // Gọi hàm lấy tin nhắn gần nhất cho từng room
                    fetchLatestMessage(null, room.id, function(latestMessage) {
                        latestMessages.push({
                            id: room.id,
                            room_name: room.room_name,
                            avatar: room.avatar,
                            type: 'room',
                            latestMessage: latestMessage
                        });
                        // Cập nhật giao diện sau khi có tất cả thông tin
                        updateChatListDisplay();
                    });
                });
            }
        },
        error: function (error) {
            console.error('Error fetching chat rooms:', error);
        }
    });
}

// Hàm lấy tin nhắn gần nhất và gọi callback với thông tin tin nhắn
function fetchLatestMessage(user_id, room_id, callback) {
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
                let latestMessage = messages[messages.length - 1]; // Lấy tin nhắn gần nhất
                callback(latestMessage); // Gọi callback với thông tin tin nhắn gần nhất
            } else {
                callback(null); // Không có tin nhắn nào
            }
        },
        error: function(error) {
            console.error('Error fetching latest message:', error);
            callback(null); // Gọi callback với null khi có lỗi
        }
    });
}

// Cập nhật giao diện hiển thị danh sách chat
function updateChatListDisplay() {
    $('.chat_users_list').html('');
    // Sắp xếp mảng latestMessages theo thời gian gần nhất
    latestMessages.sort((a, b) => {
        const aDate = a.latestMessage ? new Date(a.latestMessage.created_at) : 0;
        const bDate = b.latestMessage ? new Date(b.latestMessage.created_at) : 0;
        return bDate - aDate; // Sắp xếp giảm dần
    });

    // Hiển thị lại danh sách người dùng và phòng chat
    $.each(latestMessages, function(index, item) {
        let html = '';
        if (item.type === 'user') {
            html = `
            <a onclick="openChat(${item.id}, null)">
                <div class="mess1" id="chat-user" style="position:relative" data-chat-user-id="${item.id}">
                    <div class="ava" style="background-image: url('${imgBaseUrl}${item.avatar}'); background-position: center"></div>
                    <div class="username">${item.username}</div>
                    <br><br>
                    <div class="mini_content" style="max-width:200px;">
                        <span class="latest_message">${item.latestMessage.content}</span>
                        <div style="font-size:12px;position:absolute;right:20px;bottom:20px;" class="time_description">${calculateTimeAgo(item.latestMessage.created_at)}</div>
                    </div>
                </div>
            </a>`;
        } else if (item.type === 'room') {
            html = `
            <a onclick="openChat(null, ${item.id})">
                <div class="mess1" id="chat-room" data-chat-room-id="${item.id}" style="position:relative">
                    <div class="ava" style="background-image: url('${imgBaseUrl}${item.avatar}');"></div>
                    <div class="username">${item.room_name}</div>
                    <br><br>
                    <div class="mini_content" style="max-width:200px;">
                        <span class="latest_message">${item.latestMessage.content}</span>
                        <div style="font-size:12px;position:absolute;right:20px;bottom:20px;" class="time_description">${calculateTimeAgo(item.latestMessage.created_at)}</div>
                    </div>
                </div>
            </a>`;
        }
        $('.chat_users_list').append(html); // Thêm HTML vào danh sách chat
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

function openChat(recipientId, roomId) {
    // Xóa nội dung hiện tại
    $('.content').html('');

    if (chatSocket) {
        chatSocket = null;
    }
    // Nếu chưa có kết nối, tạo kết nối WebSocket
    if (roomId) {
        setupWebSocket(roomId, null, currentUserId);
    } else if (recipientId) {
        setupWebSocket(null, recipientId, currentUserId);
    }

    loadMessage(roomId, recipientId, currentUserId);
    console.log('currentUserId là:', currentUserId);
}
    
document.addEventListener('DOMContentLoaded', function () {
    fetchChatUsers();  // Gọi API khi trang được tải
    fetchChatRooms();
});