# 📓 개발 일지 (Dev Log) — CodeSentry

CodeSentry를 진행하며 그날그날 배운 것, 겪은 문제, 고민했던 것들을 기록합니다.
트러블슈팅(증상→원인→해결)은 각 세션의 "겪었던 이슈들" 항목에 서술형으로 함께 남깁니다. 체크리스트와 백로그는 `WORKFLOW.md`에 따로 있습니다.

---

## 2026-07-06 · EPIC 0 마무리

### 오늘 한 일
- Python 가상환경 생성, FastAPI + Uvicorn 설치 및 빈 서버 실행 확인
- `pip install radon`, 아무 `.py` 파일에나 돌려서 출력 형태 확인
- Claude API 키 발급, tool-calling 최소 예제 1개 직접 실행
- `npm create vite@latest`로 React 프로젝트 생성, 기본 페이지 렌더링 확인
- GitHub 저장소 생성, README 스켈레톤 커밋, 폴더 구조 세팅

### 겪었던 이슈들

**1. API 키 결제 시 세금 계산 무한 대기 → 결제 버튼 비활성화**
크롬에서 청구지 주소(인천)를 입력한 뒤 결제 버튼이 끝까지 비활성화된 채 넘어가지 않았다. 콘솔에 COOP 에러랑 `privacy-consents` 401이 같이 떠서, Stripe 쪽 세금 계산 API가 특정 청구 주소에서 응답을 안 하는 문제로 추정된다(유사 사례가 GitHub 이슈에도 몇 건 보이긴 했지만 100% 확정은 아님). 결제 폼의 "청구지 주소와 실제 주소가 다름" 체크박스를 활용해서, 청구지는 세금 계산이 걸리지 않는 미국 델라웨어로, 실제 주소는 인천으로 입력해 결제를 완료했다. 근본 원인을 고친 게 아니라 우회한 것이라 찜찜하긴 한데, 일단 EPIC 0 진행에 막힘없이 넘어갈 수 있었다.

### 오늘 배운 것 / 느낀 점
- 결제/외부 서비스 연동에서 막히면 원인을 100% 규명하기보다, 일단 우회 경로가 있는지부터 찾는 게 실용적일 때가 있다는 걸 체감했다. 다만 "우회했다"와 "고쳤다"는 구분해서 기록해둬야 나중에 헷갈리지 않는다.
- 환경 세팅 하나하나(venv, radon, Claude API, Vite)는 개별로는 단순했는데, 다섯 개를 하루에 몰아서 하니 각각이 "왜 필요한지"를 잊지 않고 넘어가는 게 생각보다 신경 쓰였다.

### 다음에 할 일
- EPIC 1 Task 1-1: 스캐너 핵심 로직 (파일 순회, 복잡도 계산, 테스트 파일 확인)

---

## 2026-07-06 · EPIC 1 Task 1-1 (스캐너 핵심 로직)

### 오늘 한 일
- 대상 저장소 `.py` 파일 순회 스크립트 (`walker.py`) — `os.walk` 기반, `venv`/`__pycache__`/`node_modules` 등 제외
- radon 기반 함수별 순환 복잡도 계산 (`complexity.py`)
- 테스트 파일 존재 여부 확인 (`test_check.py`) — 파일명 패턴 매칭 방식
- `_manual_test.py`로 세 함수를 직접 조합해서 로컬에서 돌려봄

### 겪었던 이슈들

**1. `ModuleNotFoundError` — 실행 위치에 따라 import가 깨짐**
`scanner` 폴더 안에서 `from walker import ...`처럼 상대 파일명으로 import했는데, `backend` 폴더 등 다른 위치에서 실행하면 곧바로 못 찾는다는 걸 알게 됐다. 파이썬은 "지금 서 있는 폴더" 기준으로 모듈을 찾는다는 걸 직접 겪고서야 확실히 이해함. 지금은 일단 `scanner` 폴더 안에서만 실행하는 걸로 넘어갔고, DB 붙이는 Task 1-2에서 이 구조를 제대로 정리해야 한다는 걸 미리 적어둠.

