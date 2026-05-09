<template>
  <div class="ai-chat-container">
    <van-nav-bar title="AI问答" fixed>
      <template #left>
        <van-icon name="bars" @click="showSessionList = true" />
      </template>
      <template #right>
        <van-icon name="plus" @click="createNewSession" />
      </template>
    </van-nav-bar>
    
    <!-- 会话列表侧边栏 -->
    <van-popup v-model:show="showSessionList" position="left" :style="{ width: '80%', height: '100%' }">
      <div class="session-sidebar">
        <div class="session-header">
          <h3>对话历史</h3>
          <van-button size="small" type="primary" @click="createNewSession">+ 新建对话</van-button>
        </div>
        <div class="session-list">
          <van-cell
            v-for="session in sessions"
            :key="session.session_id"
            :title="session.title || '新对话'"
            :label="formatTime(session.updated_at)"
            :class="{ active: currentSessionId === session.session_id }"
            @click="switchSession(session.session_id)"
          >
            <template #right-icon>
              <van-icon name="delete" @click.stop="deleteSession(session.session_id)" />
            </template>
          </van-cell>
          <van-empty v-if="sessions.length === 0" description="暂无对话历史" />
        </div>
      </div>
    </van-popup>
    
    <div class="chat-content">
      <div class="messages-container" ref="messagesContainer">
        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          :class="['message', message.role === 'user' ? 'user-message' : 'ai-message']"
        >
          <div class="message-content">
            <div v-if="message.role === 'assistant' && message.content === ''" class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <div v-else v-html="formatMessage(message.content)"></div>
          </div>
        </div>
      </div>
      
      <div class="input-container">
        <van-field
          v-model="userInput"
          rows="1"
          autosize
          type="textarea"
          placeholder="请输入问题..."
          class="chat-input"
          @keypress.enter.prevent="sendMessage"
        />
        <van-button 
          type="primary" 
          class="send-button" 
          :disabled="isLoading || !userInput.trim()" 
          @click="sendMessage"
        >
          发送
        </van-button>
      </div>
    </div>
    
    <tab-bar />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue';
import TabBar from '../components/TabBar.vue';
import { showToast, showConfirmDialog } from 'vant';
import * as marked from 'marked';
import DOMPurify from 'dompurify';
import axios from 'axios';
import { useUserStore } from '../store/user';
import { apiConfig } from '../config/api';

// 获取用户 store
const userStore = useUserStore();

// 聊天消息
const messages = ref([
  { role: 'assistant', content: '你好！我是AI助手，有什么可以帮助你的吗？' }
]);
const userInput = ref('');
const messagesContainer = ref(null);
const isLoading = ref(false);

// 会话管理
const sessions = ref([]);
const currentSessionId = ref('');
const showSessionList = ref(false);

// API 配置（使用完整URL）
const apiBase = `${apiConfig.baseURL}/api/ai`;

// 获取 token（从 user store）
const getToken = () => {
  return userStore.token;
};

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '';
  const date = new Date(timeStr);
  const now = new Date();
  const diff = now - date;
  
  if (diff < 60000) return '刚刚';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
  return date.toLocaleDateString();
};

// 格式化消息内容（支持Markdown）
const formatMessage = (content) => {
  if (!content) return '';
  return DOMPurify.sanitize(marked.parse(content));
};

