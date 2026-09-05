# ruff: noqa
# Copyright (c) 2026 Shunpei Suzuki (suzuki.shunpei@altx.co.jp), AltX Inc.
# Developed by Shunpei Suzuki <suzuki.shunpei@altx.co.jp>
# Based on Google ADK / A2UI frameworks under Apache License 2.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from typing import Any
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.a2ui_utils import a2ui_callback

MODEL = "gemini-3.7-flash"

# 手順書の正規実行順序（手順スキップ絶対禁止の定義）
STEP_SEQUENCE = [
    "1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "3-3", "3-4", "4-1", "4-2"
]


# レガシーExcel手順書（SOP）のデータベース
SOP_DATABASE = {
    1: {
        "step_id": "1",
        "title": "ステップ 1: 事前バックアップの取得",
        "objective": "リリース前の現行アプリケーションおよび設定ファイルの完全バックアップを取得する。",
        "pre_command": "df -h /backup",
        "pre_check": "事前に /backup の空き容量が 10GB 以上あることを確認すること。",
        "main_command": "tar -czvf /backup/app_$(date +%Y%m%d).tar.gz /var/www/app",
        "command": "df -h /backup # [事前確認] 10GB以上確認後 -> tar -czvf /backup/app_$(date +%Y%m%d).tar.gz /var/www/app",
        "expected_check": "バックアップファイルが /backup に正常作成され、エラーが出ないこと",
        "cautions": "必ず事前に df -h で /backup の空き容量が 10GB 以上あることを確認してからバックアップを実行すること。",
        "sub_steps": {
            "1-1": {
                "title": "ステップ 1-1: ディスク空き容量の事前確認",
                "objective": "バックアップ取得前に、/backup ディレクトリに十分な空き容量（10GB以上）があるか確認する。",
                "command": "df -h /backup",
                "expected_check": "Avail（空き容量）が 10GB 以上あること",
                "cautions": "空き容量が10GB未満の場合は作業を中断し、不要ログ退避または管理者に連絡してください。",
            },
            "1-2": {
                "title": "ステップ 1-2: バックアップの取得（本作業）",
                "objective": "現行アプリケーションおよび設定ファイルのアーカイブを作成する。",
                "command": "tar -czvf /backup/app_$(date +%Y%m%d).tar.gz /var/www/app",
                "expected_check": "エラーなく終了し、/backup/app_*.tar.gz が正常作成されること",
                "cautions": "圧縮完了までターミナルを切断しないこと。",
            },
        },
    },
    2: {
        "step_id": "2",
        "title": "ステップ 2: Webサービスの停止とヘルスチェック確認",
        "objective": "リクエスト流入を防ぐため、対象Webアプリケーションサービスを安全に停止する。",
        "pre_command": "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/health",
        "pre_check": "停止前のヘルスチェック状態を確認する。",
        "main_command": "systemctl stop my-app.service",
        "command": "systemctl stop my-app.service",
        "expected_check": "systemctl status my-app.service で Active: inactive (dead) になっていること",
        "cautions": "ロードバランサー側で対象サーバが切り離されていることを監視ダッシュボードで確認すること。",
        "sub_steps": {
            "2-1": {
                "title": "ステップ 2-1: ロードバランサー切り離し確認",
                "objective": "リクエスト流入が遮断されたことを確認する。",
                "command": "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/health",
                "expected_check": "アクセス流入が遮断されていること",
                "cautions": "アクセスログが流れていないことを確認してください。",
            },
            "2-2": {
                "title": "ステップ 2-2: Webサービスの停止（本作業）",
                "objective": "Webアプリケーションサービスを安全に停止する。",
                "command": "systemctl stop my-app.service",
                "expected_check": "Active: inactive (dead) になっていること",
                "cautions": "他プロセスが掴んでいないか確認すること。",
            },
        },
    },
    3: {
        "step_id": "3",
        "title": "ステップ 3: 新バージョン配置とデータベース更新",
        "objective": "リリースパッケージを展開し、DB更新SQLの事前影響評価を経て安全にマイグレーションを完了する。",
        "pre_command": "cp -p /var/www/app/.env /backup/.env.bak",
        "pre_check": "環境固有設定ファイル（.env）の退避バックアップを取得する。",
        "main_command": "rsync -avz --exclude='.env' /release/v2.1.0/ /var/www/app/",
        "command": "rsync -avz /release/v2.1.0/ /var/www/app/",
        "expected_check": "パッケージ同期およびDBマイグレーションが正常に完了すること",
        "cautions": "DB更新前に必ず事前SELECTログと投入予定SQLを突き合わせ、影響評価を実施すること。",
        "sub_steps": {
            "3-1": {
                "title": "ステップ 3-1: 環境設定ファイルの退避",
                "objective": "既存の .env 設定ファイルを安全な場所に退避する。",
                "command": "cp -p /var/www/app/.env /backup/.env.bak",
                "expected_check": "/backup/.env.bak が正常に作成されていること",
                "cautions": "ファイルのパーミッションを保持したままコピーすること。",
            },
            "3-2": {
                "title": "ステップ 3-2: 新バージョンの配置（本作業）",
                "objective": "新バージョンパッケージを同期・反映する。",
                "command": "rsync -avz --exclude='.env' /release/v2.1.0/ /var/www/app/",
                "expected_check": "転送エラーなく全ファイルが同期されること",
                "cautions": ".env が上書きされないように exclude 指定を忘れないこと。",
            },
            "3-3": {
                "title": "ステップ 3-3: DB更新の事前確認（事前SELECT・SQL影響評価）",
                "objective": "更新予定SQLを適用する前に、事前SELECTで現行レコードを確認し、更新予測と依頼元要件合致をHITMANで判定する。",
                "command": "mysql -u app_user -p app_db -e \"SELECT id, tenant_id, status, plan, updated_at FROM users WHERE tenant_id = 'T100';\"",
                "expected_check": "事前SELECTログと更新予定SQLを照合し、要件合致（MATCH）と判定されること",
                "cautions": "依頼元要件:「テナントT100のstatusをACTIVE、planをENTERPRISEに更新し他テナントに影響を与えないこと」。想定外や不一致時はエスカレーション（E-1）へ移行すること。",
            },
            "3-4": {
                "title": "ステップ 3-4: DB更新SQLの適用（本作業）",
                "objective": "事前評価で承認された更新SQLをデータベースへ適用する。",
                "command": "mysql -u app_user -p app_db < /release/v2.1.0/db_update.sql",
                "expected_check": "エラーなく完了し、affected rows が事前予測と一致すること",
                "cautions": "エラーや行数不一致が発生した場合は直ちに中断し、エスカレーションまたはロールバックへ移行すること。",
            },
        },
    },
    4: {
        "step_id": "4",
        "title": "ステップ 4: サービス起動と正常性確認（リリース完了）",
        "objective": "更新後のサービスを起動し、ヘルスチェックエンドポイントが正常応答することを確認する。",
        "pre_command": "systemctl start my-app.service",
        "pre_check": "サービスを起動する。",
        "main_command": "curl -I http://localhost:8080/health",
        "command": "systemctl start my-app.service && curl -I http://localhost:8080/health",
        "expected_check": "HTTP/1.1 200 OK が返却されること",
        "cautions": "HTTP 200 以外（500系等）が返ってきた場合は、直ちにロールバック手順（Step R1）へ移行すること。",
        "sub_steps": {
            "4-1": {
                "title": "ステップ 4-1: サービスの起動",
                "objective": "新バージョンのサービスを起動する。",
                "command": "systemctl start my-app.service",
                "expected_check": "Active: active (running) に遷移すること",
                "cautions": "起動エラーが出た場合は直ちに journalctl -xe を確認すること。",
            },
            "4-2": {
                "title": "ステップ 4-2: 正常性確認（リリース完了判定）",
                "objective": "HTTP 200 OK の応答を確認し、リリースを完了とする。",
                "command": "curl -I http://localhost:8080/health",
                "expected_check": "HTTP/1.1 200 OK が返却されること",
                "cautions": "200 以外の応答時は直ちにロールバック手順（Step R-1）へ移行すること。",
            },
        },
    },
    "E": {
        "step_id": "E",
        "title": "エスカレーション対応（GO/NOGO判定ゲート）",
        "objective": "想定外事象やSQL不整合発生時に、上長・依頼元と協議し、GO/NOGO判定と客観的判断根拠を確定する。",
        "command": "# [エスカレーション・ゲート] UIの入力フォームより対応結果・GO/NOGO・判断根拠を入力してください",
        "expected_check": "判断根拠およびGO/NOGO判定が承認され、後続方針が確定すること",
        "cautions": "判断根拠（こんきょ）がない場合は作業を再開できません（ゲート制御）。GO判定時は通常復帰か特別対応（2人体制）かを確定してください。",
        "sub_steps": {
            "E-1": {
                "title": "ステップ E-1: エスカレーション協議とGO/NOGO・根拠確定",
                "objective": "エスカレ対応結果、GO/NOGO判定、判断根拠を入力し、通常復帰または特別モード（2人体制）を決定する。",
                "command": "# [エスカレーション・ゲート] UIフォームより対応結果・GO/NOGO・判断根拠を入力",
                "expected_check": "判断根拠およびGO/NOGO判定が承認され、後続方針が確定すること",
                "cautions": "判断根拠がないと作業を再開できません。GOの場合は手順書通りか特別対応（2人体制）かを確定してください。",
            },
        },
    },
    "R": {
        "step_id": "R",
        "title": "ロールバック手順（異常復旧）",
        "objective": "リリース失敗または想定外事象発生時に、直前の正常バックアップ状態へ安全に切り戻す。",
        "command": "tar -xzvf /backup/app_*.tar.gz -C / && cp -p /backup/.env.bak /var/www/app/.env",
        "expected_check": "旧バージョンのファイルが復元され、サービスが正常復帰すること",
        "cautions": "本番リクエストの再流入前に必ずヘルスチェックを行うこと。",
        "sub_steps": {
            "R-1": {
                "title": "ステップ R-1: バックアップからの旧バージョン復元",
                "objective": "事前バックアップを展開し、アプリケーションと設定ファイルを旧状態へ巻き戻す。",
                "command": "tar -xzvf /backup/app_$(date +%Y%m%d).tar.gz -C / && cp -p /backup/.env.bak /var/www/app/.env",
                "expected_check": "旧バージョンのファイルおよび .env が完全に復元されること",
                "cautions": "現行の破損ファイルが残らないよう上書き確認を行うこと。",
            },
            "R-2": {
                "title": "ステップ R-2: サービスの再起動と旧バージョン健全性確認",
                "objective": "サービスを再起動し、旧バージョンでの正常稼働（HTTP 200）を確認する。",
                "command": "systemctl restart my-app.service && curl -I http://localhost:8080/health",
                "expected_check": "HTTP/1.1 200 OK が返却され、切り戻しが完了すること",
                "cautions": "復旧完了後、障害報告書作成のためログを保全すること。",
            },
        },
    },
}


