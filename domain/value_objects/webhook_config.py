"""Webhook設定値オブジェクト

Discord WebhookのURLとメンションをセットで管理する
"""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class WebhookConfig:
    """Discord Webhook設定を表す値オブジェクト"""

    url: str
    mention: str = ""

    # Discord Webhook URLの形式: https://discord.com/api/webhooks/{id}/{token}
    WEBHOOK_PATTERN = re.compile(
        r"^https://discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_-]+$"
    )

    def __post_init__(self):
        if not self.WEBHOOK_PATTERN.match(self.url):
            raise ValueError(f"不正なWebhook URL形式: {self.url}")

    def __eq__(self, other) -> bool:
        if not isinstance(other, WebhookConfig):
            return False
        return self.url == other.url and self.mention == other.mention

    def __hash__(self) -> int:
        return hash((self.url, self.mention))