**2. 복잡도 임계값 검증 — 확인용 더미 함수가 필요했다**
실제 코드만 돌려보면 우리가 짠 함수들은 다 복잡도가 낮아서(1~2), "임계값 넘으면 진짜로 걸리는지"를 확인할 방법이 없었다. `if`문을 억지로 9개 겹쳐서 복잡도 10짜리 더미 함수(`_dummy_complex.py`)를 만들어 확인했는데, 이렇게 "일부러 극단적인 케이스를 만들어서 경계값을 찔러보는" 검증 방식을 처음 제대로 써봄.

**3. `has_test_file`의 한계를 스스로 인정하고 넘어간 지점**
파일명 매칭 방식으로 "테스트 파일이 존재하는가"만 확인하고, 그 안에서 실제로 해당 함수를 테스트하는지는 확인하지 않기로 했다. 처음엔 "이게 대충 만든 거 아닌가" 싶었는데, 정확히 어떤 질문에 답하고 어떤 질문엔 답하지 않는지를 명확히 알고 선택한 거라 괜찮다고 판단. 백로그에 한계를 명시적으로 적어둠.

### 오늘 배운 것 / 느낀 점
- 순환 복잡도라는 개념이 추상적으로만 알던 것에서, `if`/`for`가 늘어날 때마다 숫자가 실제로 어떻게 오르는지 손으로 계산해서 맞춰보니 확실히 체감됐다.
- "코드가 에러 없이 돌아간다"와 "의도한 로직이 실제로 검증됐다"는 다른 얘기라는 걸 되새김. 정상 케이스만 돌려보고 넘어갔으면 임계값 판정이 진짜 작동하는지 몰랐을 뻔함 — 일부러 극단적 케이스(더미 함수, 빈 테스트 파일)를 만들어서 확인하는 습관을 들여야겠다.

### 다음에 할 일
- Task 1-2: 판정 로직(복잡도≥임계값 AND 테스트없음) + DB 저장

---

## 2026-07-21 · EPIC 1 Task 1-2 (판정 로직 + DB 저장) — EPIC 1 완료

### 오늘 한 일
- SQLAlchemy 엔진/세션 설정 (`database.py`)
- `Scan`, `Finding` 테이블 정의 (`models.py`)
- 판정 로직 + DB 저장 (`run_scan.py`) — 복잡도≥10 AND 테스트없음 → `Finding` 생성
- `backend`를 정식 파이썬 패키지로 승격 (`__init__.py` 추가, 모든 내부 import를 절대경로로 통일)
- 조회용 스크립트(`_check_db.py`)로 실제 DB에 값이 정확히 저장됐는지 확인
- `_dummy_complex.py`로 판정 로직이 실제로 걸러내는지까지 재검증 완료

### 겪었던 이슈들

**1. import 구조를 패키지 방식으로 다시 정리**
지난 Task 1-1에서 미뤄뒀던 문제. `backend`, `backend/scanner`에 `__init__.py`를 추가해서 정식 패키지로 만들고, 모든 내부 import를 `from backend.scanner.walker import ...`처럼 절대경로로 통일했다. 실행도 `scanner` 폴더 안에 들어가서 하는 대신 최상위 폴더에서 `python -m backend.scanner.run_scan`으로 고정. 이렇게 해두니 나중에 FastAPI가 이 모듈들을 가져다 쓸 때도 안 꼬일 구조가 됐다는 게 체감됨.

