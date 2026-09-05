# Copyright (c) 2026 Shunpei Suzuki (suzuki.shunpei@altx.co.jp), AltX Inc.
# Developed by Shunpei Suzuki <suzuki.shunpei@altx.co.jp>
#
from app.agent import (
    ACTIVE_STEP_SEQUENCE,
    analyze_sql_impact,
    evaluate_escalation_gate,
    generate_final_report,
    get_active_sop,
    get_procedure_step,
    import_sop_procedure,
    reset_active_sop,
    verify_step_output,
)


def test_get_procedure_step_found():
    step1 = get_procedure_step(1)
    assert step1["status"] == "found"
    assert "バックアップ" in step1["title"]
    assert "tar" in step1["command"]


def test_get_procedure_step_not_found():
    invalid_step = get_procedure_step(999)
    assert invalid_step["status"] == "not_found"


def test_verify_step_output_success():
    result = verify_step_output(1, "tar: app_20260904.tar.gz created successfully.")
    assert result["verdict"] == "SUCCESS"


def test_verify_step_output_teraterm_log():
    raw_teraterm_log = """[2026-09-06 00:10:52.123] \x1b[?2004h[app-user@bastion ~]$ df -h /backup\x1b[0m\r
[2026-09-06 00:10:53.456] Filesystem\t\tSize\tUsed\tAvail\tUse%\tMounted on\r
[2026-09-06 00:10:53.457] /dev/mapper/vg-backup\t50G\t15G\t33G\t32%\t/backup\r
[2026-09-06 00:10:54.000] \x1b[?2004l[app-user@bastion ~]$ \x1b[0m"""
    result = verify_step_output("1-1", raw_teraterm_log)
    assert result["verdict"] == "SUCCESS"
    assert "空き容量が十分" in result["message"]


def test_verify_step_output_failure():
    result = verify_step_output(2, "Job for my-app.service failed because of error.")
    assert result["verdict"] == "FAILED"
    assert "エラーキーワード" in result["reason"]


def test_analyze_sql_impact_match():
    pre_select = """+-----+-----------+---------+----------+
| id  | tenant_id | status  | plan     |
+-----+-----------+---------+----------+
| 105 | T100      | PENDING | STANDARD |
+-----+-----------+---------+----------+
1 row in set (0.01 sec)"""
    sql = "UPDATE users SET status = 'ACTIVE', plan = 'ENTERPRISE' WHERE tenant_id = 'T100';"
    res = analyze_sql_impact("3-3", pre_select, sql)
    assert res["verdict"] == "MATCH"
    assert res["escalation_required"] is False
    assert "要件合致" in res["requirement_satisfaction"]


def test_analyze_sql_impact_dangerous_missing_where():
    pre_select = "1 row in set"
    sql = "UPDATE users SET status = 'ACTIVE';"
    res = analyze_sql_impact("3-3", pre_select, sql)
    assert res["verdict"] == "HIGH_RISK"
    assert res["escalation_required"] is True
    assert res["branch_to"] == "E-1"
    assert "WHERE" in res["reason"]


def test_analyze_sql_impact_mismatch_tenant():
    pre_select = "105 | T100 | PENDING"
    sql = "UPDATE users SET status = 'ACTIVE' WHERE tenant_id = 'T999';"
    res = analyze_sql_impact("3-3", pre_select, sql)
    assert res["verdict"] == "MISMATCH"
    assert res["escalation_required"] is True
    assert res["branch_to"] == "E-1"


def test_evaluate_escalation_gate_blocked_without_grounds():
    res = evaluate_escalation_gate(
        escalation_result="協議しました",
        decision="GO",
        grounds="",  # 空の根拠
    )
    assert res["status"] == "BLOCKED"
    assert res["allowed_to_proceed"] is False
    assert "根拠" in res["reason"]


def test_evaluate_escalation_gate_nogo():
    res = evaluate_escalation_gate(
        escalation_result="開発元と協議し、不整合が解消できないため作業中断を決定",
        decision="NOGO",
        grounds="データ破損リスクが高く、夜間メンテ枠での再作業に切り替えるため (承認: 運用責任者 田中)",
    )
    assert res["status"] == "NOGO"
    assert res["allowed_to_proceed"] is False
    assert res["branch_to"] == "R-1"


