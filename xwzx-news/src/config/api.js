/**
 * API配置文件
 * 包含API基础URL和AI问答功能所需的API参数
 */

// API基础URL配置
export const apiConfig = {
  // 后端API基础URL
  baseURL: 'http://127.0.0.1:8000',
}

// AI聊天配置 - 使用后端代理
export const aiChatConfig = {
  // 通过后端API调用（推荐，避免暴露API Key）
  apiEndpoint: `${apiConfig.baseURL}/api/ai/chat`,
  
  // 流式响应接口
  streamEndpoint: `${apiConfig.baseURL}/api/ai/chat/stream`,
  
  // 使用的模型（可选，后端有默认配置）
  model: 'qwen-plus'
}
