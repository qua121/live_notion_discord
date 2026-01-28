"""Discord通知の複数Webhook対応の統合テスト"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from infrastructure.discord.discord_notification_gateway import (
    DiscordNotificationGateway,
    NotificationError,
)
from domain.entities.channel import Channel
from domain.entities.stream import Stream
from domain.value_objects.channel_id import ChannelId
from domain.value_objects.stream_status import StreamStatus
from domain.value_objects.webhook_config import WebhookConfig


class TestDiscordNotificationMultipleWebhooks:
    """複数Webhook通知のテスト"""

    @pytest.fixture
    def gateway(self):
        """テスト用のゲートウェイを作成"""
        return DiscordNotificationGateway(color=16711680)

    @pytest.fixture
    def test_stream(self):
        """テスト用のストリームを作成"""
        return Stream(
            video_id="test123",
            title="テスト配信",
            thumbnail_url="http://example.com/thumb.jpg",
            started_at=datetime.now(),
            status=StreamStatus.LIVE,
        )

    def test_notify_single_webhook_success(self, gateway, test_stream):
        """単一Webhookへの通知が成功する"""
        webhooks = [
            WebhookConfig(
                url="https://discord.com/api/webhooks/123456789/abcdefg",
                mention="@everyone"
            )
        ]
        channel = Channel(
            id=ChannelId("UC1234567890123456789012"),
            name="テストチャンネル",
            webhooks=webhooks
        )

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 204
            mock_post.return_value = mock_response

            # 通知送信（エラーが発生しないことを確認）
            gateway.notify_stream_start(channel, test_stream)

            # 1回だけ呼ばれることを確認
            assert mock_post.call_count == 1

    def test_notify_multiple_webhooks_all_success(self, gateway, test_stream):
        """複数Webhookへの通知が全て成功する"""
        webhooks = [
            WebhookConfig(
                url="https://discord.com/api/webhooks/111111111/aaa",
                mention="@everyone"
            ),
            WebhookConfig(
                url="https://discord.com/api/webhooks/222222222/bbb",
                mention="<@&1234567890>"
            ),
            WebhookConfig(
                url="https://discord.com/api/webhooks/333333333/ccc",
                mention=""
            )
        ]
        channel = Channel(
            id=ChannelId("UC1234567890123456789012"),
            name="テストチャンネル",
            webhooks=webhooks
        )

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 204
            mock_post.return_value = mock_response

            # 通知送信
            gateway.notify_stream_start(channel, test_stream)

            # 3回呼ばれることを確認
            assert mock_post.call_count == 3

            # 各Webhookに正しいURLとメンションが送信されたことを確認
            calls = mock_post.call_args_list
            assert calls[0][0][0] == "https://discord.com/api/webhooks/111111111/aaa"
            assert calls[1][0][0] == "https://discord.com/api/webhooks/222222222/bbb"
            assert calls[2][0][0] == "https://discord.com/api/webhooks/333333333/ccc"

            assert calls[0][1]["json"]["content"] == "@everyone"
            assert calls[1][1]["json"]["content"] == "<@&1234567890>"
            assert calls[2][1]["json"]["content"] == ""

    def test_notify_multiple_webhooks_partial_failure(self, gateway, test_stream):
        """複数Webhookの一部が失敗しても他は成功する"""
        webhooks = [
            WebhookConfig(
                url="https://discord.com/api/webhooks/111111111/aaa",
                mention="@everyone"
            ),
            WebhookConfig(
                url="https://discord.com/api/webhooks/222222222/bbb",
                mention="<@&1234567890>"
            )
        ]
        channel = Channel(
            id=ChannelId("UC1234567890123456789012"),
            name="テストチャンネル",
            webhooks=webhooks
        )

        with patch("requests.post") as mock_post:
            # 1つ目は失敗、2つ目は成功
            def side_effect(*args, **kwargs):
                mock_response = Mock()
                if "111111111" in args[0]:
                    mock_response.status_code = 404
                    mock_response.text = "Webhook not found"
                else:
                    mock_response.status_code = 204
                return mock_response

            mock_post.side_effect = side_effect

            # 通知送信（エラーが発生しないことを確認 - 1つでも成功すればOK）
            gateway.notify_stream_start(channel, test_stream)

            # 2回呼ばれることを確認
            assert mock_post.call_count == 2

    def test_notify_multiple_webhooks_all_failure(self, gateway, test_stream):
        """全てのWebhookが失敗した場合、NotificationErrorが発生"""
        webhooks = [
            WebhookConfig(
                url="https://discord.com/api/webhooks/111111111/aaa",
                mention="@everyone"
            ),
            WebhookConfig(
                url="https://discord.com/api/webhooks/222222222/bbb",
                mention="<@&1234567890>"
            )
        ]
        channel = Channel(
            id=ChannelId("UC1234567890123456789012"),
            name="テストチャンネル",
            webhooks=webhooks
        )

        with patch("requests.post") as mock_post:
            # 全て失敗
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Webhook not found"
            mock_post.return_value = mock_response

            # NotificationErrorが発生することを確認
            with pytest.raises(NotificationError, match="全てのWebhookへの送信に失敗"):
                gateway.notify_stream_start(channel, test_stream)

    def test_notify_no_webhooks(self, gateway, test_stream):
        """Webhookが設定されていない場合、Channel作成時にValueErrorが発生"""
        # Channelのバリデーションで既にエラーになる
        with pytest.raises(ValueError, match="最低1つのWebhook設定が必要です"):
            Channel(
                id=ChannelId("UC1234567890123456789012"),
                name="テストチャンネル",
                webhooks=[]
            )

    def test_send_to_webhook_timeout(self, gateway, test_stream):
        """タイムアウトが発生した場合、NotificationErrorが発生"""
        webhooks = [
            WebhookConfig(
                url="https://discord.com/api/webhooks/123456789/abcdefg",
                mention="@everyone"
            )
        ]
        channel = Channel(
            id=ChannelId("UC1234567890123456789012"),
            name="テストチャンネル",
            webhooks=webhooks
        )

        with patch("requests.post") as mock_post:
            import requests
            mock_post.side_effect = requests.Timeout("Connection timeout")

            # NotificationErrorが発生することを確認
            with pytest.raises(NotificationError, match="全てのWebhookへの送信に失敗"):
                gateway.notify_stream_start(channel, test_stream)
