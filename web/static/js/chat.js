// 虚拟女友聊天界面 JavaScript

// 全局变量
let messageCount = 0;
let isProcessing = false;

// 格式化时间
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    // 如果是今天
    if (diff < 86400000 && date.getDate() === now.getDate()) {
        return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    }
    
    // 如果是昨天
    if (diff < 172800000 && date.getDate() === now.getDate() - 1) {
        return '昨天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    }
    
    // 其他日期
    return date.toLocaleString('zh-CN', { 
        month: '2-digit', 
        day: '2-digit', 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

// 添加消息到聊天窗口
function addMessage(sender, type, content, timestamp) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-3 animate-fade-in';
    
    if (sender === 'user') {
        messageDiv.className += ' flex-row-reverse space-x-reverse';
    }
    
    // 头像
    const avatar = document.createElement('div');
    avatar.className = 'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0';
    
    if (sender === 'girlfriend') {
        avatar.className += ' bg-gradient-to-br from-pink-200 to-pink-300';
        avatar.innerHTML = '<span class="text-xl">👧</span>';
    } else {
        avatar.className += ' bg-gradient-to-br from-blue-200 to-blue-300';
        avatar.innerHTML = '<span class="text-xl">👤</span>';
    }
    
    // 消息内容容器
    const contentDiv = document.createElement('div');
    contentDiv.className = 'flex flex-col max-w-md';
    
    if (sender === 'user') {
        contentDiv.className += ' items-end';
    }
    
    // 消息气泡
    const bubble = document.createElement('div');
    bubble.className = 'rounded-2xl px-4 py-3 shadow-sm';
    
    if (sender === 'girlfriend') {
        bubble.className += ' bg-girlfriend-bubble text-gray-800 rounded-tl-sm';
    } else {
        bubble.className += ' bg-user-bubble text-gray-800 rounded-tr-sm';
    }
    
    // 根据消息类型显示内容
    if (type === 'text') {
        const textContent = document.createElement('p');
        textContent.textContent = content;
        textContent.className = 'whitespace-pre-wrap break-words';
        bubble.appendChild(textContent);
    } else if (type === 'image') {
        const img = document.createElement('img');
        img.src = `/uploads/${content}`;
        img.alt = 'Uploaded image';
        img.className = 'message-image';
        img.onclick = () => showImagePreview(img.src);
        bubble.appendChild(img);
    }
    
    contentDiv.appendChild(bubble);
    
    // 时间戳
    const timeSpan = document.createElement('span');
    timeSpan.className = 'text-xs text-gray-400 mt-1 ml-2';
    if (sender === 'user') {
        timeSpan.className += ' mr-2 text-right';
    }
    timeSpan.textContent = formatTime(timestamp);
    contentDiv.appendChild(timeSpan);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    messagesContainer.appendChild(messageDiv);
    
    // 滚动到底部
    scrollToBottom();
    
    // 更新消息计数
    updateMessageCount();
}

// 滚动到底部
function scrollToBottom() {
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 更新消息计数
function updateMessageCount() {
    const messagesContainer = document.getElementById('chat-messages');
    const messages = messagesContainer.querySelectorAll('.animate-fade-in');
    messageCount = messages.length - 1; // 减去欢迎消息
    document.getElementById('message-count').textContent = `${messageCount} 条`;
}

// 显示/隐藏加载指示器
function toggleLoading(show) {
    const loadingIndicator = document.getElementById('loading-indicator');
    const sendButton = document.getElementById('send-button');
    const messageInput = document.getElementById('message-input');
    
    if (show) {
        loadingIndicator.classList.remove('hidden');
        sendButton.disabled = true;
        sendButton.classList.add('opacity-50', 'cursor-not-allowed');
        messageInput.disabled = true;
    } else {
        loadingIndicator.classList.add('hidden');
        sendButton.disabled = false;
        sendButton.classList.remove('opacity-50', 'cursor-not-allowed');
        messageInput.disabled = false;
    }
}

// 发送消息
async function sendMessage() {
    if (isProcessing) return;
    
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    
    if (!message) {
        showNotification('请输入消息', 'warning');
        return;
    }
    
    isProcessing = true;
    toggleLoading(true);
    
    try {
        // 显示用户消息
        addMessage('user', 'text', message, new Date().toISOString());
        
        // 清空输入框
        messageInput.value = '';
        updateCharCount();
        adjustTextareaHeight(messageInput);
        
        // 发送到服务器
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // 显示女友回复
            addMessage('girlfriend', 'text', data.reply, data.timestamp);
        } else {
            showNotification(data.message || '发送失败', 'error');
        }
        
    } catch (error) {
        console.error('发送消息失败:', error);
        showNotification('网络错误，请稍后重试', 'error');
    } finally {
        isProcessing = false;
        toggleLoading(false);
        messageInput.focus();
    }
}

// 处理图片上传
async function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
        showNotification('请选择图片文件', 'warning');
        return;
    }
    
    // 检查文件大小（10MB）
    if (file.size > 10 * 1024 * 1024) {
        showNotification('图片大小不能超过10MB', 'warning');
        return;
    }
    
    isProcessing = true;
    toggleLoading(true);
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // 显示用户上传的图片
            addMessage('user', 'image', data.filename, new Date().toISOString());
            
            // 显示女友回复
            addMessage('girlfriend', 'text', data.reply, new Date().toISOString());
            
            showNotification('图片上传成功！', 'success');
        } else {
            showNotification(data.message || '上传失败', 'error');
        }
        
    } catch (error) {
        console.error('上传图片失败:', error);
        showNotification('上传失败，请稍后重试', 'error');
    } finally {
        isProcessing = false;
        toggleLoading(false);
        // 清空文件选择
        event.target.value = '';
    }
}

