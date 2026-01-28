"""Settings設定ファイル読み込みと移行のユニットテスト"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from config.settings import Settings


class TestSettingsMigration:
    """設定ファイルの読み込みと移行のテスト"""

    def test_parse_webhooks_new_format_single_webhook(self):
        """新形式（単一webhook）を正しく解析できる"""
        channel_data = {
            "id": "UC1234567890123456789012",
            "name": "テストチャンネル",
            "webhooks": [
                {
                    "url": "https://discord.com/api/webhooks/123456789/abcdefg",
                    "mention": "@everyone"
                }
            ]
        }
        default_url = "https://discord.com/api/webhooks/999999999/default"

        webhooks = Settings._parse_webhooks(channel_data, default_url)

        assert len(webhooks) == 1
        assert webhooks[0].url == "https://discord.com/api/webhooks/123456789/abcdefg"
        assert webhooks[0].mention == "@everyone"

    def test_parse_webhooks_new_format_multiple_webhooks(self):
        """新形式（複数webhook）を正しく解析できる"""
        channel_data = {
            "id": "UC1234567890123456789012",
            "name": "テストチャンネル",
            "webhooks": [
                {
                    "url": "https://discord.com/api/webhooks/111111111/aaa",
                    "mention": "@everyone"
                },
                {
                    "url": "https://discord.com/api/webhooks/222222222/bbb",
                    "mention": "<@&1234567890>"
                }
            ]
        }
        default_url = "https://discord.com/api/webhooks/999999999/default"

        webhooks = Settings._parse_webhooks(channel_data, default_url)

        assert len(webhooks) == 2
        assert webhooks[0].url == "https://discord.com/api/webhooks/111111111/aaa"
        assert webhooks[0].mention == "@everyone"
        assert webhooks[1].url == "https://discord.com/api/webhooks/222222222/bbb"
        assert webhooks[1].mention == "<@&1234567890>"

    def test_parse_webhooks_new_format_no_mention(self):
        """新形式でmentionが省略された場合、空文字列になる"""
        channel_data = {
            "id": "UC1234567890123456789012",
            "name": "テストチャンネル",
            "webhooks": [
                {
                    "url": "https://discord.com/api/webhooks/123456789/abcdefg"
                }
            ]
        }
        default_url = "https://discord.com/api/webhooks/999999999/default"

        webhooks = Settings._parse_webhooks(channel_data, default_url)

        assert len(webhooks) == 1
        assert webhooks[0].mention == ""

    def test_parse_webhooks_old_format_with_mention(self):
        """旧形式（mention指定あり）を新形式に自動変換できる"""
        channel_data = {
            "id": "UC1234567890123456789012",
            "name": "テストチャンネル",
            "mention": "@everyone"
        }
        default_url = "https://discord.com/api/webhooks/999999999/default"

        webhooks = Settings._parse_webhooks(channel_data, default_url)

        assert len(webhooks) == 1
        assert webhooks[0].url == default_url
        assert webhooks[0].mention == "@everyone"

    def test_parse_webhooks_old_format_without_mention(self):
        """旧形式（mention省略）を新形式に自動変換できる"""
        channel_data = {
            "id": "UC1234567890123456789012",
            "name": "テストチャンネル"
        }
        default_url = "https://discord.com/api/webhooks/999999999/default"

        webhooks = Settings._parse_webhooks(channel_data, default_url)

        assert len(webhooks) == 1
        assert webhooks[0].url == default_url
        assert webhooks[0].mention == "@everyone"

    def test_load_with_new_format_config(self, tmp_path, monkeypatch):
        """新形式の設定ファイルを正しく読み込める"""
        # 一時的な設定ファイルを作成
        config_data = {
            "check_interval": 300,
            "channels": [
                {
                    "id": "UC1234567890123456789012",
                    "name": "テストチャンネル",
                    "webhooks": [
                        {
                            "url": "https://discord.com/api/webhooks/123456789/abcdefg",
                            "mention": "@everyone"
                        }
                    ]
                }
            ],
            "notification": {
                "color": 16711680
            },
            "log_level": "INFO"
        }

        config_file = tmp_path / "config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f)

        # 環境変数を設定
        monkeypatch.setenv("YOUTUBE_API_KEY", "test_api_key")
        monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/999999999/default")

        # 設定を読み込む
        settings = Settings.load(str(config_file))

        assert settings.check_interval == 300
        assert len(settings.channels) == 1
        assert settings.channels[0].name == "テストチャンネル"
        assert len(settings.channels[0].webhooks) == 1
        assert settings.channels[0].webhooks[0].url == "https://discord.com/api/webhooks/123456789/abcdefg"

    def test_load_with_old_format_config(self, tmp_path, monkeypatch):
        """旧形式の設定ファイルを自動変換して読み込める"""
        # 一時的な設定ファイルを作成（旧形式）
        config_data = {
            "channels": [
                {
                    "id": "UC1234567890123456789012",
                    "name": "テストチャンネル",
                    "mention": "@everyone"
                }
            ]
        }

        config_file = tmp_path / "config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f)

        # 環境変数を設定
        monkeypatch.setenv("YOUTUBE_API_KEY", "test_api_key")
        monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/999999999/default")

        # 設定を読み込む
        settings = Settings.load(str(config_file))

        assert len(settings.channels) == 1
        assert settings.channels[0].name == "テストチャンネル"
        assert len(settings.channels[0].webhooks) == 1
        # 環境変数のwebhook URLが使用されている
        assert settings.channels[0].webhooks[0].url == "https://discord.com/api/webhooks/999999999/default"
        assert settings.channels[0].webhooks[0].mention == "@everyone"
