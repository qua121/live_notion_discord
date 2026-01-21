"""配信状態データ転送オブジェクト"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class StreamStateDto:
    """配信状態を表すDTO（レイヤー間のデータ転送用）"""

    is_live: bool
    video_id: Optional[str]
    last_checked: datetime
    last_notified: Optional[datetime]

    def to_dict(self) -> dict:
        """辞書形式に変換（JSON保存用）"""
        return {
            'is_live': self.is_live,
            'video_id': self.video_id,
            'last_checked': self.last_checked.isoformat(),
            'last_notified': self.last_notified.isoformat() if self.last_notified else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'StreamStateDto':
        """辞書形式から復元（JSON読み込み用）"""
        return cls(
            is_live=data['is_live'],
            video_id=data.get('video_id'),
            last_checked=datetime.fromisoformat(data['last_checked']),
            last_notified=datetime.fromisoformat(data['last_notified']) if data.get('last_notified') else None
        )
