# backend/orchestrator/approval_manager.py

from backend.database import SessionLocal
from backend.models import Approval
import shutil
import os
from datetime import datetime
import patch as patch_lib
from backend.models import Approval, Action, Finding
import re


def create_approval(action_id: int) -> int:
    """
    propose_fix 결과 하나를 결재함(approvals)에 '대기' 상태로 올린다.
    비유: 문서를 결재함에 넣는 행위 자체 — 아직 아무도 도장을 찍지 않은 상태
    반환값: 생성된 approval의 id 
    """
    db = SessionLocal()
    
    approval = Approval(
        action_id=action_id,
        status="pending",
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    
    approval_id = approval.id  # DetachedInstanceError 방지 — 닫기 전에 미리 복사
    db.close()
    
    return approval_id


def _normalize_diff_paths(diff_content: str, real_path: str) -> str:
    """
    LLM이 생성한 diff의 --- a/..., +++ b/... 헤더를 실제 파일 경로로 덮어쓴다.
    비유: 택배 송장에 대충 적힌 주소를, 실제 배송지 주소로 다시 써 붙이는 것.
    LLM이 파일 경로를 정확히 맟춰서 diff를 만든다는 보장이 없어서 필요한 안전장치.
    """
    lines = diff_content.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith("--- "):
            lines[i] = f"--- a/{real_path}\n"
        elif line.startswith("+++ "):
            lines[i] = f"+++ b/{real_path}\n"
    return "".join(lines)


def _verify_diff_matches_file(file_path: str, diff_content: str) -> bool:
    """
    diff의 context/삭제 라인이 실제 파일 내용과 정말 일치하는지 직접 재확인한다.
    비유: 택배기사의 "배송 완료" 보고를 그대로 믿지 않고, CCTV로 한번 더 확인하는 것.
    patch 라이브러리가 컨텍스트 불일치를 항상 걸러주지 않는다는 걸 실제 테스트로 확인함.
    """
    with open(file_path, encoding="utf-8") as f:
        actual_lines = f.readlines()
        
    lines = diff_content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("@@"):
            m = re.match(r"@@ -(\d+),?(\d*) \+\d+,?\d* @@", line)
            if not m:
                return False
            old_start = int(m.group(1))
            
            expected = []
            j = i + 1
            while j < len(lines) and not lines[j].startswith("@@"):
                if lines[j].startswith(" ") or lines[j].startswith("-"):
                    expected.append(lines[j][1:])
                j += 1
                
            actual_slice = [
                l.rstrip("\n") for l in actual_lines[old_start - 1 : old_start - 1 + len(expected)]
            ]
            if actual_slice != expected:
                return False  # ← 여기서 불일치 잡힘
            
            i = j
        else:
            i += 1
    return True


def _normalize_diff_line_numbers(diff_content: str, line_offset: int) -> str:
    """
    LLM에게 넘겨준 코드 조각은 항상 1번째 줄부터 시작하는 것처럼 보이지만,
    실제 파일에서는 line_offset+1번째 줄부터 시작한다.
    diff의 @@ 헤더에 적힌 줄 번호를 실제 파일 기준으로 밀어서 맞춰준다.
    비유: 책 4페이지부터 복사해서 준 걸 친구가 "1페이지"라고 표시했다면,
    실제 책 기준으로 다시 "4페이지"로 계산해서 고쳐주는 것.
    """
    def _shift(match):
        old_start = int(match.group(1)) + line_offset
        old_count = match.group(2)
        new_start = int(match.group(3)) + line_offset
        new_count = match.group(4)
        return f"@@ -{old_start},{old_count} +{new_start},{new_count} @@"

    return re.sub(r"@@ -(\d+),(\d+) \+(\d+),(\d+) @@", _shift, diff_content)


def _recompute_diff_counts(diff_content: str) -> str:
    """
    LLM이 @@ 헤더에 적은 줄 개수가 실제 본문과 다를 수 있어(긴 diff일수록 세다가 실수하기 쉬움),
    본문을 직접 세어서 old_count/new_count를 정확한 값으로 다시 써준다.
    비유: 택배 송장의 "3개 들었음" 표시를 믿지 않고, 실제 박스 안을 세어서 정확한 개수로 다시 써 붙이는 것.
    """
    lines = diff_content.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"@@ -(\d+),\d+ \+(\d+),\d+ @@", line)
        if m:
            old_start = int(m.group(1))
            new_start = int(m.group(2))
            j = i + 1
            old_count = 0
            new_count = 0
            while j < len(lines) and not lines[j].startswith("@@"):
                body_line = lines[j]
                if body_line.startswith(" "):
                    old_count += 1
                    new_count += 1
                elif body_line.startswith("-"):
                    old_count += 1
                elif body_line.startswith("+"):
                    new_count += 1
                j += 1
            out.append(f"@@ -{old_start},{old_count} +{new_start},{new_count} @@\n")
            out.extend(lines[i + 1 : j])
            i = j
        else:
            out.append(line)
            i += 1
    return "".join(out)             


