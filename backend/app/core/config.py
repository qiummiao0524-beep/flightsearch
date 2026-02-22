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
    
    # Claude API 配置
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_API_URL: str = "https://api.anthropic.com"  # 可配置为内部代理地址
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    
    # CORS 配置
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://10.181.132.217:5173"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
