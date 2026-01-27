"""CLIコントローラー

ユーザーインターフェースとして動作
"""

import logging
import time
import signal
from typing import List

from domain.entities.channel import Channel
from application.use_cases.monitor_streams_use_case import MonitorStreamsUseCase

logger = logging.getLogger(__name__)


class MonitorController:
    """監視を制御するCLIコントローラー"""

    def __init__(
        self, use_case: MonitorStreamsUseCase, channels: List[Channel], check_interval: int
    ):
        """
        Args:
            use_case: 配信監視ユースケース
            channels: 監視対象チャンネル
            check_interval: チェック間隔（秒）
        """
        self._use_case = use_case
        self._channels = channels
        self._check_interval = check_interval
        self._running = False

    def start(self) -> None:
        """監視を開始"""
        self._running = True

        # シグナルハンドラー設定（Ctrl+C対応）
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

        logger.info("=" * 60)
        logger.info("YouTube配信監視システム起動")
        logger.info(f"監視チャンネル数: {len(self._channels)}")
        logger.info(f"チェック間隔: {self._check_interval}秒")
        logger.info("=" * 60)

        for channel in self._channels:
            logger.info(f"  - {channel.name} ({channel.id})")

        logger.info("=" * 60)
        logger.info("監視開始（Ctrl+Cで終了）")

        # 監視ループ
        while self._running:
            try:
                self._use_case.execute(self._channels)

                if self._running:  # 終了フラグチェック
                    time.sleep(self._check_interval)

            except Exception as e:
                logger.error(f"監視ループでエラー発生: {e}", exc_info=True)
                time.sleep(self._check_interval)

    def _handle_shutdown(self, signum, frame):
        """シャットダウンハンドラー"""
        logger.info("終了シグナルを受信しました...")
        self._running = False
