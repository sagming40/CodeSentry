# 📦 CodeSentry WORKFLOW — 사공민규

| 항목 | 내용 |
| --- | --- |
| 카테고리 | 개발 참고 문서 (완성 후 별도로 포트폴리오용 회고 문서 정리 예정) |
| 파일형태 | 문서 |
| 버전 | v0.4 (EPIC 3 완료) |
| 생성일 | 2026년 7월 3일 |
| 수정일 | 2026년 7월 22일 |
| 담당자 | 사공민규 |
| 기술 스택 | Python (FastAPI · radon) · SQLite (SQLAlchemy) · WebSocket · React · Claude API (tool-calling) |
| 관련 문서 | `docs/AI에이전트_프로젝트_기획근거자료.md` — 근거자료·판단기준·아키텍처·LLM Tool·DB 스키마 전부 여기 있음 |
| 개발 일지 | `docs/DEVLOG.md` — 세션 단위 회고 (겪은 이슈 서술형 기록) |
| GitHub 레포 URL | https://github.com/sagming40/CodeSentry |

> ⚠️ **작업명 안내**
> "CodeSentry"는 임시 작업명입니다. 개발 진행하면서 원하는 이름으로 바꾸셔도 됩니다.

> ⚠️ **이 문서의 성격**
> "왜 이 선택을 했는가"는 다시 설명하지 않고 관련 문서 섹션만 표기합니다(중복 방지). 이 문서는 오직 **무엇을 어떤 순서로 할지** 잃어버리지 않기 위한 실행 체크리스트입니다. 세션마다 겪은 일의 서술형 회고와 트러블슈팅은 DEVLOG.md에 남깁니다.

---

> 💡 **전체 흐름 한 줄 요약**
> 학습 준비 → 스캐너 → 오케스트레이터(LLM 판단) → 생성·샌드박스 실행 → 승인 게이트 → 백엔드 API 완성 → React 대시보드 → 통합 → 포트폴리오 마감

> 🗺️ **사용자 플로우**
> 대상 저장소 지정 → 스캔 실행 → 위험 코드 자동 판정 → 에이전트가 테스트 생성(자동 검증) 또는 수정 제안(승인 대기) → 대시보드에서 진행 상황·비용 실시간 확인 → 수정 제안은 승인/거부 → 결과 확인

> 💼 **포트폴리오 포인트**
>
> - 규칙 기반 필터 + LLM 판단의 2단계 하이브리드 설계 (비용 관리 근거 반영)
> - AI 생성 코드의 격리 실행·검증·재시도 제한 (리스크 통제 설계)
> - 코드 수정은 신뢰도와 무관하게 항상 사람 승인 — 명확한 human-in-the-loop 설계
> - FastAPI + WebSocket 실시간 통신, React 대시보드
> - PwC·Gartner 공식 자료 기반의 방어 가능한 기획 의도 (근거자료 문서 별첨)

---

## 🗓️ 개발 일정 (8~11주, 평일 3시간·주말 버퍼 기준)

| 주차 | EPIC | 목표 |
| --- | --- | --- |
| 1주차 | EPIC 0 | 개발 환경·도구 사용법 학습 완료 |
| 2주차 | EPIC 1 | 스캐너 단독 실행 — 위험 코드 목록이 콘솔/DB에 찍힘 |
| 3~4주차 | EPIC 2 | 오케스트레이터 연동 — 위험 코드에 대한 LLM 판단까지 파이프라인 연결 |
| 5주차 | EPIC 3 | 테스트/수정안 생성 + 샌드박스 실행·검증까지 동작 |
| 6주차 | EPIC 4~5 | 승인 게이트 + 백엔드 API 전체 정리 |
| 7~8주차 | EPIC 6 | React 대시보드 완성 |
| 9~10주차 | EPIC 7 | 통합 테스트 + 버그 수정 |
| 11주차 (버퍼) | EPIC 8 | README·테스트·Docker·발표자료 → 마감 |

- [x]  1주차 목표 달성
- [x]  2주차 목표 달성
- [x]  3~4주차 목표 달성
- [x]  5주차 목표 달성
- [ ]  6주차 목표 달성
- [ ]  7~8주차 목표 달성
- [ ]  9~10주차 목표 달성
- [ ]  11주차 목표 달성 (여유 시)

---

## 📁 폴더 구조

