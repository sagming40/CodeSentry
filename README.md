# CodeSentry

> 저장소를 스캔해 위험도를 판단하고, 테스트 작성 또는 코드 수정 중
> 필요한 조치를 스스로 선택해 실행·검증하는 AI 에이전트

🚧 개발 중 (2026.07~) · 현재 진행 상황: **EPIC 2 완료** (스캐너 + LLM 판단 파이프라인 자동 실행 가능, 자동 수정·대시보드는 아직 미구현)

> ⚠️ "CodeSentry"는 임시 프로젝트명입니다. 작업/프로젝트명은 추후 변동될 수 있습니다.

---

## 이 프로젝트가 증명하려는 것

이 저장소는 "실무 역량을 증명하는 완성작"이 아니라, **근거를 먼저 찾고 그 위에서 설계 판단을 내리는 사고방식**을 보여주기 위한 학습 프로젝트입니다. 컴퓨터공학과 하이테크 과정(2026.03~) 4개월차에 시작했고, 인문학 전공 배경에서 프로그래밍을 처음 배우는 중입니다. 그래서 이 저장소를 볼 때 기대해도 좋은 것과 아닌 것을 미리 밝혀둡니다.

- **기대해도 되는 것**: 기능/설계를 정할 때 근거(공식 자료·통계)를 먼저 찾고, 신뢰도를 구분해서 표기하고, 선택의 트레이드오프를 숨기지 않고 기록하는 태도. `docs/` 폴더의 기획 근거자료와 개발 일지가 그 과정을 그대로 담고 있습니다.
- **기대하지 않아도 되는 것**: 프로덕션 수준의 완성도나 엣지 케이스 전부 커버. 예를 들어 스캐너의 테스트 파일 확인 로직(`test_check.py`)은 "파일명 패턴 매칭"이라는 의도적으로 좁은 방식을 쓰고 있고, 이 한계는 숨기지 않고 백로그에 명시해뒀습니다.

## 왜 만들었나

AI가 코드를 더 빨리 짤수록 사람에게 남는 병목은 "이 코드를 믿어도 되는가"를 검증하는 일인데, 정작 시중의 AI 에이전트 대다수는 자율적 판단 없이 재포장된 자동화 도구에 그치고 있습니다. 이 프로젝트는 위험도를 스스로 판단해 테스트로 검증할지 수정을 제안할지 결정하고, 그 결과까지 검증하는 에이전트를 직접 만들어보는 것을 목표로 합니다.

기획 배경과 근거자료(PwC 2026 Global AI Jobs Barometer, Gartner 2025 agentic AI 자료 등)는 [`docs/AI에이전트_프로젝트_기획근거자료.md`](./docs/AI에이전트_프로젝트_기획근거자료.md) 참고.

## 핵심 설계 원칙

- **규칙 기반 1차 필터 → LLM 2차 판단**: radon 순환 복잡도 + 테스트 부재를 결정론적·비용 없는 규칙으로 먼저 걸러내고, 통과한 것만 LLM(`assess_risk`)에게 판단을 맡깁니다. 모든 파일을 LLM에게 넘기지 않는 이유는 비용 관리 목적입니다.
- **안전장치는 프롬프트가 아니라 코드로 강제**: LLM의 판단 신뢰도(`confidence`)가 0.6 미만이면, 모델이 뭐라 답했든 백엔드 코드가 강제로 사람에게 넘깁니다(`escalate_human`). "확신 없으면 알아서 넘겨줘"처럼 프롬프트로 부탁하는 방식은 신뢰하지 않습니다.
- **코드 수정 제안은 항상 사람 승인**: `propose_fix`(코드 수정 제안)는 신뢰도와 무관하게 항상 사람이 승인해야 적용됩니다. 반면 `write_test`(테스트 작성)는 실패 시 최대 1회만 재시도하고, 그래도 실패하면 사람에게 넘깁니다.
- **관심사 분리**: 스캐너 / 오케스트레이터(LLM 판단) / 샌드박스(격리 실행)를 독립된 모듈로 분리하고, 프론트엔드(React)는 백엔드와 REST + WebSocket으로만 통신합니다. 프론트엔드를 통째로 바꿔도 백엔드 로직은 흔들리지 않는 구조를 목표로 합니다.

## 현재 상태

| EPIC | 내용 | 상태 |
| --- | --- | --- |
| EPIC 0 | 개발 환경·도구 학습 | ✅ 완료 |
| EPIC 1 | 스캐너 (규칙 기반 필터) | ✅ 완료 |
| EPIC 2 | 오케스트레이터 (LLM 판단) | ✅ 완료 |
| EPIC 3 | 생성 & 샌드박스 실행 | ⬜ 예정 |
| EPIC 4~5 | 승인 게이트 + 백엔드 API | ⬜ 예정 |
| EPIC 6 | React 대시보드 | ⬜ 예정 |
| EPIC 7~8 | 통합·마무리·포트폴리오 정리 | ⬜ 예정 |

세부 진행 상황과 트러블슈팅 기록은 [`docs/WORKFLOW.md`](./docs/WORKFLOW.md), 세션 단위 회고는 [`docs/DEVLOG.md`](./docs/DEVLOG.md)에 있습니다.

