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

## 2026-07-22 · EPIC 3 Task 3-1/3-2 (생성 tool + 샌드박스 실행기) — EPIC 3 완료

### 오늘 한 일
- EPIC 3 진입 전 "결정 필요" 항목 확정: 재시도는 샌드박스 재실행이 아니라 generate_test 재호출(실패 로그 피드백 포함)로, 생성→샌드박스→재시도 로직은 `run_pipeline.py`가 아닌 신규 모듈 `generation_manager.py`로 분리하기로 결론
- `GENERATE_TEST_TOOL`, `PROPOSE_FIX_TOOL` 스키마 정의 (`orchestrator/tools.py`)
- `generate_test()`, `propose_fix()` API 호출 함수 (`orchestrator/llm_client.py`)
- `sandbox/executor.py` — subprocess+resource 기반 격리 실행기 (Windows에서 resource 미지원 확인 후 조건부 처리)
- `Finding`에 `line_number`/`end_line_number`, `Action`에 `content`/`detail`/`execution_status` 컬럼 추가 (`models.py`)
- `_read_function_source()` 헬퍼 — line_number 기준으로 파일에서 함수 소스만 슬라이싱
- `generation_manager.py`의 `process_write_test()` — 재시도 루프(최대 2회, 실패 로그 피드백) + `run_write_test_phase()`로 자동 순회
- `persistence.py`에 `save_generation_action()` 추가 — 생성 결과 전용 저장 함수
- 더미 함수(`_dummy_target.py`)로 실제 findings 만들어서 판단→생성→샌드박스 검증까지 end-to-end 확인 완료

### 겪었던 이슈들

**1. function_code를 가져올 방법이 애초에 없었다**
`generate_test()`가 함수 소스코드를 요구하는데, `Finding` 테이블엔 `function_name`만 있고 정확한 위치 정보가 없었다. 원인을 파보니 `complexity.py`가 radon에게서 `block.endline`을 이미 받아오고 있었는데 그걸 그냥 버리고 있었던 것 — "새 기능 추가"가 아니라 "누락 복구"에 가까웠다. `line_number`/`end_line_number`를 저장하도록 스캐너 쪽까지 거슬러 올라가서 고쳤다.

**2. `resource` 모듈이 Windows에서 아예 import가 안 됨**
샌드박스 실행기에 메모리 제한을 걸려고 `resource.setrlimit`을 썼는데, 이 모듈이 POSIX(Linux/Mac) 전용이라 Windows 개발 환경에서 `import` 자체가 실패한다는 걸 뒤늦게 알게 됨. `platform.system()`으로 분기해서 POSIX에서만 메모리 제한을 걸고, Windows에서는 timeout만 적용하는 것으로 우아하게 성능 저하시키는 방식을 택했다. 완벽한 격리는 아니지만, 애초에 subprocess+resource 자체가 "타협"으로 인정하고 시작한 설계라 이 한계 하나 추가되는 것도 같은 맥락으로 문서화하기로 함.

**3. `max_tokens` 한도에 걸려 응답이 잘리면서 `KeyError` 발생**
`generate_test()` 호출 결과에서 `test_code` 키가 없다는 `KeyError`가 났다. 진단용 스크립트로 실제 응답을 찍어보니 `test_code`, `covered_cases` 키 자체는 정상적으로 존재해서 처음엔 원인을 못 잡았는데, 생성된 테스트 코드가 굉장히 길다는 걸 보고 `max_tokens=1500`이 너무 작았을 가능성을 의심함. `1500 → 3000`으로 올리고, `stop_reason == "max_tokens"`를 명시적으로 체크해서 응답이 잘렸을 때 바로 알 수 있게 방어 코드를 추가했다. 재시도 루프 안에서 이 예외가 터지면 전체 프로세스가 죽어버리는 문제도 같이 발견해서, `try/except`로 감싸 "생성 자체 실패"도 하나의 실패 attempt로 흡수하도록 고침.

**4. 검증용 더미 함수의 복잡도가 임계값에 못 미쳤던 것 두 번 반복**
처음 만든 더미 함수(`classify_score`, if/elif 6분기)의 실제 순환 복잡도가 7이라 임계값(10)을 못 넘어서 findings가 0건으로 나왔다. "연결이 안 된 건가" 의심했었는데, radon으로 직접 복잡도를 미리 계산해보고 나서야 원인이 스캐너 연결 문제가 아니라 그냥 더미 함수 설계 자체의 문제였다는 걸 확인함. 이후로는 코드를 주기 전에 radon으로 복잡도를 미리 계산해보고 확실히 임계값을 넘는 걸 확인하는 습관을 들임.