```
CodeSentry/
├── docs/
│   ├── AI에이전트_프로젝트_기획근거자료.md
│   ├── WORKFLOW.md
│   └── DEVLOG.md
│
├── backend/
│   ├── main.py                     # FastAPI 앱 진입점
│   ├── database.py                 # SQLite 연결 (SQLAlchemy)
│   ├── models.py                   # scans / findings / llm_calls / actions / approvals
│   │
│   ├── scanner/                    # EPIC 1
│   │   ├── walker.py               # 대상 저장소 .py 파일 순회
│   │   ├── complexity.py           # radon 연동
│   │   ├── test_check.py           # 테스트 파일 존재 확인
│   │   └── run_scan.py             # 판정 로직 + DB 저장
│   │
│   ├── orchestrator/               # EPIC 2~3
│   │   ├── tools.py                # assess_risk / generate_test / propose_fix 스키마
│   │   ├── llm_client.py           # Claude API 호출 래퍼
│   │   ├── persistence.py          # llm_calls/actions DB 저장 (save_action) 
│   │   ├── generation_manager.py   # write_test 재시도 루프(생성 → 샌드박스 → 재시도) + 자동순회
│   │   └── run_pipeline.py         # findings 순회 → 판단 → 저장 자동화 
│   │ 
│   ├── sandbox/                    # EPIC 3
│   │   └── executor.py             # subprocess 격리 실행 + 재시도 로직
│   │
│   ├── routers/                    # EPIC 5
│   │   ├── scans.py
│   │   ├── findings.py
│   │   ├── approvals.py
│   │   └── ws.py
│   │
│   └── requirements.txt
│
└── frontend/                       # EPIC 6 (React)
    ├── src/
    │   ├── App.jsx
    │   ├── pages/
    │   │   ├── FindingsList.jsx
    │   │   └── FindingDetail.jsx
    │   ├── components/
    │   │   ├── DiffViewer.jsx
    │   │   └── CostReport.jsx
    │   └── services/
    │       ├── api.js
    │       └── ws.js
    └── package.json
```

---

## ✅ EPIC 0. 학습 준비

> 목표: 이후 단계에서 막히지 않도록 필요한 도구 사용법을 먼저 익힘

### ✅ Task 0-1 · 개발 환경 준비

- [x]  Python 가상환경 생성, FastAPI + Uvicorn 설치 및 빈 서버 실행 확인
- [x]  `pip install radon`, 아무 `.py` 파일에나 돌려서 출력 형태 확인
- [x]  Claude API 키 발급, tool-calling 최소 예제 1개 직접 실행
- [x]  `npm create vite@latest`로 React 프로젝트 생성, 기본 페이지 렌더링 확인
- [x]  GitHub 저장소 생성, README 스켈레톤 커밋, 폴더 구조 세팅

## ✅ EPIC 1. 스캐너 — 규칙 기반 필터

> 판단 기준 근거: 설계문서 4장 / 아키텍처: 설계문서 5장

### ✅ Task 1-1 · 복잡도 분석

```python
# backend/scanner/complexity.py — 초안
from radon.complexity import cc_visit

def analyze_file(filepath: str) -> list[dict]:
    with open(filepath) as f:
        code = f.read()
    results = []
    for block in cc_visit(code):
        results.append({
            "function_name": block.name,
            "complexity": block.complexity,
            "line_number": block.lineno,
        })
    return results
```

- [x]  대상 저장소 `.py` 파일 순회 스크립트 (`walker.py`)
- [x]  함수별 순환 복잡도 계산 (`complexity.py`)
- [x]  테스트 파일 존재 여부 확인 (`test_check.py`, 파일명 패턴 매칭)
  - ⚠️ 한계 인지: 파일 *존재 여부*만 확인, 그 안에서 실제로 해당 함수를 테스트하는지는 확인 안 함 (백로그 참고)

### ✅ Task 1-2 · 판정 & 저장

- [x]  판정 규칙 구현: 복잡도 ≥ 임계값(10) AND 테스트 없음 → `status = "found"`
- [x]  `models.py`에 `scans`, `findings` 테이블 정의 (DB 스키마: 설계문서 7장)
- [x]  스캔 결과 DB 저장, 샘플 저장소로 단독 실행 테스트 (`_check_db.py`로 조회 검증 완료)
- [x]  **✅ EPIC 1 완료 → GitHub 커밋 Push**

## ✅ EPIC 2. 오케스트레이터 — LLM 판단

> LLM Tool 설계 근거: 설계문서 6장

### ✅ Task 2-1 · assess_risk 연동

- [x]  `orchestrator/tools.py` — `assess_risk` tool 스키마 정의
- [x]  `orchestrator/llm_client.py` — Claude API 호출 래퍼 작성 (.env + python-dotenv로 API 키 분리)

> ⚠️ **안전장치는 프롬프트가 아니라 코드로 강제**
> `confidence < 0.6`이면 LLM이 뭐라 답했든 백엔드 if문에서 `action_type`을 `escalate_human`으로 덮어씀. 프롬프트로 "확신 없으면 escalate 해줘"라고 부탁하는 방식은 신뢰하지 않음.

