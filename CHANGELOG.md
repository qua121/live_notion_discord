# Changelog

このファイルは、プロジェクトの注目すべきすべての変更を記録します。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.0.0/) に基づいており、
このプロジェクトは [セマンティックバージョニング](https://semver.org/lang/ja/) に準拠しています。

## [Unreleased]

### 予定されている機能
- 英語版ドキュメント
- Dockerサポート
- 配信終了通知
- 複数Discord Webhookサポート（チャンネルごと）

---

## [1.0.0] - 2026-01-21

### Added

#### コアアーキテクチャ
- クリーンアーキテクチャに基づいた初期実装
- Domain層: エンティティと値オブジェクト
- Application層: ユースケースとアプリケーションサービス
- Infrastructure層: YouTube API、Discord Webhook、JSON状態管理
- Presentation層: CLIコントローラー

#### 機能
- YouTube配信の自動監視
- 複数チャンネルの同時監視
- Discord Webhookによるリッチな通知（Embed形式）
- 配信状態の永続化（重複通知防止）
- カスタマイズ可能な設定（チェック間隔、メンション、通知色）

#### ドキュメント
- 包括的なREADME
- アーキテクチャ図
- セットアップガイド
- トラブルシューティングセクション
- FAQ

#### テスト
- エンティティのユニットテスト
- StreamChangeDetectorのユニットテスト
- pytest設定

#### CI/CD
- GitHub Actionsワークフロー
- 自動テスト実行
- コードフォーマットチェック（Black）
- Lintチェック（Flake8）
- 型チェック（mypy）
- セキュリティスキャン（Safety）

#### OSS準備
- MIT License
- Code of Conduct
- Contributing Guide
- Security Policy
- Issue Templates（Bug Report, Feature Request）
- Pull Request Template

#### 設定管理
- 環境変数による秘密情報管理（.env）
- JSON設定ファイル（config.json）
- ログローテーション機能

### Dependencies
- requests >= 2.31.0
- google-api-python-client >= 2.100.0
- python-dotenv >= 1.0.0

### Development Dependencies
- pytest >= 7.4.0
- pytest-cov >= 4.1.0
- pytest-mock >= 3.11.1
- black >= 23.7.0
- flake8 >= 6.1.0
- mypy >= 1.5.0

---

## バージョニングルール

- **MAJOR**: 後方互換性のない変更
- **MINOR**: 後方互換性のある機能追加
- **PATCH**: 後方互換性のあるバグ修正

## カテゴリ

- `Added`: 新機能
- `Changed`: 既存機能の変更
- `Deprecated`: 今後削除予定の機能
- `Removed`: 削除された機能
- `Fixed`: バグ修正
- `Security`: セキュリティ関連の修正

---

[Unreleased]: https://github.com/YOUR_USERNAME/live-stream-discord-bot/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/YOUR_USERNAME/live-stream-discord-bot/releases/tag/v1.0.0