### 오늘 배운 것 / 느낀 점
- "에러 없이 실행됨"과 "의도한 대로 동작함"이 다르다는 걸 이번에도 확인함 — `previous_failure` 인자를 실수로 안 넘겼을 때 에러는 전혀 안 났고, 결과만 봐서는 재시도가 "정상적으로" 실패한 것처럼 보였다. attempt 1과 attempt 2의 `covered_cases` 내용이 실질적으로 다른지까지 비교해봐야 재시도 로직이 진짜 작동하는지 확인할 수 있었다.
- 검증 스크립트(`_check_*.py`)를 매번 짧게 만들어서 "이 함수 하나만" 떼어 확인하는 방식이, 전체 파이프라인을 통째로 돌려보고 원인 추적하는 것보다 훨씬 빠르게 문제를 좁혀준다는 걸 여러 번 체감함.
- Task 3-1(생성 tool)과 Task 3-2(샌드박스)가 서로 의존관계라 커밋을 하나로 묶었는데, 이런 예외가 생길 때 "왜 원칙에서 벗어났는지"를 커밋 메시지에 남겨두는 게 나중에 히스토리 볼 때 헷갈리지 않게 해준다는 걸 확인함.

### 다음에 할 일
- EPIC 4: 승인 게이트 — `approvals` 테이블 설계, `process_propose_fix()` 구현, 승인/거부 API
- EPIC 4 진입 전 확인할 것: propose_fix 결과(diff)를 실제로 어떻게 "적용"할지 — diff만 보여주고 사람이 수동 적용할지, 승인 시 자동으로 파일에 patch 적용할지 (설계문서에 명시 안 된 부분)

---

## 2026-07-23 · EPIC 4 Task 4-1/4-2 (승인 게이트) — EPIC 4 완료

### 오늘 한 일
- EPIC 4 진입 전 "결정 필요" 항목 확정: 승인 시 diff만 표시가 아니라 자동으로 patch까지 적용하는 것으로 결론 (승인 게이트가 실제 행동을 트리거해야 의미가 있다는 논리, 대신 백업+롤백 필수 조건)
- `models.py`에 `Approval` 테이블 추가
- `orchestrator/approval_manager.py` 신규 — `create_approval()`, `approve_approval()`, `reject_approval()`, `apply_patch()`
- `generation_manager.py`에 `process_propose_fix()`, `run_propose_fix_phase()` 추가
- `routers/approvals.py` 신규 — 프로젝트 첫 FastAPI 라우터, `PATCH /approvals/{id}`
- `patch`(PyPI) 라이브러리 도입 — unified diff를 순수 파이썬으로 적용 (git 저장소 여부·OS 무관하게 동작)
- Swagger(`/docs`)로 실제 승인 API 호출 → patch 적용 성공/충돌 롤백 양쪽 케이스 end-to-end 검증

### 겪었던 이슈들

**1. `patch` 라이브러리가 diff 헤더의 파일 경로를 그대로 신뢰함**
LLM이 `propose_fix`로 만든 diff의 `--- a/...` 헤더가 실제 파일 경로가 아니라 함수 이름 기준의 임의 경로였다(`a/analyze_file`처럼). `apply_patch()`에 넘긴 `file_path`는 백업 뜰 때만 쓰이고, 실제 patch 적용 대상은 diff 헤더가 결정한다는 걸 알게 됨. `_normalize_diff_paths()`로 헤더를 실제 경로로 강제 치환해서 해결.

**2. `patch` 라이브러리가 컨텍스트 불일치를 걸러주지 않음**
일부러 실제 파일과 안 맞는 diff(존재하지 않는 줄을 지우려는 diff)를 만들어서 테스트했더니, 라이브러리가 실패 처리 없이 `applied=True`로 조용히 잘못된 위치를 덮어써버림. 줄 번호만 믿고 컨텍스트 내용은 검증하지 않는 라이브러리라는 걸 확인. `_verify_diff_matches_file()`로 적용 전 직접 재검증하는 이중 안전장치를 추가해서 해결 — 라이브러리 하나만 믿지 않고 우리 코드로 한 번 더 확인하는 게 왜 필요한지 실전으로 체감한 케이스.

