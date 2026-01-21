"""チャンネルID値オブジェクト

YouTubeのチャンネルIDの形式を保証する
"""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ChannelId:
    """YouTubeチャンネルIDを表す値オブジェクト"""

    value: str

    # YouTubeチャンネルIDの形式: UCで始まる24文字
    PATTERN = re.compile(r'^UC[a-zA-Z0-9_-]{22}$')

    def __post_init__(self):
        if not self.PATTERN.match(self.value):
            raise ValueError(f"不正なチャンネルID形式: {self.value}")

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        if not isinstance(other, ChannelId):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
