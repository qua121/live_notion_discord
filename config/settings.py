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

        # チャンネルリスト作成（新旧両形式サポート）
        channels = cls._load_channels(config_data, discord_webhook_url)

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

    @classmethod
    def _load_channels(
        cls, config_data: Dict[str, Any], default_webhook_url: str
    ) -> List[Channel]:
        """
        新旧両形式の設定をサポートしたチャンネル読み込み

        Args:
            config_data: config.jsonの内容
            default_webhook_url: 環境変数のDISCORD_WEBHOOK_URL

        Returns:
            Channelのリスト

        Raises:
            ValueError: 設定が不正な場合
        """
        # Step 1: 新形式 webhooks セクションを解析
        # チャンネルID → Webhookリスト のマッピングを作成
        channel_to_webhooks_from_new = {}  # Dict[str, List[WebhookConfig]]

        if "webhooks" in config_data:
            logger.info("Webhook中心設定を検出")
            for webhook_entry in config_data["webhooks"]:
                cls._validate_webhook_entry(webhook_entry)

                webhook_name = webhook_entry.get("name", "")
                webhook_url = webhook_entry["url"]
                webhook_mention = webhook_entry.get("mention", "")
                channel_ids = webhook_entry.get("channels", [])

                if len(channel_ids) == 0:
                    logger.warning(
                        f"Webhook '{webhook_name or webhook_url[:50]}' は "
                        f"監視対象チャンネルが設定されていません（スキップ）"
                    )
                    continue

                # WebhookConfigを作成
                webhook_config = WebhookConfig(url=webhook_url, mention=webhook_mention)

                # 各チャンネルIDに対してこのwebhookを追加
                for channel_id in channel_ids:
                    if channel_id not in channel_to_webhooks_from_new:
                        channel_to_webhooks_from_new[channel_id] = []
                    channel_to_webhooks_from_new[channel_id].append(webhook_config)

                logger.info(
                    f"  Webhook '{webhook_name or webhook_url[:50]}...' "
                    f"→ {len(channel_ids)}チャンネル"
                )

        # Step 2: channels セクションからチャンネル情報を取得
        channel_info = {}  # Dict[str, {"name": str, "webhooks": List[WebhookConfig], "mention": str}]

        for channel_data in config_data.get("channels", []):
            channel_id = channel_data["id"]
            channel_name = channel_data["name"]

            # 旧形式のwebhooks（channels[].webhooks または mention）を解析
            # ただし、新形式のwebhooksセクションが存在する場合は、
            # channels[].webhooks または mention が明示的に指定されている場合のみ解析
            webhooks_from_old = []
            has_channel_level_webhook = "webhooks" in channel_data or "mention" in channel_data

            if has_channel_level_webhook:
                webhooks_from_old = cls._parse_webhooks(channel_data, default_webhook_url)

            channel_info[channel_id] = {
                "name": channel_name,
                "webhooks": webhooks_from_old,
                "mention": channel_data.get("mention", "")
            }

        # Step 3: 新形式と旧形式をマージ
        for channel_id, webhooks in channel_to_webhooks_from_new.items():
            if channel_id not in channel_info:
                raise ValueError(
                    f"チャンネルID '{channel_id}' が webhooks セクションで参照されていますが、"
                    f"channels セクションに定義されていません。"
                )

            # Webhookリストをマージ（重複排除）
            existing_webhooks = channel_info[channel_id]["webhooks"]
            for new_webhook in webhooks:
                if new_webhook not in existing_webhooks:
                    existing_webhooks.append(new_webhook)
                else:
                    logger.debug(
                        f"重複したWebhook設定を検出（スキップ）: "
                        f"{new_webhook.url[:50]}..."
                    )

        # Step 4: Channel エンティティを生成
        channels = []
        for channel_id, info in channel_info.items():
            if not info["webhooks"]:
                raise ValueError(
                    f"チャンネル '{info['name']}' ({channel_id}) には "
                    f"最低1つのWebhook設定が必要です"
                )

            channel = Channel(
                id=ChannelId(channel_id),
                name=info["name"],
                webhooks=info["webhooks"],
                mention=info["mention"]
            )
            channels.append(channel)

            # ログ出力（Webhook数）
            if len(info["webhooks"]) > 1:
                logger.info(
                    f"チャンネル '{info['name']}' は {len(info['webhooks'])} 個の"
                    f"Webhookで監視されています（重複監視）"
                )

        return channels

    @staticmethod
    def _validate_webhook_entry(webhook_entry: Dict[str, Any]) -> None:
        """
        新形式のwebhook設定をバリデーション

        Args:
            webhook_entry: webhooksセクションの各エントリ

        Raises:
            ValueError: 設定が不正な場合
        """
        # 必須フィールドチェック
        if "url" not in webhook_entry:
            raise ValueError(
                "webhooks セクションの各エントリには 'url' が必要です"
            )

        if "channels" not in webhook_entry:
            webhook_name = webhook_entry.get("name", webhook_entry["url"][:50] + "...")
            raise ValueError(
                f"webhooks セクションの各エントリには 'channels' が必要です\n"
                f"Webhook: {webhook_name}"
            )

        # channelsは配列であることを確認
        if not isinstance(webhook_entry["channels"], list):
            webhook_name = webhook_entry.get("name", webhook_entry["url"][:50] + "...")
            raise ValueError(
                f"webhooks.channels は配列である必要があります\n"
                f"Webhook: {webhook_name}"
            )