> ✅ **결정 완료 (2026-07-22)**
> confidence는 action마다 가리키는 대상이 다름 — write_test/propose_fix에 대한 confidence(판단 신뢰도)와 escalate_human에 대한 confidence(escalate가 맞다는 확신)는 별개.  모델이 confidence 높게 escalate_human을 고르는 건 "자기 권한 밖 케이스를 정확히 인지한 것"이지 오류가 아님. 
> → action_type enum 3개 그대로 유지, 스키마에서 제한하지 않음.
> → `actions` 테이블에 `escalation_source` 컬럼(`model_choice` / `confidence_override`) 추가로 모델 자발적 선택과 백엔드 강제 override를 구분 기록.

- [x]  `confidence < 0.6` 강제 override 로직 (`finalize_action()`, 4가지 분기 케이스 단위 테스트 검증 완료)
- [x]  `llm_calls`, `actions` 테이블에 판단 결과·토큰 수·비용 저장 (`persistence.py`의 `save_action()`)
- [x]  스캐너 → 오케스트레이터 파이프라인 1차 통합 테스트 (`run_pipeline.py`, status='found' 자동 순회)
- [x]  **✅ EPIC 2 완료 → GitHub 커밋 Push**

## ✅ EPIC 3. 생성 & 샌드박스 실행

> 리스크 통제 설계: 설계문서 5.2

> ✅ **EPIC 3 진입 전 결정 (2026-07-22)**
> - 재시도는 샌드박스 재실행이 아니라 **generate_test 재호출**(실패 pytest 로그를 프롬프트에 포함해 재생성)로 확정. 코드가 결정론적이라 같은 코드 재실행은 의미 없음.
> - 생성→샌드박스→재시도 로직은 `run_pipeline.py`에 얹지 않고 `orchestrator/generation_manager.py`로 신규 분리 — 관심사 분리 원칙 유지.

> ⚠️ **구현 중 발견한 블로커 — function_code 조회 방법 없었음**
> `generate_test`/`propose_fix`는 함수 소스코드가 필요한데, `Finding` 테이블에 `line_number`가 애초에 저장되지 않고 있었음(radon이 제공하는 `endline`을 스캔 단계에서 버리고 있었음). `Finding`에 `line_number`/`end_line_number` 컬럼을 추가하고, `_read_function_source()` 헬퍼로 파일에서 해당 줄 범위만 슬라이싱하는 방식으로 해결.

### ✅ Task 3-1 · 생성 tool

- [x]  `generate_test` tool 구현 (write_test 케이스 → pytest 코드 생성) — end-to-end 검증 완료
- [x]  `propose_fix` tool 구현 (propose_fix 케이스 → diff 생성) — 스키마 · API 호출 함수까지 구현, 실제 처리 흐름(approvals 연동)은 EPIC 4에서 이어서 구현 예정

### ✅ Task 3-2 · 샌드박스 실행기

```python
# backend/sandbox/executor.py — 초안 (subprocess 기반 격리, Docker 아님 — 설계문서 5.3/8장 참고)
import subprocess

def run_test_isolated(test_code_path: str, timeout_sec: int = 10) -> dict:
    result = subprocess.run(
        ["python", "-m", "pytest", test_code_path, "--tb=short"],
        capture_output=True, text=True, timeout=timeout_sec,
        # TODO: resource 모듈로 메모리 제한, 네트워크 차단 추가
    )
    return {"passed": result.returncode == 0, "output": result.stdout}
```
> ⚠️ **초안 대비 실제 구현 시 달라진 점**
> - `resource` 모듈은 POSIX 전용이라 Windows 개발 환경에서는 `import` 자체가 실패함 → `platform.system()` 체크로 조건부 처리, Windows에서는 timeout만 적용되고 메모리 제한은 미적용 (백로그 참고)
> - `generate_test` 호출 시 `max_tokens=1500`으로는 응답이 중간에 잘리는 경우 확인 → `3000`으로 상향, `stop_reason == "max_tokens"` 체크로 방어 처리 추가

- [x]  격리 실행 환경 구성 (timeout, 리소스 제한 — Windows 한계는 위 메모 참고)
- [x]  통과/실패 판정 → `execution_status` 갱신
- [x]  실패 시 1회만 재시도(`attempt_number` 증가) → 그래도 실패면 `needs_review`
- [x]  **✅ EPIC 3 완료 → GitHub 커밋 Push**

## ⬜ EPIC 4. 승인 게이트