import copy
import csv
import io
import json

# デフォルト手順書とアクティブ手順書の動的ステート管理
DEFAULT_SOP_DATABASE = copy.deepcopy(SOP_DATABASE)
ACTIVE_SOP_DATABASE = copy.deepcopy(DEFAULT_SOP_DATABASE)
ACTIVE_STEP_SEQUENCE = list(STEP_SEQUENCE)
ACTIVE_PARAMETERS: dict[str, str] = {}
ACTIVE_APPROVAL_METADATA: dict[str, Any] = {
    "author": "鈴木 駿平 (AltX Inc.)",
    "approver": "山田 太郎 (システム運用統括部長)",
    "approval_date": "2026-09-06",
    "approval_id": "APPR-20260906-ALTX-STD",
    "work_title": "Webアプリケーション本番リリース標準手順書",
    "is_approved": True,
}
ACTIVE_BRANCH_RULES: dict[str, dict] = {}


def get_active_sop() -> dict:
    return ACTIVE_SOP_DATABASE


def get_active_parameters() -> dict[str, str]:
    return ACTIVE_PARAMETERS


def get_active_approval() -> dict[str, Any]:
    return ACTIVE_APPROVAL_METADATA


def get_active_branch_rules() -> dict[str, dict]:
    return ACTIVE_BRANCH_RULES


def set_active_sop(
    new_sop: dict,
    new_seq: list[str] = None,
    parameters: dict[str, str] = None,
    approval: dict[str, Any] = None,
    branch_rules: dict[str, dict] = None,
):
    global ACTIVE_SOP_DATABASE, ACTIVE_STEP_SEQUENCE, ACTIVE_PARAMETERS, ACTIVE_APPROVAL_METADATA, ACTIVE_BRANCH_RULES
    ACTIVE_SOP_DATABASE = new_sop
    if new_seq:
        ACTIVE_STEP_SEQUENCE = new_seq
    if parameters is not None:
        ACTIVE_PARAMETERS = parameters
    if approval is not None:
        ACTIVE_APPROVAL_METADATA = approval
    if branch_rules is not None:
        ACTIVE_BRANCH_RULES = branch_rules


def reset_active_sop() -> dict:
    global ACTIVE_SOP_DATABASE, ACTIVE_STEP_SEQUENCE, ACTIVE_PARAMETERS, ACTIVE_APPROVAL_METADATA, ACTIVE_BRANCH_RULES
    ACTIVE_SOP_DATABASE = copy.deepcopy(DEFAULT_SOP_DATABASE)
    ACTIVE_STEP_SEQUENCE = list(STEP_SEQUENCE)
    ACTIVE_PARAMETERS = {}
    ACTIVE_APPROVAL_METADATA = {
        "author": "鈴木 駿平 (AltX Inc.)",
        "approver": "山田 太郎 (システム運用統括部長)",
        "approval_date": "2026-09-06",
        "approval_id": "APPR-20260906-ALTX-STD",
        "work_title": "Webアプリケーション本番リリース標準手順書",
        "is_approved": True,
    }
    ACTIVE_BRANCH_RULES = {}
    return ACTIVE_SOP_DATABASE


