from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# uvicorn이 로드하는 ASGI 앱 객체 (uv run uvicorn main:app)
app = FastAPI(
    title="Insurance-RAG", description="인보험 약관 PDF 기반 질의응답 챗봇 API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 오리진 허용
    allow_credentials=False,  # origins = ["*"] 일 때 True 불가 (브라우저 규칙)
    allow_methods=["*"],  # 모든 메서드 허용 (GET, POST 등등 )
    allow_headers=["*"],  # 모든 요청 헤더 허용
)


@app.get("/")
def root() -> dict[str, str]:
    """헬스 체크용 루트 엔드포인트."""
    return {"message": "Hello from insurance-rag!"}


def main() -> None:
    """스크립트 직접 실행 시 사용 (선택)."""
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
