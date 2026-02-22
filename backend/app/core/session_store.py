"""会话存储 - 内存实现"""
from collections import defaultdict
from datetime import datetime
from typing import Optional
import uuid


class SessionStore:
    """内存会话存储，重启清空"""
    
    def __init__(self):
        self.sessions: dict[str, dict] = {}
        self.messages: dict[str, list] = defaultdict(list)
    
    def create_session(self) -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "trip_info": None
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def update_trip_info(self, session_id: str, trip_info: dict):
        """更新行程信息"""
        if session_id in self.sessions:
            self.sessions[session_id]["trip_info"] = trip_info
            self.sessions[session_id]["updated_at"] = datetime.now()
    
    def add_message(self, session_id: str, role: str, content: str, 
                    trip_info: dict = None, response_type: str = None):
        """添加消息"""
        self.messages[session_id].append({
            "role": role,
            "content": content,
            "trip_info": trip_info,
            "response_type": response_type,
            "timestamp": datetime.now()
        })
    
    def get_messages(self, session_id: str) -> list:
        """获取会话消息历史"""
        return self.messages.get(session_id, [])
    
    def get_recent_messages(self, session_id: str, limit: int = 10) -> list:
        """获取最近的消息"""
        messages = self.messages.get(session_id, [])
        return messages[-limit:] if len(messages) > limit else messages


# 全局单例
session_store = SessionStore()