// 加载会话列表
const loadSessions = async () => {
  try {
    const token = getToken();
    if (!token) {
      console.log('未登录，无法加载会话');
      return;
    }
    
    const response = await axios.get(`${apiBase}/chat/sessions`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    if (response.data.code === 200) {
      sessions.value = response.data.data.sessions;
      
      // 如果有会话且当前没有选中，加载第一个
      if (sessions.value.length > 0 && !currentSessionId.value) {
        await switchSession(sessions.value[0].session_id);
      }
    }
  } catch (error) {
    console.error('加载会话列表失败:', error);
  }
};

// 创建新会话
const createNewSession = async () => {
  try {
    const token = getToken();
    
    if (!token) {
      showToast('请先登录');
      return;
    }
    
    const response = await axios.post(
      `${apiBase}/chat/new-session`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );
    
    if (response.data.code === 200) {
      const newSessionId = response.data.data.session_id;
      currentSessionId.value = newSessionId;
      messages.value = [
        { role: 'assistant', content: '你好！我是AI助手，有什么可以帮助你的吗？' }
      ];
      showSessionList.value = false;
      await loadSessions();
      showToast('新对话已创建');
    }
  } catch (error) {
    console.error('创建会话失败:', error);
    showToast(error.response?.data?.message || '创建会话失败');
  }
};

// 切换会话
const switchSession = async (sessionId) => {
  try {
    const token = getToken();
    if (!token) {
      showToast('请先登录');
      return;
    }
    
    const response = await axios.get(
      `${apiBase}/chat/history/${sessionId}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    
    if (response.data.code === 200) {
      currentSessionId.value = sessionId;
      const history = response.data.data.history;
      
      // 转换历史消息格式
      if (history.length > 0) {
        messages.value = history.map(msg => ({
          role: msg.role,
          content: msg.content
        }));
      } else {
        messages.value = [
          { role: 'assistant', content: '你好！我是AI助手，有什么可以帮助你的吗？' }
        ];
      }
      
      showSessionList.value = false;
      await nextTick();
      scrollToBottom();
    }
  } catch (error) {
    console.error('加载会话历史失败:', error);
    showToast('加载失败');
  }
};

// 删除会话
const deleteSession = async (sessionId) => {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: '确定要删除这个对话吗？'
    });
    
    const token = getToken();
    if (!token) return;
    
    const response = await axios.delete(
      `${apiBase}/chat/history/${sessionId}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    
    if (response.data.code === 200) {
      showToast('删除成功');
      await loadSessions();
      
      // 如果删除的是当前会话，清空消息
      if (currentSessionId.value === sessionId) {
        currentSessionId.value = '';
        messages.value = [
          { role: 'assistant', content: '你好！我是AI助手，有什么可以帮助你的吗？' }
        ];
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除会话失败:', error);
      showToast('删除失败');
    }
  }
};

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;
  
  // 如果没有当前会话，创建新会话
  if (!currentSessionId.value) {
    await createNewSession();
  }
  
  // 添加用户消息
  const userMessage = userInput.value.trim();
  messages.value.push({ role: 'user', content: userMessage });
  userInput.value = '';
  
  // 添加AI消息占位
  messages.value.push({ role: 'assistant', content: '' });
  
  // 滚动到底部
  await nextTick();
  scrollToBottom();
  
  // 发送请求
  isLoading.value = true;
  try {
    await fetchAIResponse(userMessage);
  } catch (error) {
    console.error('Error fetching AI response:', error);
    messages.value[messages.value.length - 1].content = `发生错误: ${error.message || '请检查网络连接'}`;
    showToast('AI回复失败，请稍后重试');
  } finally {
    isLoading.value = false;
    await nextTick();
    scrollToBottom();
  }
};

// 获取AI响应
const fetchAIResponse = async (userMessage) => {
  try {
    const token = getToken();
    if (!token) {
      throw new Error('未登录');
    }
    
    const response = await axios.post(
      `${apiBase}/chat`,
      {
        message: userMessage,
        session_id: currentSessionId.value
      },
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    
    if (response.data && response.data.code === 200) {
      const aiReply = response.data.data.reply;
      messages.value[messages.value.length - 1].content = aiReply || '抱歉，我无法生成回复。请稍后再试。';
      
      // 更新会话ID（如果是新会话）
      if (response.data.data.session_id) {
        currentSessionId.value = response.data.data.session_id;
      }
      
      await nextTick();
      scrollToBottom();
      
      // 重新加载会话列表以更新标题
      await loadSessions();
    } else {
      throw new Error(response.data.message || '请求失败');
    }
  } catch (error) {
    console.error('API请求错误:', error);
    throw new Error(error.response?.data?.detail || error.message || '网络请求失败');
  }
};

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

// 监听消息变化，自动滚动
watch(messages, () => {
  nextTick(scrollToBottom);
}, { deep: true });

// 组件挂载时加载会话
onMounted(() => {
  loadSessions();
  scrollToBottom();
});
</script>

<style scoped>
.ai-chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding-top: 46px;
  padding-bottom: 50px;
  box-sizing: border-box;
}

/* 会话侧边栏样式 */
.session-sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f7f8fa;
}

.session-header {
  padding: 16px;
  background-color: #fff;
  border-bottom: 1px solid #ebedf0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.session-list {
  flex: 1;
  overflow-y: auto;
}

.session-list .van-cell.active {
  background-color: #e8f4ff;
  color: #1989fa;
}

.session-list .van-cell:active {
  background-color: #f2f3f5;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.message {
  margin-bottom: 10px;
  max-width: 80%;
}

.user-message {
  margin-left: auto;
}

.ai-message {
  margin-right: auto;
}

.message-content {
  padding: 10px;
  border-radius: 10px;
  word-break: break-word;
}

.user-message .message-content {
  background-color: #007aff;
  color: white;
}

.ai-message .message-content {
  background-color: #f2f2f2;
  color: #333;
}

.input-container {
  display: flex;
  padding: 10px;
  border-top: 1px solid #eee;
  background-color: #fff;
}

.chat-input {
  flex: 1;
  margin-right: 10px;
}

.send-button {
  align-self: flex-end;
}

/* Markdown 样式 */
.message-content pre {
  background-color: #f8f8f8;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
}

.message-content code {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 4px;
  border-radius: 3px;
}

.message-content img {
  max-width: 100%;
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  padding: 5px;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  background-color: #999;
  border-radius: 50%;
  margin: 0 2px;
  display: inline-block;
  animation: bounce 1.5s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-5px);
  }
}

/* Markdown样式 */
:deep(pre) {
  background-color: #f0f0f0;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

:deep(code) {
  font-family: monospace;
  background-color: #f0f0f0;
  padding: 2px 4px;
  border-radius: 4px;
}

:deep(p) {
  margin: 8px 0;
}

:deep(ul), :deep(ol) {
  padding-left: 20px;
}

:deep(a) {
  color: #1989fa;
  text-decoration: none;
}
</style>