def test_evaluate_escalation_gate_go_normal():
    res = evaluate_escalation_gate(
        escalation_result="SQLファイルのWHERE句をT100に修正し、再レビュー完了",
        decision="GO",
        grounds="手順書仕様書v2.1の要件定義に完全一致することを確認 (Slack承認: #rel-deploy-105)",
        is_standard_procedure=True,
    )
    assert res["status"] == "GO_NORMAL"
    assert res["allowed_to_proceed"] is True
    assert res["mode"] == "NORMAL"


def test_evaluate_escalation_gate_go_special_pair():
    res = evaluate_escalation_gate(
        escalation_result="本番特例として上長立会いのもとパッチ適用を決定",
        decision="GO",
        grounds="システム統括部長特命承認（ID: APPR-9912）に基づき2人体制で即時反映",
        is_standard_procedure=False,
        supervisor_name="山田部長",
    )
    assert res["status"] == "GO_SPECIAL"
    assert res["allowed_to_proceed"] is True
    assert res["mode"] == "SPECIAL_PAIR"
    assert res["supervisor"] == "山田部長"


def test_evaluate_escalation_gate_go_special_leader_approval():
    # 「リーダー承認でいい」: supervisor_nameが空でも「作業リーダー（承認済）」を自動設定して進行許可
    res = evaluate_escalation_gate(
        escalation_result="作業リーダーと現場確認し特別対応の実施を合意",
        decision="GO",
        grounds="リーダー承認済、暫定パッチによる即時復旧方針",
        is_standard_procedure=False,
        supervisor_name="",
    )
    assert res["status"] == "GO_SPECIAL"
    assert res["allowed_to_proceed"] is True
    assert res["mode"] == "SPECIAL_PAIR"
    assert "作業リーダー" in res["supervisor"]


def test_step_sequence_definition():
    from app.agent import STEP_SEQUENCE
    assert STEP_SEQUENCE == [
        "1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "3-3", "3-4", "4-1", "4-2"
    ]


def test_generate_final_report():
    report = generate_final_report(
        start_time="2026-09-06 00:00:00",
        end_time="2026-09-06 00:30:00",
        duration_minutes=30,
        mode="SPECIAL_PAIR",
        supervisor_name="山田部長",
    )
    assert "最終評価" in report["title"]
    assert report["work_duration"]["elapsed_minutes"] == 30
    assert report["operation_mode"]["two_person_rule_applied"] is True
    assert len(report["deliverables"]) >= 4


def test_consult_sop_knowledge():
    from app.agent import consult_sop_knowledge

    # 1. 正常系: ディスク容量不足の検索
    res = consult_sop_knowledge("バックアップ時のディスク空き容量不足について教えて")
    assert res["status"] == "found"
    assert "セクション1" in res["section_title"] or "ディスク" in res["section_title"]
    assert "df -h" in res["guidance"]

    # 2. 正常系: エスカレーション基準の検索
    res_esc = consult_sop_knowledge("エスカレーション基準やロールバック判断")
    assert res_esc["status"] == "found"
    assert "エスカレーション" in res_esc["section_title"]

    # 3. 該当なし
    res_none = consult_sop_knowledge("xyzxyz123456全く関係ないキーワード")
    assert res_none["status"] == "not_found"


def test_import_sop_procedure_markdown_table():
    reset_active_sop()
    md_content = """# PostgreSQL 定期メンテ手順書
| 項番 | 作業内容 | 投入コマンド | 期待ログ・判定基準 | 注意事項 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | DBヘルスチェック | pg_isready -h localhost -p 5432 | accepting connections | 接続不可時は即時連絡 |
| 2 | インデックス再構築 | REINDEX TABLE CONCURRENTLY users; | REINDEX | ピーク時実行厳禁 |
| 3 | 統計情報更新 | ANALYZE VERBOSE users; | ANALYZE | 負荷を監視 |
"""
    res = import_sop_procedure(md_content, format_type="markdown")
    assert res["status"] == "success"
    assert res["imported_steps_count"] >= 3
    assert any("1" in s for s in res["step_sequence"])

    # 検証: 新しい手順が取得できること
    step1 = get_procedure_step(1)
    assert step1["status"] == "found"
    assert "pg_isready" in step1["command"]
    assert "accepting connections" in step1["expected_check"]

    # 標準ロールバックとエスカレーションが安全のため維持されていること
    active_sop = get_active_sop()
    assert "R" in active_sop
    assert "E" in active_sop

    # クリーンアップ
    reset_active_sop()


