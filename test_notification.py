"""Discord通知のテスト送信スクリプト

使用方法:
    python test_notification.py
"""

import os
from datetime import datetime
from dotenv import load_dotenv

from infrastructure.discord.discord_notification_gateway import DiscordNotificationGateway
from domain.entities.stream import Stream
from domain.entities.channel import Channel
from domain.value_objects.channel_id import ChannelId
from domain.value_objects.stream_status import StreamStatus
from domain.value_objects.webhook_config import WebhookConfig


def main():
    """テスト通知を送信"""
    print("=" * 60)
    print("Discord通知テスト")
    print("=" * 60)

    # 環境変数読み込み
    load_dotenv("config/.env")
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        print("[ERROR] DISCORD_WEBHOOK_URL が設定されていません")
        print("config/.env ファイルを確認してください")
        return 1

    print(f"\n[INFO] Webhook URL: {webhook_url[:50]}...")

    # 通知ゲートウェイ作成
    gateway = DiscordNotificationGateway(color=16711680)

    # テスト用のチャンネルとストリーム
    test_webhook = WebhookConfig(url=webhook_url, mention="@everyone")
    test_channel = Channel(
        id=ChannelId("UC1234567890123456789012"),
        name="テストチャンネル",
        webhooks=[test_webhook],
    )

    test_stream = Stream(
        video_id="dQw4w9WgXcQ",
        title="【テスト配信】Discord通知のテスト送信です",
        thumbnail_url="https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        started_at=datetime.now(),
        status=StreamStatus.LIVE,
    )

    # 通知送信
    print("\n[INFO] テスト通知を送信中...")
    try:
        gateway.notify_stream_start(test_channel, test_stream)
        print("\n[SUCCESS] テスト通知の送信に成功しました！")
        print("Discordサーバーで通知を確認してください。")
        return 0

    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\n確認事項:")
        print("1. Webhook URLが正しいか")
        print("2. Webhookが削除されていないか")
        print("3. インターネット接続が正常か")
        return 1


if __name__ == "__main__":
    exit(main())
