"""エンティティのユニットテスト"""

import pytest
from datetime import datetime

from domain.entities.channel import Channel
from domain.entities.stream import Stream
from domain.value_objects.channel_id import ChannelId
from domain.value_objects.stream_status import StreamStatus


class TestChannelId:
    """ChannelIdのテスト"""

    def test_valid_channel_id(self):
        """正しいチャンネルID形式の場合、正常に作成される"""
        channel_id = ChannelId("UC1234567890123456789012")
        assert str(channel_id) == "UC1234567890123456789012"

    def test_invalid_channel_id_short(self):
        """短すぎるチャンネルIDの場合、ValueErrorが発生"""
        with pytest.raises(ValueError, match="不正なチャンネルID形式"):
            ChannelId("UC123")

    def test_invalid_channel_id_no_uc_prefix(self):
        """UCで始まらないチャンネルIDの場合、ValueErrorが発生"""
        with pytest.raises(ValueError, match="不正なチャンネルID形式"):
            ChannelId("AB1234567890123456789012")

    def test_channel_id_equality(self):
        """同じ値のChannelIdは等しい"""
        id1 = ChannelId("UC1234567890123456789012")
        id2 = ChannelId("UC1234567890123456789012")
        assert id1 == id2

    def test_channel_id_hash(self):
        """ChannelIdはハッシュ可能"""
        id1 = ChannelId("UC1234567890123456789012")
        id2 = ChannelId("UC1234567890123456789012")
        assert hash(id1) == hash(id2)


class TestChannel:
    """Channelのテスト"""

    def test_create_channel(self):
        """正常にChannelを作成できる"""
        channel = Channel(
            id=ChannelId("UC1234567890123456789012"), name="テストチャンネル", mention="@everyone"
        )
        assert channel.name == "テストチャンネル"
        assert channel.mention == "@everyone"

    def test_channel_empty_name(self):
        """チャンネル名が空の場合、ValueErrorが発生"""
        with pytest.raises(ValueError, match="チャンネル名は空にできません"):
            Channel(id=ChannelId("UC1234567890123456789012"), name="", mention="@everyone")

    def test_channel_equality(self):
        """同じIDのChannelは等しい"""
        channel_id = ChannelId("UC1234567890123456789012")
        channel1 = Channel(id=channel_id, name="チャンネル1", mention="@everyone")
        channel2 = Channel(id=channel_id, name="チャンネル2", mention="@here")
        assert channel1 == channel2

    def test_channel_inequality(self):
        """異なるIDのChannelは等しくない"""
        channel1 = Channel(
            id=ChannelId("UC1234567890123456789012"), name="チャンネル1", mention="@everyone"
        )
        channel2 = Channel(
            id=ChannelId("UC9876543210987654321098"), name="チャンネル2", mention="@everyone"
        )
        assert channel1 != channel2


class TestStream:
    """Streamのテスト"""

    def test_create_stream(self):
        """正常にStreamを作成できる"""
        stream = Stream(
            video_id="test123",
            title="テスト配信",
            thumbnail_url="http://example.com/thumb.jpg",
            started_at=datetime.now(),
            status=StreamStatus.LIVE,
        )
        assert stream.video_id == "test123"
        assert stream.title == "テスト配信"
        assert stream.is_live() is True

    def test_stream_empty_video_id(self):
        """video_idが空の場合、ValueErrorが発生"""
        with pytest.raises(ValueError, match="video_idは必須です"):
            Stream(
                video_id="",
                title="テスト配信",
                thumbnail_url="http://example.com/thumb.jpg",
                started_at=datetime.now(),
                status=StreamStatus.LIVE,
            )

    def test_stream_empty_title(self):
        """タイトルが空の場合、ValueErrorが発生"""
        with pytest.raises(ValueError, match="タイトルは必須です"):
            Stream(
                video_id="test123",
                title="",
                thumbnail_url="http://example.com/thumb.jpg",
                started_at=datetime.now(),
                status=StreamStatus.LIVE,
            )

    def test_stream_is_live(self):
        """配信中の場合、is_live()がTrueを返す"""
        stream = Stream(
            video_id="test123",
            title="テスト配信",
            thumbnail_url="http://example.com/thumb.jpg",
            started_at=datetime.now(),
            status=StreamStatus.LIVE,
        )
        assert stream.is_live() is True

    def test_stream_is_not_live(self):
        """配信終了の場合、is_live()がFalseを返す"""
        stream = Stream(
            video_id="test123",
            title="テスト配信",
            thumbnail_url="http://example.com/thumb.jpg",
            started_at=datetime.now(),
            status=StreamStatus.ENDED,
        )
        assert stream.is_live() is False

    def test_stream_equality(self):
        """同じvideo_idのStreamは等しい"""
        stream1 = Stream(
            video_id="test123",
            title="タイトル1",
            thumbnail_url="http://example.com/thumb1.jpg",
            started_at=datetime.now(),
            status=StreamStatus.LIVE,
        )
        stream2 = Stream(
            video_id="test123",
            title="タイトル2",
            thumbnail_url="http://example.com/thumb2.jpg",
            started_at=datetime.now(),
            status=StreamStatus.LIVE,
        )
        assert stream1 == stream2

    def test_stream_inequality(self):
        """異なるvideo_idのStreamは等しくない"""
        stream1 = Stream(
            video_id="test123",
            title="テスト配信",
            thumbnail_url="http://example.com/thumb.jpg",
            started_at=datetime.now(),
            status=StreamStatus.LIVE,
        )
        stream2 = Stream(
            video_id="test456",
            title="テスト配信",
            thumbnail_url="http://example.com/thumb.jpg",
            started_at=datetime.now(),
            status=StreamStatus.LIVE,
        )
        assert stream1 != stream2
