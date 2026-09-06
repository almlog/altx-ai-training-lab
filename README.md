<div align="center">

# 🚀 AltX AI Training Lab
### 株式会社ＡｌｔＸ 社内AIアプリ開発実践研修 ＆ 実務実証基盤
**Google ADK & Gemini 3.6 Flash で創るエンタープライズAIエージェント**

<br/>

[![Organization](https://img.shields.io/badge/Organization-AltX%20Inc.%20(%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE%EF%BC%A1%EF%BD%8C%EF%BD%94%EF%BC%B8)-0052CC)](https://www.altx.co.jp/)
[![Developer](https://img.shields.io/badge/Developer-Shunpei%20Suzuki%20(AltX%20Inc.)-blue)](mailto:suzuki.shunpei@altx.co.jp)
[![Engine](https://img.shields.io/badge/Model-Gemini%203.6%20Flash-34A853?logo=googlecloud)](https://cloud.google.com/vertex-ai)
[![Framework](https://img.shields.io/badge/Framework-Google%20ADK%201.5.0-FBBC05)](https://google.github.io/adk-docs/)
[![Production URL](https://img.shields.io/badge/Production-Cloud%20Run%20(Live)-34A853?logo=googlecloud)](https://altx-hitman-cockpit-1070367799384.us-central1.run.app)
[![Tests](https://img.shields.io/badge/Tests-31%2F31%20Passed-brightgreen)](https://github.com/almlog/altx-ai-training-lab)

<br/>

<sub>💡 本プロジェクトは、Google Cloud「Build with Gemini World Tour」の知見・アーキテクチャをベースに、<br/>
株式会社ＡｌｔＸ（AltX Inc.）の社内教育カリキュラムとして **鈴木 駿平（Shunpei Suzuki）が独自に設計・開発した研修プラットフォーム** です。</sub>

</div>

---

## 📖 研修コンセプト：全員がHITMANを作るのではない

本研修の目的は、全員が同じHITMANを複製・スクラッチ開発することではありません。

1. **HITMAN Cockpit（公式ペアオペレーター）**:
   - 鈴木 駿平が設計・開発し、Cloud Run 上で本番稼働中（`gemini-3.6-flash` 駆動）。
   - 受講生はユーザーとしてアクセスし、Excel手順書（.xlsm）やSOPを進行、安全チェックとWチェック承認を経て、「検証済みプロンプト」を取得します。
2. **アンチグラビティ（Antigravity）へのコピペ体験**:
   - 受講生は自身の **個人Googleアカウントで払い出した有料APIキー** を設定したアンチグラビティにプロンプトを投入。
   - 裏側で待機する **Skills（M0〜M5 ガバナンス研修、開発・デプロイスキル）** が自律的に処理を完遂する様を体験します。
3. **思い思いのオリジナルツールを開発・デプロイする体験**:
   - スキルとAIの力を体感した受講生は、自らの現場課題を解決する **「自分専用のAIツール・エージェント」** をアンチグラビティと共に企画・実装し、各自の Cloud Run 環境へデプロイします。

---

## 🌟 公式プラットフォーム：HITMAN Cockpit

👉 **本番稼働 URL (Cloud Run)**:  
**[https://altx-hitman-cockpit-1070367799384.us-central1.run.app](https://altx-hitman-cockpit-1070367799384.us-central1.run.app)**

```text
[受講者 / オペレーターのブラウザ]
             │
             ▼ (HTTPS: https://altx-hitman-cockpit-1070367799384.us-central1.run.app)
┌─────────────────────────────────────────────────────────────┐
│ Cloud Run サービス: altx-hitman-cockpit                     │
│  ├─ 左右2画面 Web Cockpit (FastAPI Proxy + A2UI レンダラー)  │
│  │   ├─ 左ペイン: AI対話チャット & A2UI リッチカード        │
│  │   └─ 右ペイン: 手順進捗バー、SQL影響評価、エスカレゲート │
│  └─ HITMAN ADK Agent Core (Gemini 3.6 Flash 推論 / Global)  │
│      ├─ 現場標準Excel手順書エンジン (.xlsm マクロ対応)      │
│      ├─ ログ客観自動判定 (verify_step_output)               │
│      ├─ SQL事前影響評価 (analyze_sql_impact)                │
│      ├─ エスカレーション・ゲート制御 (evaluate_escalation)  │
│      ├─ 最終評価完了報告書 (generate_final_report)          │
│      ├─ 長期記憶 (Memory Bank / PreloadMemoryTool)          │
│      └─ 障害対応ナレッジベース (RAG / consult_sop_knowledge)│
└─────────────────────────────────────────────────────────────┘
```

---

## 📚 社内研修カリキュラム (`TRAINING_GUIDE.md`)

受講生は、本リポジトリに同梱されている **[`TRAINING_GUIDE.md`](./TRAINING_GUIDE.md)** に沿って以下の全10マイルストーンを実践します：

| マイルストーン | 学習内容・実践タスク |
|---|---|
| **マイルストーン 1** | **個人GCPプロジェクト作成と課金の有効化**（初心者の最重要関門・トラブル回避） |
| **マイルストーン 2** | **個人有料APIキー発行と種別の理解**（Vertex AI Express `AQ...` と AI Studio `AIza...`） |
| **マイルストーン 3** | **クラウド必須APIの一括有効化**（`aiplatform`, `run`, `cloudbuild`, `artifactregistry`） |
| **マイルストーン 4** | **HITMAN Cockpit 操作とプロンプト取得**（Excel .xlsm 投入、パラメータ解決、Wチェック） |
| **マイルストーン 5** | **アンチグラビティ投入と裏側SKILL体感**（M0〜M5 ガバナンス・セキュリティ検証） |
| **マイルストーン 6** | **思い思いのツール企画**（`pick-your-agent-project` によるアイデアの具現化） |
| **マイルストーン 7** | **エージェントコード＆フロントエンド実装**（ADK Agent + A2UI + FastAPI） |
| **マイルストーン 8** | **テスト自動化による品質保証**（Pytest による 31件全テスト Green） |
| **マイルストーン 9** | **自作ツールの Cloud Run 本番デプロイ**（受講生個人GCP環境への即時URL発行） |
| **マイルストーン 10** | **成果物の発表と共有**（GitHub リポジトリプッシュとチーム内デモ） |

---

## 🗂️ リポジトリ構成

```text
altx-ai-training-lab/
├── TRAINING_GUIDE.md         # ★社内研修用 完全ハンズオンガイド（全10マイルストーン）
├── README.md                 # ★本ドキュメント
├── hitman/                   # ★公式プロダクト: AIペアオペレーター・コックピット
│   ├── app/                  # ADK エージェントコア (agent.py: gemini-3.6-flash, excel_parser.py)
│   ├── frontend/             # 2画面 Web Cockpit (main.py, static/index.html)
│   ├── knowledge/            # 障害対応 SOP ガイドナレッジ & 実務標準 .xlsm
│   └── tests/                # 自動テストスイート (unit/ 27件, integration/ 4件 = 計31件)
└── .agents/
    └── skills/               # ★アンチグラビティが裏で活用する実践スキル群
        ├── novasmart-governance-lab/ # AltX AIガバナンス＆セキュリティ実践研修 (M0〜M5)
        ├── pick-your-agent-project/  # 受講生の思い思いのツール企画支援
        ├── build-agent-frontend/     # A2UI 対応フロントエンド構築
        ├── enable-a2ui/              # A2UI リッチカード統合
        ├── build-rag/                # RAG エンジン構築
        └── setup-memory-bank/        # 長期記憶 Memory Bank セットアップ
```

---

## 📄 ライセンス・著作権

Copyright (c) 2026 Shunpei Suzuki (AltX Inc.) All Rights Reserved.  
Based on Google ADK / A2UI frameworks under Apache License 2.0.