## 아키텍처

### 전체 구조

```
웹 대시보드 (React) — diff 뷰어 · 승인 · 모니터링
        │  REST + WebSocket
        ▼
백엔드 API (FastAPI)
        │
   ┌────┼──────────────┐
   ▼    ▼              ▼
스캐너  오케스트레이터   샌드박스 실행기
(radon+  (LLM 판단·      (격리 환경
테스트    액션 분기)      테스트 실행)
확인)
   └────┼──────────────┘
        ▼
DB (SQLite) — 상태 · 승인여부 · 비용 로그
```

스캐너(무엇이 위험한지 탐지) → 오케스트레이터(어떻게 대응할지 판단) → 샌드박스(실행·검증)로 역할을 분리했습니다. 각 모듈이 독립적으로 테스트 가능하고, 한 모듈만 교체해도 나머지가 흔들리지 않는다는 것이 이 구조의 실익입니다 — 실제로 프론트엔드를 Flutter에서 React로 교체할 때 백엔드 4개 모듈은 전혀 변경되지 않았습니다.

### DB 관계

```
scans (1) ──< findings (N)
findings (1) ──< llm_calls (N)   // 판단 1회 + 생성 1~2회
findings (1) ──< actions (N)     // 재시도 시 여러 row
actions (1) ──< approvals (0~1)  // propose_fix인 경우만 생성
```

`llm_calls`를 별도 테이블로 분리한 이유는 비용(토큰·금액) 집계를 finding 단위로 깔끔하게 뽑기 위함이고, `approvals`를 `actions`와 분리한 이유는 자동 검증되는 `write_test`와 사람 승인이 필요한 `propose_fix`의 흐름이 완전히 다르기 때문입니다. 스키마 설계 근거 전체는 기획 근거자료 7장 참고.

## 폴더 구조

> 아래는 현재 시점 스냅샷입니다. 최신 구조는 [`docs/WORKFLOW.md`](./docs/WORKFLOW.md)를 기준으로 봐주세요.

```
CodeSentry/
├── docs/
│   ├── AI에이전트_프로젝트_기획근거자료.md
│   ├── WORKFLOW.md
│   └── DEVLOG.md
│
├── backend/
│   ├── main.py                       # FastAPI 앱 진입점
│   ├── database.py                   # SQLite 연결 (SQLAlchemy)
│   ├── models.py                     # scans / findings / llm_calls / actions / approvals
│   │
│   ├── scanner/                      # EPIC 1
│   │   ├── walker.py                 # 대상 저장소 .py 파일 순회
│   │   ├── complexity.py             # radon 연동
│   │   ├── test_check.py             # 테스트 파일 존재 확인
│   │   └── run_scan.py               # 판정 로직 + DB 저장
│   │
│   ├── orchestrator/                 # EPIC 2~3
│   │   ├── tools.py                  # assess_risk / generate_test / propose_fix 스키마
│   │   ├── llm_client.py             # Claude API 호출 래퍼 + usage/cost 계산
│   │   ├── persistence.py            # llm_calls/actions DB 저장
│   │   └── run_pipeline.py           # findings 순회 자동 파이프라인
│   │
│   ├── sandbox/                      # EPIC 3
│   │   └── executor.py               # subprocess 격리 실행 + 재시도 로직
│   │
│   ├── routers/                      # EPIC 5
│   │   ├── scans.py
│   │   ├── findings.py
│   │   ├── approvals.py
│   │   └── ws.py
│   │
│   └── requirements.txt
│
└── frontend/                         # EPIC 6 (React)
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

## 실행 방법 (현재까지 구현된 범위)

전체 서비스(FastAPI + React)는 아직 미완성이며, 지금은 스캐너 모듈만 단독으로 실행할 수 있습니다.

```powershell
# 프로젝트 최상위 폴더에서, venv 활성화 상태로
python -m backend.scanner.run_scan
```

`backend` 폴더를 대상으로 스캔해서 SQLite(`codesentry.db`)에 결과를 저장합니다. 전체 API·대시보드 실행 방법은 EPIC 5~6 완료 후 이 섹션에 채울 예정입니다.

스캔 이후, 아직 판단이 끝나지 않은(`status='found'`) 위험 코드에 대해 LLM 판단을 실행하려면:

```powershell
python -m backend.orchestrator.run_pipeline
```

실행 전 프로젝트 최상위 폴더에 `.env` 파일을 만들고 `ANTHROPIC_API_KEY=본인_키` 형식으로 API 키를 넣어야 합니다.

## 기술 스택

- **백엔드**: Python (FastAPI, radon, SQLAlchemy, python-dotenv)
- **프론트엔드**: React (Vite)
- **DB**: SQLite
- **LLM**: Claude API (tool-calling, `claude-haiku-4-5`)
- **버전 관리**: GitHub, Conventional Commits

## 참고 문서

- [기획 근거자료](./docs/AI에이전트_프로젝트_기획근거자료.md)
- [WORKFLOW — 진행 체크리스트 & 백로그](./docs/WORKFLOW.md)
- [DEVLOG — 세션별 개발 일지 & 트러블슈팅](./docs/DEVLOG.md)
