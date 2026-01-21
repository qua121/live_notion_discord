"""配信情報取得のリポジトリインターフェース（抽象）

Infrastructure層で実装される
"""

from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.channel import Channel
from domain.entities.stream import Stream


class StreamRepository(ABC):
    """配信情報を取得するためのリポジトリインターフェース"""

    @abstractmethod
    def get_current_stream(self, channel: Channel) -> Optional[Stream]:
        """
        チャンネルの現在の配信を取得

        Args:
            channel: 取得対象のチャンネル

        Returns:
            配信中の場合はStreamオブジェクト、配信していない場合はNone

        Raises:
            RepositoryError: APIエラーやネットワークエラー
        """
        pass
