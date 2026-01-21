"""状態管理のリポジトリインターフェース（抽象）"""

from abc import ABC, abstractmethod
from typing import Optional
from domain.value_objects.channel_id import ChannelId
from application.dto.stream_state_dto import StreamStateDto


class StateRepository(ABC):
    """配信状態を永続化するためのリポジトリインターフェース"""

    @abstractmethod
    def get_state(self, channel_id: ChannelId) -> Optional[StreamStateDto]:
        """
        チャンネルの前回の状態を取得

        Args:
            channel_id: チャンネルID

        Returns:
            前回の状態。初回の場合はNone
        """
        pass

    @abstractmethod
    def save_state(self, channel_id: ChannelId, state: StreamStateDto) -> None:
        """
        チャンネルの状態を保存

        Args:
            channel_id: チャンネルID
            state: 保存する状態

        Raises:
            StateRepositoryError: 保存エラー
        """
        pass
