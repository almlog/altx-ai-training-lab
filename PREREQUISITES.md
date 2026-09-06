# 🛠️ 受講者 事前準備・前提スキル・PC環境ガイド
## 〜 株式会社ＡｌｔＸ 社内AI実践研修（HITMAN & アンチグラビティ）〜

**監修・作成**: 株式会社ＡｌｔＸ（AltX Inc.） 鈴木 駿平 (Shunpei Suzuki) <suzuki.shunpei@altx.co.jp>  
**対象**: 本研修に参加するすべての受講生（研修当日の3日前までに必ず完了してください）

---

## 📌 はじめに（重要なお知らせ）

本研修では、講師から**共有のGoogleアカウントや開発用PCの貸与はありません**。  
受講生各自が **個人のPC環境・個人のGoogleアカウント** を使用し、各自で発行した **有料APIキー（または課金設定済みGCPプロジェクト）** を用いて、AIエージェントの開発・デプロイを実践します。

研修当日に環境構築で時間を浪費しないよう、**必ず受講前日までに以下の【最低受講条件（4大必須要件）】をすべて満たし、動作確認を完了させてください**。

---

## 1. 🚨 最低受講条件（4大必須要件）

以下の 4 項目が揃っていない場合、研修当日のハンズオン（API呼び出し、コード生成、Cloud Runデプロイ）を進めることができません。

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                     【受講のための4大必須条件】                         │
├─────────────────────────────────────────────────────────────────────────┤
│  1. 個人Googleアカウントの所持（@gmail.com 等）                         │
│  2. 有料APIキーの発行（クレジットカード紐付け or 事前入金の請求先設定） │
│  3. アンチグラビティ（Google AntiGravity / agy）のインストール・認証    │
│  4. Python（3.11 または 3.12+）のインストールおよびターミナル実行確認   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 🎯 受講者に求められる最低限のスキル

本研修は「AIペアプログラミング」を活用するため、高度なアルゴリズムの実装経験は不要ですが、以下の**基本操作・基礎知識**があることを前提に進めます：

| スキル分野 | 最低限求められるレベル | 具体的な操作例 |
|:---|:---|:---|
| **ターミナル / CLI 操作** | コマンドの入力・実行、パスの概念、環境変数の設定ができる | `cd` による移動、`ls` / `dir` による確認、`export` / `$env:` での環境変数設定 |
| **Python の基礎** | Pythonスクリプトを実行でき、エラーが出た際にメッセージを読める | `python app.py` の実行、インデントの概念、ライブラリの `pip` / `uv` インストール |
| **Git / GitHub** | リポジトリのクローン、コミット、プッシュができる（個人GitHubアカウント所持） | `git clone`、`git add`、`git commit`、`git push` |
| **Web / クラウドの基本知識** | URL、HTTPステータス（200, 403, 500等）、APIキーの役割を理解している | ブラウザでのWebアプリ操作、開発者ツールの表示、JSONデータの構造 |

---

## 3. 💻 推奨PC環境・ネットワーク要件

| 項目 | 最低要件 | 推奨環境 | 備考 |
|:---|:---|:---|:---|
| **OS** | Windows 10 (64bit) / macOS 12+ | Windows 11 / macOS 最新版 | Linux (Ubuntu 22.04+) も可 |
| **CPU** | 4コア以上 | 8コア以上 (Intel Core i5/i7, AMD Ryzen 5/7, Apple M系) | コンテナビルドやローカル実行が快適になります |
| **メモリ (RAM)** | 8 GB | **16 GB 以上** | 8GBの場合、ブラウザとIDEで負荷が高くなることがあります |
| **ストレージ** | 10 GB 以上の空き容量 | 20 GB 以上の空き容量 (SSD) | Python仮想環境、Dockerイメージキャッシュ等 |
| **ネットワーク** | 安定したインターネット回線 | 高速ブロードバンド / Wi-Fi | テザリングは容量消費にご注意ください |
| **社内制限への留意** | - | プロキシやVPN、端末制限の確認 | 会社の貸与PCの場合、外部APIアクセスやソフトウェアインストールが制限されていないか事前に情シスへご確認ください |

---

## 4. 📝 ステップ・バイ・ステップ 事前セットアップ手順

