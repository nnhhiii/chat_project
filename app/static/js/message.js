function setupWebSocket(roomId, recipientId, currentUserId) {
    let ws_url = 'ws://' + window.location.host + '/ws/app/';

    if (roomId) {
        ws_url += `rooms/${roomId}/`;
    } else if (recipientId) {
        ws_url += `users/${recipientId}/`;
    }

    chatSocket = new WebSocket(ws_url);
    // Nhận tin nhắn mới từ WebSocket
    chatSocket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        console.log("Received data:", data);
        if (data) {
            displayMessage(data, currentUserId);  // Hàm này sẽ thêm tin nhắn vào giao diện
        }
    };

    // Gửi tin nhắn qua WebSocket và API khi form được submit
    $('#messageForm').off('submit').on('submit', function (event) {
        event.preventDefault();
        const content = $('textarea[name="content"]').val();
        if (content.trim() !== "") {
            // Gửi tin nhắn qua WebSocket
            chatSocket.send(JSON.stringify({
                'content': content,
                'message_by': currentUserId,
                'message_type': 'text'
            }));

            // Dữ liệu để gửi qua API
            const payload = {
                'content': content,
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

            // Gửi tin nhắn đến API
            $.ajax({
                url: 'api/messages/',
                type: 'POST',
                contentType: 'application/json',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                data: JSON.stringify(payload),
                success: function (data) {
                    console.log('Tin nhắn đã được thêm vào cơ sở dữ liệu:', data);
                    latestMessages = [];
                    fetchChatUsers();
                    fetchChatRooms();
                },
                error: function(error) {
                    console.error("Lỗi khi lưu tin nhắn:", error);
                }
            });

            // Xóa nội dung sau khi gửi
            $('textarea[name="content"]').val('');
        }
    });

    chatSocket.onopen = function () {
        console.log('WebSocket kết nối thành công');
    };

    chatSocket.onclose = function () {
        console.error('WebSocket kết nối bị đóng. Đang thử kết nối lại...');
        setTimeout(function () {
            location.reload();
        }, 5000);
    };
}


// Lấy các tin nhắn cũ qua API
function loadMessage(roomId = null, recipientId = null, currentUserId) {
    let apiUrl = '/api/messages/get-messages';

    if (roomId) {
        apiUrl += `?room_id=${roomId}`;  // Lấy tin nhắn theo phòng
    } else if (recipientId) {
        apiUrl += `?user_id=${recipientId}`;  // Lấy tin nhắn 1-1
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

    if (data.message_by == currentUserId) {
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