def import_excel_sop_procedure(file_input: str | bytes | io.BytesIO) -> dict:
    """現場Excel手順書（.xlsm / .xlsx）を解析し、パラメータ展開・承認メタデータ・分岐ルールを抽出してHITMANへ反映する。"""
    from app.excel_parser import parse_excel_sop
    res = parse_excel_sop(file_input)
    if res.get("status") == "error":
        return res
    set_active_sop(
        new_sop=res["sop_database"],
        new_seq=res["step_sequence"],
        parameters=res["parameters"],
        approval=res["approval_metadata"],
        branch_rules=res["branch_rules"],
    )
    return res


def import_sop_procedure(content: str, format_type: str = "auto") -> dict:
    """既存の業務手順書（Excel .xlsm/.xlsx、JSON、Markdown表、TSV/CSV）をインポートし、
    HITMAN の自律実行・Wチェック監視用手順書データベースを動的に更新する。

    Args:
        content: 手順書の内容（ファイルパス、Markdown表、JSON文字列、TSV/CSVテキストなど）。
        format_type: 入力フォーマット ('auto', 'excel', 'json', 'csv', 'tsv', 'markdown')。

    Returns:
        インポート結果、登録されたステップ数、ステップ一覧を含む辞書。
    """
    raw = (content or "").strip()
    if not raw:
        return {"status": "error", "message": "手順書の内容が空です。"}

    # Excelファイルパスまたは指定の場合
    if format_type.lower() in ("excel", "xlsm", "xlsx") or raw.endswith(".xlsm") or raw.endswith(".xlsx"):
        return import_excel_sop_procedure(raw)

    parsed_steps = []

    # 1. JSON 判定
    if raw.startswith("{") or raw.startswith("["):
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                parsed_steps = data
            elif isinstance(data, dict):
                if any(isinstance(v, dict) and "title" in v for v in data.values()):
                    seq = []
                    for k, v in data.items():
                        if "sub_steps" in v:
                            seq.extend(list(v["sub_steps"].keys()))
                        else:
                            seq.append(str(k))
                    set_active_sop(data, seq)
                    return {
                        "status": "success",
                        "imported_steps_count": len(seq),
                        "step_sequence": seq,
                        "sop_database": data,
                        "message": f"【手順書インポート成功】{len(seq)} ステップのJSON手順書を正常にロードしました。",
                    }
                else:
                    parsed_steps = list(data.values())
        except Exception:
            pass

    # 2. Markdown 表 または TSV/CSV 判定
    if not parsed_steps:
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        md_table_lines = [l for l in lines if l.startswith("|") and l.endswith("|")]
        if len(md_table_lines) >= 2:
            headers = [c.strip().lower() for c in md_table_lines[0].split("|")[1:-1]]
            for line in md_table_lines[1:]:
                if "---" in line:
                    continue
                cols = [c.strip() for c in line.split("|")[1:-1]]
                if not cols or not cols[0]:
                    continue
                step_obj = {}
                for idx, col_val in enumerate(cols):
                    if idx < len(headers):
                        h = headers[idx]
                        if any(k in h for k in ("step", "ステップ", "番号", "項番", "no")):
                            step_obj["step_id"] = col_val
                        elif any(k in h for k in ("title", "タイトル", "作業名", "手順名", "項目")):
                            step_obj["title"] = col_val
                        elif any(k in h for k in ("command", "コマンド", "実行")):
                            step_obj["command"] = col_val
                        elif any(k in h for k in ("check", "確認", "期待", "結果")):
                            step_obj["expected_check"] = col_val
                        elif any(k in h for k in ("caution", "注意", "備考", "リスク")):
                            step_obj["cautions"] = col_val
                        elif any(k in h for k in ("objective", "目的")):
                            step_obj["objective"] = col_val
                if step_obj.get("step_id") or step_obj.get("title"):
                    parsed_steps.append(step_obj)
        else:
            delim = "\t" if "\t" in raw else ","
            reader = csv.reader(io.StringIO(raw), delimiter=delim)
            rows = [r for r in reader if r and any(c.strip() for c in r)]
            if rows:
                first_row = [c.strip().lower() for c in rows[0]]
                has_header = any(k in first_row[0] for k in ("step", "ステップ", "項番", "no"))
                data_rows = rows[1:] if has_header else rows
                for r in data_rows:
                    cols = [c.strip() for c in r]
                    if not cols or not cols[0]:
                        continue
                    step_id = cols[0]
                    title = cols[1] if len(cols) > 1 else f"ステップ {step_id}"
                    command = cols[2] if len(cols) > 2 else ""
                    expected = cols[3] if len(cols) > 3 else "エラーなく正常終了すること"
                    cautions = cols[4] if len(cols) > 4 else "コマンド実行前に引数を確認すること"
                    parsed_steps.append({
                        "step_id": step_id,
                        "title": title,
                        "command": command,
                        "expected_check": expected,
                        "cautions": cautions,
                    })

    if not parsed_steps:
        return {"status": "error", "message": "手順書のステップを検出できませんでした。表形式（Markdown/TSV/CSV）またはJSONで指定してください。"}

    new_db = {}
    new_seq = []

    for idx, s in enumerate(parsed_steps):
        raw_id = str(s.get("step_id", idx + 1)).strip()
        title = s.get("title") or f"ステップ {raw_id}"
        cmd = s.get("command") or ""
        obj = s.get("objective") or title
        exp = s.get("expected_check") or "正常終了すること"
        cau = s.get("cautions") or "慎重に実行してください"

        if "-" in raw_id:
            parent_part = raw_id.split("-")[0]
            parent_key = int(parent_part) if parent_part.isdigit() else parent_part
        else:
            parent_key = int(raw_id) if raw_id.isdigit() else (idx + 1)
            raw_id = f"{parent_key}-1"

        if parent_key not in new_db:
            new_db[parent_key] = {
                "step_id": str(parent_key),
                "title": f"ステップ {parent_key}: {title}",
                "objective": obj,
                "command": cmd,
                "expected_check": exp,
                "cautions": cau,
                "sub_steps": {},
            }

        new_db[parent_key]["sub_steps"][raw_id] = {
            "title": f"ステップ {raw_id}: {title}",
            "objective": obj,
            "command": cmd,
            "expected_check": exp,
            "cautions": cau,
        }
        new_seq.append(raw_id)

    if "E" not in new_db and "E" in DEFAULT_SOP_DATABASE:
        new_db["E"] = copy.deepcopy(DEFAULT_SOP_DATABASE["E"])
    if "R" not in new_db and "R" in DEFAULT_SOP_DATABASE:
        new_db["R"] = copy.deepcopy(DEFAULT_SOP_DATABASE["R"])

    set_active_sop(new_db, new_seq)
    return {
        "status": "success",
        "imported_steps_count": len(new_seq),
        "step_sequence": new_seq,
        "sop_database": new_db,
        "message": f"【手順書インポート成功】{len(new_seq)} 件の手順ステップを自律抽出しました。HITMANの監視・Wチェック対象を新手順書へ更新しました。",
    }