### 【Step 1】Googleアカウントの準備と請求先アカウント（Billing）の設定
1. 個人の Google アカウント（`@gmail.com` 等）を用意します。
2. [Google Cloud Console](https://console.cloud.google.com/) にアクセスします。
3. **お支払い（Billing）の設定**:
   - メニュー ➡️「お支払い」を開き、**有効なクレジットカードの登録**、または **事前入金（前払い）** による請求先アカウントを設定します。
   - ※新規アカウントの場合は $300分の無料トライアルクレジットが利用可能です。
   - ⚠️ **課金が未設定の場合、Vertex AI および Cloud Run のAPI呼び出しがすべて拒否（403 Forbidden）されます。**

### 【Step 2】有料APIキーの発行
いずれかの方法で API キーを発行し、安全な場所に控えておいてください。

- **方法 A（推奨: Vertex AI Express Mode キー）**:
  1. Google Cloud Console で新規プロジェクト（例: `altx-ai-training-<名前>`）を作成。
  2. プロジェクトに上記で作成した「お支払い（Billing）」を紐付け。
  3. [Vertex AI Studio] ➡️ [APIキー] より新規キーを作成（先頭が `AQ...` で始まるキー）。
- **方法 B（Google AI Studio キー）**:
  1. [Google AI Studio](https://aistudio.google.com/) に個人のGoogleアカウントでログイン。
  2. 左メニュー「Get API key」➡️「Create API key」をクリック。
  3. 課金が有効なプロジェクトを選択してキーを発行（先頭が `AIza...` で始まるキー）。

### 【Step 3】Python のインストールと動作確認
1. **Python 3.11 または 3.12** をインストールします。
   - Windows: [Python 公式サイト](https://www.python.org/downloads/) からインストーラーをダウンロード。  
     ⚠️ **必ず「Add python.exe to PATH」にチェックを入れてインストールしてください。**
   - macOS: `brew install python@3.12`
2. **高速パッケージマネージャー `uv`（推奨）**:
   - Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - macOS / Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### 【Step 4】アンチグラビティ（Google AntiGravity / agy）の準備
1. Google 公式の **AntiGravity**（IDE または CLI `agy`）をインストールします。
2. インストール後、個人の Google アカウントでサインインを完了させます。
3. ターミナルで `agy --version` またはデスクトップアプリが正常に起動することを確認します。

### 【Step 5】Git のインストールと個人GitHubアカウントの準備
1. [Git 公式サイト](https://git-scm.com/) より Git をインストールします。
2. [GitHub](https://github.com/) の個人アカウントを作成（またはログイン確認）しておきます。
   - 研修の最後（マイルストーン10）で、各自が開発したAIツールのソースコードを自分のGitHubへ公開します。

---

## 5. ✅ 事前セルフチェックシート（当日朝に慌てないために）

ターミナル（WindowsはPowerShell、MacはTerminal）を開き、以下のコマンドを順番に実行してください。  
**すべて成功すれば事前準備は100%完了です！**

```bash
# ① Python の確認（3.11 または 3.12+ が表示されること）
python --version

# ② Git の確認（バージョンが表示されること）
git --version

# ③ APIキー疎通テスト（ご自身のAPIキーに置き換えて実行）
# ※ Windows PowerShell の場合:
$env:GEMINI_API_KEY="あなたのAPIキー"
python -c "import urllib.request, json, os; key=os.getenv('GEMINI_API_KEY'); url=f'https://generativelanguage.googleapis.com/v1beta/models?key={key}'; print('✅ APIキー認証成功！' if urllib.request.urlopen(url).getcode()==200 else '❌ エラー')"

# ※ macOS / Linux の場合:
export GEMINI_API_KEY="あなたのAPIキー"
python3 -c "import urllib.request, json, os; key=os.getenv('GEMINI_API_KEY'); url=f'https://generativelanguage.googleapis.com/v1beta/models?key={key}'; print('✅ APIキー認証成功！' if urllib.request.urlopen(url).getcode()==200 else '❌ エラー')"
```

### チェックリスト
- [ ] 個人Googleアカウントでログインできる
- [ ] クレジットカードまたは事前入金の課金設定が完了している
- [ ] APIキーが発行され、上記の疎通テストで `✅ APIキー認証成功！` と表示された
- [ ] アンチグラビティが起動し、ログインできている
- [ ] `python --version` で 3.11 または 3.12+ が表示される
- [ ] `git --version` で Git が認識されている
- [ ] 個人GitHubアカウントにログインできる
- [ ] HITMAN Cockpit（[https://altx-hitman-cockpit-1070367799384.us-central1.run.app](https://altx-hitman-cockpit-1070367799384.us-central1.run.app)）にブラウザでアクセスできる

---

## 6. ❓ よくあるトラブルと解決策（FAQ）

### Q1. `python` コマンドを打つと Microsoft Store が開いてしまう (Windows)
- **原因**: Windows の「アプリ実行エイリアス」が有効になっており、PythonのPATHが通っていません。
- **対処法**:
  1. Windowsの [設定] ➡️ [アプリ] ➡️ [アプリの詳細設定] ➡️ [アプリ実行エイリアス] を開く。
  2. 「アプリ インストーラー (python.exe)」および「python3.exe」を **オフ** にする。
  3. Pythonインストール時に「Add python.exe to PATH」をオンにして再インストールする。

### Q2. APIキーの疎通テストで 403 Forbidden が返る
- **原因**: 請求先アカウント（クレジットカードまたは事前入金）が設定されていないか、Google Cloud プロジェクトでお支払い情報が有効化されていません。
- **対処法**: [Google Cloud Console お支払い](https://console.cloud.google.com/billing) を確認し、プロジェクトに請求先アカウントがリンクされていることを確認してください。

### Q3. 会社の貸与PCで pip や git がエラーになる / SSL証明書エラーが出る
- **原因**: 会社のセキュリティプロキシやSSL復号化フィルタが通信をブロックしています。
- **対処法**: 自宅のネットワークで事前セットアップを行うか、社内IT管理者（情シス）に本研修で使用する外部通信（Google Cloud / GitHub）の許可を申請してください。

---

事前準備に関してご不明な点がある場合は、研修前日までに講師（鈴木 駿平：`suzuki.shunpei@altx.co.jp`）までお気軽にお問い合わせください。
