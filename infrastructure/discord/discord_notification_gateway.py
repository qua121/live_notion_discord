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

    def __init__(self, color: int = 16711680):
        """
        Args:
            color: 埋め込みの色（デフォルト: 赤）
        """
        self._color = color

    def notify_stream_start(self, channel: Channel, stream: Stream) -> None:
        """
        配信開始通知を複数のDiscord Webhookに送信

        複数のwebhookが設定されている場合、全てに送信を試みる。
        - 1つでも成功すれば通知成功とみなす
        - 全て失敗した場合のみNotificationErrorを投げる
        """
        if not channel.webhooks:
            raise NotificationError(f"チャンネル '{channel.name}' にWebhookが設定されていません")

        embed = self._create_embed(channel, stream)
        success_count = 0
        failed_webhooks = []

        logger.info(f"Discord通知送信開始: {channel.name} (Webhook数: {len(channel.webhooks)})")

        for webhook_config in channel.webhooks:
            try:
                self._send_to_webhook(webhook_config.url, webhook_config.mention, embed)
                success_count += 1
                logger.info(
                    f"Discord通知送信成功: {channel.name} -> {webhook_config.url[:50]}..."
                )
            except Exception as e:
                failed_webhooks.append((webhook_config.url, str(e)))
                logger.warning(
                    f"Discord通知送信失敗: {channel.name} -> {webhook_config.url[:50]}... - {e}"
                )

        # 結果のサマリーをログ出力
        logger.info(
            f"Discord通知送信完了: {channel.name} - 成功: {success_count}/{len(channel.webhooks)}"
        )

        # 全て失敗した場合のみエラーを投げる
        if success_count == 0:
            error_msg = f"全てのWebhookへの送信に失敗: {channel.name}\n"
            for url, error in failed_webhooks:
                error_msg += f"  - {url[:50]}...: {error}\n"
            raise NotificationError(error_msg)

    def _send_to_webhook(self, webhook_url: str, mention: str, embed: dict) -> None:
        """
        単一のWebhookに通知を送信

        Args:
            webhook_url: Discord Webhook URL
            mention: メンション文字列
            embed: Embed辞書

        Raises:
            NotificationError: 送信に失敗した場合
        """
        try:
            payload = {"content": mention, "embeds": [embed]}
            response = requests.post(webhook_url, json=payload, timeout=10)

            if response.status_code != 204:
                raise NotificationError(
                    f"Discord API エラー: status={response.status_code}, body={response.text}"
                )

        except requests.RequestException as e:
            raise NotificationError(f"通知送信失敗: {e}") from e

    def _create_embed(self, channel: Channel, stream: Stream) -> dict:
        """埋め込み（Embed）を作成"""
        return {
            "title": f"🔴 {channel.name} が配信を開始しました!",
            "description": stream.title,
            "url": f"https://www.youtube.com/watch?v={stream.video_id}",
            "color": self._color,
            "image": {"url": stream.thumbnail_url},
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "YouTube Live"},
        }