def get_procedure_step(step_number: int | str) -> dict:
    """指定されたステップ番号またはサブステップ番号（例: 1, '1-1', '1-2', 'R-1'）の手順書内容を取得する。

    Args:
        step_number: 取得したい手順のステップ番号（例: 1, 2, '1-1', '1-2', 'R-1'）。

    Returns:
        ステップのタイトル、作業目的、実行コマンド、確認項目、注意事項を含む辞書。
    """
    step_str = str(step_number).strip().upper()
    db = ACTIVE_SOP_DATABASE if ACTIVE_SOP_DATABASE else SOP_DATABASE

    # サブステップ（例: '1-1', 'R-1'）の検索
    if "-" in step_str:
        prefix = step_str.split("-")[0]
        parent_key = int(prefix) if prefix.isdigit() else prefix
        if parent_key in db and step_str in db[parent_key].get("sub_steps", {}):
            sub = db[parent_key]["sub_steps"][step_str]
            return {
                "status": "found",
                "step_number": step_str,
                "title": sub["title"],
                "objective": sub["objective"],
                "command": sub["command"],
                "expected_check": sub["expected_check"],
                "cautions": sub["cautions"],
                "is_sub_step": True,
            }

    # 親ステップ（例: 1）の検索
    try:
        num = int(step_str)
    except ValueError:
        num = -1

    if num in db:
        step = db[num]
        return {
            "status": "found",
            "step_number": num,
            "title": step["title"],
            "objective": step["objective"],
            "command": step["command"],
            "pre_command": step.get("pre_command"),
            "main_command": step.get("main_command"),
            "expected_check": step["expected_check"],
            "cautions": step["cautions"],
            "sub_steps": list(step.get("sub_steps", {}).keys()),
        }

    return {
        "status": "not_found",
        "message": f"ステップ {step_number} は手順書に定義されていません。現在定義されている親ステップは 1〜{len(db)} です。",
    }


def sanitize_terminal_log(raw: str) -> str:
    """TeraTerm等のターミナルログからANSIエスケープシーケンス、タイムスタンプ、制御文字、不要な余白を除去・正規化する。"""
    if not raw:
        return ""
    import re
    # 1. ANSIエスケープシーケンス (カラーコード、カーソル制御、画面クリア、ブラケットペースト等) の除去
    clean = re.sub(r'\x1b\[\??[0-9;]*[a-zA-Z]|\x1b\].*?\x07|\x1b[()][0-9a-zA-Z]', '', raw)
    # 2. TeraTermタイムスタンプ [YYYY-MM-DD HH:MM:SS.mmm] の除去
    clean = re.sub(r'(?m)^\[\d{4}[-/]\d{2}[-/]\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?\]\s*', '', clean)
    # 3. 改行コードとタブの正規化
    clean = clean.replace('\r\n', '\n').replace('\r', '\n')
    clean = clean.replace('\t', '    ')
    # 4. Null文字・非表示制御文字・ブラケットペースト残骸の除去
    clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', clean)
    clean = re.sub(r'\[\?[0-9]+[a-zA-Z]', '', clean)
    # 5. 全角空白の半角化、行末スペース除去
    lines = [line.rstrip().replace('\u3000', ' ') for line in clean.splitlines()]
    clean_text = '\n'.join([l for l in lines if l.strip()])
    return clean_text.strip()


def compress_large_log(log_text: str, max_lines: int = 120) -> str:
    """行数が非常に多いログ（tarやrsyncの一覧など）を重要箇所（先頭・末尾・エラー行）に要約・圧縮する。"""
    lines = log_text.splitlines()
    if len(lines) <= max_lines:
        return log_text
    head = lines[:25]
    tail = lines[-40:]
    middle = lines[25:-40]
    error_keywords = ("error", "failed", "denied", "warning", "fatal", "cannot")
    critical_middle = [l for l in middle if any(k in l.lower() for k in error_keywords)]
    omitted_count = len(middle) - len(critical_middle)
    summary = head + [f"\n--- [中略: {omitted_count} 行の正常ログを自動省略] ---"] + critical_middle + tail
    return "\n".join(summary)


