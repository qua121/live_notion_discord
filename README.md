# Live Stream Discord Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Architecture: Clean](https://img.shields.io/badge/architecture-clean-green.svg)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
[![API Cost](https://img.shields.io/badge/API%20cost-98%25%20reduced-brightgreen.svg)](https://developers.google.com/youtube/v3/getting-started#quota)

YouTube配信の開始を自動検知してDiscordに通知するPythonアプリケーションです。
**YouTube API使用量を98%削減**した超低コスト設計で、1分間隔の高頻度チェックが可能。
クリーンアーキテクチャに準拠した保守性の高い設計で、VTuberや配信者のファンコミュニティに最適です。

---

## 目次

- [特徴](#特徴)
- [デモ](#デモ)
- [クイックスタート](#クイックスタート)
- [インストール](#インストール)
- [設定](#設定)
- [使用方法](#使用方法)
- [アーキテクチャ](#アーキテクチャ)
- [トラブルシューティング](#トラブルシューティング)
- [FAQ](#faq)
- [開発](#開発)
- [コントリビューション](#コントリビューション)
- [ライセンス](#ライセンス)

---

## 特徴

### コア機能
- ✅ **複数チャンネル同時監視**: 複数のYouTubeチャンネルを同時に監視可能
- ✅ **リッチな通知**: Discord Webhookで埋め込み（Embed）形式の美しい通知を送信
- ✅ **重複通知防止**: 配信状態を永続化し、同じ配信の重複通知を防止
- ✅ **クリーンアーキテクチャ**: 保守性・拡張性・テスタビリティを重視した設計
- ✅ **詳細なログ**: ファイル＆コンソールに詳細なログを出力
- ✅ **カスタマイズ可能**: チェック間隔、メンション、通知色などを柔軟に設定
- ✅ **テストコード完備**: ユニットテスト + 統合テストで品質を保証

### API最適化（v1.1.0）
- 🚀 **超低コストAPI設計**: わずか2 units/回のクォータ消費（一般的な方式の1/50）
- 🚀 **高頻度チェック対応**: 1分間隔の監視でも1日2,880 units（無料枠10,000の30%未満）
- 🚀 **事前作成配信枠対応**: 週初めに複数配信枠を作成するケースにも対応
- 🚀 **自動リトライ機能**: 一時的なネットワークエラーに自動対応（指数バックオフ）

---

## デモ

### 通知イメージ

![Discord通知のサンプル](docs/images/discord-notification-sample.png)
<!-- スクリーンショットを docs/images/ に追加してください -->

### 実行例

```bash
$ python main.py
2026-01-21 20:00:00 - root - INFO - ロギング設定完了
2026-01-21 20:00:00 - __main__ - INFO - YouTube配信監視システムを起動します
2026-01-21 20:00:00 - __main__ - INFO - ============================================================
2026-01-21 20:00:00 - __main__ - INFO - YouTube配信監視システム起動
2026-01-21 20:00:00 - __main__ - INFO - 監視チャンネル数: 2
2026-01-21 20:00:00 - __main__ - INFO - チェック間隔: 60秒
2026-01-21 20:00:00 - __main__ - INFO - ============================================================
2026-01-21 20:00:00 - __main__ - INFO -   - 配信者A (UCxxxxxxxxxxxxxxxxxxxxxx)
2026-01-21 20:00:00 - __main__ - INFO -   - 配信者B (UCyyyyyyyyyyyyyyyyyyyyyy)
2026-01-21 20:00:00 - __main__ - INFO - ============================================================
2026-01-21 20:00:00 - __main__ - INFO - 監視開始（Ctrl+Cで終了）
```

---

## クイックスタート

最速で動かすための3ステップ:

```bash
# 1. 依存関係をインストール
pip install -r requirements.txt

# 2. 環境変数を設定（.envファイル作成）
cp config/.env.example config/.env
# config/.env を編集してYouTube API KeyとDiscord Webhook URLを設定

# 3. 監視対象チャンネルを設定
# config/config.json を編集してチャンネルIDを追加

# 4. 起動
python main.py
```

詳細は[インストール](#インストール)セクションを参照してください。

---

## インストール

### 前提条件

- **Python 3.10以上**
- **YouTube Data API v3のAPIキー**
- **Discord Webhook URL**

### 1. リポジトリのクローン

```bash
git clone https://github.com/YOUR_USERNAME/live-stream-discord-bot.git
cd live-stream-discord-bot
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

**必要なパッケージ:**
- `requests` - Discord Webhook通信用
- `google-api-python-client` - YouTube Data API v3クライアント
- `python-dotenv` - 環境変数管理

### 3. YouTube Data API v3キーの取得

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
3. **APIとサービス** → **ライブラリ** から **YouTube Data API v3** を検索して有効化
4. **認証情報** → **認証情報を作成** → **APIキー** を選択
5. 作成されたAPIキーをコピー

**重要**: APIキーは第三者に公開しないでください。

### 4. Discord Webhookの作成

1. Discordサーバーの設定を開く
2. **連携サービス** → **ウェブフック** → **新しいウェブフック**
3. ウェブフック名を設定（例: `YouTube配信通知`）
4. 通知を送信したいチャンネルを選択
5. **ウェブフックURLをコピー** をクリック

### 5. 環境変数の設定

```bash
cp config/.env.example config/.env
```

`config/.env` を編集:

```env
YOUTUBE_API_KEY=あなたのYouTube API Key
DISCORD_WEBHOOK_URL=あなたのDiscord Webhook URL
```

### 6. 監視対象チャンネルの設定

`config/config.json` を編集:

```json
{
  "check_interval": 60,
  "channels": [
    {
      "id": "UCxxxxxxxxxxxxxxxxxxxxxx",
      "name": "配信者A",
      "mention": "@everyone"
    }
  ],
  "notification": {
    "show_thumbnail": true,
    "color": 16711680,
    "include_end_notification": false
  },
  "log_level": "INFO"
}
```

#### YouTubeチャンネルIDの取得方法

**方法1: チャンネルURLから取得**
```
https://www.youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxx
                             ↑ この部分がチャンネルID
```

**方法2: @ハンドルから取得**
1. `https://www.youtube.com/@channelname` にアクセス
2. ページのソースを表示（Ctrl+U）
3. `"channelId"` で検索
4. `"channelId":"UCxxxxxxxxxxxxxxxxxxxxxx"` を見つける

**注意**: チャンネルIDは必ず **UC で始まる24文字** です。`?si=` などのパラメータは不要です。

---

## 設定

### config/config.json の詳細

| 項目 | 型 | 説明 | デフォルト |
|------|------|------|------------|
| `check_interval` | number | チェック間隔（秒） | 60 |
| `channels[].id` | string | YouTubeチャンネルID（UC始まり24文字） | - |
| `channels[].name` | string | 表示名（任意） | - |
| `channels[].mention` | string | Discordメンション（`@everyone`, `@here`, `<@&ロールID>`） | `@everyone` |
| `notification.color` | number | 埋め込みの色（10進数） | 16711680（赤） |
| `notification.show_thumbnail` | boolean | サムネイル表示 | true |
| `log_level` | string | ログレベル（DEBUG/INFO/WARNING/ERROR） | INFO |

### Discordメンションの書き方

- **全員にメンション**: `@everyone`
- **オンラインユーザーにメンション**: `@here`
- **特定ロールにメンション**: `<@&ロールID>`
  - ロールIDの取得方法:
    1. Discord開発者モードを有効化
    2. ロールを右クリック → IDをコピー
    3. `<@&コピーしたID>` の形式で設定

### 通知色のカスタマイズ

埋め込みの色は10進数で指定します:

| 色 | 10進数 |
|----|--------|
| 赤 | 16711680 |
| 青 | 255 |
| 緑 | 65280 |
| 黄 | 16776960 |
| 紫 | 10181046 |

**カラーコード変換**: [RGB to Decimal Converter](https://www.shodor.org/stella2java/rgbint.html)

---

## 使用方法

### 起動

```bash
python main.py
```

### 停止

`Ctrl+C` で安全に停止できます。

### ログの確認

- **コンソール**: INFO レベル以上のログを表示
- **ファイル**: `logs/monitor.log` に DEBUG レベル以上のログを記録

ログファイルは10MBごとにローテーションされ、最大5世代まで保存されます。

### バックグラウンド実行（常時稼働）

#### Windows: タスクスケジューラ

1. タスクスケジューラを起動
2. **基本タスクの作成**
3. トリガー: **システム起動時**
4. 操作: `python C:\path\to\live-stream-discord-bot\main.py`

#### Linux/Mac: systemd

`/etc/systemd/system/youtube-monitor.service` を作成:

```ini
[Unit]
Description=YouTube Live Stream Monitor
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/live-stream-discord-bot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

サービスの有効化と起動:
```bash
sudo systemctl enable youtube-monitor
sudo systemctl start youtube-monitor
sudo systemctl status youtube-monitor
```

---

## API最適化について（v1.1.0の新機能）

### 超低コストAPI設計の仕組み

本アプリケーションは**YouTube Data API v3を効率的に使用する独自実装**を採用しています。

#### 一般的な実装方式（多くのボットが使用）
```
search.list(eventType='live')
→ 1回のチェックで100 units消費
→ 1分間隔 × 24時間 = 144,000 units/日（無料枠10,000を大幅超過）
```

#### 本アプリの効率的実装
```
1. playlistItems.list（アップロード済み動画の最新20件取得）→ 1 unit
2. videos.list（一括取得してlive判定）→ 1 unit
→ 1回のチェックで2 units消費
→ 1分間隔 × 24時間 = 2,880 units/日（無料枠の30%未満）
```

**比較**: 一般的な実装と比べて **1/50のコスト**（98%の効率化）

#### この設計のメリット
- ✅ **1分間隔でも余裕**: 無料枠内で高頻度チェック可能
- ✅ **複数チャンネル対応**: 3チャンネルまで1分間隔で監視可能
- ✅ **事前配信枠に対応**: 週初めに7個の配信枠を作成しても検知可能
- ✅ **より正確な開始時刻**: liveStreamingDetails.actualStartTimeを使用
- ✅ **リトライ機能**: ネットワークエラー時の自動再試行（指数バックオフ）

詳細は公式ドキュメント「[クォータの節約](https://developers.google.com/youtube/v3/getting-started#quota)」を参照。

---

## アーキテクチャ

このプロジェクトは**クリーンアーキテクチャ**に準拠して設計されています。

```
┌─────────────────────────────────────────────┐
│         Presentation Layer (CLI)             │  ← ユーザーインターフェース
├─────────────────────────────────────────────┤
│         Application Layer (Use Cases)        │  ← ビジネスロジック
├─────────────────────────────────────────────┤
│         Domain Layer (Entities, Interfaces)  │  ← ドメインモデル（最内層）
├─────────────────────────────────────────────┤
│         Infrastructure Layer (Impl)          │  ← 外部システム実装
└─────────────────────────────────────────────┘

依存の方向: Presentation → Application → Domain ← Infrastructure
```

### ディレクトリ構造

```
live-stream-discord-bot/
├── domain/              # ドメイン層（エンティティ、インターフェース）
│   ├── entities/        # ビジネスオブジェクト
│   ├── value_objects/   # 値オブジェクト
│   └── repositories/    # リポジトリインターフェース（抽象）
├── application/         # アプリケーション層（ユースケース）
│   ├── use_cases/       # ビジネスロジック
│   ├── services/        # アプリケーションサービス
│   └── dto/             # データ転送オブジェクト
├── infrastructure/      # インフラ層（外部システム実装）
│   ├── youtube/         # YouTube API実装
│   ├── discord/         # Discord Webhook実装
│   ├── persistence/     # 状態管理実装
│   └── logging/         # ロギング設定
├── presentation/        # プレゼンテーション層（UI）
│   └── cli/             # CLIコントローラー
├── config/              # 設定ファイル
├── data/                # 状態保存
├── logs/                # ログファイル
├── tests/               # テストコード
└── main.py              # エントリーポイント
```

### 設計原則

1. **依存性逆転の原則**: 内側のレイヤーは外側を知らない
2. **単一責任の原則**: 各クラスは1つの責務のみを持つ
3. **インターフェース分離**: 抽象に依存し、具象実装は注入
4. **テスタビリティ**: モックやスタブでテスト可能

詳細は [アーキテクチャドキュメント](docs/ARCHITECTURE.md) を参照してください。

---

## トラブルシューティング

### エラー: "YOUTUBE_API_KEY が設定されていません"

**原因**: `config/.env` にAPIキーが設定されていない

**解決策**:
1. `config/.env` ファイルが存在するか確認
2. `YOUTUBE_API_KEY=your_api_key_here` の形式で設定されているか確認
3. APIキーの前後に余分なスペースがないか確認

### エラー: "不正なチャンネルID形式"

**原因**: チャンネルIDの形式が正しくない

**解決策**:
- チャンネルIDは **UC で始まる24文字** である必要があります
- `?si=` などのパラメータが含まれていないか確認
- 例: `UCxxxxxxxxxxxxxxxxxxxxxx` （正しい）
- 例: `UCxxxxxxxxxxxxxxxxxxxxxx?si=xxxxx` （誤り）

### エラー: "YouTube API クォータ超過"

**原因**: YouTube Data API v3の無料枠を超過

**詳細**:
- 無料枠: 1日10,000クォータ
- 本アプリは**1回のチェックで2クォータのみ消費**（最適化済み）
- 1分間隔で24時間監視: 1,440回 × 2 = 2,880クォータ（無料枠の30%未満）
- デフォルト設定（1分間隔）なら余裕で運用可能

**解決策**（万が一超過した場合）:
1. 監視チャンネル数を確認（3チャンネル以下を推奨）
2. Google Cloud Consoleでクォータ使用状況を確認
3. 他のアプリケーションと同じAPIキーを共有していないか確認

### Discord通知が届かない

**原因1**: Webhook URLが間違っている
- `config/.env` のURLを再確認

**原因2**: Webhookが削除された
- Discordサーバー設定でWebhookが存在するか確認

**原因3**: ネットワークエラー
- ログファイル `logs/monitor.log` でエラー詳細を確認

### 配信中なのに通知が来ない

**考えられる原因**:
1. **すでに通知済み**: 同じ配信の重複通知は防止されます
2. **チェック間隔**: 次のチェックまで待つ必要があります
3. **APIエラー**: ログでエラーを確認

**確認方法**:
```bash
# ログレベルをDEBUGに変更
# config/config.json の log_level を "DEBUG" に変更
# 再起動してログを確認
```

---

## FAQ

### Q1: YouTube以外の配信プラットフォームに対応していますか？

現在はYouTube専用ですが、クリーンアーキテクチャ設計により拡張は容易です。
`infrastructure/` 配下に新しいリポジトリ実装を追加することで対応可能です。

### Q2: Discordボットとして動作しますか？

いいえ、このアプリケーションはWebhookを使用するため、Discordボットトークンは不要です。
サーバーに常駐させる形式で動作します。

### Q3: 複数のDiscordサーバーに通知できますか？

`config/config.json` の各チャンネル設定で異なるWebhook URLを指定することで可能です。
（現在の実装では全チャンネル共通のWebhook URLですが、拡張可能です）

### Q4: 配信終了通知にも対応していますか？

現在の実装では配信開始通知のみですが、`StreamChangeDetector` の `is_stream_ended` メソッドを活用することで実装可能です。

### Q5: API制限を気にせず使えますか？

はい、**ほぼ気にせず使えます**。
本アプリは超低コスト設計で、1分間隔でも1日2,880クォータ（無料枠10,000の30%未満）です。
3チャンネルまでなら余裕で24時間監視可能です。

### Q6: Windowsで動作しますか？

はい、Python 3.10以上がインストールされていれば動作します。

### Q7: Dockerコンテナで動作させられますか？

可能です。Dockerfileは現在含まれていませんが、追加は簡単です。
コントリビューションをお待ちしています。

---

## 開発

### 開発環境のセットアップ

```bash
# 開発用依存関係をインストール
pip install -r requirements-dev.txt
```

### テストの実行

```bash
# ユニットテストを実行
pytest tests/unit/ -v

# 統合テスト（実際のYouTube APIを使用）
# 事前に .env に TEST_CHANNEL_ID を設定してください
pytest tests/integration/ -v -m integration

# カバレッジ付き
pytest tests/unit/ --cov=. --cov-report=html

# 特定のテストのみ
pytest tests/unit/test_entities.py
```

**統合テストの実行には環境変数が必要です:**

```env
# config/.env に追加
TEST_CHANNEL_ID=UCxxxxxxxxxxxxxxxxxxxxxx
TEST_CHANNEL_NAME=Test Channel Name
```

### コードフォーマット

```bash
# Black でフォーマット
black .

# Flake8 でリント
flake8 .

# mypy で型チェック
mypy .
```

### ディレクトリ構造の確認

```bash
# プロジェクト構造を確認（tree コマンド）
tree -I "__pycache__|*.pyc|venv|env"
```

---

## コントリビューション

コントリビューションを歓迎します。

プルリクエストを送る前に、以下を確認してください:

1. テストが全て通ること（`pytest`）
2. コードフォーマットが適用されていること（`black .`）
3. 型チェックが通ること（`mypy .`）

詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

### 貢献方法

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

---

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
詳細は [LICENSE](LICENSE) ファイルを参照してください。

---

## 謝辞

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) by Robert C. Martin
- [YouTube Data API v3](https://developers.google.com/youtube/v3)
- [Discord Webhooks](https://discord.com/developers/docs/resources/webhook)

---

## サポート

問題が発生した場合は、[Issue](https://github.com/YOUR_USERNAME/live-stream-discord-bot/issues) を作成してください。

---

**Made with QUA for VTuber fans and stream communities**