def apply_patch(file_path: str, diff_content: str, line_offset: int = 0) -> dict:
    """
    diff_content(unified diff)를 file_path에 실제로 적용한다.
    적용 전 원본을 백업해두고, 실패하면 백업본으로 되돌린다.
    비유: 수술 전에 혈액형을 확보해두는 것 — 잘못되면 바로 원상복구할 수 있게 대비해두는 것.
    반환값: {"success": bool, "error": str | None}
    """
    backup_path = file_path + ".bak"
    shutil.copy2(file_path, backup_path)  # 원본 백업
    
    try:
        diff_content = _normalize_diff_line_numbers(diff_content, line_offset)  # ← 이 줄 추가 (맨 먼저)
        
        if not _verify_diff_matches_file(file_path,diff_content):
            raise ValueError("diff 컨텍스트 실제 파일 내용과 다름 — patch 라이브러리 결과를 신뢰할 수 없어 직접 검증에서 막음")
        
        diff_content = _normalize_diff_paths(diff_content, file_path)   # ← 이 줄 추가
        diff_content = _recompute_diff_counts(diff_content)   # ← 이 줄 추가
        patch_set = patch_lib.fromstring(diff_content.encode("utf-8"))
        if not patch_set:
            raise ValueError("diff 파싱 실패 — LLM이 만든 diff 형식이 올바르지 않음")
        
        applied = patch_set.apply(root=".")
        if not applied:
            raise ValueError("patch 적용 실패 — 대상 파일 내용이 diff와 안 맞음(충돌 가능성)")
        
        return {"success": True, "error": None}

    except Exception as e:
        # 실패했으니 백업본으로 원상복구
        shutil.copy2(backup_path, file_path)
        return {"success": False, "error": str(e)}
    
    finally:
        # 성공/실패 상관없이 백업 파일은 정리 (시스크에 흔적 남기지 않기 — EPIC 3 원칙 재사용)
        os.remove(backup_path)
        
        
def approve_approval(approval_id: int) -> dict:
    """
    결재함의 pending 문서 하나를 승인 처리한다.
    승인 = 자동으로 patch까지 적용하는 것 (EPIC 4 진입 전 확정한 설계.)
    반환값: {"status", "applied_status", "error"}
    """
    db = SessionLocal()
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    if not approval:
        db.close()
        raise ValueError(f"approval id={approval_id}를 찾을 수 없음")
    if approval.status != "pending":
        db.close()
        raise ValueError(f"이미 처리된 approval입니다 (status={approval.status})")
    
    action = db.query(Action).filter(Action.id == approval.action_id).first()
    finding = db.query(Finding).filter(Finding.id == action.finding_id).first()
    
    line_offset = finding.line_number - 1   # ← 이 줄 추가
    result = apply_patch(finding.file_path, action.content, line_offset)  # ← line_offset 인자 추가
    
    approval.status = "approved"
    approval.applied_status = "success" if result["success"] else "failed"
    approval.error_message = result["error"]
    approval.resolved_at = datetime.utcnow()
    
    finding.status = "fix_applied" if result["success"] else "fix_apply_failed"
    
    db.commit()
    
    response = {
        "status": "approved",
        "applied_status": approval.applied_status,
        "error": approval.error_message,
    }
    db.close()
    return response


def reject_approval(approval_id: int) -> dict:
    """
    결재함의 pending 문서를 반려 처리한다. patch는 절대 적용하지 않는다.
    비유: 서류함의 '반려' 도장만 찍고 끝 — 실제 세상(파일)엔 아무 영향 없음.
    """
    db = SessionLocal()
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    if not approval:
        db.close()
        raise ValueError(f"approval id={approval_id}를 찾을 수 없음")
    if approval.status != "pending":
        db.close()
        raise ValueError(f"이미 처리된 approval입니다 (status={approval.status})")
    
    action = db.query(Action).filter(Action.id == approval.action_id).first()
    finding = db.query(Finding).filter(Finding.id == action.finding_id).first()
    
    approval.status = "rejected"
    approval.resolved_at = datetime.utcnow()
    finding.status = "fix_rejected"
    
    db.commit()
    db.close()
    return {"status": "rejected"}                       
        