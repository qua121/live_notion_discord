"""配信状態の列挙型"""

from enum import Enum, auto


class StreamStatus(Enum):
    """配信状態"""

    LIVE = auto()  # 配信中
    OFFLINE = auto()  # 未配信
    ENDED = auto()  # 配信終了
