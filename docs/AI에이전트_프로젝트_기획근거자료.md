# AI 에이전트 프로젝트 — 기획 근거자료 & 설계 문서

사공민규

최초 작성: 2026년 7월 3일 · 수정: 2026년 7월 3일 · 버전 v0.4

---

## 1. 개요

본 문서는 "AI 에이전트" 프로젝트를 기획하며 확보한 근거자료와, 그 근거 위에서 확정한 설계 결정(판단 기준, 아키텍처, LLM Tool, DB 스키마)을 정리한 것이다. 개인적 필요나 막연한 관심이 아니라, 검증 가능한 통계·공식 발표자료를 바탕으로 기획 의도를 구성하는 것을 목표로 한다.

## 2. 근거자료 정리

🟢는 발행 기관의 공식 페이지에서 직접 확인한 1차 출처, 🟡는 2차 출처(다른 매체의 인용)를 통해 확인한 것으로 발표 전 원문 확인을 권장한다.

| 출처 | 발행일 | 핵심 내용 | 신뢰도 |
| --- | --- | --- | --- |
| PwC 2026 Global AI Jobs Barometer | 2026.06 | AI 노출도가 높은 기업의 생산성 성장률이 그렇지 않은 기업보다 40% 높음. 요구 스킬 변화 속도는 2배 이상 빠름. 에이전틱 AI를 인간 전문성의 핵심 보완 기술로 투자 권고. | 🟢 1차 확인 |
| Gartner, Inc. 공식 보도자료 | 2025.06.25 | 2027년 말까지 에이전틱 AI 프로젝트의 40% 이상이 비용 급증·불명확한 가치·부실한 리스크 관리로 취소될 것으로 전망. 실제 자율성을 갖춘 벤더는 약 130개뿐("agent washing"). | 🟢 1차 확인 |
| Stanford HAI AI Index Report 2026 | 2026 | 에이전틱 AI 관련 채용 공고가 전년 대비 280% 증가. | 🟡 2차 인용 |
| Stack Overflow 2025 Developer Survey | 2025 | 개발자의 52%는 AI 에이전트를 전혀 사용하지 않거나 단순 도구 수준에서만 사용 중. | 🟡 2차 인용 |

## 3. 기획 의도

### 3.1 근거 간 관계

- 수요는 실재하고 검증됨 — PwC 10억 건 이상 채용 공고 분석에서, AI를 적극 활용하는 기업일수록 생산성·고용·임금 모두 더 빠르게 성장.
- 공급(실제 역량 보유자)은 부족함 — 개발자 절반 이상이 아직 에이전트를 실제로 사용해보지 않았고, 벤더 대다수도 실질적 자율성이 없는 재포장 수준.
- 동시에 실패율도 높음 — Gartner가 지적한 실패 요인(모호한 목표, 비용 관리 부재, 리스크 통제 부재)은 이 프로젝트의 설계 원칙으로 반영.

### 3.2 기획 의도 (종합)

PwC의 2026년 글로벌 AI 고용 바로미터에 따르면 AI를 적극 활용하는 기업은 생산성이 40% 더 높으며, 에이전틱 AI를 인간 전문성의 핵심 보완 기술로 권고하고 있다. 그러나 Gartner는 2027년까지 에이전틱 AI 프로젝트의 40% 이상이 불명확한 가치와 부실한 리스크 설계로 취소될 것이라 경고하며, 현존하는 에이전트 벤더 대다수가 실질적 자율성 없이 재포장된 챗봇에 불과하다고 지적한다. 본 프로젝트는 이 간극 — "수요는 실재하나 진짜 역량은 희소한" 지점 — 을 개인 규모에서 학습 목적으로 재현하는 것을 목표로 하며, Gartner가 지적한 실패 요인을 설계 단계에서부터 의도적으로 반영한다.

### 3.3 한 문장 정의