**3. diff의 줄 번호가 "코드 조각 기준"이지 "실제 파일 기준"이 아니었음**
`_read_function_source()`로 함수만 잘라서 LLM에게 넘기다 보니, LLM이 만든 diff는 항상 "1번째 줄부터 시작"하는 것처럼 헤더를 씀. 근데 실제 파일에서 그 함수는 4번째 줄부터 시작하는 식이라, 검증 로직이 엉뚱한 위치(진짜 1번째 줄)를 보고 불일치라고 판단해버림. `_normalize_diff_line_numbers()`로 `finding.line_number` 기준 offset을 계산해서 diff 헤더를 실제 위치로 밀어서 해결.

**4. LLM이 `@@` 헤더에 적은 줄 개수가 실제 본문과 다름**
diff가 길어질수록(if문 여러 개 추가) LLM이 헤더의 `old_count`/`new_count`를 직접 세다가 실수함. 라이브러리 디버그 로그(`WARNING:patch:extra lines for hunk`)로 원인 확인. `_recompute_diff_counts()`로 헤더 숫자를 본문 기준으로 재계산해서 해결. 이걸로 diff 처리 안전장치가 경로/줄번호/개수 세 가지 전부 "LLM 출력을 있는 그대로 믿지 않고 코드로 강제 보정"하는 동일한 원칙으로 통일됨.

**5. 자잘한 오타·누락 여러 건**
`__tablename__: "approvals"`(`:` 대신 `=`이어야 함), `ForeignKey("action.id")`(실제 테이블명은 `actions`), `save_generation_action()` 호출 시 `attempt_number` 누락, `.filter(...),all()`(쉼표가 점 자리에), `main.py`에서 라우터 import만 하고 `include_router()` 누락, `requirements.txt`가 PowerShell 리다이렉션(`>`) 때문에 UTF-16으로 저장돼있던 것 — 전부 실제로 재현해서 하나씩 확인 후 수정. 특히 `apply_patch()`에 `line_offset` 파라미터를 추가하면서 예전 호출 줄을 지우는 걸 깜빡해 함수가 두 번 호출되는 실수도 있었음(나중 호출이 결과를 덮어써서 조용히 무효화됨).

### 오늘 배운 것 / 느낀 점
- "승인 게이트"라는 개념 자체를 실제로 구현해보면서, 승인이라는 행위가 단순히 상태값 하나 바꾸는 게 아니라 "실제 행동을 트리거하는 관문"으로 설계돼야 의미가 있다는 걸 체감함. 이번 결정(자동 적용)과 그 반대(수동 적용)를 놓고 고민했던 과정 자체가 human-in-the-loop 설계에서 뭘 사람에게 맡기고 뭘 시스템이 자동화할지 가르는 기준을 세우는 연습이었음.
- 외부 라이브러리(`patch`)를 가져다 쓸 때 "라이브러리가 실패를 항상 정확히 보고해줄 것"이라는 가정 자체가 틀릴 수 있다는 걸 직접 부딪혀서 배움. 일부러 실패 케이스(충돌 diff)를 만들어서 확인하지 않았으면 이 문제를 계속 몰랐을 뻔했음 — EPIC 1 때 배운 "정상 케이스만 돌려보고 넘어가지 않기" 습관이 이번에도 그대로 통했음.
- 버그를 하나 고치면 그 다음 층위의 버그가 드러나는 경험을 이번에 특히 많이 함(경로 → 컨텍스트 → 줄번호 → 개수 순서로 4단계). 매번 "이번엔 진짜 끝났겠지"라는 성급한 판단 대신 실제로 재현 테스트를 계속 돌려본 게 맞는 접근이었다고 생각함.

### 다음에 할 일
- EPIC 5: 백엔드 API 완성 — `GET /findings`(상태별 필터), `GET /findings/{id}`(상세), `POST /scans`(스캔 트리거), `WS /ws/scans/{id}`(실시간 진행 상황)
- EPIC 5 진입 전 확인할 것: 딱히 없음 — routers 폴더 구조와 각 엔드포인트 스펙은 WORKFLOW.md에 이미 명시돼있어 바로 시작 가능

---
