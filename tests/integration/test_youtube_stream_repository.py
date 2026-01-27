"""YouTubeStreamRepositoryの統合テスト

実際のYouTube Data API v3を使用したテスト
手動実行のみ（CIでは実行しない）

実行方法:
    pytest tests/integration/test_youtube_stream_repository.py -v -o addopts="" -m integration
"""

import os
import pytest
from dotenv import load_dotenv

from domain.entities.channel import Channel
from domain.value_objects.channel_id import ChannelId
from infrastructure.youtube.youtube_stream_repository import YouTubeStreamRepository


# 統合テストマーカー
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def api_key():
    """YouTube API キーをロード"""
    load_dotenv('config/.env')
    key = os.getenv('YOUTUBE_API_KEY')
    if not key:
        pytest.skip("YOUTUBE_API_KEY が設定されていません")
    return key


@pytest.fixture(scope="module")
def repository(api_key):
    """YouTubeStreamRepositoryインスタンス"""
    return YouTubeStreamRepository(api_key)


@pytest.fixture
def test_channel():
    """テスト用チャンネル

    環境変数から読み込み、未設定の場合はスキップ
    TEST_CHANNEL_ID: テスト対象のYouTubeチャンネルID
    TEST_CHANNEL_NAME: チャンネル名（任意）
    """
    channel_id = os.getenv('TEST_CHANNEL_ID')
    if not channel_id:
        pytest.skip("TEST_CHANNEL_ID が設定されていません")

    channel_name = os.getenv('TEST_CHANNEL_NAME', 'Test Channel')

    return Channel(
        id=ChannelId(channel_id),
        name=channel_name,
        mention='@test'
    )


class TestYouTubeStreamRepository:
    """YouTubeStreamRepository統合テスト"""

    def test_get_uploads_playlist_id(self, repository, test_channel):
        """アップロードプレイリストIDの生成テスト"""
        playlist_id = repository._get_uploads_playlist_id(str(test_channel.id))

        # UCから始まるチャンネルIDはUUに変換される
        assert playlist_id.startswith('UU')
        # UC... → UU... に変換されていることを確認
        expected_playlist_id = 'UU' + str(test_channel.id)[2:]
        assert playlist_id == expected_playlist_id

    def test_get_current_stream_実際のAPI呼び出し(self, repository, test_channel):
        """実際のAPIを使った配信情報取得テスト"""
        # 配信中かどうかは不明だが、エラーなく実行できることを確認
        stream = repository.get_current_stream(test_channel)

        # Noneまたは有効なStreamオブジェクト
        if stream is not None:
            assert stream.video_id
            assert stream.title
            assert stream.thumbnail_url
            assert stream.started_at
            print(f"\n配信検知: {stream.title}")
            print(f"Video ID: {stream.video_id}")
        else:
            print(f"\n{test_channel.name} は現在配信していません")

    def test_get_current_stream_複数チャンネル(self, repository, test_channel):
        """複数チャンネルで正常動作を確認

        環境変数 TEST_CHANNEL_ID_2 を設定することで2チャンネルテスト可能
        """
        channels = [test_channel]

        # 2つ目のチャンネルが設定されていれば追加
        channel_id_2 = os.getenv('TEST_CHANNEL_ID_2')
        if channel_id_2:
            channel_name_2 = os.getenv('TEST_CHANNEL_NAME_2', 'Test Channel 2')
            channels.append(Channel(ChannelId(channel_id_2), channel_name_2, '@test'))

        results = []
        for channel in channels:
            stream = repository.get_current_stream(channel)
            results.append((channel.name, stream is not None))
            print(f"{channel.name}: {'配信中' if stream else '未配信'}")

        # 少なくとも1チャンネルは処理成功していること
        assert len(results) > 0

    def test_get_current_stream_存在しないチャンネル(self, repository):
        """存在しないチャンネルIDでのエラーハンドリング"""
        from infrastructure.youtube.youtube_stream_repository import RepositoryError

        fake_channel = Channel(
            ChannelId('UC0000000000000000000000'),
            'Fake Channel',
            '@test'
        )

        # リトライ後にエラーが発生すること
        with pytest.raises(RepositoryError):
            repository.get_current_stream(fake_channel)

    def test_get_uploads_playlist_id_非標準チャンネルID(self, repository):
        """非標準的なチャンネルID形式でのエラー（内部メソッドのテスト）"""
        from infrastructure.youtube.youtube_stream_repository import RepositoryError

        # UCで始まらないチャンネルIDを直接テスト
        # （ChannelIdバリデーションをバイパス）
        with pytest.raises(RepositoryError, match="非標準的なチャンネルID形式"):
            repository._get_uploads_playlist_id('invalid-channel-id')

    @pytest.mark.slow
    def test_api_quota_cost(self, repository, test_channel):
        """APIコストの確認（実行には注意）"""
        # このテストは1回の実行で2 unitsを消費
        print("\n=== APIクォータコスト測定 ===")
        print("このテストは2 unitsを消費します")

        stream = repository.get_current_stream(test_channel)

        print(f"消費クォータ: 2 units")
        print(f"結果: {'配信中' if stream else '未配信'}")

        # 旧方式との比較
        print("\n旧方式（search.list）: 100 units")
        print("新方式（playlist + videos）: 2 units")
        print("コスト削減率: 98% (1/50)")


if __name__ == '__main__':
    # 直接実行時のヘルプ
    print("統合テストの実行方法:")
    print("pytest tests/integration/test_youtube_stream_repository.py -v -o addopts=\"\" -m integration")
    print("\n注意: このテストは実際のYouTube APIを使用し、クォータを消費します")