> 저장소를 스캔해 위험도를 판단하고, 그 판단에 따라 테스트 작성 또는 코드 수정 중 필요한 조치를 스스로 선택해 실행한 뒤, 실행 결과를 검증하고 리포트하는 에이전트

## 4. 판단 기준 설계

### 4.1 1단계 — 규칙 기반 필터 (결정론적, 비용 없음)

| 신호 | 도구 | 의미 |
| --- | --- | --- |
| 순환 복잡도 | radon 라이브러리 | 코드 실행 경로가 얼마나 복잡한지를 자동으로 계산한 수치 |
| 테스트 존재 여부 | 파일명 패턴 확인 | 해당 코드에 대응하는 테스트 파일이 있는지 여부 |

**판정 규칙: 순환 복잡도가 임계값(예: 10) 이상이면서 테스트가 없는 코드 → "위험"으로 판정.**

### 4.2 2단계 — AI 판단 (1단계를 통과한 코드에만 적용)

- 위험 판정된 코드를 LLM에 전달해 "테스트를 작성해야 하는가, 로직 자체를 수정해야 하는가"를 스스로 판단하게 함.
- 판단 결과에 따라 테스트 생성 또는 수정안 제안으로 분기, 수정 제안은 항상 사람 승인 대기.

### 4.3 설계 근거

- 순환 복잡도·테스트 부재는 반박하기 어려운 정량 지표이며 재현 가능한 기준임.
- 모든 코드를 LLM에 전달하면 비용이 감당되지 않으므로, 규칙 기반 필터로 1차 축소 후 필요한 부분에만 AI 판단 적용 — "비용 관리 부재" 실패 요인에 대한 직접 대응.
- 최근 커밋 빈도는 위험도와의 상관관계를 설명하기 어려워 판단 기준에서 제외.

## 5. 아키텍처 설계

### 5.1 전체 구조

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

스캐너(무엇이 위험한지 탐지) → 오케스트레이터(어떻게 대응할지 판단) → 샌드박스(실행·검증)로 역할을 분리했다. 각 모듈이 독립적으로 테스트 가능하고, 한 모듈만 교체해도 나머지가 흔들리지 않는다는 것이 이 구조의 실익이다 — 실제로 프론트엔드를 Flutter에서 React로 교체할 때 백엔드 4개 모듈은 전혀 변경되지 않았다.

### 5.2 샌드박스 실행기 — 리스크 통제 설계

- AI가 생성한 테스트 코드는 격리된 임시 환경(별도 프로세스, 제한된 파일 시스템 접근, 네트워크 차단, 실행 시간 제한)에서만 실행.
- 실패 시 무한 재시도 대신 최대 1회까지만 재시도, 이후 "사람 검토 필요" 상태로 전환.
- → Gartner가 지적한 "리스크 통제 부재" 실패 요인에 대한 직접적 대응.

### 5.3 기술 스택 선택 근거 (신뢰도별 정리)

모든 기술 선택에 동일한 수준의 근거가 있는 것은 아니다. 과장 없이 세 등급으로 구분한다.

| 등급 | 선택 | 근거 |
| --- | --- | --- |
| 🟢 기술적 필요 | FastAPI | LLM 호출(I/O 대기) + WebSocket 실시간 통신이라는 요구사항이 async 기본 지원 프레임워크를 직접 요구함 |
| 🟢 기술적 필요 | radon | 순환 복잡도는 이미 검증된 표준 계산 방식 — 직접 구현은 불필요한 재발명 |
| 🟢 기술적 필요 | Claude API 직접 tool-calling (프레임워크 미사용) | 에이전트 프레임워크(LangChain 등)는 내부 동작을 추상화함 — Gartner가 지적한 "agent washing"(내부를 이해 못 하고 갖다 쓰는 문제)을 피하기 위해 직접 구현 |
| 🟡 학습목표/편의 | SQLite | 개인 프로젝트 규모에 서버형 DB는 과함, 설치 없이 실행 가능 |
| 🟡 학습목표/편의 → 재검토 후 교체 | React (구 Flutter) | 코드 리뷰는 데스크톱/웹 작업에 가까움(Cursor·Copilot 등 실제 사례 참고). Flutter는 학습 목표였을 뿐 기술적 최적은 아니었다고 판단해 React로 교체 |
| 🔴 타협(한계 인정) | 샌드박스: subprocess + resource 모듈 (Docker 아님) | Docker가 격리 수준은 더 높으나 현재 학습 단계에 비해 과함. "완벽한 리스크 통제"가 아니라 "현재 수준에서 최선"이라는 한계를 발표에서 명시 |

