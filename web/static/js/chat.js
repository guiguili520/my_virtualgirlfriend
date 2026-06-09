// 虚拟女友聊天界面 JavaScript

// 全局变量
let messageCount = 0;
let isProcessing = false;
let modelProviders = [];
let savedModelConfig = {};

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
    avatar.className = 'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden';
    
    if (sender === 'girlfriend') {
        avatar.className += ' bg-gradient-to-br from-pink-200 to-pink-300';
        avatar.innerHTML = '<img src="/static/images/girlfriend.jpg" alt="Girlfriend" class="w-full h-full object-cover">';
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

// 添加消息但不触发滚动（用于批量加载历史）
function addMessageWithoutScroll(sender, type, content, timestamp) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-3 animate-fade-in';

    if (sender === 'user') {
        messageDiv.className += ' flex-row-reverse space-x-reverse';
    }

    // 头像
    const avatar = document.createElement('div');
    avatar.className = 'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden';

    if (sender === 'girlfriend') {
        avatar.className += ' bg-gradient-to-br from-pink-200 to-pink-300';
        avatar.innerHTML = '<img src="/static/images/girlfriend.jpg" alt="Girlfriend" class="w-full h-full object-cover">';
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
    // 注意：这里不调用 scrollToBottom() 和 updateMessageCount()
}

// 添加带本地图片的消息（用于立即预览）
function addMessageWithLocalImage(sender, localImageUrl, timestamp, messageId) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-3 animate-fade-in';
    messageDiv.id = messageId; // 设置ID以便后续替换
    
    if (sender === 'user') {
        messageDiv.className += ' flex-row-reverse space-x-reverse';
    }
    
    // 头像
    const avatar = document.createElement('div');
    avatar.className = 'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden';
    avatar.className += ' bg-gradient-to-br from-blue-200 to-blue-300';
    avatar.innerHTML = '<span class="text-xl">👤</span>';
    
    // 消息内容容器
    const contentDiv = document.createElement('div');
    contentDiv.className = 'flex flex-col max-w-md items-end';
    
    // 消息气泡
    const bubble = document.createElement('div');
    bubble.className = 'rounded-2xl px-4 py-3 shadow-sm bg-user-bubble text-gray-800 rounded-tr-sm';
    
    // 图片
    const img = document.createElement('img');
    img.src = localImageUrl;
    img.alt = 'Uploading image';
    img.className = 'message-image';
    img.dataset.messageId = messageId; // 标记以便后续替换
    bubble.appendChild(img);
    
    contentDiv.appendChild(bubble);
    
    // 时间戳
    const timeSpan = document.createElement('span');
    timeSpan.className = 'text-xs text-gray-400 mt-1 mr-2 text-right';
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

// 替换消息中的图片URL（从本地URL替换为服务器URL）
function replaceMessageImage(messageId, serverFilename) {
    const messageDiv = document.getElementById(messageId);
    if (messageDiv) {
        const img = messageDiv.querySelector('img[data-message-id="' + messageId + '"]');
        if (img) {
            img.src = `/uploads/${serverFilename}`;
            img.onclick = () => showImagePreview(img.src);
            delete img.dataset.messageId;
        }
    }
}

// 移除消息
function removeMessage(messageId) {
    const messageDiv = document.getElementById(messageId);
    if (messageDiv) {
        messageDiv.remove();
        updateMessageCount();
    }
}

// 滚动到底部
function scrollToBottom(immediate = false) {
    const messagesContainer = document.getElementById('chat-messages');

    if (immediate) {
        // 立即滚动（用于加载历史后）
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    } else {
        // 使用 requestAnimationFrame 确保 DOM 更新后再滚动
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            });
        });
    }
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
        
        const selectedModel = getSelectedModelOptions();

        // 发送到服务器
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message, ...selectedModel })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // 显示女友回复
            addMessage('girlfriend', 'text', data.reply, data.timestamp);
            updateActiveModelStatus(data.model);
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

