"""CLIコントローラー

ユーザーインターフェースとして動作
"""

import logging
import time
import signal
from datetime import datetime
from typing import List
import pytz

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
        logger.info(f"チェック間隔: {self._check_interval}秒 (5分)")
        logger.info("=" * 60)

        for channel in self._channels:
            webhook_count = len(channel.webhooks)
            logger.info(f"  - {channel.name} ({channel.id}) - Webhook数: {webhook_count}")

        logger.info("=" * 60)
        logger.info("監視開始（Ctrl+Cで終了）")

        # 初回は即座にチェック
        first_check = True

        # 監視ループ
        while self._running:
            try:
                # 現在時刻（JST）を取得
                jst = pytz.timezone("Asia/Tokyo")
                now_jst = datetime.now(jst)
                logger.info(f"チェック実行: {now_jst.strftime('%Y-%m-%d %H:%M:%S JST')}")

                self._use_case.execute(self._channels)

                if self._running:  # 終了フラグチェック
                    # 次の5の倍数まで待機
                    wait_seconds = self._calculate_wait_until_next_5min()

                    # 次のチェック時刻を計算（表示用）
                    next_time = datetime.now(jst).replace(second=0, microsecond=0)
                    minutes_now = next_time.minute
                    next_5min = ((minutes_now // 5) + 1) * 5
                    if next_5min >= 60:
                        next_time = next_time.replace(hour=(next_time.hour + 1) % 24, minute=0)
                    else:
                        next_time = next_time.replace(minute=next_5min)

                    logger.info(
                        f"次回チェックまで {wait_seconds}秒 待機 "
                        f"(次回: {next_time.strftime('%H:%M:%S')} JST)"
                    )

                    if first_check:
                        first_check = False

                    self._wait_with_interrupt_check(
                        wait_seconds, check_interval=1, show_progress=False
                    )

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
                    self._wait_with_interrupt_check(60, check_interval=1, show_progress=False)

            except Exception as e:
                logger.error(f"監視ループでエラー発生: {e}", exc_info=True)
                self._wait_with_interrupt_check(
                    self._check_interval, check_interval=1, show_progress=False
                )

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

    def _wait_with_interrupt_check(
        self, total_seconds: int, check_interval: int = 60, show_progress: bool = True
    ) -> None:
        """
        指定秒数待機（定期的に終了フラグをチェック）

        Args:
            total_seconds: 待機秒数
            check_interval: チェック間隔（秒）デフォルト60秒
            show_progress: 進捗ログを表示するか（長時間待機用）
        """
        remaining = total_seconds

        while remaining > 0 and self._running:
            sleep_time = min(check_interval, remaining)
            time.sleep(sleep_time)
            remaining -= sleep_time

            # 進捗をログ出力（10分ごと、show_progressがTrueの場合のみ）
            if show_progress and remaining > 0 and remaining % 600 == 0:
                hours = remaining // 3600
                minutes = (remaining % 3600) // 60
                logger.info(f"残り待機時間: 約{hours}時間{minutes}分")

    def _calculate_wait_until_next_5min(self) -> int:
        """
        次の5の倍数の分（JST基準）まで何秒待つかを計算

        例:
        - 現在時刻が14:23:45の場合 -> 14:25:00まで = 75秒
        - 現在時刻が14:25:00の場合 -> 14:30:00まで = 300秒
        - 現在時刻が14:28:30の場合 -> 14:30:00まで = 90秒

        Returns:
            次の5分の倍数まで何秒待つか
        """
        jst = pytz.timezone("Asia/Tokyo")
        now_jst = datetime.now(jst)

        # 現在の分と秒
        current_minute = now_jst.minute
        current_second = now_jst.second

        # 次の5の倍数の分を計算
        next_5min = ((current_minute // 5) + 1) * 5

        # 次の5分の倍数までの秒数を計算
        if next_5min >= 60:
            # 次の時間に繰り上がる場合
            minutes_to_wait = 60 - current_minute
            seconds_to_wait = minutes_to_wait * 60 - current_second
        else:
            # 同じ時間内の場合
            minutes_to_wait = next_5min - current_minute
            seconds_to_wait = minutes_to_wait * 60 - current_second

        return seconds_to_wait

    def _handle_shutdown(self, signum, frame):
        """シャットダウンハンドラー"""
        logger.info("終了シグナルを受信しました...")
        self._running = False