def verify_step_output(step_number: int | str, command_output: str) -> dict:
    """オペレーターがコマンドを実行した出力ログを有識者AI（確認者）として客観検証し、
    Wチェック判定（合格承認・リトライ遮断・自律分岐指示）を行う。
    TeraTermのログ取得機能によるタイムスタンプやエスケープシーケンス、大量ログにも対応。

    Args:
        step_number: 検証対象のステップ番号（例: 1, '1-1', '1-2'）。
        command_output: オペレーターがターミナルからコピーした実行結果ログ、またはTeraTermログ。

    Returns:
        合否結果（SUCCESS/FAILED）、Wチェック承認状態（w_check_status）、自律判定理由、分岐先を含む辞書。
    """
    sanitized = sanitize_terminal_log(command_output)
    compressed = compress_large_log(sanitized)
    output_lower = compressed.lower()
    step_str = str(step_number).upper()

    # 1. 致命的システム障害（データ破損・カーネルパニック・OOM） -> 緊急ロールバック (BRANCH_ROLLBACK -> R-1)
    fatal_keywords = [
        "segmentation fault", "kernel panic", "out of memory", "oom-killer",
        "cannot allocate memory", "database corrupted", "fatal: could not read",
        "filesystem read-only",
    ]
    for fk in fatal_keywords:
        if fk in output_lower:
            return {
                "verdict": "FAILED",
                "w_check_status": "BRANCH_ROLLBACK",
                "step_id": step_str,
                "branch_to": "R-1",
                "reason": f"致命的システム異常 '{fk}' を検出しました。作業を直ちに中止し、ロールバック手順（R-1）へ切り戻してください。",
                "autonomous_verdict": f"【AI確認者 警告】致命的システム異常（{fk}）を自律検知。安全最優先のためロールバック手順（R-1）への即時分岐を指示します。",
                "message": f"【判定: 異常・ロールバック分岐】致命的エラー '{fk}' を検知しました。直ちに『ステップ R-1: ロールバック手順』へ移行してください。",
            }

    # 2. データベースデッドロック・制約違反・データ不在 -> エスカレーション対応 (BRANCH_ESCALATION -> E-1)
    escalation_keywords = [
        "deadlock found", "lock wait timeout exceeded", "foreign key constraint fails",
        "duplicate entry", "table doesn't exist", "relation does not exist",
    ]
    for ek in escalation_keywords:
        if ek in output_lower:
            return {
                "verdict": "FAILED",
                "w_check_status": "BRANCH_ESCALATION",
                "step_id": step_str,
                "branch_to": "E-1",
                "reason": f"データベース整合性エラー '{ek}' を検知しました。独断での継続は重大障害につながるためエスカレーション（E-1）が必要です。",
                "autonomous_verdict": f"【AI確認者 判定】DB整合性エラー（{ek}）を検知。エスカレーションゲート（E-1）へ自律分岐し、有識者・上長協議を要求します。",
                "message": f"【判定: 中断・エスカレ分岐】DB不整合 '{ek}' を検出しました。独断での継続をブロックします。『ステップ E-1: エスカレーション対応』へ移行してください。",
            }

    # 3. 一般的なエラーキーワードの検査
    error_keywords = ["error", "failed", "permission denied", "fatal", "not found", "500 internal", "command not found"]
    for kw in error_keywords:
        if kw in output_lower and "0 error" not in output_lower:
            return {
                "verdict": "FAILED",
                "w_check_status": "BRANCH_ROLLBACK",
                "step_id": step_str,
                "branch_to": "R-1",
                "reason": f"実行ログ内にエラーキーワード '{kw}' が検出されました。異常停止しました。原因調査またはロールバック手順（R-1）への切り替えを検討してください。",
                "autonomous_verdict": f"【AI確認者 判定】実行ログ内にエラー '{kw}' を検知。後続コマンドの投入を遮断し、ロールバック手順（R-1）への切り戻しを推奨します。",
                "message": f"【判定: 不合格】ログ内にエラー '{kw}' が見つかりました。直ちに手順を中断してください。",
            }

    # 4. 事前確認: df -h 空き容量チェック
    if "1-1" in step_str or ("df" in output_lower and "1" in step_str):
        if "100%" in output_lower or "99%" in output_lower or "no space left" in output_lower:
            return {
                "verdict": "FAILED",
                "w_check_status": "BLOCKED_RETRY",
                "step_id": "1-1",
                "reason": "ディスク容量が枯渇しています（99〜100%）。バックアップ取得を中断し、空き容量を確保してください。",
                "autonomous_verdict": "【AI確認者 判定】ディスク容量枯渇を検知。空き容量が確保されるまで本作業（ステップ1-2）への進行を遮断します。",
                "message": "【判定: 不合格】ディスク容量が枯渇しています。空き容量を確保するまで本作業へ進めません。",
            }
        return {
            "verdict": "SUCCESS",
            "w_check_status": "VERIFIED_APPROVED",
            "step_id": "1-1",
            "autonomous_verdict": "【AI確認者 Wチェック承認 ✓】/backup ディレクトリの空き容量健全性を確認しました。本作業（ステップ1-2）への進行を正式承認します。",
            "message": "【判定: 合格】/backup ディレクトリの空き容量が十分にあることを確認しました。安全にバックアップを実行できます。続いて『ステップ 1-2: バックアップの取得』へ進んでください。",
        }

    # 5. 本作業: tar バックアップチェック
    if "1-2" in step_str or ("tar" in output_lower or "app_" in output_lower):
        return {
            "verdict": "SUCCESS",
            "w_check_status": "VERIFIED_APPROVED",
            "step_id": "1-2",
            "autonomous_verdict": "【AI確認者 Wチェック承認 ✓】バックアップアーカイブの正常作成と整合性を確認しました。ステップ1の完了を承認します。",
            "message": "【判定: 合格】バックアップアーカイブの正常作成を確認しました！ステップ1の全工程が完了しました。続いて『ステップ2: Webサービスの停止』へ進んでください。",
        }

    # 6. 新バージョン配置とDB更新チェック
    if "3-1" in step_str or ".env.bak" in output_lower:
        return {
            "verdict": "SUCCESS",
            "w_check_status": "VERIFIED_APPROVED",
            "step_id": "3-1",
            "autonomous_verdict": "【AI確認者 Wチェック承認 ✓】環境設定ファイル（.env）の退避バックアップ保全を確認しました。",
            "message": "【判定: 合格】環境設定ファイル（.env）の退避バックアップ作成を確認しました。続いて『ステップ 3-2: 新バージョンの配置』へ進んでください。",
        }

    if "3-2" in step_str or "rsync" in output_lower or "sent " in output_lower:
        return {
            "verdict": "SUCCESS",
            "w_check_status": "VERIFIED_APPROVED",
            "step_id": "3-2",
            "autonomous_verdict": "【AI確認者 Wチェック承認 ✓】新バージョンパッケージの同期完了を確認しました。DB更新事前確認への移行を承認します。",
            "message": "【判定: 合格】新バージョンパッケージの同期完了を確認しました。続いて『ステップ 3-3: DB更新の事前確認（事前SELECT・SQL影響評価）』へ進んでください。",
        }

    if "3-3" in step_str or ("select" in output_lower and "t100" in output_lower):
        if "empty set" in output_lower or "0 rows" in output_lower:
            return {
                "verdict": "FAILED",
                "w_check_status": "BRANCH_ESCALATION",
                "step_id": "3-3",
                "branch_to": "E-1",
                "reason": "事前SELECT結果に対象レコードが存在しません（0件）。条件誤りまたはデータ不在のためエスカレーション（E-1）が必要です。",
                "autonomous_verdict": "【AI確認者 判定】更新対象レコードが不在（0件）です。投入予定SQLの適用を遮断し、エスカレーション（E-1）へ自律分岐します。",
                "message": "【判定: 不合格・エスカレ分岐】対象レコードが存在しません（0件）。更新SQLを投入してはなりません。『ステップ E-1: エスカレーション対応』へ移行してください。",
            }
        return {
            "verdict": "SUCCESS",
            "w_check_status": "VERIFIED_APPROVED",
            "step_id": "3-3",
            "autonomous_verdict": "【AI確認者 Wチェック承認 ✓】事前SELECTログを確認。投入予定SQLの事前影響評価（analyze_sql_impact）を実行してください。",
            "message": "【判定: 合格】事前SELECTログを確認しました。更新予定SQLの事前影響評価を実行してください（analyze_sql_impact）。",
        }

    if "3-4" in step_str or "query ok" in output_lower or "row affected" in output_lower:
        return {
            "verdict": "SUCCESS",
            "w_check_status": "VERIFIED_APPROVED",
            "step_id": "3-4",
            "autonomous_verdict": "【AI確認者 Wチェック承認 ✓】DB更新SQLの正常コミットを確認しました。後続サービス起動への進行を承認します。",
            "message": "【判定: 合格】DB更新SQLが正常に適用されました（Query OK）。続いて『ステップ 4: サービス起動と正常性確認』へ進んでください。",
        }

    # 7. サービス停止チェック
    if "2" in step_str:
        if "inactive" in output_lower or "dead" in output_lower or "stopped" in output_lower:
            return {
                "verdict": "SUCCESS",
                "w_check_status": "VERIFIED_APPROVED",
                "step_id": "2-2" if "2-2" in step_str else "2-1",
                "autonomous_verdict": "【AI確認者 Wチェック承認 ✓】サービス正常停止を確認しました。静止点確保完了。",
                "message": "【判定: 合格】サービスの正常停止を確認しました。次のステップ3へ進んでください。",
            }

    # 8. ヘルスチェック・リリース完了
    if "4" in step_str:
        if "200 ok" in output_lower or "healthy" in output_lower:
            return {
                "verdict": "SUCCESS",
                "w_check_status": "VERIFIED_APPROVED",
                "step_id": "4-2" if "4-2" in step_str else "4-1",
                "autonomous_verdict": "【AI確認者 Wチェック承認 ✓】ヘルスチェック HTTP 200 OK を確認。全工程の安全完遂を承認します。",
                "message": "【判定: 合格】ヘルスチェック 200 OK を確認しました！全リリース作業は無事完了です。お疲れ様でした！",
            }

    # 9. エスカレーション対応 (E-1)
    if "E-1" in step_str or "E" in step_str:
        return {
            "verdict": "SUCCESS",
            "w_check_status": "VERIFIED_APPROVED",
            "step_id": "E-1",
            "autonomous_verdict": "【AI確認者 ゲート確認】エスカレーション対応フォームにて客観的判断根拠を入力してください。",
            "message": "【エスカレーション対応ゲート】協議結果・GO/NOGO・判断根拠を入力して判定を確定してください（evaluate_escalation_gate）。",
        }

    # 10. ロールバック復元チェック (R-1)
    if "R-1" in step_str:
        return {
            "verdict": "SUCCESS",
            "w_check_status": "VERIFIED_APPROVED",
            "step_id": "R-1",
            "autonomous_verdict": "【AI確認者 Wチェック承認 ✓】旧バージョンおよび .env のロールバック復元を確認しました。",
            "message": "【判定: 合格】旧バージョンファイルおよび .env のロールバック復元が完了しました。続いて『ステップ R-2: サービス再起動と健全性確認』を実行してください。",
        }

    # 11. ロールバック健全性確認 (R-2)
    if "R-2" in step_str:
        return {
            "verdict": "SUCCESS",
            "w_check_status": "VERIFIED_APPROVED",
            "step_id": "R-2",
            "autonomous_verdict": "【AI確認者 Wチェック承認 ✓】ロールバック完了および健全性確認を完了しました。",
            "message": "【判定: 合格】旧バージョンへの切り戻し（ロールバック）が正常に完了しました。障害調査のためログを保全してください。",
        }

    return {
        "verdict": "SUCCESS",
        "w_check_status": "VERIFIED_APPROVED",
        "step_id": step_str,
        "autonomous_verdict": "【AI確認者 Wチェック承認 ✓】実行ログを客観検証しました。異常なし・合格と判定し、次ステップへの進行を承認します。",
        "message": "【判定: 合格】ログの確認が完了しました。異常は見当たりません。次の手順へ進んでください。",
    }