// 加载聊天历史
async function loadChatHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        
        if (data.status === 'success' && data.history.length > 0) {
            // 清空现有消息（保留欢迎消息）
            const messagesContainer = document.getElementById('chat-messages');
            const welcomeMessage = messagesContainer.firstElementChild;
            messagesContainer.innerHTML = '';
            messagesContainer.appendChild(welcomeMessage);
            
            // 添加历史消息
            data.history.forEach(msg => {
                addMessage(msg.sender, msg.type, msg.content, msg.timestamp);
            });
        }
        
    } catch (error) {
        console.error('加载历史记录失败:', error);
    }
}

// 清空聊天历史
async function clearHistory() {
    if (!confirm('确定要清空所有聊天记录吗？此操作不可恢复。')) {
        return;
    }
    
    try {
        const response = await fetch('/api/history', {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // 清空聊天窗口（保留欢迎消息）
            const messagesContainer = document.getElementById('chat-messages');
            const welcomeMessage = messagesContainer.firstElementChild;
            messagesContainer.innerHTML = '';
            messagesContainer.appendChild(welcomeMessage);
            
            messageCount = 0;
            updateMessageCount();
            
            showNotification('聊天记录已清空', 'success');
        } else {
            showNotification(data.message || '清空失败', 'error');
        }
        
    } catch (error) {
        console.error('清空历史记录失败:', error);
        showNotification('操作失败，请稍后重试', 'error');
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = 'notification';
    
    const colors = {
        success: 'text-green-600',
        error: 'text-red-600',
        warning: 'text-yellow-600',
        info: 'text-blue-600'
    };
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    notification.innerHTML = `
        <div class="flex items-center">
            <span class="text-2xl mr-3">${icons[type]}</span>
            <span class="${colors[type]} font-medium">${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// 显示图片预览
function showImagePreview(src) {
    const overlay = document.createElement('div');
    overlay.className = 'image-preview-overlay';
    overlay.onclick = () => overlay.remove();
    
    const img = document.createElement('img');
    img.src = src;
    
    overlay.appendChild(img);
    document.body.appendChild(overlay);
}

// 处理键盘事件
function handleKeyPress(event) {
    // Enter 键发送消息（Shift+Enter 换行）
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// 调整文本框高度
function adjustTextareaHeight(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
}

// 更新字符计数
function updateCharCount() {
    const messageInput = document.getElementById('message-input');
    const charCount = document.getElementById('char-count');
    const length = messageInput.value.length;
    charCount.textContent = `${length}/500`;
    
    if (length > 450) {
        charCount.classList.add('text-red-500');
    } else {
        charCount.classList.remove('text-red-500');
    }
}

// 监听输入框变化
document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('message-input');
    messageInput.addEventListener('input', () => {
        updateCharCount();
    });
});

// 防止页面刷新时丢失正在输入的内容
window.addEventListener('beforeunload', (event) => {
    const messageInput = document.getElementById('message-input');
    if (messageInput.value.trim() && isProcessing) {
        event.preventDefault();
        event.returnValue = '';
    }
});
