# HITMAN: SOP Navigation & AI Pair Operator Cockpit

**開発・設計**: 鈴木 駿平 (Shunpei Suzuki) <suzuki.shunpei@altx.co.jp>  
**所属**: 株式会社ＡｌｔＸ (AltX Inc.)  
**Copyright**: (c) 2026 Shunpei Suzuki (AltX Inc.) All Rights Reserved.  
**本番稼働 URL (Cloud Run)**: [https://altx-hitman-cockpit-1070367799384.us-central1.run.app](https://altx-hitman-cockpit-1070367799384.us-central1.run.app)

---

## 🎯 プロジェクト概要

**HITMAN** は、ミッションクリティカルなシステム移行・夜間リリース作業において、ヒューマンエラーによるシステム障害（コマンド誤投入、WHERE句欠落による全件更新、確認漏れ）を技術的に防ぐ **AIペアオペレーター・コックピット** です。

従来の「手順書を人間が目視で読み、手動でコマンドをコピペし、手作業でログを確認する」運用を刷新し、**Google ADK (Agent Development Kit)** と **Gemini 2.5 Flash** の推論能力を統合。左右2画面の専用コックピットを通じて、安全かつ客観的なリリース作業を実現します。

---

## 🌟 主要機能

1. **厳格なステップ順序制御（Anti-Skip Gate）**:
   - 1-1 から 4-2 までの工程を厳密に順序立てて管理。直前ステップのログ検証（SUCCESS）なしに後続手順を実行させません。
2. **事前確認（Pre-check）の強制**:
   - ディスク空き容量確認（df -h）や事前SELECTなどの事前確認を完了するまで、本番コマンドの実行を許可しません。
3. **SQL影響事前評価エンジン (nalyze_sql_impact)**:
   - 投入予定SQLの対象テーブル、更新カラム、WHERE句の安全性、事前SELECT結果との整合性をAIが事前突き合わせ評価。
4. **客観的判断根拠を要求するエスカレーション・ゲート (evaluate_escalation_gate)**:
   - 異常発生時、協議結果・GO/NOGO・客観的判断根拠（こんきょ）の入力がない限り作業再開を遮断。GO判定時は作業リーダー承認のもと【特別モード（2人体制）】へ移行。
5. **最終評価完了報告書 (generate_final_report)**:
   - 作業前後の状態（Before/After）、所要時間、保全成果物（バックアップ、SQL、ログ）をまとめた完了報告書を自動生成。
6. **長期記憶（Memory Bank）**:
   - PreloadMemoryTool とセッション保存コールバックにより、過去の作業履歴やオペレーターの傾向をセッション間で永続保持。
7. **RAGナレッジ検索 (consult_sop_knowledge)**:
   - ディスク枯渇、DBデッドロック、500エラー等のトラブルシューティングナレッジをプレーン関数ツール経由で即時検索。
8. **2画面 Web Cockpit (FastAPI + A2UI)**:
   - 左ペイン: AI対話チャット & A2UIリッチカード
   - 右ペイン: 手順進捗ステータス、SQL影響評価フォーム、エスカレ解除ゲート、最終評価レポート

---

## 🏗️ アーキテクチャ

`
[Web Browser]
      │
      ▼ (HTTPS: https://altx-hitman-cockpit-1070367799384.us-central1.run.app)
┌─────────────────────────────────────────────────────────────┐
│ Cloud Run Container (FastAPI + Static Cockpit UI)           │
│  ├─ / : 2画面操作コックピット (static/index.html)            │
│  ├─ /chat : A2UI レンダラー対応 AI 対話エンドポイント        │
│  └─ /api/* : SOP進捗、SQL評価、エスカレ、最終レポートAPI    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼ (ADK Runner)
┌─────────────────────────────────────────────────────────────┐
│ HITMAN ADK Agent (app/agent.py)                             │
│  ├─ Gemini 2.5 Flash (Client / Vertex AI Express Mode)      │
│  ├─ PreloadMemoryTool (Memory Bank 長期記憶)                │
│  ├─ SOP Database (手順書定義)                               │
│  ├─ verify_step_output (ログ自動判定)                       │
│  ├─ analyze_sql_impact (SQL影響事前評価)                    │
│  ├─ evaluate_escalation_gate (ゲート制御)                   │
│  ├─ generate_final_report (完了報告)                        │
│  └─ consult_sop_knowledge (RAG ナレッジ検索)                │
└─────────────────────────────────────────────────────────────┘
`

---

## 🧪 テスト実行

`ash
uv run pytest
`
- 全21件のユニットテストおよび結合テストが自動検証されます。

---

## 🚀 ローカル起動

`ash
# 依存関係インストール
uv sync

# フロントエンドコックピット起動 (ポート 3000)
uv run python frontend/main.py
`
ブラウザで http://127.0.0.1:3000 にアクセスすると、ローカル環境でコックピットが利用可能です。

---
**© 2026 Shunpei Suzuki (AltX Inc.)**
