-- 创建 AI 聊天会话表
CREATE TABLE IF NOT EXISTS chat_session (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '会话记录ID',
    user_id INT UNSIGNED NOT NULL COMMENT '用户ID',
    session_id VARCHAR(64) NOT NULL UNIQUE COMMENT '会话UUID',
    title VARCHAR(255) COMMENT '会话标题（自动生成）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted TINYINT DEFAULT 0 COMMENT '是否删除：0-否，1-是',
    
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at),
    
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI 聊天会话表';

-- 创建 AI 聊天消息表
CREATE TABLE IF NOT EXISTS chat_message (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '消息ID',
    session_id VARCHAR(64) NOT NULL COMMENT '会话ID',
    role VARCHAR(20) NOT NULL COMMENT '角色：user/assistant',
    content TEXT NOT NULL COMMENT '消息内容',
    sources JSON COMMENT '信息来源（JSON格式）',
    question_type VARCHAR(50) COMMENT '问题类型：realtime/knowledge/chat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at),
    
    FOREIGN KEY (session_id) REFERENCES chat_session(session_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI 聊天消息表';