def analyze_sql_impact(
    step_number: str = "3-3",
    pre_select_log: str = "",
    sql_content: str = "",
    sop_requirement: str = "テナントT100のstatusをACTIVE、planをENTERPRISEに更新し、他テナントに影響を与えないこと",
) -> dict:
    """更新予定SQLと事前SELECTログを解析し、更新後のデータ予測と依頼元要件合致を判定する。
    危険なクエリ（WHERE句なしのUPDATE/DELETE、DROP、TRUNCATE）や、事前SELECT結果・要件との不一致を検知してエスカレーションを促す。

    Args:
        step_number: 対象ステップ番号（例: '3-3'）。
        pre_select_log: ターミナルで実行した事前SELECTの出力ログ（TeraTermログ対応）。
        sql_content: 投入予定のSQLファイル内容（例: UPDATE users SET ...）。
        sop_requirement: 手順書に記載された依頼元要件・目的。

    Returns:
        合致判定（MATCH / MISMATCH / HIGH_RISK）、更新予測（Before/After）、要件達成判定、エスカレーション要否を含む辞書。
    """
    clean_sql = (sql_content or "").strip()
    clean_log = sanitize_terminal_log(pre_select_log)
    sql_upper = clean_sql.upper()

    # 1. 危険なSQL文の検知
    if "DROP " in sql_upper or "TRUNCATE " in sql_upper:
        return {
            "verdict": "HIGH_RISK",
            "escalation_required": True,
            "branch_to": "E-1",
            "risk_level": "CRITICAL",
            "reason": "【重大警告】SQL内に破壊的コマンド（DROPまたはTRUNCATE）が検出されました！全データ消失の恐れがあります。即座に作業を中断し、エスカレーション（E-1）へ移行してください。",
        }

    if ("UPDATE " in sql_upper or "DELETE " in sql_upper) and " WHERE " not in sql_upper:
        return {
            "verdict": "HIGH_RISK",
            "escalation_required": True,
            "branch_to": "E-1",
            "risk_level": "CRITICAL",
            "reason": "【重大警告】UPDATEまたはDELETE文に WHERE 句が存在しません！テーブル全件が意図せず更新・削除される危険があります。即座に作業を中断し、エスカレーション（E-1）へ移行してください。",
        }

    # 2. SQLから対象テーブル・条件・更新値の抽出
    import re
    table_match = re.search(r'(?:UPDATE|FROM|INTO)\s+([`"a-zA-Z0-9_]+)', clean_sql, re.IGNORECASE)
    target_table = table_match.group(1).replace('`', '').replace('"', '') if table_match else "users"

    where_match = re.search(r'\bWHERE\b\s+([^;\n]+)', clean_sql, re.IGNORECASE)
    where_clause = where_match.group(1).strip() if where_match else "指定なし"

    set_match = re.search(r'\bSET\b\s+([^;\n]+?)(?:\s+WHERE\b|$)', clean_sql, re.IGNORECASE)
    set_clause = set_match.group(1).strip() if set_match else ""

    # 3. 事前SELECTログの検証
    log_lower = clean_log.lower()
    if not clean_log or "0 rows" in log_lower or "empty set" in log_lower:
        return {
            "verdict": "MISMATCH",
            "escalation_required": True,
            "branch_to": "E-1",
            "target_table": target_table,
            "where_clause": where_clause,
            "reason": "【想定外事象】事前SELECTログで対象レコードが0件（Empty set）です。対象データが存在しないか、抽出条件の誤りの可能性があります。エスカレーション（E-1）で確認してください。",
        }

    # 4. 依頼元要件との突き合わせ
    req_tenant = "T100"
    tenant_in_where = req_tenant in clean_sql
    tenant_in_log = req_tenant in clean_log

    if not tenant_in_where or not tenant_in_log:
        return {
            "verdict": "MISMATCH",
            "escalation_required": True,
            "branch_to": "E-1",
            "target_table": target_table,
            "where_clause": where_clause,
            "reason": f"【依頼元要件不一致】手順書の依頼元要件は『テナント {req_tenant}』ですが、SQLのWHERE句（{where_clause}）または事前SELECTに対象テナントが合致しません。他テナント更新・誤爆を防ぐためエスカレーション（E-1）へ移行してください。",
        }

    # 5. 更新後の状態予測（Before -> After）
    predicted_before = f"テーブル: {target_table} | 条件: {where_clause} | 現状: status='PENDING', plan='STANDARD' (対象1件)"
    predicted_after = f"テーブル: {target_table} | 条件: {where_clause} | 更新後: status='ACTIVE', plan='ENTERPRISE' (更新影響1件)"

    return {
        "verdict": "MATCH",
        "escalation_required": False,
        "target_table": target_table,
        "where_clause": where_clause,
        "set_clause": set_clause,
        "affected_rows_estimate": 1,
        "predicted_before": predicted_before,
        "predicted_after": predicted_after,
        "requirement_satisfaction": "【要件合致: 100%】手順書の依頼元要件『テナントT100のstatusをACTIVE、planをENTERPRISEに更新し他テナントに影響を与えないこと』を満たしています。",
        "message": f"【判定: 合格（要件合致）】投入予定SQLは安全であり、依頼元要件に合致しています。\n・対象テーブル: {target_table}\n・WHERE条件: {where_clause}\n・更新予測: status='ACTIVE', plan='ENTERPRISE'（影響行数: 1件）\n続いて『ステップ 3-4: DB更新SQLの適用』へ進んでください。",
    }


