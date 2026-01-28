"""チャンネルエンティティ

ビジネスルール:
- チャンネルIDは一意である
- チャンネル名は空文字列不可
- 最低1つのWebhook設定が必要
- メンション設定は後方互換性のため保持（非推奨）
"""

from dataclasses import dataclass
from typing import List
from domain.value_objects.channel_id import ChannelId
from domain.value_objects.webhook_config import WebhookConfig


@dataclass(frozen=True)  # イミュータブル
class Channel:
    """YouTubeチャンネルを表すエンティティ"""

    id: ChannelId
    name: str
    webhooks: List[WebhookConfig]
    mention: str = ""  # 後方互換性のため保持（非推奨）

    def __post_init__(self):
        if not self.name:
            raise ValueError("チャンネル名は空にできません")
        if not self.webhooks:
            raise ValueError("最低1つのWebhook設定が必要です")

    def __eq__(self, other) -> bool:
        """同一性はIDで判断"""
        if not isinstance(other, Channel):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
