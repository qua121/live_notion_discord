"""設定管理クラス"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

from domain.entities.channel import Channel
from domain.value_objects.channel_id import ChannelId


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
    def load(cls, config_path: str = 'config/config.json') -> 'Settings':
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
        load_dotenv('config/.env')

        # 環境変数取得
        youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

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

        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # チャンネルリスト作成
        channels = [
            Channel(
                id=ChannelId(ch['id']),
                name=ch['name'],
                mention=ch.get('mention', '@everyone')
            )
            for ch in config_data['channels']
        ]

        if not channels:
            raise ValueError("監視対象チャンネルが設定されていません")

        return cls(
            youtube_api_key=youtube_api_key,
            discord_webhook_url=discord_webhook_url,
            check_interval=config_data.get('check_interval', 60),
            channels=channels,
            notification_color=config_data.get('notification', {}).get('color', 16711680),
            log_level=config_data.get('log_level', 'INFO')
        )