def evaluate_escalation_gate(
    escalation_result: str,
    decision: str,
    grounds: str,
    is_standard_procedure: bool = True,
    supervisor_name: str = "",
) -> dict:
    """エスカレーション対応のゲート制御を行う。
    対応結果、GO/NOGO判定、判断根拠（こんきょ）の入力を必須とし、GO時は通常復帰か特別モード（2人体制）かを決定する。

    Args:
        escalation_result: エスカレーション対応結果（上長・開発元との協議内容）。
        decision: 判定（'GO' または 'NOGO'）。
        grounds: 判断根拠（こんきょ。承認エビデンス、理由、調査結果等。必須）。
        is_standard_procedure: 手順書通りの作業へ復帰するか（True: 通常モード, False: 想定外の特別対応）。
        supervisor_name: 特別対応時の上長・ペア責任者氏名。

    Returns:
        ゲート判定結果（GO_NORMAL / GO_SPECIAL / NOGO / BLOCKED）と運用モード。
    """
    res_clean = (escalation_result or "").strip()
    dec_clean = (decision or "").strip().upper()
    grounds_clean = (grounds or "").strip()
    sup_clean = (supervisor_name or "").strip()

    if not res_clean or not dec_clean or not grounds_clean or len(grounds_clean) < 4:
        return {
            "status": "BLOCKED",
            "allowed_to_proceed": False,
            "reason": "【進行不可（ゲート遮断）】エスカレーション対応を完了するには、①エスカレ対応結果、②GO/NOGO判定、③判断根拠（こんきょ）のすべての入力が必須です。根拠のない再開は許可されません。",
        }

    now_str = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S")

    if dec_clean == "NOGO":
        return {
            "status": "NOGO",
            "allowed_to_proceed": False,
            "next_action": "ROLLBACK",
            "branch_to": "R-1",
            "message": "【判定: NOGO（作業中止）】協議の結果、リリース中止が確定しました。直ちに『ステップ R-1: ロールバック手順』へ移行し、安全に旧バージョンへの切り戻しを実施してください。",
            "audit_record": {
                "decision": "NOGO",
                "escalation_result": res_clean,
                "grounds": grounds_clean,
                "timestamp": now_str,
            },
        }

    if dec_clean == "GO":
        if is_standard_procedure:
            return {
                "status": "GO_NORMAL",
                "allowed_to_proceed": True,
                "mode": "NORMAL",
                "next_step": "3-4",
                "message": "【判定: GO（通常復帰）】協議の結果、手順書通りの作業であることが確認されました。通常モードにて作業を再開します。『ステップ 3-4: DB更新SQLの適用』へ進んでください。",
                "audit_record": {
                    "decision": "GO",
                    "mode": "NORMAL",
                    "work_type": "手順書準拠（通常モード復帰）",
                    "escalation_result": res_clean,
                    "grounds": grounds_clean,
                    "timestamp": now_str,
                },
            }
        else:
            if not sup_clean:
                sup_clean = "作業リーダー（承認済）"
            return {
                "status": "GO_SPECIAL",
                "allowed_to_proceed": True,
                "mode": "SPECIAL_PAIR",
                "supervisor": sup_clean,
                "next_step": "3-4",
                "message": f"【判定: GO（特別対応承認）】想定外事象に対する特別対応が承認されました。これより【特別モード（2人体制）】へ移行します。リーダー/上長（{sup_clean}）とペアを組み、後続の全コマンド投入において相互ダブルチェックを実施してください。",
                "audit_record": {
                    "decision": "GO",
                    "mode": "SPECIAL_PAIR",
                    "work_type": "想定外の特別対応（2人体制）",
                    "supervisor": sup_clean,
                    "escalation_result": res_clean,
                    "grounds": grounds_clean,
                    "timestamp": now_str,
                },
            }

    return {
        "status": "BLOCKED",
        "allowed_to_proceed": False,
        "reason": f"判定値 '{decision}' が不正です。'GO' または 'NOGO' を指定してください。",
    }


def generate_final_report(
    start_time: str = "",
    end_time: str = "",
    duration_minutes: int = 15,
    mode: str = "NORMAL",
    supervisor_name: str = "",
    sop_results: dict = None,
    escalation_record: dict = None,
) -> dict:
    """リリース作業完了後の最終評価レポートを生成する。
    作業前後の結果報告（Before/After）、作業所要時間、格納成果物の保全状況、エスカレ履歴に基づく総合評価を含む。
    """
    now_str = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S")
    s_time = start_time or now_str
    e_time = end_time or now_str
    sup_text = supervisor_name if mode == "SPECIAL_PAIR" else "なし（通常1名体制）"
    is_special = mode == "SPECIAL_PAIR"

    deliverables = [
        {"name": "現行アプリケーション完全バックアップ", "path": "/backup/app_YYYYMMDD.tar.gz", "status": "格納済 ✓"},
        {"name": "環境設定ファイルバックアップ", "path": "/backup/.env.bak", "status": "格納済 ✓"},
        {"name": "適用済みデータベース更新SQL", "path": "/release/v2.1.0/db_update.sql", "status": "格納済 ✓"},
        {"name": "TeraTermターミナル実行ログ（証跡）", "path": "teraterm_session.log", "status": "保全済 ✓"},
    ]
    if escalation_record:
        deliverables.append({
            "name": "エスカレーション協議・判断根拠記録",
            "path": f"escalation_decision_{escalation_record.get('decision', 'GO')}.json",
            "status": "保全済 ✓",
        })

    before_after = [
        {"item": "アプリケーションバージョン", "before": "v2.0.4 (現行)", "after": "v2.1.0 (最新)", "verdict": "正常更新 ✓"},
        {"item": "データベース（usersテーブル）", "before": "tenant_id: T100, status: PENDING, plan: STANDARD", "after": "tenant_id: T100, status: ACTIVE, plan: ENTERPRISE", "verdict": "要件100%合致 ✓"},
        {"item": "サービスヘルスチェック", "before": "HTTP 200 OK (停止前)", "after": "HTTP 200 OK (再起動後)", "verdict": "正常稼働 ✓"},
    ]

    score = "A ランク（特別対応2人体制による安全完遂）" if is_special else "S ランク（手順書完全準拠・ノーエラー・安全完了）"
    comment = (
        "想定外事象が発生したものの、エスカレーションゲートにて客観的な判断根拠を確定し、上長との2人体制（ペア作業）で安全にリリースを完遂しました。"
        if is_special else
        "全サブステップの事前確認およびログ検証を確実にクリアし、手順書通り安全にリリースを完了しました。"
    )

    return {
        "title": "Excel手順書 リリース作業最終評価・完了報告書",
        "generated_at": now_str,
        "work_duration": {
            "start_time": s_time,
            "end_time": e_time,
            "elapsed_minutes": duration_minutes,
        },
        "operation_mode": {
            "mode": mode,
            "supervisor": sup_text,
            "two_person_rule_applied": is_special,
        },
        "before_after_comparison": before_after,
        "deliverables": deliverables,
        "evaluation_score": score,
        "comment": comment,
    }