## 6. LLM Tool 설계

판단(1단계)과 생성(2단계)을 분리해, 애매한 케이스가 비용이 큰 생성 단계까지 가지 않도록 설계했다. 세부 스키마보다 "왜 이렇게 나눴는가"가 핵심이다.

| 단계 | Tool | 호출 시점 / 주요 출력 | 설계 이유 |
| --- | --- | --- | --- |
| 1단계 (판단) | assess_risk | 위험 판정된 모든 코드에 호출 → `action_type`, `risk_reason`, `confidence` | 가벼운 판단만 먼저 수행해 불필요한 고비용 생성 호출 차단 |
| 2-A단계 (생성) | generate_test | `action_type = write_test`일 때만 → `test_code`, `covered_cases` | 실행·검증 가능한 산출물만 생성 |
| 2-B단계 (생성) | propose_fix | `action_type = propose_fix`일 때만 → `fix_diff`, `fix_explanation` | 코드 수정은 신뢰도와 무관하게 항상 사람 승인 대상 |

### 6.1 안전장치 (결정론적 규칙으로 LLM 판단을 이중 체크)

- `confidence < 0.6` → LLM의 판단과 무관하게 백엔드 코드가 강제로 `escalate_human`으로 전환 (LLM의 자기 확신을 그대로 신뢰하지 않음).
- `write_test` 실행 실패 시 최대 1회만 재시도, 이후 `needs_review`로 전환 (무한 루프·비용 폭주 방지).
- `propose_fix`는 confidence와 무관하게 항상 사람 승인 필수 — 코드 수정이라는 되돌리기 어려운 액션에는 예외를 두지 않음.

## 7. DB 스키마 설계

LLM Tool의 출력 필드를 그대로 테이블 컬럼으로 옮기는 방식으로 설계했다.

### 7.1 테이블 구조

**`scans` — 스캔 실행 단위**

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id | PK | |
| repo_path | TEXT | 스캔 대상 저장소 경로/URL |
| status | TEXT | running / completed / failed |
| started_at / finished_at | DATETIME | finished_at은 진행 중이면 NULL |
| total_files_scanned | INTEGER | |

**`findings` — 위험 코드 (상태 흐름의 중심)**

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id / scan_id | PK / FK | scans.id 참조 |
| file_path / function_name | TEXT | |
| complexity_score | INTEGER | radon 계산값 |
| has_test | BOOLEAN | |
| status | TEXT | found → analyzing → test_generated/fix_proposed → verifying/pending_approval → passed/needs_review/approved/rejected |

**`llm_calls` — 모든 LLM 호출 로그 (비용 추적용)**

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id / finding_id | PK / FK | findings.id 참조 |
| call_type | TEXT | assess_risk / generate_test / propose_fix |
| input_tokens / output_tokens | INTEGER | |
| estimated_cost_usd | REAL | |
| raw_response | TEXT(JSON) | tool 응답 원본 전체 저장 |