**2. `DetachedInstanceError` — 처음 만나는 세션 생명주기 문제**
`db.commit()` → `db.close()`한 다음 `scan.id`를 다시 읽으려다 에러가 났다. "커밋하고 나면 세션이 객체 값을 일단 초기화해두고, 다시 필요하면 DB에 재조회하려 하는데, 세션이 이미 닫혀서 재조회할 방법이 없다"는 걸 알게 됨. 필요한 값은 세션이 살아있을 때 미리 일반 변수로 복사해두는 습관을 이번에 처음 배웠다. SQLAlchemy 쓰면서 다들 한 번씩 걸린다는 흔한 함정이라고 해서 조금 안심되기도 했다.

**3. 오타 하나(`flie_path`)가 두 번 걸림**
`models.py`에서 `file_path`를 `flie_path`로 오타 내서 `TypeError`가 났고, 고친 다음에도 조회 스크립트(`_check_db.py`)에 같은 오타가 그대로 남아있어서 `AttributeError`가 또 났다. 한 군데만 고치면 끝이라고 생각했는데, 오타가 이미 다른 파일에 복사돼서 퍼져있을 수 있다는 걸 겪고 나서 "고칠 때 그 이름을 참조하는 다른 곳도 같이 찾아봐야 한다"는 걸 배움.

### 오늘 배운 것 / 느낀 점
- 이번 세션에서 겪은 에러 네 개(import 경로, 세션 detach, 오타, 오타 전파)가 전부 종류가 달랐는데, 에러 메시지 맨 아래 줄을 정확히 읽고 어느 파일 몇 번째 줄인지부터 짚는 순서가 확실히 빨라지고 있다는 걸 느꼈다.
- "결과가 0개로 나왔다"는 것 자체가 정상인지 비정상인지는, 입력 데이터가 어떤 상태인지를 같이 봐야 판단할 수 있다는 걸 다시 확인함 (findings 0개가 "판정 로직 고장"이 아니라 "위험한 코드가 실제로 없어서"였던 것처럼).
- 커밋 메시지 형식(타입은 영어, 본문은 한국어 + 판단 근거를 화살표로 표기)을 이번에 확정해서, 앞으로 세션마다 일관되게 쓰기로 함.

### 다음에 할 일
- EPIC 2: `orchestrator/tools.py`의 `assess_risk` tool 스키마부터 시작
- EPIC 2 들어가기 전에 확정할 것: confidence 높은데도(예: 0.85) 모델이 스스로 `escalate_human`을 선택하는 경로를 허용할지 여부 (WORKFLOW.md EPIC 2 섹션의 "결정 필요" 항목 참고)

---

## 2026-07-22 · EPIC 2 Task 2-1 (assess_risk 연동) — EPIC 2 완료

### 오늘 한 일
- EPIC 2 진입 전 "결정 필요" 항목 확정: confidence 높아도 모델이 스스로 escalate_human 선택하는 경로 허용 (스키마 제한 안 함), 대신 `escalation_source` 컬럼으로 model_choice/confidence_override 구분 기록하기로 결론
- `assess_risk` tool 스키마 정의 (`orchestrator/tools.py`)
- Claude API 호출 래퍼 (`orchestrator/llm_client.py`)
- `.env` + `python-dotenv`로 API 키 관리 방식 전환 (Windows 시스템 환경변수 대신)
- confidence<0.6 강제 override 로직 (`finalize_action()`) — 가짜 데이터 4가지 케이스(confidence 높/낮 × 모델이 escalate 선택함/안 함)로 단위 테스트 검증
- `llm_calls`, `actions` 테이블 스키마 추가 (`models.py`)
- Claude Haiku 4.5 가격(공식 발표 기준 $1/$5 per M tokens)으로 토큰→비용 계산 (`calculate_cost()`)
- `llm_calls`/`actions` row 저장 함수 (`persistence.py`의 `save_action()`)
- `run_pipeline.py` — status='found'인 Finding을 자동 순회하며 판단→저장, 처리 후 status 갱신
- 실제 파이프라인 실행으로 end-to-end 검증 완료 (스캔→판단→DB저장 전체 흐름)

### 겪었던 이슈들

