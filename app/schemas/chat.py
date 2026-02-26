import datetime
from pydantic import BaseModel, Field

# ----- 요청 스키마 (클라이언트 → 서버) -----


class ChatReqeust(BaseModel):
    """
    채팅 API 요청 바디.
    사용자 질문과 세션 식별 정보를 담는다.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="사용자 질문(쿼리) 내용",
    )
    session_id: str | None = Field(
        default=None,
        description="대화 세션 식별자 , 없으면 서버에서 생성 가능",
    )


# ----- 응답 스키마 (서버 → 클라이언트) -----


class ChatResponse(BaseModel):
    """
    채팅 API 응답 바디
    명세: message, tool_used, cached, timestamp
    graph.ainvoke() 결과를 이 스키마로 변환 한다.

    """

    message: str = Field(
        ...,
        description="AI 응답 내용(또는 사용자 쿼리에 대한 답변 텍스트)",
    )

    tool_used: list[str] = Field(
        default_factory=list, description="RAG 검색 등 사용된 도구 목록"
    )

    cached: bool = Field(
        default_factory=datetime.utcnow,
        description="요청/응답 시각 (UTC 기준)",
    )

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}
