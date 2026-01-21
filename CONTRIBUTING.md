# コントリビューションガイド

Live Stream Discord Botへのコントリビューションに興味を持っていただき、ありがとうございます。
このガイドでは、プロジェクトへの貢献方法について説明します。

## 目次

- [行動規範](#行動規範)
- [始める前に](#始める前に)
- [開発環境のセットアップ](#開発環境のセットアップ)
- [開発ワークフロー](#開発ワークフロー)
- [コーディング規約](#コーディング規約)
- [コミットメッセージ規約](#コミットメッセージ規約)
- [プルリクエストのガイドライン](#プルリクエストのガイドライン)
- [テストの実行](#テストの実行)
- [ドキュメントの更新](#ドキュメントの更新)

---

## 行動規範

このプロジェクトは [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md) を採用しています。
参加することで、あなたはこの規範を遵守することに同意したものとみなされます。

---

## 始める前に

### バグ報告

バグを見つけた場合は、[GitHub Issues](https://github.com/YOUR_USERNAME/live-stream-discord-bot/issues) で報告してください。

報告時には以下の情報を含めてください:

- **バグの説明**: 何が起こったか
- **再現手順**: バグを再現するための具体的な手順
- **期待される動作**: 本来どうあるべきか
- **実際の動作**: 実際に何が起こったか
- **環境情報**:
  - OS（Windows/Linux/Mac）
  - Pythonバージョン
  - 依存パッケージのバージョン
- **ログ**: `logs/monitor.log` の関連部分

### 機能リクエスト

新機能の提案も歓迎します。

提案時には以下を説明してください:

- **機能の概要**: 何を実現したいか
- **ユースケース**: どのような場面で必要か
- **提案する実装方法**: （可能であれば）どう実装するか

---

## 開発環境のセットアップ

### 1. リポジトリのフォーク

GitHub上でこのリポジトリをフォークしてください。

### 2. ローカルにクローン

```bash
git clone https://github.com/YOUR_USERNAME/live-stream-discord-bot.git
cd live-stream-discord-bot
```

### 3. リモートの設定

```bash
# オリジナルリポジトリを upstream として追加
git remote add upstream https://github.com/ORIGINAL_OWNER/live-stream-discord-bot.git
git remote -v
```

### 4. 仮想環境の作成（推奨）

```bash
# venv を使用
python -m venv venv

# 仮想環境を有効化
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 5. 開発用依存関係のインストール

```bash
pip install -r requirements-dev.txt
```

これにより以下がインストールされます:

- `pytest` - テストフレームワーク
- `pytest-cov` - カバレッジ測定
- `pytest-mock` - モック機能
- `black` - コードフォーマッター
- `flake8` - リンター
- `mypy` - 型チェッカー

### 6. pre-commit フックの設定（オプション）

```bash
pip install pre-commit
pre-commit install
```

これにより、コミット前に自動的にコードフォーマットと型チェックが実行されます。

---

## 開発ワークフロー

### 1. 最新の変更を取得

```bash
git checkout main
git fetch upstream
git merge upstream/main
```

### 2. フィーチャーブランチを作成

```bash
git checkout -b feature/your-feature-name
```

**ブランチ命名規則**:

- `feature/機能名` - 新機能
- `fix/バグ名` - バグ修正
- `docs/内容` - ドキュメント更新
- `refactor/内容` - リファクタリング
- `test/内容` - テスト追加・修正

例:
```bash
git checkout -b feature/add-twitch-support
git checkout -b fix/api-rate-limit
git checkout -b docs/update-readme
```

### 3. 変更を加える

コードを編集し、必要に応じてテストを追加します。

### 4. テストを実行

```bash
# 全テストを実行
pytest

# カバレッジ付き
pytest --cov=. --cov-report=html
```

### 5. コードフォーマットとリント

```bash
# コードフォーマット
black .

# リント
flake8 .

# 型チェック
mypy .
```

### 6. 変更をコミット

```bash
git add .
git commit -m "feat: Add Twitch support"
```

コミットメッセージの書き方は [コミットメッセージ規約](#コミットメッセージ規約) を参照してください。

### 7. プッシュ

```bash
git push origin feature/your-feature-name
```

### 8. プルリクエストを作成

GitHub上でプルリクエストを作成してください。

---

## コーディング規約

このプロジェクトは以下の規約に従います:

### Pythonスタイル

- **PEP 8** に準拠
- **Black** でフォーマット（行長: 100文字）
- **型ヒント** を必須とする

### ネーミング規則

- **クラス名**: PascalCase (`StreamRepository`, `NotificationGateway`)
- **関数名**: snake_case (`get_current_stream`, `notify_stream_start`)
- **定数**: UPPER_SNAKE_CASE (`PATTERN`, `DEFAULT_INTERVAL`)
- **プライベート属性**: アンダースコア接頭辞 (`_state_cache`, `_youtube`)

### ドキュメンテーション

**docstring** は Google スタイルで記述:

```python
def get_current_stream(self, channel: Channel) -> Optional[Stream]:
    """
    チャンネルの現在の配信を取得

    Args:
        channel: 取得対象のチャンネル

    Returns:
        配信中の場合はStreamオブジェクト、配信していない場合はNone

    Raises:
        RepositoryError: APIエラーやネットワークエラー
    """
    pass
```

### クリーンアーキテクチャの原則

- **Domain層** は他のレイヤーを知らない
- **Application層** は Domain層のみに依存
- **Infrastructure層** は Domain層のインターフェースを実装
- **依存性注入** は `main.py` で行う

---

## コミットメッセージ規約

**Conventional Commits** に準拠します。

### フォーマット

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type（必須）

- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント変更のみ
- `style`: コードフォーマット（機能に影響なし）
- `refactor`: リファクタリング
- `test`: テスト追加・修正
- `chore`: ビルドプロセス、ツール変更

### Scope（オプション）

変更の範囲を示す:

- `domain`
- `application`
- `infrastructure`
- `presentation`
- `config`
- `tests`

### Subject（必須）

- 50文字以内
- 小文字で始める（type の後）
- 命令形で書く（"add" not "added"）
- 末尾にピリオドを付けない

### 例

```bash
# 良い例
git commit -m "feat(infrastructure): add Twitch API support"
git commit -m "fix(domain): correct channel ID validation pattern"
git commit -m "docs: update installation guide"
git commit -m "test(application): add tests for StreamChangeDetector"

# 悪い例
git commit -m "update"
git commit -m "Fix bug."
git commit -m "FEAT: Added new feature"
```

### 詳細な説明が必要な場合

```bash
git commit -m "feat(infrastructure): add Twitch API support

- Add TwitchStreamRepository class
- Implement Twitch API v5 integration
- Update README with Twitch setup instructions

Closes #42"
```

---

## プルリクエストのガイドライン

### PR作成前のチェックリスト

- [ ] テストが全て通る（`pytest`）
- [ ] コードフォーマットが適用されている（`black .`）
- [ ] リントエラーがない（`flake8 .`）
- [ ] 型チェックが通る（`mypy .`）
- [ ] 新機能にはテストを追加している
- [ ] ドキュメントを更新している（必要な場合）
- [ ] CHANGELOGを更新している（大きな変更の場合）

### PRの説明

プルリクエストには以下を含めてください:

#### タイトル

コミットメッセージと同じ形式:

```
feat: Add Twitch support
fix: Correct API rate limit handling
```

#### 本文

```markdown
## 概要
この変更の目的を簡潔に説明

## 変更内容
- 追加した機能・修正したバグ
- 変更したファイルとその理由

## テスト方法
この変更をどのようにテストしたか

## スクリーンショット（該当する場合）
UIの変更がある場合はスクリーンショットを添付

## 関連Issue
Closes #42
```

### レビュープロセス

1. プルリクエストを作成すると、メンテナーがレビューします
2. 変更が必要な場合、コメントでフィードバックします
3. フィードバックに対応したら、再度レビューをリクエストしてください
4. 承認されたらマージされます

---

## テストの実行

### 全テストを実行

```bash
pytest
```

### カバレッジレポート付き

```bash
pytest --cov=. --cov-report=html
# カバレッジレポートは htmlcov/index.html に生成されます
```

### 特定のテストファイルのみ

```bash
pytest tests/unit/test_entities.py
```

### 特定のテストメソッドのみ

```bash
pytest tests/unit/test_entities.py::TestChannel::test_create_channel
```

### テストの書き方

新しい機能には必ずテストを追加してください。

**例: エンティティのテスト**

```python
# tests/unit/test_new_feature.py
import pytest
from domain.entities.new_entity import NewEntity

class TestNewEntity:
    """NewEntityのテスト"""

    def test_create_new_entity(self):
        """正常にNewEntityを作成できる"""
        entity = NewEntity(id="123", name="Test")
        assert entity.id == "123"
        assert entity.name == "Test"

    def test_invalid_new_entity(self):
        """不正な値でValueErrorが発生"""
        with pytest.raises(ValueError, match="idは必須です"):
            NewEntity(id="", name="Test")
```

---

## ドキュメントの更新

ドキュメント変更も大歓迎です。

### 更新が必要なドキュメント

- **README.md**: ユーザー向けドキュメント
- **CONTRIBUTING.md**: コントリビューター向けガイド
- **docs/**: 詳細なドキュメント（必要に応じて）
- **コード内docstring**: APIドキュメント

### ドキュメント作成のガイドライン

- 明確で簡潔に
- 例を含める
- 日本語で記述（英語版は別途作成予定）
- マークダウン形式を使用

---

## 質問・サポート

わからないことがあれば、遠慮なく質問してください:

- **GitHub Discussions**: 一般的な質問・議論
- **GitHub Issues**: バグ報告・機能リクエスト

---

## ライセンス

このプロジェクトに貢献することで、あなたの貢献が MIT License の下でライセンスされることに同意したものとみなされます。

---

**あなたのコントリビューションに感謝します!** 🎉
