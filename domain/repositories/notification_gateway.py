"""通知送信のゲートウェイインターフェース（抽象）"""

from abc import ABC, abstractmethod
from domain.entities.channel import Channel
from domain.entities.stream import Stream


class NotificationGateway(ABC):
    """通知を送信するためのゲートウェイインターフェース"""

    @abstractmethod
    def notify_stream_start(self, channel: Channel, stream: Stream) -> None:
        """
        配信開始通知を送信

        Args:
            channel: 配信を開始したチャンネル
            stream: 開始した配信

        Raises:
            NotificationError: 通知送信エラー
        """
        pass