// 加载模型供应商预设
async function loadModelProviders() {
    try {
        const response = await fetch('/api/model/providers');
        const data = await response.json();

        if (data.status !== 'success') {
            updateActiveModelStatus(null, '模型服务加载失败');
            return;
        }

        modelProviders = data.providers || [];
        const select = document.getElementById('model-provider');
        const modelInput = document.getElementById('model-name');
        select.innerHTML = '';

        modelProviders.forEach(provider => {
            const option = document.createElement('option');
            option.value = provider.key;
            option.textContent = provider.label;
            option.dataset.model = provider.model || '';
            option.dataset.apiFormat = provider.api_format || '';
            option.dataset.configured = provider.configured ? 'true' : 'false';
            select.appendChild(option);
        });

        const active = data.active || {};
        savedModelConfig = data.config || {};
        if (active.provider && modelProviders.some(p => p.key === active.provider)) {
            select.value = active.provider;
        }
        applySavedModelConfig(savedModelConfig);
        handleProviderChange();
        updateActiveModelStatus(active);
    } catch (error) {
        console.error('加载模型供应商失败:', error);
        updateActiveModelStatus(null, '模型服务加载失败');
    }
}

// 处理模型供应商选择
function handleProviderChange() {
    const select = document.getElementById('model-provider');
    const option = select.options[select.selectedIndex];
    const modelInput = document.getElementById('model-name');
    const baseUrlInput = document.getElementById('model-base-url');
    const presetModel = option ? option.dataset.model : '';
    const provider = modelProviders.find(item => item.key === select.value);

    modelInput.placeholder = presetModel || '使用预设默认模型';
    baseUrlInput.placeholder = provider && provider.base_url ? provider.base_url : '使用预设默认地址';

    if (savedModelConfig.provider === select.value) {
        modelInput.value = savedModelConfig.model || '';
        baseUrlInput.value = savedModelConfig.base_url || '';
    } else {
        modelInput.value = '';
        baseUrlInput.value = '';
    }

    if (provider) {
        const keyConfigured = (
            provider.configured ||
            provider.key === 'mock' ||
            (savedModelConfig.provider === provider.key && savedModelConfig.key_configured)
        );
        const keyInput = document.getElementById('model-api-key');
        keyInput.placeholder = (
            savedModelConfig.provider === provider.key && savedModelConfig.key_configured
        ) ? '已保存，留空不修改' : '输入后保存到本机';
        const keyStatus = keyConfigured ? '已就绪' : `缺少 ${provider.api_key_env || 'API Key'}`;
        updateActiveModelStatus({
            label: provider.label,
            model: modelInput.value.trim() || provider.model,
            api_format: provider.api_format,
            mock: provider.key === 'mock' || !keyConfigured,
            mock_reason: keyConfigured ? null : `missing_api_key:${provider.api_key_env}`
        }, keyStatus);
    }
}

// 应用本地保存的模型配置（不包含明文Key）
function applySavedModelConfig(config) {
    const providerSelect = document.getElementById('model-provider');
    const modelInput = document.getElementById('model-name');
    const baseUrlInput = document.getElementById('model-base-url');
    const keyInput = document.getElementById('model-api-key');

    if (config.provider && modelProviders.some(p => p.key === config.provider)) {
        providerSelect.value = config.provider;
    }
    modelInput.value = config.model || '';
    baseUrlInput.value = config.base_url || '';
    keyInput.value = '';
    keyInput.placeholder = config.key_configured ? '已保存，留空不修改' : '输入后保存到本机';
}

// 保存本地模型配置
async function saveModelConfig() {
    const providerSelect = document.getElementById('model-provider');
    const modelInput = document.getElementById('model-name');
    const baseUrlInput = document.getElementById('model-base-url');
    const keyInput = document.getElementById('model-api-key');
    const provider = modelProviders.find(item => item.key === providerSelect.value) || {};

    const payload = {
        provider: providerSelect.value,
        api_format: provider.api_format || '',
        model: modelInput.value.trim(),
        base_url: baseUrlInput.value.trim(),
        api_key: keyInput.value.trim()
    };

    try {
        const response = await fetch('/api/model/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();

        if (data.status === 'success') {
            savedModelConfig = data.config || {};
            applySavedModelConfig(savedModelConfig);
            updateActiveModelStatus(data.active);
            await loadModelProviders();
            showNotification('模型配置已保存', 'success');
        } else {
            showNotification(data.message || '保存失败', 'error');
        }
    } catch (error) {
        console.error('保存模型配置失败:', error);
        showNotification('保存失败，请稍后重试', 'error');
    }
}

// 清除已保存Key
async function clearSavedApiKey() {
    const providerSelect = document.getElementById('model-provider');
    const modelInput = document.getElementById('model-name');
    const baseUrlInput = document.getElementById('model-base-url');
    const provider = modelProviders.find(item => item.key === providerSelect.value) || {};

    try {
        const response = await fetch('/api/model/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                provider: providerSelect.value,
                api_format: provider.api_format || '',
                model: modelInput.value.trim(),
                base_url: baseUrlInput.value.trim(),
                clear_api_key: true
            })
        });
        const data = await response.json();

        if (data.status === 'success') {
            savedModelConfig = data.config || {};
            applySavedModelConfig(savedModelConfig);
            updateActiveModelStatus(data.active);
            await loadModelProviders();
            showNotification('已清除本地Key', 'success');
        } else {
            showNotification(data.message || '清除失败', 'error');
        }
    } catch (error) {
        console.error('清除模型Key失败:', error);
        showNotification('清除失败，请稍后重试', 'error');
    }
}

