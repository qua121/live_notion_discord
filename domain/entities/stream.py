"""配信エンティティ

ビジネスルール:
- video_idは一意である
- タイトルは空文字列不可
- 配信状態は定義された値のみ
"""

from dataclasses import dataclass
from datetime import datetime
from domain.value_objects.stream_status import StreamStatus


@dataclass(frozen=True)
class Stream:
    """YouTube配信を表すエンティティ"""

    video_id: str
    title: str
    thumbnail_url: str
    started_at: datetime
    status: StreamStatus

    def __post_init__(self):
        if not self.video_id:
            raise ValueError("video_idは必須です")
        if not self.title:
            raise ValueError("タイトルは必須です")

    def is_live(self) -> bool:
        """配信中かどうか"""
        return self.status == StreamStatus.LIVE

    def __eq__(self, other) -> bool:
        """同一性はvideo_idで判断"""
        if not isinstance(other, Stream):
            return False
        return self.video_id == other.video_id

    def __hash__(self) -> int:
        return hash(self.video_id)
