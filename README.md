<div align="center">

# 🚀 AltX AI Training Lab
### 株式会社ＡｌｔＸ 社内AIアプリ開発実践研修 ＆ 実務実証基盤
**Google ADK (Agent Development Kit) & Gemini 2.5 Flash で創るエンタープライズAIエージェント**

<br/>

[![Organization](https://img.shields.io/badge/Organization-AltX%20Inc.%20(%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE%EF%BC%A1%EF%BD%8C%EF%BD%94%EF%BC%B8)-0052CC)](https://www.altx.co.jp/)
[![Developer](https://img.shields.io/badge/Developer-Shunpei%20Suzuki%20(AltX%20Inc.)-blue)](mailto:suzuki.shunpei@altx.co.jp)
[![Based on](https://img.shields.io/badge/Reference-Google%20Build%20with%20Gemini%20(Track%203)-4285F4?logo=google)](https://cszhu.github.io/build-with-gemini/)
[![Engine](https://img.shields.io/badge/Model-Gemini%202.5%20Flash-34A853?logo=googlecloud)](https://cloud.google.com/vertex-ai)
[![Framework](https://img.shields.io/badge/Framework-Google%20ADK%201.5.0-FBBC05)](https://google.github.io/adk-docs/)
[![Deployment](https://img.shields.io/badge/Production-Cloud%20Run%20(Live)-34A853?logo=googlecloud)](https://altx-hitman-cockpit-1070367799384.us-central1.run.app)
[![Tests](https://img.shields.io/badge/Tests-21%2F21%20Passed-brightgreen)](https://github.com/almlog/altx-ai-training-lab)

<br/>

<sub>💡 本プロジェクトは、Google Cloud 公式の「Build with Gemini World Tour · Track 3 (Agent-First Apps)」の知見・アーキテクチャを参考に、<br/>
株式会社ＡｌｔＸ（AltX Inc.）の社内研修カリキュラムおよび実務運用向けに **鈴木 駿平（Shunpei Suzuki）が独自に再構築・設計・開発したオリジナル研修・実証リポジトリ** です。</sub>

</div>

---

## 📖 研修の背景と目的

企業のDXやシステム運用現場では、いまだ「Excel手順書を目視確認し、ターミナルに手動でコマンドを投入し、ログを目視判定する」という旧来の作業形態が残っており、ヒューマンエラーによるシステム障害のリスクが常に存在します。

本研修（**AltX AI Training Lab**）では、受講生各自が個人の Google アカウントを用いて独立したクラウド環境を構築し、最新の生成AIフレームワークである **Google ADK (Agent Development Kit)** と **Gemini 2.5 Flash** を駆使して、現場の課題を技術的に解決する **「AIペアオペレーター・コックピット（HITMAN）」** をゼロから開発・テスト・クラウド本番デプロイまで自走して習得します。

---

## 🌟 オリジナル開発プロダクト：HITMAN

本リポジトリの中核成果物として、鈴木 駿平が設計・開発した **HITMAN: SOP Navigation & AI Pair Operator Cockpit** が含まれています。

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
│  └─ HITMAN ADK Agent Core (Gemini 2.5 Flash 推論)           │
│      ├─ 手順書エンジン (SOP Database: Step 1-1 〜 4-2)      │
│      ├─ ログ客観自動判定 (verify_step_output)               │
│      ├─ SQL事前影響評価 (analyze_sql_impact)                │
│      ├─ エスカレーション・ゲート制御 (evaluate_escalation)  │
│      ├─ 最終評価完了報告書 (generate_final_report)          │
│      ├─ 長期記憶 (Memory Bank / PreloadMemoryTool)          │
│      └─ 障害対応ナレッジベース (RAG / consult_sop_knowledge)│
└─────────────────────────────────────────────────────────────┘
```

### HITMAN の主要機能
1. **厳格なステップ順序制御（Anti-Skip Gate）**: 直前手順のログ検証（`SUCCESS`）なしに後続手順へのスキップをブロック。
2. **事前確認（Pre-check）の強制**: ディスク容量（`df -h`）や事前SELECTが通るまで本番コマンドを出力しない安全設計。
3. **SQL影響事前評価エンジン**: UPDATE/DELETE文の対象テーブル、更新対象列、WHERE句条件をAIが事前検証し事故を防止。
4. **客観的判断根拠を要求するエスカレーション・ゲート**: 異常発生時、協議結果・GO/NOGO・客観的判断根拠（こんきょ）が入力されない限り作業再開を遮断。上長承認で特別モード（2人体制）へ移行。
5. **最終評価完了報告書**: Before/After、所要時間、成果物保全状況（バックアップ、ログ）のレポートを自動生成。
6. **長期記憶（Memory Bank）**: セッションを跨いでオペレーターの作業履歴や特記事項を保持。
7. **RAG ナレッジベース**: ディスク枯渇、DBロック待ち、500エラーの障害対応ナレッジを即時検索（Gemini 2.5 の競合を回避するプレーン関数ツール構成）。

---

## 📚 社内研修カリキュラム (`TRAINING_GUIDE.md`)

受講生は、本リポジトリに同梱されている **[`TRAINING_GUIDE.md`](./TRAINING_GUIDE.md)** に沿って以下の全10マイルストーンを実践します：

| マイルストーン | 学習内容・実践タスク |
|---|---|
| **マイルストーン 1** | **GCPプロジェクト作成と課金の有効化**（初心者の最重要関門・トラブル回避） |
| **マイルストーン 2** | **APIキー発行と種別の理解**（AI Studio `AIza...` と Vertex AI Express `AQ...` の違い） |
| **マイルストーン 3** | **クラウド必須APIの一括有効化**（`aiplatform`, `run`, `cloudbuild`, `artifactregistry`） |
| **マイルストーン 4** | **ADK エージェントの設計とツール実装**（プロンプト、SOPツール、ログ検証） |
| **マイルストーン 5** | **セッション長期記憶（Memory Bank）の統合**（`PreloadMemoryTool` とコールバック） |
| **マイルストーン 6** | **RAG（障害対応ナレッジ）の実装**（Gemini 2.5 におけるスキーマ競合 400 エラーの回避策） |
| **マイルストーン 7** | **2画面 Web Cockpit の立ち上げ**（FastAPI プロキシ ＆ A2UI レンダラー） |
| **マイルストーン 8** | **テスト自動化による品質保証**（Pytest によるユニット・結合 21件テスト） |
| **マイルストーン 9** | **Cloud Run へのワンコマンド本番デプロイ**（Dockerfile設計、即時URL発行） |
| **マイルストーン 10** | **GitHub へのプッシュと成果物提出** |

---

## 🗂️ リポジトリ構成

```text
altx-ai-training-lab/
├── TRAINING_GUIDE.md         # ★社内研修用 完全ハンズオンガイド（全10マイルストーン）
├── hitman/                   # ★独立プロダクト: AIペアオペレーター・コックピット
│   ├── app/                  # ADK エージェントコア (agent.py, fast_api_app.py, a2ui_utils.py)
│   ├── frontend/             # 2画面 Web Cockpit (main.py, static/index.html)
│   ├── knowledge/            # 障害対応 SOP ガイドナレッジ (RAG検索対象)
│   ├── tests/                # 自動テストスイート (unit/ 16件, integration/ 4件, dummy 1件 = 計21件)
│   ├── Dockerfile            # Cloud Run 本番用コンテナ定義
│   ├── .dockerignore         # ビルド高速化除外設定
│   ├── .env.example          # 受講生用 設定テンプレート（秘匿情報保護）
│   ├── pyproject.toml        # 依存関係定義 (ADK, FastAPI, Uvicorn, Pytest)
│   └── README.md             # HITMAN 固有ドキュメント
├── .agents/skills/           # 研修で使用するエージェント開発支援スキル群
│   ├── build-agent-frontend/ # フロントエンド作成・Cloud Run連携スキル
│   ├── enable-a2ui/          # A2UI リッチカード生成スキル
│   ├── setup-memory-bank/    # Vertex AI Memory Bank 導入スキル
│   ├── build-rag/            # RAG ナレッジ構築スキル
│   ├── troubleshoot-lab-setup/# 環境検証・トラブルシューティングスキル
│   └── publish-to-github/    # GitHub 公開・提出スキル
└── project_brief.md          # プロジェクト企画設計書
```

---

## ⚡ クイックスタート（受講生向け）

### 1. リポジトリのクローン
```bash
git clone https://github.com/almlog/altx-ai-training-lab.git
cd altx-ai-training-lab/hitman
```

### 2. 依存関係のインストール
```bash
# uv パッケージマネージャーを使用
uv sync
```

### 3. 環境変数の設定
```bash
cp .env.example .env
# .env を開き、自身が発行した Vertex AI Express キー (AQ...) または AI Studio キーを設定
```

### 4. 自動テストの実行
```bash
uv run pytest
# 全21件のテストが Green になることを確認
```

### 5. ローカルコックピットの起動
```bash
uv run python frontend/main.py
# ブラウザで http://127.0.0.1:3000 にアクセス
```

---

## 📄 著作権・開発者情報

- **開発・設計・監修**: 鈴木 駿平 (Shunpei Suzuki)
- **所属**: 株式会社ＡｌｔＸ (AltX Inc.)
- **連絡先**: `suzuki.shunpei@altx.co.jp`
- **Copyright**: Copyright (c) 2026 Shunpei Suzuki (AltX Inc.) All Rights Reserved.
- **Reference**: Based on the concepts and architecture of Google Cloud's Build with Gemini World Tour (Track 3), restructured for enterprise training.
