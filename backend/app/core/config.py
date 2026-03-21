"""配置管理"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # API 配置
    APP_NAME: str = "AI Flight Search"
    DEBUG: bool = True
    
    # 二方接口配置 - 请在 .env 文件中配置实际地址
    SEARCH_API_URL: str = "http://localhost:8080/search/simplifySearch"
    SEARCH_API_TOKEN: str = ""  # Labrador-Token
    MOCK_API_URL: str = "http://dispatchmng.uat.ie.17usoft.com/service/wiki"
    
    # LLM API 配置 (OpenAI 兼容)
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_API_URL: str = "https://oneai.17usoft.com/anthropic"
    ANTHROPIC_MODEL: str = "qwen3-5-plus"

    # 兼容旧变量名（保持向后兼容）
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # CORS 配置
    CORS_ORIGINS: list[str] = ["*"]
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
