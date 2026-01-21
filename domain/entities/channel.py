"""チャンネルエンティティ

ビジネスルール:
- チャンネルIDは一意である
- チャンネル名は空文字列不可
- メンション設定は変更可能
"""

from dataclasses import dataclass
from domain.value_objects.channel_id import ChannelId


@dataclass(frozen=True)  # イミュータブル
class Channel:
    """YouTubeチャンネルを表すエンティティ"""

    id: ChannelId
    name: str
    mention: str

    def __post_init__(self):
        if not self.name:
            raise ValueError("チャンネル名は空にできません")

    def __eq__(self, other) -> bool:
        """同一性はIDで判断"""
        if not isinstance(other, Channel):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
