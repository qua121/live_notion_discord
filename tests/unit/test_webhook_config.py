"""WebhookConfig値オブジェクトのユニットテスト"""

import pytest
from domain.value_objects.webhook_config import WebhookConfig


class TestWebhookConfig:
    """WebhookConfigのテスト"""

    def test_valid_webhook_config_with_mention(self):
        """正しいWebhook URLとメンションで正常に作成される"""
        config = WebhookConfig(
            url="https://discord.com/api/webhooks/123456789/abcdefg",
            mention="<@&1234567890>"
        )
        assert config.url == "https://discord.com/api/webhooks/123456789/abcdefg"
        assert config.mention == "<@&1234567890>"

    def test_valid_webhook_config_without_mention(self):
        """メンションなしでも正常に作成される"""
        config = WebhookConfig(
            url="https://discord.com/api/webhooks/123456789/abcdefg"
        )
        assert config.url == "https://discord.com/api/webhooks/123456789/abcdefg"
        assert config.mention == ""

    def test_valid_webhook_config_with_everyone_mention(self):
        """@everyoneメンションで正常に作成される"""
        config = WebhookConfig(
            url="https://discord.com/api/webhooks/123456789/abcdefg",
            mention="@everyone"
        )
        assert config.mention == "@everyone"

    def test_valid_webhook_config_discordapp_domain(self):
        """discordapp.comドメインのURLも受け入れる"""
        config = WebhookConfig(
            url="https://discordapp.com/api/webhooks/123456789/abcdefg"
        )
        assert config.url == "https://discordapp.com/api/webhooks/123456789/abcdefg"

    def test_invalid_webhook_url_not_discord(self):
        """Discord以外のURLの場合、ValueErrorが発生"""
        with pytest.raises(ValueError, match="不正なWebhook URL形式"):
            WebhookConfig(url="https://example.com/webhook")

    def test_invalid_webhook_url_missing_id(self):
        """Webhook IDが欠けている場合、ValueErrorが発生"""
        with pytest.raises(ValueError, match="不正なWebhook URL形式"):
            WebhookConfig(url="https://discord.com/api/webhooks/")

    def test_invalid_webhook_url_missing_token(self):
        """Webhook tokenが欠けている場合、ValueErrorが発生"""
        with pytest.raises(ValueError, match="不正なWebhook URL形式"):
            WebhookConfig(url="https://discord.com/api/webhooks/123456789/")

    def test_invalid_webhook_url_http_not_https(self):
        """httpプロトコルの場合、ValueErrorが発生"""
        with pytest.raises(ValueError, match="不正なWebhook URL形式"):
            WebhookConfig(url="http://discord.com/api/webhooks/123456789/abcdefg")

    def test_webhook_config_equality(self):
        """同じURLとメンションのWebhookConfigは等しい"""
        config1 = WebhookConfig(
            url="https://discord.com/api/webhooks/123456789/abcdefg",
            mention="@everyone"
        )
        config2 = WebhookConfig(
            url="https://discord.com/api/webhooks/123456789/abcdefg",
            mention="@everyone"
        )
        assert config1 == config2

    def test_webhook_config_inequality_different_url(self):
        """異なるURLのWebhookConfigは等しくない"""
        config1 = WebhookConfig(
            url="https://discord.com/api/webhooks/123456789/abcdefg",
            mention="@everyone"
        )
        config2 = WebhookConfig(
            url="https://discord.com/api/webhooks/987654321/xyz",
            mention="@everyone"
        )
        assert config1 != config2

    def test_webhook_config_inequality_different_mention(self):
        """異なるメンションのWebhookConfigは等しくない"""
        config1 = WebhookConfig(
            url="https://discord.com/api/webhooks/123456789/abcdefg",
            mention="@everyone"
        )
        config2 = WebhookConfig(
            url="https://discord.com/api/webhooks/123456789/abcdefg",
            mention="<@&1234567890>"
        )
        assert config1 != config2

    def test_webhook_config_hash(self):
        """WebhookConfigはハッシュ可能"""
        config1 = WebhookConfig(
            url="https://discord.com/api/webhooks/123456789/abcdefg",
            mention="@everyone"
        )
        config2 = WebhookConfig(
            url="https://discord.com/api/webhooks/123456789/abcdefg",
            mention="@everyone"
        )
        assert hash(config1) == hash(config2)

    def test_webhook_config_immutable(self):
        """WebhookConfigは不変オブジェクト"""
        config = WebhookConfig(
            url="https://discord.com/api/webhooks/123456789/abcdefg",
            mention="@everyone"
        )
        with pytest.raises(Exception):  # dataclass frozen=True raises FrozenInstanceError
            config.url = "https://discord.com/api/webhooks/111111111/newtoken"