- [ ]  `propose_fix` 결과는 무조건 `approvals` 테이블에 `pending`으로 생성
- [ ]  승인/거부 API (`PATCH /approvals/{id}`)
- [ ]  승인 시 처리 방식 확정 (자동 적용 vs diff만 표시 — 구현하며 재검토)

## ⬜ EPIC 5. 백엔드 API 완성

- [ ]  `GET /findings` (상태별 필터), `GET /findings/{id}` (상세)
- [ ]  `POST /scans` (스캔 트리거)
- [ ]  `WS /ws/scans/{id}` (진행 상황 실시간 push)
- [ ]  Swagger(`/docs`)로 전체 API 점검
- [ ]  **⬜ EPIC 4~5 완료 → GitHub 커밋 Push**

## ⬜ EPIC 6. React 대시보드

- [ ]  findings 목록 화면 (상태별 필터/정렬)
- [ ]  finding 상세 + diff 뷰어 (`DiffViewer.jsx`)
- [ ]  승인/거부 버튼 + API 연동
- [ ]  WebSocket으로 스캔 진행 상황 실시간 표시
- [ ]  비용 리포트 화면 (`CostReport.jsx`)
- [ ]  **⬜ EPIC 6 완료 → GitHub 커밋 Push**

## ⬜ EPIC 7. 통합 + 버그 수정

- [ ]  실제 개인 프로젝트 저장소(또는 샘플 저장소) 대상 엔드투엔드 테스트
- [ ]  엣지 케이스 처리 (빈 저장소, LLM 응답 파싱 실패, 타임아웃 등)
- [ ]  발견된 버그는 DEVLOG.md에 기록

## ⬜ EPIC 8. 완성 & 포트폴리오

- [ ]  README 본문 완성 (아키텍처 다이어그램, 실행 방법, 스크린샷)
- [ ]  구조화 로깅 적용 (`logging` 모듈)
- [ ]  최소 pytest 테스트 추가 (백엔드 API)
- [ ]  Docker 패키징 — 여유 있으면 (백로그의 샌드박스 Docker 전환과 별개로, 배포용 Dockerfile)
- [ ]  발표 자료 정리 (설계 문서 + 실제 구현 결과)
- [ ]  이 WORKFLOW.md + DEVLOG.md를 SubLog 형식의 회고형 문서로 재정리
- [ ]  **⬜ EPIC 8 완료 → 포트폴리오 최종 정리**

---

## 🛠️ 트러블슈팅 기록

> 증상→원인→해결 로그는 이 문서가 아니라 [`docs/DEVLOG.md`](./DEVLOG.md)의 각 세션 항목("겪었던 이슈들")에서 관리합니다. 이 문서는 체크리스트+백로그 역할에 집중합니다.

---

## 📋 백로그 (설계문서와 동기화)

- 샌드박스 실행기 Docker 전환 — subprocess+resource → Docker 컨테이너 (설계문서 8장 참고)
- `test_check.py`의 `has_test_file` — 현재는 파일명 패턴 매칭으로 "테스트 파일 존재 여부"만 확인. 그 파일 안에서 실제로 해당 함수를 테스트하는지(AST 파싱 + 호출/import 추적)는 확인 안함. EPIC 1 스코프상 결정론적이고 빠른 방식을 의도적으로 채택한 것 — 시간 여유 있으면 업그레이드 검토.
- `run_pipeline.py`의 세션 관리 — 루프 안에서 finding마다 매번 `SessionLocal()`을 새로 여는 방식. Finding 개수가 크게 늘어나면 성능 이슈 가능성 있음. 지금은 "안전하게 한 건씩 확실히 처리"를 우선했고, 실제 성능 문제 확인되면 그때 리팩터링 검토.
- 샌드박스 메모리 제한 — `resource` 모듈은 POSIX 전용이라 Windows 개발 환경에서는 미적용(timeout만 적용됨). psutil 폴링이나 pywin32 Job Object로 대체 가능하나, 사전 차단이 아니거나 Windows 전용 의존성 추가가 필요해 현재 스코프에서는 보류.
- `Action` 테이블의 실패 유형 구분 — "생성 자체 실패"(max_tokens 잘림 등, DB row 안 남음)와 "실행 실패"(execution_status='failed', DB row 남음)가 현재 다르게 기록됨. 나중에 대시보드/통계 볼 때 혼동 가능성 있어 인지해둘 것.
- `propose_fix` 처리 흐름(`process_propose_fix()`) — EPIC 4에서 `approvals` 테이블과 함께 구현 예정 (지금 만들면 반쪽짜리가 됨). 

---

*CodeSentry WORKFLOW v0.4 · 사공민규 · 최초 작성 2026.07.03 · 최종 수정 2026.07.22 (EPIC 3 완료)*
