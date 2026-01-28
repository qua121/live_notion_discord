"""設定管理クラス"""

import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

from domain.entities.channel import Channel
from domain.value_objects.channel_id import ChannelId
from domain.value_objects.webhook_config import WebhookConfig

logger = logging.getLogger(__name__)


@dataclass
class Settings:
    """アプリケーション設定"""

    youtube_api_key: str
    discord_webhook_url: str
    check_interval: int
    channels: List[Channel]
    notification_color: int
    log_level: str

    @classmethod
    def load(cls, config_path: str = "config/config.json") -> "Settings":
        """
        設定ファイルと環境変数から設定を読み込む

        Args:
            config_path: config.jsonのパス

        Returns:
            Settingsインスタンス

        Raises:
            ValueError: 設定が不正な場合
        """
        # .envファイル読み込み
        load_dotenv("config/.env")

        # 環境変数取得
        youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

        if not youtube_api_key:
            raise ValueError("YOUTUBE_API_KEY が設定されていません")
        if not discord_webhook_url:
            raise ValueError("DISCORD_WEBHOOK_URL が設定されていません")

        # config.json読み込み
        config_file = Path(config_path)
        if not config_file.exists():
            raise ValueError(
                f"設定ファイルが見つかりません: {config_path}\n"
                f"config/config.json.example をコピーして config/config.json を作成してください。\n"
                f"コマンド: cp config/config.json.example config/config.json"
            )

        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)

        # チャンネルリスト作成
        channels = []
        for ch in config_data["channels"]:
            webhooks = cls._parse_webhooks(ch, discord_webhook_url)
            channel = Channel(
                id=ChannelId(ch["id"]),
                name=ch["name"],
                webhooks=webhooks,
                mention=ch.get("mention", "")  # 後方互換性のため保持
            )
            channels.append(channel)

        if not channels:
            raise ValueError("監視対象チャンネルが設定されていません")

        return cls(
            youtube_api_key=youtube_api_key,
            discord_webhook_url=discord_webhook_url,
            check_interval=config_data.get("check_interval", 60),
            channels=channels,
            notification_color=config_data.get("notification", {}).get("color", 16711680),
            log_level=config_data.get("log_level", "INFO"),
        )

    @staticmethod
    def _parse_webhooks(channel_data: Dict[str, Any], default_webhook_url: str) -> List[WebhookConfig]:
        """
        チャンネル設定からWebhook設定リストを解析する

        新形式（推奨）:
        {
            "id": "UC...",
            "name": "...",
            "webhooks": [
                {"url": "https://...", "mention": "@everyone"}
            ]
        }

        旧形式（後方互換性）:
        {
            "id": "UC...",
            "name": "...",
            "mention": "@everyone"
        }

        Args:
            channel_data: チャンネル設定の辞書
            default_webhook_url: 環境変数のDISCORD_WEBHOOK_URL

        Returns:
            WebhookConfigのリスト
        """
        # 新形式: webhooksフィールドがある場合
        if "webhooks" in channel_data:
            webhooks = []
            for webhook_data in channel_data["webhooks"]:
                webhook = WebhookConfig(
                    url=webhook_data["url"],
                    mention=webhook_data.get("mention", "")
                )
                webhooks.append(webhook)
            return webhooks

        # 旧形式: mentionフィールドのみの場合
        # 環境変数のDISCORD_WEBHOOK_URLを使用して自動変換
        logger.warning(
            f"チャンネル '{channel_data['name']}' は旧形式の設定を使用しています。"
            f"新形式への移行を推奨します。詳細はREADME.mdを参照してください。"
        )

        mention = channel_data.get("mention", "@everyone")
        webhook = WebhookConfig(url=default_webhook_url, mention=mention)
        return [webhook]
