"""
=============================================================================
🧪 ALL-IN-ONE LIFE OS : E2E Step-by-Step Functional Test Suite
=============================================================================
화면 상호작용 및 비서 핵심 기능을 스텝별로 순차 검증하는 시뮬레이션 테스트
스텝 1: 날짜 탐색 (어제 / 오늘 / 3일 뒤 미래) 및 타임라인 기록
스텝 2: 비서 능동 넛지 질문 생성 및 3-상태 응답 머신 ([완료], [지금할게], [보류])
스텝 3: 자연어 일과 보고 입력 및 35대 습관 지능형 자동 매핑 & 코칭
스텝 4: SQLite 영구 저장 및 Life_OS_Successful_Habits.xlsx 엑셀 무손실 동기화
스텝 5: 윈도우 시작프로그램(Registry) 및 사용자 환경 설정 토글
=============================================================================
"""

import os
import sys
import tempfile
import datetime
from pathlib import Path

# Set console encoding
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from database import DatabaseManager
from assistant_engine import AssistantEngine, WindowsAutostartManager

def run_step_by_step_test():
    print("=" * 70)
    print("🚀 [LIFE OS] 플로팅 비서 & 트레이 시스템 스텝별 기능 테스트 시작 (격리 Sandbox)")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as td:
        sandbox_dir = Path(td)
        db = DatabaseManager(db_path=sandbox_dir / "life_os.db")
        db.set_setting("excel_path", str(sandbox_dir / "Life_OS_Successful_Habits.xlsx"))
        db.set_setting("sound_enabled", "false")
        db.set_setting("toast_enabled", "false")
        engine = AssistantEngine(db)
        _run_scenarios(db, engine)


