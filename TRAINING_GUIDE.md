# AltX 社内AIアプリ開発実践研修カリキュラム
## 〜 Google ADK & Gemini で創るエンタープライズAIエージェント・コックピット 〜

**開発・監修**: 株式会社ＡｌｔＸ（AltX Inc.） 鈴木 駿平 (Shunpei Suzuki) <suzuki.shunpei@altx.co.jp>  
**著作権**: Copyright (c) 2026 Shunpei Suzuki (AltX Inc.) All Rights Reserved.  
**プロジェクト名**: ltx-ai-training-lab

---

## 1. 研修の目的と全体概要

本研修は、Google の最新エージェントフレームワークである **ADK (Agent Development Kit)** と **Gemini 2.5 Flash** を駆使し、レガシーな運用現場（Excel手順書、TeraTermログ確認、本番DB更新など）の課題を根本解決する「AIペアオペレーター・コックピット（HITMAN）」の設計・開発・テスト・クラウド本番デプロイまでを一気通貫で体験する実践研修です。

受講者は各自の個人 Google アカウントを用いて独立したクラウド環境を構築し、プロトタイプから本番運用レベルのコンテナデプロイまでを自らの手で完成させます。

### システムアーキテクチャ
`
[受講者 / オペレーターのブラウザ]
             │
             ▼ (HTTPS / Cloud Run)
┌─────────────────────────────────────────────────────────────┐
│ HITMAN Ops Assistant Cockpit (FastAPI Proxy + 2-Pane UI)   │
│  ├─ 左ペイン: リアルタイムAIチャット & A2UI リッチカード     │
│  └─ 右ペイン: 手順進捗バー、SQL影響評価、エスカレゲート      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼ (ADK / In-Process & Agent Engine)
┌─────────────────────────────────────────────────────────────┐
│ ADK Agent (HITMAN Core)                                     │
│  ├─ Gemini 2.5 Flash (LLM推論)                              │
│  ├─ SOP Database (手順書エンジン: Step 1-1 〜 4-2, R-1, E-1)│
│  ├─ ログ客観検証ツール (verify_step_output)                 │
│  ├─ SQL影響予測・要件合致ツール (analyze_sql_impact)        │
│  ├─ エスカレーション・ゲート制御 (evaluate_escalation_gate) │
│  ├─ 最終評価完了報告書 (generate_final_report)              │
│  ├─ 長期記憶 (Memory Bank / PreloadMemoryTool)              │
│  └─ 障害対応ナレッジベース (RAG / consult_sop_knowledge)    │
└─────────────────────────────────────────────────────────────┘
`

---

## 2. 受講者環境の前提条件

- **PC環境**: Windows 10/11 または macOS
- **開発ツール**: Python 3.12+, uv (推奨パッケージマネージャー), Git
- **Google アカウント**: 各受講者個人の Google アカウント（GCP利用可能）

---

## 3. 実践ハンズオン・ステップ（全10マイルストーン）

### 【マイルストーン 1】GCPプロジェクト作成と課金の有効化
※ 初心者が最もつまずきやすい最重要ステップです！