def test_import_sop_procedure_tsv():
    reset_active_sop()
    tsv_content = (
        "項番\t作業内容\t実行コマンド\t期待結果\t注意事項\n"
        "1\tキャッシュクリア\tsystemctl restart redis\tActive: active\tデータ揮発確認\n"
        "2\tキュー監視\trq info\t0 failed\t滞留なし\n"
    )
    res = import_sop_procedure(tsv_content, format_type="tsv")
    assert res["status"] == "success"
    assert res["imported_steps_count"] >= 2
    step1 = get_procedure_step(1)
    assert "redis" in step1["command"]

    reset_active_sop()


def test_import_sop_procedure_json():
    reset_active_sop()
    import json
    steps_data = [
        {"id": "1", "title": "設定ファイル検証", "command": "nginx -t", "expected_output": "syntax is ok", "caution": "文法エラー時中断"},
        {"id": "2", "title": "リロード実行", "command": "systemctl reload nginx", "expected_output": "Active: active", "caution": "無停止リロード"}
    ]
    res = import_sop_procedure(json.dumps(steps_data), format_type="json")
    assert res["status"] == "success"
    assert res["imported_steps_count"] == 2
    step = get_procedure_step(1)
    assert "nginx -t" in step["command"]

    reset_active_sop()


def test_reset_active_sop():
    # カスタムSOPをインポートしてからリセット
    md_content = """| 項番 | 作業内容 | 投入コマンド | 期待結果 |
| 99 | 特別タスク | echo 'special' | special |"""
    import_sop_procedure(md_content, format_type="markdown")
    active_keys = [str(k) for k in get_active_sop().keys()]
    assert "99" in active_keys

    # リセット実行
    reset_res = reset_active_sop()
    assert isinstance(reset_res, dict)
    active_keys_after = [str(k) for k in reset_res.keys()]
    assert "99" not in active_keys_after
    assert "1" in active_keys_after
    assert "4" in active_keys_after


def test_verify_step_output_autonomous_verdicts():
    reset_active_sop()

    # 1. 承認合格: VERIFIED_APPROVED
    res_ok = verify_step_output("1-1", "Filesystem 50G 15G 33G 32% /backup")
    assert res_ok["verdict"] == "SUCCESS"
    assert res_ok["w_check_status"] == "VERIFIED_APPROVED"
    assert "Wチェック承認" in res_ok["autonomous_verdict"]

    # 2. 致命的エラーによる自律ロールバック判定: BRANCH_ROLLBACK
    res_fatal = verify_step_output("3-2", "Segmentation fault (core dumped) - fatal error occurred")
    assert res_fatal["verdict"] == "FAILED"
    assert res_fatal["w_check_status"] == "BRANCH_ROLLBACK"
    assert res_fatal["branch_to"] == "R-1"

    # 3. 競合・ロックによる自律エスカレーション判定: BRANCH_ESCALATION
    res_lock = verify_step_output("3-4", "ERROR 1205 (HY000): Lock wait timeout exceeded; deadlock detected")
    assert res_lock["verdict"] == "FAILED"
    assert res_lock["w_check_status"] == "BRANCH_ESCALATION"
    assert res_lock["branch_to"] == "E-1"

    # 4. ディスク容量枯渇・再実行ブロック: BLOCKED_RETRY
    res_retry = verify_step_output("1-1", "Filesystem 50G 50G 0G 100% /backup No space left on device")
    assert res_retry["verdict"] == "FAILED"
    assert res_retry["w_check_status"] == "BLOCKED_RETRY"


def test_frontend_api_sop_endpoints():
    from fastapi.testclient import TestClient
    from frontend.main import app
    client = TestClient(app)

    # 1. GET /api/sop
    res = client.get("/api/sop")
    assert res.status_code == 200
    data = res.json()
    assert "sop" in data
    assert "sequence" in data

    # 2. POST /api/sop/import
    md_content = """| 項番 | 作業内容 | 投入コマンド | 期待結果 |
| 1 | テスト手順 | echo test | test |"""
    res_import = client.post("/api/sop/import", json={"content": md_content, "format_type": "markdown"})
    assert res_import.status_code == 200
    import_data = res_import.json()
    assert import_data["result"]["status"] == "success"

    # 3. POST /api/sop/reset
    res_reset = client.post("/api/sop/reset")
    assert res_reset.status_code == 200
    reset_data = res_reset.json()
    assert "1" in [str(k) for k in reset_data["sop"].keys()]





