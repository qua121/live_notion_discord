"""CLIコントローラー

ユーザーインターフェースとして動作
"""

import logging
import time
import signal
from typing import List

from domain.entities.channel import Channel
from application.use_cases.monitor_streams_use_case import MonitorStreamsUseCase
from infrastructure.youtube.youtube_stream_repository import QuotaExceededError

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

            except QuotaExceededError as e:
                # クォータ超過エラー: JST 18:00まで待機
                logger.error(f"YouTube APIクォータ超過: {e}")

                # エラーメッセージから待機秒数を抽出
                wait_seconds = self._extract_wait_seconds(str(e))

                if wait_seconds > 0:
                    hours = wait_seconds // 3600
                    minutes = (wait_seconds % 3600) // 60
                    logger.info(f"JST 18:00まで待機します（約{hours}時間{minutes}分）...")
                    logger.info("待機中はCtrl+Cで中断できます")

                    # 待機（1分ごとにチェックして終了フラグを確認）
                    self._wait_with_interrupt_check(wait_seconds)

                    if self._running:
                        logger.info("待機完了。監視を再開します...")
                else:
                    logger.error("待機時間の計算に失敗しました。60秒後にリトライします...")
                    time.sleep(60)

            except Exception as e:
                logger.error(f"監視ループでエラー発生: {e}", exc_info=True)
                time.sleep(self._check_interval)

    def _extract_wait_seconds(self, error_message: str) -> int:
        """
        エラーメッセージから待機秒数を抽出

        Args:
            error_message: エラーメッセージ

        Returns:
            待機秒数（抽出失敗時は0）
        """
        import re

        match = re.search(r"(\d+)秒待機", error_message)
        if match:
            return int(match.group(1))
        return 0

    def _wait_with_interrupt_check(self, total_seconds: int) -> None:
        """
        指定秒数待機（1分ごとに終了フラグをチェック）

        Args:
            total_seconds: 待機秒数
        """
        remaining = total_seconds
        check_interval = 60  # 1分ごとにチェック

        while remaining > 0 and self._running:
            sleep_time = min(check_interval, remaining)
            time.sleep(sleep_time)
            remaining -= sleep_time

            # 進捗をログ出力（10分ごと）
            if remaining > 0 and remaining % 600 == 0:
                hours = remaining // 3600
                minutes = (remaining % 3600) // 60
                logger.info(f"残り待機時間: 約{hours}時間{minutes}分")

    def _handle_shutdown(self, signum, frame):
        """シャットダウンハンドラー"""
        logger.info("終了シグナルを受信しました...")
        self._running = False
