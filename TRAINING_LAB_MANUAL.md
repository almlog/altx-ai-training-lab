# AltX 社内AI実践研修 公式ハンズオンマニュアル
## 〜 HITMAN Cockpit と AntiGravity で創る「A2UI駆動 自律型AIエージェント」開発・デプロイ実践 〜

**開発・監修**: 株式会社ＡｌｔＸ（AltX Inc.） 鈴木 駿平 (Shunpei Suzuki) <suzuki.shunpei@altx.co.jp>  
**著作権**: Copyright (c) 2026 Shunpei Suzuki (AltX Inc.) All Rights Reserved.  
**プロジェクト名**: `altx-ai-training-lab`  
**HITMAN Cockpit 公式本番URL**: [https://altx-hitman-cockpit-1070367799384.us-central1.run.app](https://altx-hitman-cockpit-1070367799384.us-central1.run.app)  
**公式GitHubリポジトリ**: [https://github.com/almlog/altx-ai-training-lab](https://github.com/almlog/altx-ai-training-lab)  
**対応AIモデル**: `gemini-3.8-flash`（優先）/ `gemini-3.6-flash`（フォールバック）  

---

## 目次

1. [はじめに & 本ラボで習得すること](#1-はじめに--本ラボで習得すること)
2. [3者協調アーキテクチャ（エージェントの混同を避ける！）](#2-3者協調アーキテクチャエージェントの混同を避ける)
3. [環境のセットアップ & 前提条件](#3-環境のセットアップ--前提条件)
4. [スターターリポジトリと Skills & MCP の完全解説](#4-スターターリポジトリと-skills--mcp-の完全解説)
5. [HITMAN Cockpit と AntiGravity の伴走メカニズム](#5-hitman-cockpit-と-antigravity-の伴走メカニズム)
6. [受講コースの選択（コースA vs コースB）](#6-受講コースの選択コースa-vs-コースb)
7. [実践ハンズオン: ステップ T-1 〜 T-6 完全ウォークスルー](#7-実践ハンズオン-ステップ-t-1--t-6-完全ウォークスルー)
   - [Step T-1: 開発環境構築とスキル・MCP同期](#step-t-1-開発環境構築とスキルmcp同期)
   - [Step T-2: コース別 要件定義（Project Brief策定 / 仕様設計）](#step-t-2-コース別-要件定義project-brief策定--仕様設計)
   - [Step T-3: エージェントコア・拡張機能＆A2UI実装](#step-t-3-エージェントコア拡張機能a2ui実装)
   - [Step T-4: ローカルテスト＆自律Wチェック（品質保証）](#step-t-4-ローカルテスト自律wチェック品質保証)
   - [Step T-5: Cloud Run 本番デプロイ＆フロントエンド連携](#step-t-5-cloud-run-本番デプロイフロントエンド連携)
   - [Step T-6: 個人GitHub公開＆研修修了報告書発行](#step-t-6-個人github公開研修修了報告書発行)
8. [ストレッチゴール（高度な応用機能）](#8-ストレッチゴール高度な応用機能)
9. [トラブルシューティング & FAQ](#9-トラブルシューティング--faq)

---

## 1. はじめに & 本ラボで習得すること

本ラボでは、Google Cloud の最先端 AI ツール群（Google ADK、A2UI、Vertex AI Agent Platform、Cloud Run、AntiGravity 2.0）を活用し、**「プロダクション環境で安全に動作する、A2UI 駆動の自律型エージェントアプリケーション全体」**を構築・運用する実践的スキルを習得します。

### 本研修で行うこと：
- **Google ADK (Agent Development Kit)** を使用した Python エージェントコアの実装
- **A2UI (Agent-to-UI v0.8)** を動力とする、エージェント駆動型リッチカードフロントエンドの構築
- **Memory Bank（セッション横断長期記憶）** と **Persistent Storage（Firestore / GCS）** の装備
- **RAG Engine（サーバーレスベクトル検索コーパス）** による社内ドキュメントのグラウンディング
- **生成メディア機能（Gemini 画像生成モデル）** および **セキュアなコード実行サンドボックス** の統合
- **Pytest** による自律 W チェック（自己申告テキストの自動差し戻しと客観ログ検証）
- **Google Cloud Run** へのコンテナデプロイと世界公開
- **個人 GitHub** へのソースコード公開と、HITMAN による最終評価レポート（修了証）の発行

---

## 2. 3者協調アーキテクチャ（エージェントの混同を避ける！）

本研修をスムーズに進める上で、最も重要な原則が **「エージェントの混同を避ける！」** です。
このラボでは、役割の異なる **3者がチームとなって協調作業** を行います。

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                           【3者協調モデル】                              │
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────────┐   │
│   │ ① 指導・品質ゲート管理: HITMAN Cockpit（Cloud Run 本番稼働中）   │   │
│   │    ・手順ステップ（T-1〜T-6）の提示                               │   │
│   │    ・先走り防止ストッパー付きプロンプトの発行                     │   │
│   │    ・成果物ログの客観Wチェック判定（合格承認 / 差し戻し）         │   │
│   │    ・最終評価レポート・修了証の発行                               │   │
│   └────────────────────────────────┬─────────────────────────────────┘   │
│                                    │ ① プロンプト取得                     │
│                                    ▼                                     │
│   ┌──────────────────────────────────────────────────────────────────┐   │
│   │ ② 操作者・意思決定者: 受講生（あなた）                           │   │
│   │    ・HITMANからプロンプトをワンクリックコピー                     │   │
│   │    ・AntiGravityのチャット欄へ投入                               │   │
│   │    ・AntiGravityの生成物を確認し、エビデンスをHITMANへ提出       │   │
│   └────────────────────────────────┬─────────────────────────────────┘   │
│                                    │ ② プロンプト投入                     │
│                                    ▼                                     │
│   ┌──────────────────────────────────────────────────────────────────┐   │
│   │ ③ 開発・作業担当: AntiGravity 2.0 (AGY)（ローカルAIペアプログラマ）│   │
│   │    ・gemini-3.8-flash (優先) / 3.6-flash で自律動作              │   │
│   │    ・専用フォルダ（altx-agent-workspace）内でのファイル作成・編集 │   │
│   │    ・Skills (.agents/skills/) & MCP の自律活用                   │   │
│   │    ・テスト実行、Cloud Run デプロイ、GitHub プッシュ             │   │
│   └──────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
```

- **HITMAN とは？**: 株式会社ＡｌｔＸが開発した「現場標準SOP AIペアオペレーター」です。受講生を導き、ステップごとの品質を客観的に判定する「教官・審査官」の役割を果たします。
- **AntiGravity (AGY) とは？**: Google のエージェント型次世代 IDE です。受講生の指示（プロンプト）を受けて、実際にコードを書き、ツールを作り、コマンドを実行する「開発実務パートナー」です。
- **受講生（あなた）とは？**: 全体の指揮を執り、HITMAN のゲートチェックを通過しながら AntiGravity と共にアプリケーションを完成させる「プロジェクトリーダー・エンジニア」です。

---

## 3. 環境のセットアップ & 前提条件

受講前に、以下の事前準備を各自の PC で完了させてください（詳細は [PREREQUISITES.md](./PREREQUISITES.md) 参照）。

### 【最低受講要件（4大必須事項）】
1. **個人 Google アカウント**: `@gmail.com` 等の個人アカウント。
2. **有料 API キーの設定**:
   - Google Cloud Console の [Vertex AI Studio] ➡️ [API キー] より発行した **Vertex AI Express Mode キー**（推奨、先頭が `AQ.`）、または Google AI Studio キー（先頭が `AIza`）。
   - クレジットカードまたは事前入金の請求先アカウント（Billing）が紐付いていること。
3. **AntiGravity 2.0 (agy) のインストール**:
   - AntiGravity を起動し、Google アカウントでログイン認証が完了していること。
4. **Python (3.11 または 3.12+)**:
   - ターミナルで `python --version` が実行できること。

### クラウド必須 API の有効化（Google Cloud CLI）
```bash
# Google Cloud CLI へのログイン
gcloud auth login
gcloud auth application-default login

# プロジェクトの設定
gcloud config set project <あなたのGCPプロジェクトID>

# 必須APIの一括有効化
gcloud services enable   aiplatform.googleapis.com   generativelanguage.googleapis.com   run.googleapis.com   cloudbuild.googleapis.com   artifactregistry.googleapis.com   firestore.googleapis.com   storage.googleapis.com
```

---

## 4. スターターリポジトリと Skills & MCP の完全解説

AntiGravity 2.0 の真骨頂は、**Skills（技能）** と **MCP（Model Context Protocol）** による能力拡張にあります。
受講生が講師リポジトリ（`https://github.com/almlog/altx-ai-training-lab.git`）をクローンすると、以下の武器が自動的に装備されます。

### ① Skills（`.agents/skills/`）とは？
Skills は、特定のタスクをプロレベルで実行するための **「手順・ベストプラクティス・テンプレートコードのバンドル」** です。AntiGravity は受講生のプロンプトやコンテキストに応じて、適切なスキルを自律的にロードして実行します。

| スキル名 | 格納パス | 役割と提供機能 |
| :--- | :--- | :--- |
| **`pick-your-agent-project`** | `.agents/skills/pick-your-agent-project/` | 受講生の現場課題を対話形式でブレインストーミングし、ツール構成・メモリ・UI仕様を棚卸しして `project_brief.md` を自動策定する。 |
| **`enable-a2ui`** | `.agents/skills/enable-a2ui/` | Google ADK エージェントに A2UI (v0.8) リッチカード表示機能を装備する。`a2ui_utils.py` の `after_model_callback` 接続テンプレートを提供。 |
| **`build-agent-frontend`** | `.agents/skills/build-agent-frontend/` | ブラウザとエージェントを A2A プロトコルで中継する FastAPI プロキシおよび A2UI レンダラー付きチャットフロントエンドを構築する。 |
| **`memory-bank-setup`** | `.agents/skills/setup-memory-bank/` | Vertex AI Memory Bank を用いて、セッションを跨いでユーザーの好みや業務事実を永続記憶する長期記憶ハーネスをエージェントに装備する。 |
| **`rag-engine-setup`** | `.agents/skills/build-rag/` | サーバーレス Vertex AI RAG Engine コーパスを作成し、大容量ドキュメントに対するセマンティック検索ツールを構築する。 |
| **`publish-to-github`** | `.agents/skills/publish-to-github/` | GitHub CLI (gh) のデバイス認証フローを用いて、安全に受講生個人の GitHub へパブリックリポジトリを作成・プッシュする。 |
| **`troubleshoot-lab-setup`** | `.agents/skills/troubleshoot-lab-setup/` | 403 PERMISSION_DENIED、IAMロール不足、API未有効化などの環境エラーを自律診断・自動修復する。 |
| **`novasmart-governance-lab`**| `.agents/skills/novasmart-governance-lab/`| AIガバナンス・セキュリティ研修（シャドウエージェント検知、IAM分離、Model Armor防護、監査ログ）を実践する。 |

---

### ② MCP（Model Context Protocol）とは？
MCP は、AntiGravity が外部のデータソースや API 仕様と安全に通信するためのオープンスタンダードです。本ラボでは `.agents/mcp_config.json` により以下の 2 つの MCP サーバーが常時接続されます。

1. **`Developer Knowledge MCP` (`developerknowledge_*`)**:
   - Google Cloud、Vertex AI、Google ADK、Firebase の公式ドキュメントおよび最新 API 仕様を AntiGravity が直接クエリできるナレッジエンジン。
   - **メリット**: AI が古い記憶や推測（ハルシネーション）でコマンドを打つことを防ぎ、常に最新かつ正確なコードを生成します。
2. **`Firebase MCP` (`firebase_*`)**:
   - サーバーレス NoSQL データベースである Cloud Firestore と AntiGravity を直接接続。
   - **メリット**: アプリケーション用のコレクション作成、スキーマ設計、シードデータの投入を自然言語で実行可能にします。

---

## 5. HITMAN Cockpit と AntiGravity の伴走メカニズム

自律型 AI（AntiGravity）は非常に優秀ですが、大きなプロンプトを 1 つ渡すと **「気を利かせて実装からテスト・デプロイまで勝手に一気に先走り（自走し）てしまう」** という性質があります。これでは受講生が何が起きているか理解できず、学習効果が失われてしまいます。

そこで、HITMAN Cockpit が **「品質ゲート管理（関所）」** として伴走します。

```text
  [HITMAN Cockpit]                                          [AntiGravity]
         │                                                        │
         ├────── 1. 先走り防止ストッパー付きプロンプトを提示 ────>│
         │                                                        ├─ 指定ステップのみ集中実行
         │                                                        ├─ マイルストーン成果物を生成
         │                                                        └─ 「後続は待機」して完了報告
         │<───── 2. 受講生が特定成果物（エビデンス）を提出 ───────┤
         │
   [客観Wチェック判定]
   ・自己申告（「できました」等）は厳格差し戻し
   ・成果物シグネチャを客観検証
         │
         ├─【合格承認 (VERIFIED_APPROVED)】
         ▼
   次ステップのプロンプトをアンロック！
```

### 3つの伴走ルール:
1. **先走り防止ストッパー（Gate Instruction）**:
   HITMAN が発行する各ステップのプロンプト末尾には、「**今回はステップ T-○ のみを実施し、後続の実装やデプロイは受講生の確認を待つこと**」という制約が必ず埋め込まれています。
2. **提出エビデンスの特定**:
   受講生が HITMAN に何を貼り付ければ合格になるのか（ログ、Markdown、URLなど）を 1 つに特定して案内します。
3. **二刀流の客観 W チェック**:
   受講生が「AntiGravity のチャット回答テキスト」を貼っても、「ターミナルでコマンドを実行した生ログ」を貼っても、HITMAN の判定エンジンが正確に検証して合格判定を出します。

---

## 6. 受講コースの選択（コースA vs コースB）

HITMAN Cockpit（画面左上）で「🎓 研修モード」を選択すると、以下の 2 大コースを切り替えるボタンが表示されます。受講生自身の状況に合わせて選択してください。

```text
┌──────────────────────────────────────┐  ┌──────────────────────────────────────┐
│ 🚀 【コースA】オリジナルAIツール開発  │  │ 🛡️ 【コースB】HITMANクローン構築    │
├──────────────────────────────────────┤  ├──────────────────────────────────────┤
│ ・対象: 自分の現場課題を解決したい方 │  │ ・対象: 何を作るか決まっていない方   │
│ ・内容: pick-your-agent-project スキ │  │ ・内容: 手順書パーサー、客観Wチェッ  │
│   ルで要件を棚卸し、自分専用の自作AI │  │   ク、A2UIカード、エスカレ制御を備え │
│   エージェントを企画・開発・公開。   │  │   たペアオペレーター自身を自作・公開 │
└──────────────────────────────────────┘  └──────────────────────────────────────┘
```

---

## 7. 実践ハンズオン: ステップ T-1 〜 T-6 完全ウォークスルー

これより、実際の研修カリキュラムである **ステップ T-1 〜 T-6** の具体的な操作手順を解説します。

---

### Step T-1: 開発環境構築とスキル・MCP同期

#### 【作業目的】
AntiGravity のモデル設定を行い、専用作業フォルダ（`altx-agent-workspace`）を作成して講師リポジトリをクローンし、Skills 群および MCP サーバーを同期・認識させます。

#### 【HITMAN での操作】
1. HITMAN Cockpit で「🎓 研修モード」を選択。
2. ステップ `T-1` のカードにある **`[📋 AGYプロンプトをコピー]`** ボタンをクリック。

#### 【AntiGravity に投入するプロンプト】
```text
【AntiGravity投入用プロンプト: Step T-1】
あなたは株式会社AltXのAI研修専属メンターです。
1. モデル選定: チャットのモデル設定でまず「gemini-3.8-flash」を選択してください。エラーや利用不可の場合は「gemini-3.6-flash」を選択してください。
2. 作業ディレクトリ: 「altx-agent-workspace」を作成し、以後のファイル作成や作業はすべてこのフォルダ内で行ってください。
3. リポジトリクローン:
   git clone https://github.com/almlog/altx-ai-training-lab.git
   を実行し、リポジトリ内の .agents/skills/ にある研修スキル群（pick-your-agent-project, build-agent-frontend, enable-a2ui 等）および .agents/mcp_config.json を読み込んで自己学習してください。
4. 準備完了の確認: Pythonバージョン（3.11/3.12+）およびAPIキー疎通確認テストを行い、実行結果ログを出力してください。
【重要制約】今回は環境構築とスキル同期のみを行ってください。エージェントの実装やデプロイはまだ行わず、準備完了ログを出力して待機してください。
```

#### 【AntiGravity の動作】
- ターミナルで `mkdir altx-agent-workspace && cd altx-agent-workspace` を実行。
- `git clone https://github.com/almlog/altx-ai-training-lab.git` を実行。
- Python および Gemini API への疎通テストを実行し、結果を表示。

#### 【HITMAN へ貼り付ける提出エビデンス】
AntiGravity が出力した「環境確認ログ」またはターミナルでのクローン実行ログをコピーし、HITMAN のチャット欄に貼り付けて送信します：
```text
Cloning into 'altx-ai-training-lab'...
remote: Enumerating objects: 120, done.
Python 3.12.10
Gemini API Connection: SUCCESS (Model: gemini-3.8-flash)
Skills loaded: pick-your-agent-project, enable-a2ui, build-agent-frontend, memory-bank-setup, rag-engine-setup, publish-to-github
```

#### 【HITMAN の Wチェック判定】
- **合格 (VERIFIED_APPROVED)**: 「専用作業ディレクトリの作成、講師リポジトリのクローン、およびスキル同期を確認しました！」と承認され、ステップ T-2 がアンロックされます。
- **差し戻し**: 「環境構築完了しました」等の自己申告テキストのみの場合、「客観的なターミナル実行ログが検知できません」と差し戻されます。

---

### Step T-2: コース別 要件定義（Project Brief策定 / 仕様設計）

#### 【作業目的】
エージェントの目的、現場課題、必要な関数ツール、A2UIカード表示仕様、長期記憶方針を定義し、設計書（`project_brief.md` または `hitman_spec.md`）を作成します。

#### 【HITMAN での操作】
ステップ `T-2` のカードで **`[📋 AGYプロンプトをコピー]`** をクリック。

#### 【AntiGravity に投入するプロンプト】
**【コースA: オリジナルAIツールの場合】**
```text
【AntiGravity投入用プロンプト: Step T-2】
スキル「pick-your-agent-project」を活用して、私が現場で抱える課題を解決するオリジナルAIエージェントの企画・要件定義を作成してください。
私の課題・作りたいもの: （※例: クラウドログ監視と異常検知、障害一次切り分けボット、社内規程FAQなど）
以下の項目を含む「altx-agent-workspace/project_brief.md」を作成し、内容を出力してください：
1. エージェント名と目的（解決する現場課題）
2. 使用するモデル（gemini-3.8-flash または 3.6-flash）
3. 必要な関数ツール（自作ツール最低1つ）
4. A2UIカード表示仕様（カードレイアウト、表示項目）
5. 長期記憶（Memory Bank）活用方針
【重要制約】今回は project_brief.md の策定のみを行ってください。Pythonコードの実装やデプロイはまだ行わないでください。
```

**【コースB: HITMANクローンの場合】**
```text
【AntiGravity投入用プロンプト: Step T-2 (HITMANクローン)】
AIペアオペレーター「HITMAN」クローンの仕様を設計します。
1. Excel/CSV手順書を読み込むデータ構造
2. ターミナルログを検証するWチェック判定ルール（正常合格、エラー検知、自己申告遮断）
3. 上長協議エスカレーションゲートの仕様
以上の設計を「altx-agent-workspace/hitman_spec.md」として作成し、内容を出力してください。
【重要制約】今回は仕様書作成のみを行い、実装コードの生成はまだ待機してください。
```

#### 【HITMAN へ貼り付ける提出エビデンス】
AntiGravity が出力した `project_brief.md`（または `hitman_spec.md`）の Markdown テキスト全体を HITMAN のチャット欄に貼り付けます。

#### 【HITMAN の Wチェック判定】
- **合格 (VERIFIED_APPROVED)**: エージェント名、課題、ツール設計、A2UIカード仕様が確認され、ステップ T-3 がアンロックされます。

---

### Step T-3: エージェントコア・拡張機能＆A2UI実装

#### 【作業目的】
Google ADK (Python) を用いてエージェント本体（`agent.py`）をコーディングし、自作関数ツール、外部ストレージ、長期記憶、RAG、および A2UI カードコールバックを実装します。

#### 【HITMAN での操作】
ステップ `T-3` のカードで **`[📋 AGYプロンプトをコピー]`** をクリック。

#### 【AntiGravity に投入するプロンプト】
```text
【AntiGravity投入用プロンプト: Step T-3】
project_brief.md の定義に基づき、Google ADK (Python) で自作エージェントを実装してください。
作業ディレクトリ: altx-agent-workspace/my_agent/
スキル「enable-a2ui」および「google-agents-cli-adk-code-ja」を参照し、以下を構築してください：
1. agent.py:
   - Google ADK Agent (MODEL: gemini-3.8-flash / 3.6-flash)
   - 自作関数ツール（ログ解析、API連携、計算処理など）
   - A2UI カードコールバック (after_model_callback=a2ui_callback)
2. a2ui_utils.py: スキル enable-a2ui から A2UI v0.8 コールバックを配置
3. pyproject.toml / requirements.txt: 依存パッケージ定義
ファイルを生成後、ディレクトリ構造と agent.py の先頭30行を出力してください。
【重要制約】今回はコード実装のみを行ってください。テストの実行やデプロイはまだ行わないでください。
```

#### 【高度な機能拡張（必要に応じて指示）】
- **長期記憶の追加**: 「スキル `memory-bank-setup` を使用して、Vertex AI Memory Bank による長期記憶を追加して」
- **RAGの追加**: 「スキル `rag-engine-setup` を使用して、参照ドキュメントに対するセマンティック検索ツールを追加して」
- **Firestoreの追加**: 「Firebase MCP を使用して、Firestore データベースへの読み書きツールを追加して」
- **画像生成の追加**: 「`gemini-3.1-flash-lite-image` モデルを使って、ドメインアイテムの画像を生成し Cloud Storage に保存するツールを追加して」

#### 【HITMAN へ貼り付ける提出エビデンス】
AntiGravity が出力した `my_agent/` のファイル構成、または `agent.py` のコード先頭部分を HITMAN に貼り付けます：
```python
# altx-agent-workspace/my_agent/agent.py
from google.adk.agents import Agent
from google.adk.models import Gemini
from app.a2ui_utils import a2ui_callback

MODEL = "gemini-3.8-flash"
root_agent = Agent(
    name="my_custom_agent",
    model=Gemini(model=MODEL),
    tools=[my_custom_tool],
    after_model_callback=a2ui_callback,
)
```

#### 【HITMAN の Wチェック判定】
- **合格 (VERIFIED_APPROVED)**: ADK Agent、関数ツール、A2UI コールバックの実装が客観確認され、ステップ T-4 がアンロックされます。

---

### Step T-4: ローカルテスト＆自律Wチェック（品質保証）

#### 【作業目的】
エージェントの関数ツール、A2UIカード生成、および「自己申告テキストの自動差し戻し機能」を検証する Pytest 単体テストを実行し、全件 PASSED を確認します。

#### 【HITMAN での操作】
ステップ `T-4` のカードで **`[📋 AGYプロンプトをコピー]`** をクリック。

#### 【AntiGravity に投入するプロンプト】
```text
【AntiGravity投入用プロンプト: Step T-4】
altx-agent-workspace/my_agent/ に対する単体テスト（tests/test_agent.py）を作成し、pytest を実行してください。
テスト項目:
1. 正常系: 関数ツールの呼び出しと正しい戻り値の検証
2. A2UIカード: after_model_callback による A2UI v0.8 カードの生成検証
3. Wチェック安全性: 「完了しました」のような中身のないテキストが正しく差し戻されることの検証
全テストを実行し、ターミナルの pytest 実行結果ログを出力してください。
```

#### 【HITMAN へ貼り付ける提出エビデンス】
ターミナルまたは AntiGravity に出力された **Pytest 実行結果ログ** をそのまま貼り付けます：
```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1
collected 5 items

tests/test_agent.py::test_tool_execution PASSED                          [ 20%]
tests/test_agent.py::test_a2ui_card_rendering PASSED                     [ 40%]
tests/test_agent.py::test_w_check_pure_assertion_rejected PASSED         [ 60%]
tests/test_agent.py::test_error_handling PASSED                          [ 80%]
tests/test_agent.py::test_agent_response PASSED                          [100%]

============================== 5 passed in 0.24s ==============================
```

#### 【HITMAN の Wチェック判定】
- **合格 (VERIFIED_APPROVED)**: 全テストが PASSED であることを検知し、ステップ T-5（デプロイ）がアンロックされます。
- **不合格・進行ブロック (BLOCKED_RETRY)**: テストが 1 件でも `FAILED` または `ERROR` の場合、「単体テストでエラーが検知されました。修正して全件PASSEDとなるまでデプロイへは進めません」と進行がブロックされます。

---

### Step T-5: Cloud Run 本番デプロイ＆フロントエンド連携

#### 【作業目的】
完成したエージェントのフロントエンド（FastAPI + A2UI レンダラー）を構築し、Google Cloud Run へコンテナデプロイして本番公開 URL を発行します。

#### 【HITMAN での操作】
ステップ `T-5` のカードで **`[📋 AGYプロンプトをコピー]`** をクリック。

#### 【AntiGravity に投入するプロンプト】
```text
【AntiGravity投入用プロンプト: Step T-5】
スキル「build-agent-frontend」および「google-agents-cli-deploy-ja」を活用して、作成したエージェントを Google Cloud Run へデプロイしてください。
1. frontend/ の配置: FastAPI プロキシ、チャットUI (static/index.html)、A2UI レンダラーの構築
2. サービスアカウント権限: Cloud Run サービスアカウントに roles/aiplatform.user を付与
3. デプロイコマンドの実行:
   gcloud run deploy my-custom-agent      --source altx-agent-workspace/my_agent      --region us-central1      --allow-unauthenticated
4. 発行された本番公開サービスURL（https://...run.app）を出力してください。
```

#### 【HITMAN へ貼り付ける提出エビデンス】
デプロイ完了時にターミナルに出力された **Cloud Run Service URL** を含むログを貼り付けます：
```text
Building Container... done
Creating Revision... done
Routing traffic... done
Service [my-custom-agent] revision [my-custom-agent-00001-abc] has been deployed.
Service URL: https://my-custom-agent-1070367799384.us-central1.run.app
```

#### 【HITMAN の Wチェック判定】
- **合格 (VERIFIED_APPROVED)**: 本番稼働 URL（`https://...run.app`）を検知し、「Cloud Run への本番デプロイと公開URLの発行を確認しました！」と承認され、最終ステップ T-6 がアンロックされます。

---

### Step T-6: 個人GitHub公開＆研修修了報告書発行

#### 【作業目的】
完成した自作 AI エージェントのソースコードを受講生自身の個人 GitHub アカウントへオープンソース公開し、HITMAN Cockpit から最終研修修了報告書を発行・保全します。

#### 【HITMAN での操作】
ステップ `T-6` のカードで **`[📋 AGYプロンプトをコピー]`** をクリック。

#### 【AntiGravity に投入するプロンプト】
```text
【AntiGravity投入用プロンプト: Step T-6】
スキル「publish-to-github」を活用して、完成したエージェントのソースコードを私の個人GitHubリポジトリへ公開（Public）してください。
1. gh auth login（デバイス認証）による個人GitHubログイン（ワンタイムコードを表示）
2. リポジトリ作成: altx-ai-[アプリ名] として新規パブリックリポジトリを作成
3. .gitignore の確認とシークレットスキャン（APIキー等の漏洩防止）
4. コミット＆プッシュの実行
5. 公開されたリポジトリURL（https://github.com/...）を出力してください。
```

#### 【HITMAN へ貼り付ける提出エビデンス】
個人 GitHub へのプッシュ完了ログ、またはリポジトリ URL（`https://github.com/<あなたのユーザー名>/...`）を貼り付けます：
```text
Enumerating objects: 45, done.
To https://github.com/suzuki-shunpei/altx-ai-ops-agent.git
 * [new branch]      main -> main
Repository URL: https://github.com/suzuki-shunpei/altx-ai-ops-agent
```

#### 【HITMAN の最終修了承認 ＆ 修了証発行】
- **全研修工程 修了承認 (VERIFIED_APPROVED ✓✓)**:
  「🎉【全研修工程 修了認定・Wチェック承認】🎉 受講生ご自身の個人GitHubへのリポジトリ公開を確認しました！自作AIエージェントの企画から本番デプロイ・オープンソース公開まで完走しました！」と祝福メッセージが表示されます。
- **最終評価レポートの出力**:
  画面右上の **「📊 最終評価レポート」** ボタンをクリックすると、全ステップの実行日時・合否結果・所要時間・成果物エビデンスがまとめられた **公式研修修了報告書（Markdown / 印刷対応）** を即座に出力・保存できます。

---

## 8. ストレッチゴール（高度な応用機能）

基礎カリキュラムを早く完走した受講生は、以下の応用機能に挑戦してみましょう。

### 1. 動画生成モデル Omni (`gemini-omni-flash-preview`)
静止画の代わりに、エージェントが短い動画クリップ（.webm / .mp4）を生成するツールを追加できます：
```text
global リージョンで Google の Omni モデル (gemini-omni-flash-preview) を使用して、
エージェントのドメイン内アイテムの短い動画を生成するツールを追加してください。
```

### 2. Cloud Trace による分散トレーシング
Cloud Run 上で動作するエージェントの LLM 推論時間、ツール実行時間、ネットワークレイテンシを Google Cloud Console の [Cloud Trace] でリアルタイムに可視化・分析します。

### 3. デモ動画の自動レコーディング（`record-demo` スキル）
スキル `record-demo` を呼び出し、ヘッドレスブラウザで自作チャットフロントエンドを自動操作して、ブランドフレーム付きのデモ動画（.webm / GIF）を生成します：
```bash
node .agents/skills/record-demo/record-agent.js -q "おすすめのレシピは？" -o demo.webm
```

---

## 9. トラブルシューティング & FAQ

| 症状 / エラーメッセージ | 主な原因 | 解決手順 |
| :--- | :--- | :--- |
| **403 PERMISSION_DENIED** | 個人 GCP プロジェクトの請求先アカウント（Billing）が未設定、または API が無効 | Cloud Console の「お支払い」でカードまたは無料枠の紐付けを確認し、`gcloud services enable aiplatform.googleapis.com` を再実行。 |
| **AntiGravity で毎回確認ダイアログが出る** | Review モードになっている | AntiGravity の設定（⚙️）の Agent Settings から **Tool Execution Policy** を **`Always Proceed`**（または Turbo）に変更。 |
| **A2UI カードが表示されず生 JSON になる** | コールバック（`a2ui_utils.py`）が未接続、または Token Streaming が ON になっている | 1. `agent.py` の `after_model_callback` に `a2ui_callback` が設定されているか確認。<br>2. ブラウザの設定で Token Streaming を OFF に切り替え。 |
| **ステップ T-4 でテストが失敗（FAILED）する** | 関数の戻り値型やインポートパスの不整合 | エラーログを AntiGravity に貼り付け、「この pytest エラーを修正してください」と依頼してコードを修正し、再実行。 |
| **Cloud Run デプロイで 403 Forbidden** | サービスアカウントに `roles/aiplatform.user` 権限がない | `gcloud projects add-iam-policy-binding` コマンドで、Cloud Run のサービスアカウントに `roles/aiplatform.user` を付与。 |
| **GitHub 認証でブラウザが開かない** | リモート環境での認証制約 | 表示されたワンタイムコードと `https://github.com/login/device` を手元の PC / スマホで開いて入力し認証完了。 |

---

**監修**: 株式会社ＡｌｔＸ（AltX Inc.） 鈴木 駿平 (Shunpei Suzuki) <suzuki.shunpei@altx.co.jp>  
**著作権**: Copyright (c) 2026 Shunpei Suzuki (AltX Inc.) All Rights Reserved.
