# 🚀 인보험 약관 RAG 챗봇 개발 로드맵

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **목표** | 인보험 약관 PDF 기반 질의응답 챗봇 백엔드 개발 |
| **기술 스택** | FastAPI, LangGraph, Supabase(pgvector), Upstage API (LLM/Embedding) |
| **핵심 전략** | **Contextual Retrieval**(문맥 입히기) + **Multi-Vector**(가상 질문 검색 + 원본 답변) 혼합으로 정확도·신뢰성 극대화 |

---

## Phase 1. 기본 환경 및 FastAPI 뼈대 구축

서버 진입점과 공통 설정을 구성합니다.

### 1. `app/core/config.py` — Settings 클래스

- [ ] `environment` — dev/prod 환경 구분
- [ ] `debug` — 디버그 모드 여부
- [ ] `upstage_api_key` — LLM·임베딩 API 키
- [ ] `llm_model` — 사용 모델명
- [ ] `model_config` — `SettingsConfigDict`로 `.env` 연동
- [ ] `@lru_cache` — 설정 인스턴스 캐싱

### 2. `app/schemas/chat.py` — 채팅 스키마

- [ ] `message` — 사용자 쿼리 / AI 응답 내용
- [ ] `tool_used` — RAG 검색 등 사용 도구 추적
- [ ] `cached` — 캐싱 여부
- [ ] `timestamp` — 요청/응답 시각

### 3. `app/main.py` — FastAPI 앱

- [ ] FastAPI 인스턴스 생성 (`app = FastAPI(...)`)
- [ ] CORS 미들웨어 등록 (프론트 연동용)
- [ ] 루트 엔드포인트 (헬스체크/API 상태 확인)

---

## Phase 2. 데이터 파이프라인 구축 ⭐

단순 청킹 대신 **약관 특화 전처리** 후 Supabase에 적재. LangGraph 구축 전 필수 선행 작업.

### 1. PDF 구조적 파싱·청킹

- [ ] **텍스트 추출** — Upstage Document Parse 등으로 PDF → 텍스트
- [ ] **구조적 청킹** — 글자 수가 아닌 **제○조(제목)**·**항/호** 단위로 분할

### 2. 문맥 입히기 & 가상 질문 생성 (Data Enrichment)

- [ ] **문맥(Context)** — LLM으로 각 조항 앞에 상위 목차 텍스트 병합  
  (예: `[무배당 굿앤굿어린이보험] - [암특약]`)
- [ ] **예상 질문(Q&A)** — LLM으로 “이 조항을 찾기 위해 사용자가 할 법한 질문 3가지” 생성

### 3. Supabase(pgvector) 테이블 설계·벡터 적재

- [ ] **pgvector 활성화** — SQL 에디터에서 `CREATE EXTENSION vector;` 실행
- [ ] **테이블 스키마**

  | 컬럼 | 용도 |
  |------|------|
  | `id` | 고유 식별자 |
  | `search_content` | 검색용 (문맥 + 예상 질문 3개) |
  | `original_content` | 답변용 (순수 약관 원문) |
  | `metadata` | 조항번호, 특약명 등 JSON |
  | `embedding` | `search_content` 임베딩 벡터 |

- [ ] **임베딩·Insert** — Upstage 임베딩으로 벡터화 후 Supabase 적재

---

## Phase 3. LangGraph 기반 AI 에이전트 구축

검색 → 원본 추출 → 답변 흐름을 그래프로 설계합니다.

### 1. `app/graph/state.py` — AgentState

- [ ] `messages` — 전체 대화 기록
- [ ] `intent` — 의도 분류 (일반대화 vs 약관검색)
- [ ] `retrieved_docs` — RAG 검색 결과 `original_content` 저장
- [ ] 도구 관련 필드 3개 (사용 이력·상태)
- [ ] 세션 관련 필드 2개 (사용자/세션 식별)

### 2. `app/graph/nodes.py` — 노드 함수

- [ ] **의도 분류** — 마지막 사용자 메시지 추출, `with_structured_output`로 스키마 고정 후 LLM 호출
- [ ] **RAG 검색** — 사용자 질문 임베딩 → Supabase 유사도 검색 (`search_content` 기준)
- [ ] **검색 결과 추출** — Row에서 `original_content`만 추출해 State에 저장
- [ ] **ToolExecutor** — 필요 도구 실행
- [ ] **응답 프롬프트** — intent에 따라 분기, 약관 검색 시 “제공된 약관 원본(`retrieved_docs`)만으로 보수적 답변” 지시
- [ ] **응답 생성** — LLM 호출 후 `messages`에 AI 응답 추가

### 3. `app/graph/edges.py` — 조건부 엣지

- [ ] **의도 기반 라우팅** — intent에 따라 (RAG 검색 노드) vs (일반 대화 노드) 분기

### 4. `app/graph/graph.py` — 그래프 조립

- [ ] `StateGraph` 생성 (AgentState 기반)
- [ ] `graph.add_node` — 노드 4개 등록
- [ ] `graph.set_entry_point` — 진입점 설정
- [ ] 조건부 엣지 — 의도 분류 후 분기
- [ ] 일반 엣지 — 노드 간 선형 흐름 3개
- [ ] `graph.compile()` — 컴파일된 에이전트 완성

---

## Phase 4. API 엔드포인트 연동

LangGraph 에이전트를 FastAPI 라우터에 연결합니다.

### `app/api/routes/chat.py` — 채팅 API

- [ ] 컴파일된 LangGraph 에이전트 import
- [ ] 요청 바탕으로 초기 `AgentState` 딕셔너리 구성
- [ ] `graph.ainvoke()` 비동기 실행
- [ ] 결과 State의 `messages` 마지막 요소로 최종 응답 추출
- [ ] `ChatResponse` 스키마로 JSON 응답 반환
