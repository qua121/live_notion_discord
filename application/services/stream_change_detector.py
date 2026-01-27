"""配信状態変化検出サービス

ビジネスロジック:
- 前回未配信 & 今回配信中 → 配信開始
- 前回配信中 & 今回未配信 → 配信終了
- video_idの変化 → 新しい配信開始
"""

from typing import Optional
from domain.entities.stream import Stream
from application.dto.stream_state_dto import StreamStateDto


class StreamChangeDetector:
    """配信状態の変化を検出するサービス"""

    def is_stream_started(
        self, previous_state: Optional[StreamStateDto], current_stream: Optional[Stream]
    ) -> bool:
        """
        配信が開始されたかどうかを判定

        Args:
            previous_state: 前回の状態（初回はNone）
            current_stream: 現在の配信状態（配信していない場合はNone）

        Returns:
            配信開始と判定された場合True
        """
        # 現在配信していない場合は開始ではない
        if current_stream is None:
            return False

        # 初回チェックの場合は配信開始とみなす
        if previous_state is None:
            return True

        # 前回未配信で今回配信中 → 配信開始
        if not previous_state.is_live:
            return True

        # 前回と異なるvideo_id → 新しい配信開始
        if previous_state.video_id != current_stream.video_id:
            return True

        return False

    def is_stream_ended(
        self, previous_state: Optional[StreamStateDto], current_stream: Optional[Stream]
    ) -> bool:
        """
        配信が終了したかどうかを判定

        Args:
            previous_state: 前回の状態
            current_stream: 現在の配信状態

        Returns:
            配信終了と判定された場合True
        """
        # 前回の状態がない場合は終了ではない
        if previous_state is None:
            return False

        # 前回配信中で今回未配信 → 配信終了
        return previous_state.is_live and current_stream is None