**`actions` — 판단·생성 결과**

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id / finding_id / llm_call_id | PK / FK / FK | |
| action_type | TEXT | write_test / propose_fix / escalate_human |
| confidence / risk_reason | REAL / TEXT | 1단계 판단 결과 |
| content / detail | TEXT | 생성된 test_code·fix_diff / covered_cases·fix_explanation |
| attempt_number | INTEGER | 재시도 횟수 (최대 1회 규칙과 연결) |
| execution_status | TEXT | pending / passed / failed (테스트만 해당) |

**`approvals` — 사람 승인 게이트 (fix 제안 전용)**

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id / action_id | PK / FK | actions.id 참조 |
| status | TEXT | pending / approved / rejected |
| reviewer_note / reviewed_at | TEXT / DATETIME | NULL 허용 |

### 7.2 관계

```
scans (1) ──< findings (N)
findings (1) ──< llm_calls (N)   // 판단 1회 + 생성 1~2회
findings (1) ──< actions (N)     // 재시도 시 여러 row
actions (1) ──< approvals (0~1)  // propose_fix인 경우만 생성
```

### 7.3 설계 근거

- `llm_calls`를 별도 테이블로 분리 — actions는 재시도마다 여러 row가 생기므로, 비용 집계(SUM)를 finding 단위로 깔끔하게 뽑기 위함.
- `raw_response` 전체 저장 — 판단 근거를 나중에 디버깅하거나 발표 자료에서 실제 응답 예시를 재구성할 필요가 없도록 함.
- `approvals`를 actions와 분리 — write_test(자동 검증)와 propose_fix(사람 승인)는 흐름이 완전히 달라, 승인 개념이 없는 test 액션에 불필요한 컬럼을 두지 않기 위함.
- `attempt_number` 기록 — "최대 1회 재시도" 규칙을 DB 레벨에서도 추적, 재시도 발생 빈도를 통계로 낼 수 있음.

## 8. 백로그 — 시간 여유 시 고도화

현재 설계에서 의도적으로 범위를 좁히거나 타협한 부분 중, 핵심 로직 완성 후 여유가 있으면 반영할 항목을 기록한다.

| 항목 | 내용 |
| --- | --- |
| 샌드박스 실행기: Docker 전환 | 현재는 subprocess + resource 모듈 기반 격리(섹션 5.3 참고). 핵심 로직(스캐너·오케스트레이터·DB)이 완성된 후 시간이 남으면 샌드박스 모듈만 Docker 컨테이너 기반으로 교체. 관심사 분리 설계 덕분에 다른 모듈은 변경 없이 샌드박스만 교체 가능 — Flutter→React 교체 때 백엔드가 흔들리지 않았던 것과 같은 이유. |

*※ 이 섹션은 설계·구현 중 새로운 항목이 생길 때마다 계속 추가한다.*

## 9. 참고문헌

1. PwC. (2026). *2026 Global AI Jobs Barometer*. https://www.pwc.com/gx/en/services/ai/ai-jobs-barometer.html
2. Gartner, Inc. (2025, June 25). *Gartner Predicts Over 40% of Agentic AI Projects Will Be Canceled by End of 2027*. https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027
3. Stanford Institute for Human-Centered AI (HAI). (2026). *AI Index Report 2026*. (원문 미확인 — 발표 전 https://aiindex.stanford.edu 에서 직접 확인 권장)
4. Stack Overflow. (2025). *2025 Developer Survey*. (원문 미확인 — 발표 전 https://survey.stackoverflow.co 에서 직접 확인 권장)

*※ 3, 4번 자료는 발표 전 원문 페이지를 직접 열람하여 인용 문구·수치를 재확인할 것을 권장한다.*

*※ 개정 이력: v0.1(2026.07.03) 근거자료 및 기획 의도 작성 → v0.2(2026.07.03) 판단 기준 설계 섹션 추가 → v0.3(2026.07.03) 아키텍처·LLM Tool·DB 스키마 설계 추가, 프론트엔드 Flutter→React 변경 반영 → v0.4(2026.07.03) 백로그 섹션 추가(Docker 전환 항목)*