**1. API 인증 에러 — `anthropic.Anthropic()`이 키를 못 찾음**
`TypeError: Could not resolve authentication method` 발생. 원인은 API 키를 이전 세션에서만 터미널에 임시로 넣어뒀었고, 새 터미널 창엔 그 값이 안 남아있었던 것. `.env` 파일 + `python-dotenv`의 `load_dotenv()`로 영구 등록하는 방식으로 전환. `.env`는 반드시 `.gitignore`에 먼저 등록한 뒤에 만들어야 실수로 커밋되는 걸 막을 수 있다는 걸 순서로 체감함.

**2. 코드 저장 안 하고 실행 — `NameError: name 'load_dotenv' is not defined`**
`load_dotenv()` 코드를 추가한 직후 저장(Ctrl+S) 없이 바로 실행해서, 파이썬이 디스크에 저장된 예전 버전을 읽어 실행한 게 원인. 저장하고 재실행하니 해결. "코드 수정 → 저장 → 실행" 순서를 습관으로 붙여야겠다고 느낌.

**3. `codesentry.db`가 이미 Git 추적 중이었던 것 뒤늦게 발견**
`.gitignore`에 `codesentry.db`를 추가했는데도 GitHub Desktop에 계속 "Modified"로 떴음. `.gitignore`는 "새로 추적을 시작하는 걸 막는" 규칙이지 "이미 추적 중인 걸 잊게" 하는 게 아니라는 걸 알게 됨. `git rm --cached codesentry.db`로 추적만 해제(로컬 파일은 유지)하고서야 해결.

**4. 임시 검증용 파일(`_check_tables.py`, `_test_assess_risk.py`)이 실수로 커밋에 포함됨**
`.gitignore`에 미리 등록 안 한 상태로 커밋해버려서, 나중에 뒤늦게 `.gitignore` 추가 + `git rm --cached`로 별도 정리 커밋을 만들어야 했음. `_list_findings.py`는 애초에 커밋된 적이 없어서 `.gitignore` 추가만으로 충분했던 것과 대비되는 케이스 — "이미 추적 중이었는가"에 따라 필요한 조치가 다르다는 걸 두 파일을 비교하며 확실히 이해함.

**5. `python -m` 실행 시 모듈 경로에 `.py` 확장자를 붙인 실수**
`python -m backend._test_assess_risk.py`처럼 실행해서 `ModuleNotFoundError` 발생. `-m` 방식은 점(`.`)으로 구분하는 모듈 경로 표기이지 실제 파일 경로가 아니라는 걸 다시 확인. 에러 메시지가 정확한 대안(`backend._test_assess_risk`)까지 알려줘서 바로 해결.

### 오늘 배운 것 / 느낀 점
- confidence라는 숫자 하나가 액션 종류에 따라 "가리키는 대상"이 다를 수 있다는 걸 실제 관찰(높은 confidence로 escalate 선택)과 설계 토론을 거쳐 이해하게 됨 — 겉보기엔 이상해 보이는 모델 행동이 실은 설계 의도와 정확히 맞아떨어지는 경우가 있다는 걸 체감.
- `git rm --cached`의 `--cached` 옵션 하나 차이로 "추적 해제"와 "실제 파일 삭제"가 완전히 갈린다는 걸 정확히 이해하고 넘어감.
- EPIC 1 때 배운 `DetachedInstanceError` 회피 패턴(세션 살아있을 때 값 미리 변수로 복사)을 이번 `persistence.py`, `run_pipeline.py`에서도 그대로 재적용 — 한 번 배운 교훈이 다음 코드에 자연스럽게 스며드는 걸 느낌.

### 다음에 할 일
- EPIC 3: `generate_test`, `propose_fix` tool 구현부터 시작
- EPIC 3 진입 전 확인할 것: 샌드박스 실행기(subprocess+resource)와 재시도 로직(`attempt_number`) 연결 방식

---