1. [Google Cloud Console](https://console.cloud.google.com/) に個人の Google アカウントでログイン。
2. 画面上部のプロジェクト選択から **「新しいプロジェクト」** をクリック。
   - プロジェクト名: ltx-ai-training-lab（または個人識別可能な名称）
3. **課金（Billing）の紐付け（必須）**:
   - メニューから「お支払い（Billing）」を開き、有効な請求先アカウントをプロジェクトに紐付ける。
   - **注意**: 課金が未設定のプロジェクトでは Vertex AI の推論および Cloud Run のビルドが 403 Forbidden で遮断されます。

### 【マイルストーン 2】APIキーの発行と種別の理解

1. **APIキーの種類**:
   - **AI Studio キー (AIza...)**: Generative Language API (generativelanguage.googleapis.com) 向け。個人開発や手軽な検証用。
   - **Vertex AI Express Mode キー (AQ...)**: Vertex AI (iplatform.googleapis.com) 向け。エンタープライズのクォータと連携する高信頼キー。
2. キーを取得したら、プロジェクトルートの .env ファイルに設定します：
   `ash
   GOOGLE_API_KEY=AQ.xxxx...
   GOOGLE_CLOUD_PROJECT=altx-ai-training-lab
   GOOGLE_CLOUD_LOCATION=us-central1
   GOOGLE_GENAI_USE_VERTEXAI=true
   `

### 【マイルストーン 3】クラウド必須APIの有効化

Cloud Shell またはローカルの gcloud CLI にて以下のコマンドを実行し、必要な API を一括有効化します：

`ash
# Google Cloud CLI へのログイン
gcloud auth login

# プロジェクトの設定
gcloud config set project altx-ai-training-lab

# 必須APIの有効化
gcloud services enable \
  aiplatform.googleapis.com \
  generativelanguage.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
`

### 【マイルストーン 4】ADK エージェントの設計とツール実装

pp/agent.py にエージェントのプロンプトとビジネスロジックを関数ツールとして実装します。

1. **ステップ順序の厳格制御（ルール1）**: 前ステップの検証が合格していない場合、手順スキップを拒否する。
2. **事前確認コマンドの強制**: 本番コマンド前に必ず空き容量（df -h）や事前SELECTを実行させる。
3. **ログ客観検証ツール (erify_step_output)**: ターミナルログから成功・警告・失敗を判定。
4. **SQL事前影響評価 (nalyze_sql_impact)**: 投入予定SQLのWHERE条件と更新予測を事前検証。
5. **エスカレーション・ゲート (evaluate_escalation_gate)**: 判断根拠のない作業再開を遮断。上長・リーダー承認で特別モード（2人体制）へ移行。
6. **最終評価報告書 (generate_final_report)**: 作業所要時間、Before/After、成果物保全状況をレポート化。

### 【マイルストーン 5】セッション長期記憶（Memory Bank）の統合

過去の作業セッションで得られたオペレーターの習熟度や注意点を記憶するため、ADKの Memory Bank 機構を導入します：

`python
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.agents.callback_context import CallbackContext

async def generate_memories_callback(callback_context: CallbackContext):
    try:
        await callback_context.add_session_to_memory()
    except Exception:
        pass # ローカル実行時のフォールバック

root_agent = Agent(
    name="hitman",
    tools=[PreloadMemoryTool(), ...],
    after_agent_callback=generate_memories_callback,
    ...
)
`

### 【マイルストーン 6】RAG（障害対応ナレッジベース）の実装と注意点

> ⚠️ **Gemini 2.5 のツール競合ルール（超重要）:**
> Vertex AI の組み込み RAG（VertexAiRagRetrieval）は、Gemini 2.5 では他のカスタム関数ツール（A2UIやSOPツール）と同時に渡すと 400 Bad Request INVALID_ARGUMENT エラーとなります。
> そのため、RAGナレッジの検索は **プレーンな Python 関数ツール（consult_sop_knowledge）** として定義し、自然言語クエリから社内マニュアルを検索して回答する構成にします。

### 【マイルストーン 7】2画面インタラクティブWebコックピット

rontend/main.py と rontend/static/index.html により、以下の2画面コックピットを立ち上げます：
- **左画面**: AIペアオペレーターとの対話チャット（A2UIリッチカード表示）
- **右画面**: 手順進捗バー、事前SQL影響評価フォーム、エスカレーション・ゲート解除パネル、最終評価レポート出力

### 【マイルストーン 8】自動テストによる品質保証（Pytest）

テスト駆動で品質を担保するため、全機能のユニットテストと結合テストを実行します：
`ash
uv run pytest
`
- 全21件のテストが Green（合格）になることを確認します。

### 【マイルストーン 9】Cloud Run へのワンコマンド本番デプロイ

自作した AI コックピットを世界中からアクセス可能な Cloud Run へデプロイします：

`ash
# Dockerfile と .dockerignore を準備し、以下を実行
gcloud run deploy altx-hitman-cockpit \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_API_KEY=AQ.xxx,GOOGLE_CLOUD_PROJECT=altx-ai-training-lab,GOOGLE_CLOUD_LOCATION=us-central1,GOOGLE_GENAI_USE_VERTEXAI=true"
`

デプロイ完了後に出力される Service URL (https://altx-hitman-cockpit-xxxx.run.app) をブラウザで開けば、受講生の開発したコックピットが本番稼働します！

### 【マイルストーン 10】GitHubへのプッシュと共有

開発したリポジトリを受講生各自の GitHub アカウントにプッシュし、成果物として提出・ポートフォリオ化します。

---

## 4. 講師・研修生向け FAQ & トラブルシューティング

| 症状 / エラー | 原因 | 解決手順 |
|---|---|---|
| 403 PERMISSION_DENIED | GCPプロジェクトの課金が未有効、またはAPI未有効 | マイルストーン1と3を確認し、課金紐付けと gcloud services enable を実行 |
| gcloud: このシステムではスクリプトの実行が無効 | Windows PowerShell の ExecutionPolicy 制約 | Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force を実行 |
| A2UI が空白または JSON 文字列で表示される | A2UI スキーママネージャーのプロンプト不整合 | BasicCatalog の指定と fter_model_callback の戻り値構造を確認 |
| Cloud Build のアップロードが極端に遅い | .venv やキャッシュがアップロードに含まれている | .dockerignore に .venv/ や __pycache__/ を追加して除外 |

---
**© 2026 Shunpei Suzuki (AltX Inc.)**