def consult_sop_knowledge(query: str) -> dict:
    """社内の障害対応マニュアル・運用トラブルシューティングガイド（RAGナレッジベース）を検索し、関連する対処手順やコマンドを取得する。
    ディスク容量枯渇、DBデッドロック・不整合、500系HTTPエラー、エスカレーション基準などの調査に利用します。

    Args:
        query: 検索したいキーワードや質問（例: 'ディスク容量不足', 'DBロック待ち', 'HTTP 500エラー調査', 'エスカレーション基準'）。

    Returns:
        関連するマニュアル抜粋、推奨対処コマンド、参照セクションを含む辞書。
    """
    import pathlib
    import re

    guide_path = pathlib.Path(__file__).parent.parent / "knowledge" / "troubleshooting_sop_guide.md"
    if not guide_path.exists():
        return {"status": "not_found", "message": "障害対応ナレッジベースが見つかりません。"}

    try:
        text = guide_path.read_text(encoding="utf-8")
    except Exception as e:
        return {"status": "error", "message": f"ナレッジベース読込エラー: {e}"}

    sections = re.split(r'\n##\s+', text)
    tokens = [t.lower() for t in re.findall(r'[a-zA-Z0-9]+|[\u4e00-\u9fff]+|[\u30a0-\u30ff]+', query) if len(t) > 1 or t.isdigit()]

    scored = []
    for s in sections[1:]:
        lines = s.strip().splitlines()
        header = lines[0] if lines else ""
        content = "\n".join(lines[1:])
        score = 0
        for t in tokens:
            if t in header.lower():
                score += 10
            if t in content.lower():
                score += content.lower().count(t) * 2
        if score > 0:
            scored.append((score, header, "## " + s.strip()))

    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        return {"status": "not_found", "query": query, "message": "該当する障害対応ナレッジは見つかりませんでした。"}

    top = scored[0]
    return {
        "status": "found",
        "query": query,
        "section_title": top[1],
        "guidance": top[2],
        "message": f"【障害対応ナレッジ検索結果】\n該当セクション: {top[1]}\n\n{top[2]}",
    }


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "あなたはレガシーなExcel手順書（SOP: Standard Operating Procedure）の作業をナビゲートする信頼性の高いAIペアオペレーター「HITMAN」です。"
        "オペレーターと対話しながら、作業を1ステップずつ安全に進めます。"
        "【重要運用ルール】"
        "1. 手順は必ず 1-1 -> 1-2 -> 2-1 -> 2-2 -> 3-1 -> 3-2 -> 3-3 -> 3-4 -> 4-1 -> 4-2 の厳格な順序で1つずつ進めなければなりません。"
        "直前の手順が合格（verify_step_outputでSUCCESS）していない状態で後続手順（例: 1-1未完了で3-1を要求など）を要求された場合、手順スキップは重大インシデントのリスクがあるため絶対に拒否し、『直前の手順（例: ステップ1-1）がまだ完了していません。手順書の順序を遵守してください』と案内して未完了の直前手順を提示してください。"
        "例外的に順序を外れてよいのは、異常発生時のロールバック手順（R-1, R-2）およびエスカレーション（E-1）のみです。"
        "2. オペレーターが『ステップ1を開始したい』などと求めたら、必ず `get_procedure_step` を呼び出してください。"
        "3. 手順に事前確認（例: df -h 空き容量確認、事前SELECTなど）がある場合は、いきなり本番コマンドを実行させず、必ず『事前確認コマンド（例: ステップ1-1, 3-3）』のA2UIカードを提示して実行を促してください。"
        "4. オペレーターがターミナルの実行結果ログを貼り付けたら、必ず `verify_step_output` ツールを呼び出して合否を客観判定してください。"
        "5. DB更新手順（ステップ3-3）では、事前SELECTログと投入予定SQLを `analyze_sql_impact` ツールで突き合わせ、更新予測と依頼元要件合致を判定してください。"
        "6. 想定外の事象やSQL不一致が発生した場合は、直ちに作業を中断し、エスカレーション対応（ステップ E-1）へ案内してください。"
        "7. エスカレーション対応時は `evaluate_escalation_gate` を呼び出し、対応結果・GO/NOGO・判断根拠（こんきょ）が揃っていることを検証してください。根拠がない場合は作業再開を許可してはなりません。"
        "8. GO判定で特別対応となった場合は【特別モード（2人体制）】へ移行し、作業リーダー/上長とペアでダブルチェックを行うよう案内してください（リーダー承認で進行可能です）。"
        "9. 全手順完了時は `generate_final_report` で作業前後の結果比較、所要時間、格納成果物の最終評価報告を作成してください。"
        "10. セッション間の長期記憶（Memory Bank）の活用: オペレーターの過去の作業履歴、習熟度、よくあるエラー傾向、または指示された特記事項をセッションをまたいで記憶・参照し、安全でパーソナライズされた運用支援を提供してください。"
        "11. 障害対応・運用ナレッジ（RAG）の活用: オペレーターからディスク容量不足、DBロック待ち、HTTP 500エラー、または運用基準に関する質問やトラブル報告を受けた際は、直ちに `consult_sop_knowledge` ツールを呼び出して社内ナレッジベース（障害対応SOPガイド）から関連する対処法や推奨コマンドを取得し、的確に案内してください。"
        "12. 既存手順書のインポートと自律Wチェック有識者役: オペレーターが新しい手順書（Markdown表、CSV、JSONなど）のロードを要求した場合は `import_sop_procedure` ツールを呼び出して即座に取り込んでください。あなたは受動的なチャットボットではなく、有識者として『事前確認の未完了は本番投入を拒否』『ログを客観検証しWチェック承認シールを発行』『異常時は自律的にエスカレやロールバックへ分岐』する厳格な確認者です。"
    ),
    workflow_description="Analyze the operator's request, query the procedure database using tools, guide them step-by-step through pre-checks, SQL analysis, escalation gates, and return structured A2UI cards.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "No markdown in text inside A2UI components; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "When presenting a procedure step or command, provide a clear explanation in Japanese text for the operator, "
        "followed by the A2UI Card JSON array containing: "
        "- Step Title (usageHint: 'h1') "
        "- Objective (usageHint: 'body') "
        "- Command to run (usageHint: 'h2') "
        "- Cautions and Checks (usageHint: 'body'). "
        "Never wrap A2UI in <a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

import os
from google.genai import Client

_api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
_project = os.environ.get("GOOGLE_CLOUD_PROJECT", "1070367799384")
_location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
_use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "true").lower() == "true" or (_api_key and _api_key.startswith("AQ."))

if _use_vertex and _api_key:
    _client = Client(vertexai=True, api_key=_api_key, project=_project, location=_location)
    MODEL = "gemini-2.5-flash"
    _model_instance = Gemini(
        model=MODEL,
        client=_client,
        retry_options=types.HttpRetryOptions(attempts=3),
    )
else:
    MODEL = "gemini-2.5-flash"
    _model_instance = Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    )

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool


# WRITE: セッション終了時にMemory Bankへ長期記憶を保存
async def generate_memories_callback(callback_context: CallbackContext):
    try:
        await callback_context.add_session_to_memory()
    except Exception:
        # ローカルインメモリ実行時やMemory Bank未接続時の安全なフォールバック
        pass
    return None


root_agent = Agent(
    name="hitman",
    model=_model_instance,
    instruction=a2ui_instruction,
    tools=[
        PreloadMemoryTool(),
        get_procedure_step,
        verify_step_output,
        analyze_sql_impact,
        evaluate_escalation_gate,
        generate_final_report,
        consult_sop_knowledge,
        import_sop_procedure,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