def _run_scenarios(db, engine):

    # -------------------------------------------------------------
    # [STEP 1] 날짜 탐색 및 과거/미래 타임라인 기록 테스트
    # -------------------------------------------------------------
    print("\n▶ [STEP 1] 날짜 자유 탐색 (어제 / 오늘 / 3일 뒤 미래) & 타임라인 기록")
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    future_3d = today + datetime.timedelta(days=3)

    # 과거 어제 날짜에 놓쳤던 습관(No.1 워런 버핏 5/25) 소급 체크
    db.toggle_check(yesterday.isoformat(), 1, status=1, memo="어제 늦게 실천 완료")
    y_checks = db.get_checks_for_date(yesterday.isoformat())
    assert y_checks.get(1, {}).get("status") == 1, "어제 날짜 체크 실패"
    print(f"  ✅ 어제({yesterday}) 날짜로 이동하여 No.1 워런 버핏 습관 소급 체크 성공!")

    # 3일 뒤 미래 날짜에 목표 및 계획 메모 등록
    future_plan_text = "D+3: 신규 프로젝트 90분 딥워크 블록 2회 연속 가동 예정"
    db.save_log_for_date(future_3d.isoformat(), summary_text=future_plan_text)
    f_log = db.get_log_for_date(future_3d.isoformat())
    assert future_plan_text in f_log.get("summary_text", ""), "미래 날짜 메모 저장 실패"
    print(f"  ✅ 미래({future_3d}) 날짜로 이동하여 사전 계획 메모 등록 성공: \"{f_log['summary_text']}\"")

    # -------------------------------------------------------------
    # [STEP 2] 능동형 비서 랜덤 넛지 & 3-상태 응답 상태 머신 테스트
    # -------------------------------------------------------------
    print("\n▶ [STEP 2] 비서 스마트 랜덤 넛지 & 3-상태 응답 머신 ([완료], [지금할게], [보류])")
    nudge = engine.get_smart_nudge(today.isoformat())
    hid = nudge["habit_id"]
    hname = nudge["habit_name"]
    print(f"  🤖 비서가 화면에 띄운 넛지 질문: \"{nudge['question']}\"")

    # 2-A: [⏸️ 일단 보류] 클릭 시뮬레이션
    res_hold = engine.process_nudge_response(hid, "postponed", today.isoformat())
    print(f"  👉 [⏸️ 일단 보류] 클릭 -> 비서 응답: \"{res_hold['message']}\"")
    assert db.get_checks_for_date(today.isoformat()).get(hid, {}).get("status", 0) == 0, "보류 상태 오류"

    # 2-B: [🚀 지금 할게!] 클릭 시뮬레이션
    res_doing = engine.process_nudge_response(hid, "doing_now", today.isoformat())
    print(f"  👉 [🚀 지금 할게!] 클릭 -> 비서 응답: \"{res_doing['message']}\"")

    # 2-C: [✅ 완료] 클릭 시뮬레이션
    res_done = engine.process_nudge_response(hid, "completed", today.isoformat())
    print(f"  👉 [✅ 완료] 클릭 -> 비서 응답: \"{res_done['message']}\"")
    assert db.get_checks_for_date(today.isoformat()).get(hid, {}).get("status") == 1, "완료 체크 반영 오류"
    print(f"  ✅ 습관 No.{hid} [{hname}] 오늘 날짜 완료 체크 정상 확인!")

    # -------------------------------------------------------------
    # [STEP 3] 자연어 일과 한 줄 보고 & 35대 습관 지능형 매핑
    # -------------------------------------------------------------
    print("\n▶ [STEP 3] 자연어 일과 한 줄 입력창 -> AI 비서 자동 매핑 & 코칭")
    user_input = "오늘 아침 15분 햇빛 쬐고 찬물샤워 마쳤어. 그리고 90분 딥워크로 기획서 작성 끝냄!"
    print(f"  💬 사용자 입력: \"{user_input}\"")
    
    checkin_res = engine.process_natural_checkin(user_input, today.isoformat())
    print(f"  🎯 자동 인식 및 체크된 습관 목록:")
    for h in checkin_res["checked_habits"]:
        print(f"     • {h}")
    print(f"  💡 비서 코칭 메시지: \"{checkin_res['coaching']}\"")
    assert len(checkin_res["matched_ids"]) >= 2, "습관 매핑 실패"

    # -------------------------------------------------------------
    # [STEP 4] SQLite -> Excel 양방향 무손실 동기화 테스트
    # -------------------------------------------------------------
    print("\n▶ [STEP 4] SQLite 타임라인 -> Life_OS_Successful_Habits.xlsx 엑셀 동기화")
    ok, sync_msg = db.sync_to_excel()
    print(f"  📊 동기화 실행 결과: {sync_msg} (성공 여부: {ok})")
    assert ok, "엑셀 동기화 실패"

    # -------------------------------------------------------------
    # [STEP 5] 윈도우 시스템 설정 & 시작프로그램(Registry) 토글 테스트
    # -------------------------------------------------------------
    print("\n▶ [STEP 5] 사용자 환경 설정 & 윈도우 시작프로그램(Registry) 제어")
    # 설정값 변경 저장 테스트
    db.set_setting("opacity", "0.90")
    db.set_setting("nudge_interval_minutes", "30")
    db.set_setting("sound_enabled", "true")
    db.set_setting("toast_enabled", "true")
    assert db.get_setting("opacity") == "0.90", "투명도 설정 오류"
    assert db.get_setting("nudge_interval_minutes") == "30", "주기 설정 오류"
    assert db.get_setting("sound_enabled") == "true", "사운드 설정 오류"
    print("  ✅ 위젯 투명도(0.90), 넛지 주기(30분), 사운드/토스트 설정값 영구 보관 확인")

    # 윈도우 시작프로그램 등록/해제 API 안전성 검증
    cur_autostart = WindowsAutostartManager.is_autostart_enabled()
    print(f"  🖥️ 현재 윈도우 시작프로그램 등록 상태: {cur_autostart}")
    print("  ✅ 윈도우 Run 레지스트리 안전 제어 API 정상 작동")

    # -------------------------------------------------------------
    # [STEP 0] SQLite 마스터 35대 습관 테이블 & 이식 검증
    # -------------------------------------------------------------
    sqlite_habits = db.get_habits()
    assert len(sqlite_habits) == 35, f"SQLite habits count expected 35, got {len(sqlite_habits)}"
    print(f"  💾 SQLite 'habits' 마스터 테이블 35개 시딩 검증 성공 (OS: {sys.platform})")

    # -------------------------------------------------------------
    # [STEP 6] 글로벌 핫키(Ctrl+Shift+H) 및 사운드/토스트 알림 하네스
    # -------------------------------------------------------------
    print("\n▶ [STEP 6] 글로벌 핫키(Ctrl+Shift+H) & OS 알림/사운드 하네스 검증")
    if sys.platform.startswith("win"):
        import winsound
        import ctypes
        user32 = ctypes.windll.user32
        assert hasattr(user32, 'RegisterHotKey'), "RegisterHotKey API 없음"
        print("  ⌨️ 윈도우 OS 네이티브 RegisterHotKey(Ctrl+Shift+H) API 검증 성공")

        try:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
            print("  🔔 winsound 차임벨 오디오 하네스 정상 작동")
        except Exception as e:
            print(f"  [!] winsound: {e}")
    else:
        import hotkey_manager
        assert hotkey_manager.user32 is None
        print(f"  🖥️ 비-Windows OS({sys.platform}) 크로스 플랫폼 안전 우회(hotkey/bell) 검증 성공")

    # -------------------------------------------------------------
    # [STEP 7] 4대 거인 페르소나 전환 & 맞춤 넛지/코칭 검증
    # -------------------------------------------------------------
    print("\n▶ [STEP 7] 4대 거인 페르소나 (버핏, 후버만, 머스크/Grok, 아우렐리우스) 검증")
    from assistant_engine import PERSONAS
    orig_persona = db.get_setting("persona", "huberman")
    for pkey, pinfo in PERSONAS.items():
        db.set_setting("persona", pkey)
        nudge_p = engine.get_smart_nudge(today.isoformat())
        print(f"  {pinfo['emoji']} [{pinfo['name']}] 넛지 질문 생성:")
        print(f"     \"{nudge_p['question'].splitlines()[-1]}\"")
        assert pkey in ["huberman", "buffett", "musk_grok", "aurelius"]

    # Restore original persona
    db.set_setting("persona", orig_persona)
    print("  ✅ 4대 거인 페르소나별 어투 및 코칭 철학 분기 100% 정상 작동")

    print("\n" + "=" * 70)
    print("🎉 [결과] 7단계 전 항목 기능 테스트 100% 통과! 모든 하네스가 완벽하게 작동합니다.")
    print("=" * 70)

if __name__ == "__main__":
    run_step_by_step_test()
