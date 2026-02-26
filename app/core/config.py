from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스

    pydantic==-settings 를 사용해서 환경변수를 자동으로 로드
    각 필드는 환경변수 이름과 1:1로 매핑
    대소문자 무시.
    """

    enviroment: Literal["dev", "staging", "prod"] = "dev"

    # 디버그 모드 여부
    debug: bool = True

    upstage_api_key: str = ""

    llm_model: str = "solar-pro2"

    supabase_url: str = ""
    supabase_key: str = ""

    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    설정 객체를 반환 (싱글톤)

    lru_cache 데코레이터를 사용하여 설정 객체를 캐싱
    전체 동일한 설정 객체를 사용

    Returns:
        Settings: 설정 객체

    """

    return Settings()


# 전역 설정 객체
# 다른 모듈에서 from app.core.config import settings 로 사용
settings = get_settings()
