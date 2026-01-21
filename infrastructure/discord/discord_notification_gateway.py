"""Discord Webhookを使用した通知送信実装

NotificationGatewayインターフェースの具象実装
"""

import logging
import requests
from datetime import datetime
from typing import Optional

from domain.entities.channel import Channel
from domain.entities.stream import Stream
from domain.repositories.notification_gateway import NotificationGateway

logger = logging.getLogger(__name__)


class NotificationError(Exception):
    """通知送信エラー"""
    pass


class DiscordNotificationGateway(NotificationGateway):
    """Discord Webhookを使用した通知送信の実装"""

    def __init__(self, webhook_url: str, color: int = 16711680):
        """
        Args:
            webhook_url: Discord Webhook URL
            color: 埋め込みの色（デフォルト: 赤）
        """
        self._webhook_url = webhook_url
        self._color = color

    def notify_stream_start(self, channel: Channel, stream: Stream) -> None:
        """
        配信開始通知をDiscordに送信

        Webhook形式のリッチ埋め込み（Embed）で送信
        """
        try:
            embed = self._create_embed(channel, stream)
            payload = {
                'content': channel.mention,  # メンション
                'embeds': [embed]
            }

            response = requests.post(
                self._webhook_url,
                json=payload,
                timeout=10
            )

            if response.status_code == 204:
                logger.info(f"Discord通知送信成功: {channel.name}")
            else:
                logger.warning(f"Discord通知送信失敗: status={response.status_code}, body={response.text}")
                raise NotificationError(f"Discord API エラー: {response.status_code}")

        except requests.RequestException as e:
            logger.error(f"Discord通知送信エラー: {e}", exc_info=True)
            raise NotificationError(f"通知送信失敗: {e}") from e

    def _create_embed(self, channel: Channel, stream: Stream) -> dict:
        """埋め込み（Embed）を作成"""
        return {
            'title': f'🔴 {channel.name} が配信を開始しました!',
            'description': stream.title,
            'url': f'https://www.youtube.com/watch?v={stream.video_id}',
            'color': self._color,
            'image': {
                'url': stream.thumbnail_url
            },
            'timestamp': datetime.utcnow().isoformat(),
            'footer': {
                'text': 'YouTube Live'
            }
        }
