"""配信監視ユースケース

責務:
1. 各チャンネルの現在の配信状態を取得
2. 前回の状態と比較して変化を検出
3. 配信開始を検出した場合は通知
4. 状態を更新して保存

依存性: インターフェース（抽象）のみに依存
"""

from typing import List
import logging
from datetime import datetime

from domain.entities.channel import Channel
from domain.repositories.stream_repository import StreamRepository
from domain.repositories.notification_gateway import NotificationGateway
from domain.repositories.state_repository import StateRepository
from application.services.stream_change_detector import StreamChangeDetector
from application.dto.stream_state_dto import StreamStateDto

logger = logging.getLogger(__name__)


class MonitorStreamsUseCase:
    """配信監視を実行するユースケース"""

    def __init__(
        self,
        stream_repository: StreamRepository,
        notification_gateway: NotificationGateway,
        state_repository: StateRepository,
        change_detector: StreamChangeDetector
    ):
        """
        依存性注入（すべて抽象インターフェースに依存）
        """
        self._stream_repo = stream_repository
        self._notification_gateway = notification_gateway
        self._state_repo = state_repository
        self._change_detector = change_detector

    def execute(self, channels: List[Channel]) -> None:
        """
        監視を実行

        Args:
            channels: 監視対象のチャンネルリスト
        """
        logger.info(f"監視開始: {len(channels)}チャンネル")

        for channel in channels:
            try:
                self._check_channel(channel)
            except Exception as e:
                logger.error(f"チャンネル {channel.name} の監視中にエラー: {e}", exc_info=True)

    def _check_channel(self, channel: Channel) -> None:
        """単一チャンネルの監視処理"""
        logger.debug(f"チャンネル {channel.name} をチェック中")

        # 1. 現在の配信状態を取得
        current_stream = self._stream_repo.get_current_stream(channel)

        # 2. 前回の状態を取得
        previous_state = self._state_repo.get_state(channel.id)

        # 3. 配信開始を検出
        if self._change_detector.is_stream_started(previous_state, current_stream):
            logger.info(f"配信開始を検知: {channel.name} - {current_stream.title}")

            # 4. 通知送信
            try:
                self._notification_gateway.notify_stream_start(channel, current_stream)
                logger.info(f"通知送信完了: {channel.name}")
            except Exception as e:
                logger.error(f"通知送信失敗: {channel.name} - {e}")
                # 通知失敗しても状態は更新しない（次回再試行）
                return

            # 5. 状態更新
            new_state = StreamStateDto(
                is_live=True,
                video_id=current_stream.video_id,
                last_checked=datetime.now(),
                last_notified=datetime.now()
            )
            self._state_repo.save_state(channel.id, new_state)

        # 配信中だが通知済みの場合は状態のみ更新
        elif current_stream is not None and previous_state and previous_state.is_live:
            updated_state = StreamStateDto(
                is_live=True,
                video_id=current_stream.video_id,
                last_checked=datetime.now(),
                last_notified=previous_state.last_notified
            )
            self._state_repo.save_state(channel.id, updated_state)

        # 配信していない場合
        elif current_stream is None:
            if previous_state is None or previous_state.is_live:
                # 状態を未配信に更新
                offline_state = StreamStateDto(
                    is_live=False,
                    video_id=None,
                    last_checked=datetime.now(),
                    last_notified=previous_state.last_notified if previous_state else None
                )
                self._state_repo.save_state(channel.id, offline_state)
