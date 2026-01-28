"""Webhook中心設定形式のユニットテスト"""

import json
import pytest
from unittest.mock import patch, mock_open
from config.settings import Settings

# テスト用の有効なYouTubeチャンネルID（24文字、UCで始まる）
CHANNEL_ID_1 = "UCxxxxxxxxxxxxxxxx111111"
CHANNEL_ID_2 = "UCxxxxxxxxxxxxxxxx222222"
CHANNEL_ID_3 = "UCxxxxxxxxxxxxxxxx333333"
CHANNEL_ID_999 = "UCxxxxxxxxxxxxxxxx999999"


class TestWebhookCentricConfiguration:
    """Webhook中心設定形式のテスト"""

    @patch("config.settings.os.getenv")
    @patch("config.settings.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_new_format_single_webhook_multiple_channels(
        self, mock_file, mock_exists, mock_getenv
    ):
        """新形式: 1 Webhook → 複数チャンネル"""
        # 設定データ
        config_data = {
            "check_interval": 300,
            "webhooks": [
                {
                    "name": "メインサーバー",
                    "url": "https://discord.com/api/webhooks/111/aaa",
                    "mention": "@everyone",
                    "channels": [CHANNEL_ID_1, CHANNEL_ID_2, CHANNEL_ID_3]
                }
            ],
            "channels": [
                {"id": CHANNEL_ID_1, "name": "配信者A"},
                {"id": CHANNEL_ID_2, "name": "配信者B"},
                {"id": CHANNEL_ID_3, "name": "配信者C"}
            ],
            "notification": {"color": 16711680},
            "log_level": "INFO"
        }

        # モック設定
        mock_getenv.side_effect = lambda key: {
            "YOUTUBE_API_KEY": "test_key",
            "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/999/zzz"
        }.get(key)
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(config_data)

        # 実行
        settings = Settings.load()

        # 検証
        assert len(settings.channels) == 3

        # 全チャンネルが同じWebhookを持つ
        for channel in settings.channels:
            assert len(channel.webhooks) == 1
            assert channel.webhooks[0].url == "https://discord.com/api/webhooks/111/aaa"
            assert channel.webhooks[0].mention == "@everyone"

    @patch("config.settings.os.getenv")
    @patch("config.settings.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_new_format_multiple_webhooks(
        self, mock_file, mock_exists, mock_getenv
    ):
        """新形式: 複数Webhook → 異なるチャンネルセット"""
        config_data = {
            "webhooks": [
                {
                    "name": "webhook_a",
                    "url": "https://discord.com/api/webhooks/111/aaa",
                    "channels": [CHANNEL_ID_1, CHANNEL_ID_2]
                },
                {
                    "name": "webhook_b",
                    "url": "https://discord.com/api/webhooks/222/bbb",
                    "channels": [CHANNEL_ID_3]
                }
            ],
            "channels": [
                {"id": CHANNEL_ID_1, "name": "A"},
                {"id": CHANNEL_ID_2, "name": "B"},
                {"id": CHANNEL_ID_3, "name": "C"}
            ]
        }

        # モック設定
        mock_getenv.side_effect = lambda key: {
            "YOUTUBE_API_KEY": "test_key",
            "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/999/zzz"
        }.get(key)
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(config_data)

        # 実行
        settings = Settings.load()

        # 検証
        assert len(settings.channels) == 3

        # CHANNEL_ID_1, CHANNEL_ID_2はwebhook_aを持つ
        channel_1 = [ch for ch in settings.channels if ch.id.value == CHANNEL_ID_1][0]
        assert len(channel_1.webhooks) == 1
        assert channel_1.webhooks[0].url == "https://discord.com/api/webhooks/111/aaa"

        channel_2 = [ch for ch in settings.channels if ch.id.value == CHANNEL_ID_2][0]
        assert len(channel_2.webhooks) == 1
        assert channel_2.webhooks[0].url == "https://discord.com/api/webhooks/111/aaa"

        # CHANNEL_ID_3はwebhook_bを持つ
        channel_3 = [ch for ch in settings.channels if ch.id.value == CHANNEL_ID_3][0]
        assert len(channel_3.webhooks) == 1
        assert channel_3.webhooks[0].url == "https://discord.com/api/webhooks/222/bbb"

    @patch("config.settings.os.getenv")
    @patch("config.settings.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_mixed_format(self, mock_file, mock_exists, mock_getenv):
        """混在形式: 新形式と旧形式を同時使用"""
        config_data = {
            "webhooks": [
                {
                    "name": "webhook_a",
                    "url": "https://discord.com/api/webhooks/111/aaa",
                    "channels": [CHANNEL_ID_1, CHANNEL_ID_2]
                }
            ],
            "channels": [
                {"id": CHANNEL_ID_1, "name": "A"},
                {
                    "id": CHANNEL_ID_2,
                    "name": "B",
                    "webhooks": [
                        {"url": "https://discord.com/api/webhooks/222/bbb", "mention": "@everyone"}
                    ]
                }
            ]
        }

        # モック設定
        mock_getenv.side_effect = lambda key: {
            "YOUTUBE_API_KEY": "test_key",
            "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/999/zzz"
        }.get(key)
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(config_data)

        # 実行
        settings = Settings.load()

        # 検証
        # CHANNEL_ID_1は1つのwebhook
        channel_1 = [ch for ch in settings.channels if ch.id.value == CHANNEL_ID_1][0]
        assert len(channel_1.webhooks) == 1
        assert channel_1.webhooks[0].url == "https://discord.com/api/webhooks/111/aaa"

        # CHANNEL_ID_2は2つのwebhook（新形式 + 旧形式）
        channel_2 = [ch for ch in settings.channels if ch.id.value == CHANNEL_ID_2][0]
        assert len(channel_2.webhooks) == 2
        webhook_urls = {wh.url for wh in channel_2.webhooks}
        assert "https://discord.com/api/webhooks/111/aaa" in webhook_urls
        assert "https://discord.com/api/webhooks/222/bbb" in webhook_urls

    @patch("config.settings.os.getenv")
    @patch("config.settings.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_duplicate_webhook_removal(self, mock_file, mock_exists, mock_getenv):
        """重複したWebhook設定は排除される"""
        config_data = {
            "webhooks": [
                {
                    "url": "https://discord.com/api/webhooks/111/aaa",
                    "mention": "@everyone",
                    "channels": [CHANNEL_ID_1]
                }
            ],
            "channels": [
                {
                    "id": CHANNEL_ID_1,
                    "name": "A",
                    "webhooks": [
                        {
                            "url": "https://discord.com/api/webhooks/111/aaa",
                            "mention": "@everyone"
                        }
                    ]
                }
            ]
        }

        # モック設定
        mock_getenv.side_effect = lambda key: {
            "YOUTUBE_API_KEY": "test_key",
            "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/999/zzz"
        }.get(key)
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(config_data)

        # 実行
        settings = Settings.load()

        # 検証: 重複は排除されて1つだけ
        channel = settings.channels[0]
        assert len(channel.webhooks) == 1

    @patch("config.settings.os.getenv")
    @patch("config.settings.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_duplicate_monitoring(self, mock_file, mock_exists, mock_getenv):
        """重複監視: 同じチャンネルを複数Webhookで監視"""
        config_data = {
            "webhooks": [
                {
                    "name": "webhook_a",
                    "url": "https://discord.com/api/webhooks/111/aaa",
                    "channels": [CHANNEL_ID_1, CHANNEL_ID_2]
                },
                {
                    "name": "webhook_b",
                    "url": "https://discord.com/api/webhooks/222/bbb",
                    "channels": [CHANNEL_ID_2]
                }
            ],
            "channels": [
                {"id": CHANNEL_ID_1, "name": "A"},
                {"id": CHANNEL_ID_2, "name": "B"}
            ]
        }

        # モック設定
        mock_getenv.side_effect = lambda key: {
            "YOUTUBE_API_KEY": "test_key",
            "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/999/zzz"
        }.get(key)
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(config_data)

        # 実行
        settings = Settings.load()

        # 検証
        # CHANNEL_ID_1は1つのwebhook
        channel_1 = [ch for ch in settings.channels if ch.id.value == CHANNEL_ID_1][0]
        assert len(channel_1.webhooks) == 1

        # CHANNEL_ID_2は2つのwebhook（重複監視）
        channel_2 = [ch for ch in settings.channels if ch.id.value == CHANNEL_ID_2][0]
        assert len(channel_2.webhooks) == 2
        webhook_urls = {wh.url for wh in channel_2.webhooks}
        assert "https://discord.com/api/webhooks/111/aaa" in webhook_urls
        assert "https://discord.com/api/webhooks/222/bbb" in webhook_urls

    @patch("config.settings.os.getenv")
    @patch("config.settings.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_channel_not_defined_error(self, mock_file, mock_exists, mock_getenv):
        """エラー: webhooksで参照したチャンネルがchannelsに存在しない"""
        config_data = {
            "webhooks": [
                {
                    "name": "test",
                    "url": "https://discord.com/api/webhooks/111/aaa",
                    "channels": [CHANNEL_ID_999]  # 存在しないチャンネル
                }
            ],
            "channels": [
                {"id": CHANNEL_ID_1, "name": "A"}
            ]
        }

        # モック設定
        mock_getenv.side_effect = lambda key: {
            "YOUTUBE_API_KEY": "test_key",
            "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/999/zzz"
        }.get(key)
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(config_data)

        # 実行と検証
        with pytest.raises(ValueError, match=f"{CHANNEL_ID_999}.*channels セクションに定義されていません"):
            Settings.load()

    @patch("config.settings.os.getenv")
    @patch("config.settings.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_webhook_missing_url_error(self, mock_file, mock_exists, mock_getenv):
        """エラー: webhooksエントリにurlがない"""
        config_data = {
            "webhooks": [
                {
                    "name": "test",
                    "channels": [CHANNEL_ID_1]  # urlがない
                }
            ],
            "channels": [
                {"id": CHANNEL_ID_1, "name": "A"}
            ]
        }

        # モック設定
        mock_getenv.side_effect = lambda key: {
            "YOUTUBE_API_KEY": "test_key",
            "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/999/zzz"
        }.get(key)
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(config_data)

        # 実行と検証
        with pytest.raises(ValueError, match="webhooks セクションの各エントリには 'url' が必要です"):
            Settings.load()

    @patch("config.settings.os.getenv")
    @patch("config.settings.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_webhook_missing_channels_error(self, mock_file, mock_exists, mock_getenv):
        """エラー: webhooksエントリにchannelsがない"""
        config_data = {
            "webhooks": [
                {
                    "name": "test",
                    "url": "https://discord.com/api/webhooks/111/aaa"
                    # channelsがない
                }
            ],
            "channels": [
                {"id": CHANNEL_ID_1, "name": "A"}
            ]
        }

        # モック設定
        mock_getenv.side_effect = lambda key: {
            "YOUTUBE_API_KEY": "test_key",
            "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/999/zzz"
        }.get(key)
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(config_data)

        # 実行と検証
        with pytest.raises(ValueError, match="webhooks セクションの各エントリには 'channels' が必要です"):
            Settings.load()

    @patch("config.settings.os.getenv")
    @patch("config.settings.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_backward_compatibility(self, mock_file, mock_exists, mock_getenv):
        """後方互換性: 旧形式のみの設定ファイル"""
        config_data = {
            "channels": [
                {
                    "id": CHANNEL_ID_1,
                    "name": "A",
                    "webhooks": [
                        {"url": "https://discord.com/api/webhooks/111/aaa", "mention": "@everyone"}
                    ]
                }
            ]
        }

        # モック設定
        mock_getenv.side_effect = lambda key: {
            "YOUTUBE_API_KEY": "test_key",
            "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/999/zzz"
        }.get(key)
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(config_data)

        # 実行
        settings = Settings.load()

        # 検証: 正常に動作
        assert len(settings.channels) == 1
        assert len(settings.channels[0].webhooks) == 1
        assert settings.channels[0].webhooks[0].url == "https://discord.com/api/webhooks/111/aaa"

    @patch("config.settings.os.getenv")
    @patch("config.settings.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_webhook_with_empty_channels(self, mock_file, mock_exists, mock_getenv):
        """警告: webhookのchannels配列が空の場合はスキップされる"""
        config_data = {
            "webhooks": [
                {
                    "name": "empty_webhook",
                    "url": "https://discord.com/api/webhooks/111/aaa",
                    "channels": []  # 空配列
                }
            ],
            "channels": [
                {
                    "id": CHANNEL_ID_1,
                    "name": "A",
                    "webhooks": [
                        {"url": "https://discord.com/api/webhooks/222/bbb", "mention": "@everyone"}
                    ]
                }
            ]
        }

        # モック設定
        mock_getenv.side_effect = lambda key: {
            "YOUTUBE_API_KEY": "test_key",
            "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/999/zzz"
        }.get(key)
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(config_data)

        # 実行
        settings = Settings.load()

        # 検証: 空のwebhookはスキップされ、チャンネルの個別webhookのみ使用される
        assert len(settings.channels) == 1
        assert len(settings.channels[0].webhooks) == 1
        assert settings.channels[0].webhooks[0].url == "https://discord.com/api/webhooks/222/bbb"