// 获取当前模型选择
function getSelectedModelOptions() {
    const providerSelect = document.getElementById('model-provider');
    const modelInput = document.getElementById('model-name');
    const baseUrlInput = document.getElementById('model-base-url');
    const provider = providerSelect ? providerSelect.value : 'mock';
    const model = modelInput ? modelInput.value.trim() : '';
    const baseUrl = baseUrlInput ? baseUrlInput.value.trim() : '';
    const providerPreset = modelProviders.find(item => item.key === provider) || {};

    const options = {
        provider,
        api_format: providerPreset.api_format || ''
    };
    if (model) {
        options.model = model;
    }
    if (baseUrl) {
        options.base_url = baseUrl;
    }
    return options;
}

// 更新模型状态展示
function updateActiveModelStatus(model, fallbackText) {
    const status = document.getElementById('model-status');
    if (!status) return;

    if (!model) {
        status.textContent = fallbackText || '';
        status.className = 'mt-2 text-xs text-gray-500';
        return;
    }

    const label = model.label || model.provider || '模型';
    const apiFormat = model.api_format || '';
    const modelName = model.model || '';
    const text = fallbackText || (model.mock ? '模拟模式' : '在线 API');
    status.textContent = `${label} · ${apiFormat} · ${modelName} · ${text}`;
    status.className = model.mock
        ? 'mt-2 text-xs text-yellow-600'
        : 'mt-2 text-xs text-green-600';
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
    
    // 创建本地预览URL，立即显示图片
    const localImageUrl = URL.createObjectURL(file);
    const tempMessageId = 'temp-' + Date.now();
    
    // 立即显示用户上传的图片（使用本地URL）
    addMessageWithLocalImage('user', localImageUrl, new Date().toISOString(), tempMessageId);
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        // 显示加载指示器，等待女友回复
        toggleLoading(true);
        
        // 上传图片到服务器
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // 替换为服务器URL
            replaceMessageImage(tempMessageId, data.filename);
            
            // 释放本地URL
            URL.revokeObjectURL(localImageUrl);
            
            // 显示女友回复
            addMessage('girlfriend', 'text', data.reply, new Date().toISOString());
            
            showNotification('图片上传成功！', 'success');
        } else {
            // 上传失败，移除临时消息
            removeMessage(tempMessageId);
            URL.revokeObjectURL(localImageUrl);
            showNotification(data.message || '上传失败', 'error');
        }
        
    } catch (error) {
        console.error('上传图片失败:', error);
        // 上传失败，移除临时消息
        removeMessage(tempMessageId);
        URL.revokeObjectURL(localImageUrl);
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
            const messagesContainer = document.getElementById('chat-messages');
            const welcomeMessage = messagesContainer.firstElementChild;
            messagesContainer.innerHTML = '';
            messagesContainer.appendChild(welcomeMessage);

            // 批量添加消息，不触发单条滚动
            data.history.forEach(msg => {
                addMessageWithoutScroll(msg.sender, msg.type, msg.content, msg.timestamp);
            });

            // 等待 DOM 完全更新后再滚动到底部
            await new Promise(resolve => setTimeout(resolve, 100));
            scrollToBottom(true);

            // 更新消息计数
            updateMessageCount();
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
    loadModelProviders();
});

// 防止页面刷新时丢失正在输入的内容
window.addEventListener('beforeunload', (event) => {
    const messageInput = document.getElementById('message-input');
    if (messageInput.value.trim() && isProcessing) {
        event.preventDefault();
        event.returnValue = '';
    }
});
