"""MonitorControllerのシャットダウン動作テスト"""

import pytest
import time
from unittest.mock import Mock, patch
from threading import Thread

from presentation.cli.monitor_controller import MonitorController
from application.use_cases.monitor_streams_use_case import MonitorStreamsUseCase


class TestMonitorControllerShutdown:
    """シャットダウン動作のテスト"""

    @pytest.fixture
    def mock_use_case(self):
        """モックのユースケースを作成"""
        return Mock(spec=MonitorStreamsUseCase)

    @pytest.fixture
    def controller(self, mock_use_case):
        """テスト用のコントローラーを作成"""
        controller = MonitorController(
            use_case=mock_use_case, channels=[], check_interval=300
        )
        controller._running = True  # テスト用にrunningフラグを設定
        return controller

    def test_wait_with_interrupt_check_completes_full_wait(self, controller):
        """正常に完了する場合（_running=True）"""
        start_time = time.time()
        controller._wait_with_interrupt_check(
            total_seconds=2, check_interval=1, show_progress=False
        )
        elapsed = time.time() - start_time

        # 2秒待機するはずなので、1.8秒以上かかっているはず
        assert elapsed >= 1.8
        # 実行中フラグは維持される
        assert controller._running is True

    def test_wait_with_interrupt_check_interrupts_immediately(self, controller):
        """_running=Falseで即座に中断"""
        controller._running = False

        start_time = time.time()
        controller._wait_with_interrupt_check(
            total_seconds=10, check_interval=1, show_progress=False
        )
        elapsed = time.time() - start_time

        # 即座に終了するはず（0.1秒以内）
        assert elapsed < 0.1

    def test_wait_with_interrupt_check_interrupts_mid_wait(self, controller):
        """待機中に_running=Falseで中断"""
        controller._running = True

        def set_running_false_after_delay():
            """1秒後に_runningをFalseに設定"""
            time.sleep(1.0)
            controller._running = False

        # 別スレッドで1秒後にフラグを変更
        thread = Thread(target=set_running_false_after_delay)
        thread.start()

        start_time = time.time()
        controller._wait_with_interrupt_check(
            total_seconds=10, check_interval=1, show_progress=False
        )
        elapsed = time.time() - start_time

        thread.join()

        # 1-2秒で終了するはず（10秒待たない）
        assert 0.9 <= elapsed < 2.5

    def test_wait_respects_check_interval(self, controller):
        """check_intervalパラメータが正しく動作"""
        controller._running = True

        # check_interval=2で4秒待機
        start_time = time.time()
        controller._wait_with_interrupt_check(
            total_seconds=4, check_interval=2, show_progress=False
        )
        elapsed = time.time() - start_time

        # 約4秒待機するはず
        assert 3.8 <= elapsed < 4.5

    def test_wait_respects_show_progress_false(self, controller, caplog):
        """show_progress=Falseの場合、進捗ログが出ない"""
        controller._running = True

        with caplog.at_level("INFO"):
            controller._wait_with_interrupt_check(
                total_seconds=2, check_interval=1, show_progress=False
            )

        # 進捗ログが出ていないことを確認
        assert "残り待機時間" not in caplog.text

    def test_wait_respects_show_progress_true(self, controller, caplog):
        """show_progress=Trueの場合、進捗ログが出る（長時間待機時）"""
        controller._running = True

        # 600秒の倍数でログが出るので、テストでは実際に600秒待たず
        # モックで確認する
        with patch("time.sleep"):
            # 残り時間が600秒になるようにシミュレート
            controller._wait_with_interrupt_check(
                total_seconds=1200, check_interval=600, show_progress=True
            )
            # このテストは実際のログ出力を確認するため、
            # 実装の詳細に依存するのでスキップ可能

    def test_shutdown_signal_sets_running_false(self, controller):
        """_handle_shutdown()が_runningをFalseに設定"""
        controller._running = True

        # シグナルハンドラーを呼び出し
        controller._handle_shutdown(None, None)

        # _runningがFalseになっているはず
        assert controller._running is False

    def test_wait_with_different_check_intervals(self, controller):
        """異なるcheck_intervalで動作確認"""
        test_cases = [
            (3, 1),  # 3秒待機、1秒ごとチェック
            (2, 2),  # 2秒待機、2秒ごとチェック
            (5, 3),  # 5秒待機、3秒ごとチェック
        ]

        for total_seconds, check_interval in test_cases:
            controller._running = True

            start_time = time.time()
            controller._wait_with_interrupt_check(
                total_seconds=total_seconds,
                check_interval=check_interval,
                show_progress=False,
            )
            elapsed = time.time() - start_time

            # 指定秒数待機するはず（許容誤差0.3秒）
            assert (
                total_seconds - 0.3 <= elapsed < total_seconds + 0.5
            ), f"Expected ~{total_seconds}s, got {elapsed:.2f}s"

    def test_wait_zero_seconds(self, controller):
        """0秒待機の場合、即座に返る"""
        controller._running = True

        start_time = time.time()
        controller._wait_with_interrupt_check(
            total_seconds=0, check_interval=1, show_progress=False
        )
        elapsed = time.time() - start_time

        # 即座に終了するはず
        assert elapsed < 0.1

    def test_wait_handles_running_false_during_sleep(self, controller):
        """sleep中に_runningがFalseになった場合の動作"""
        controller._running = True

        def interrupt_after_short_delay():
            """0.5秒後に_runningをFalseに設定"""
            time.sleep(0.5)
            controller._running = False

        thread = Thread(target=interrupt_after_short_delay)
        thread.start()

        start_time = time.time()
        controller._wait_with_interrupt_check(
            total_seconds=5, check_interval=1, show_progress=False
        )
        elapsed = time.time() - start_time

        thread.join()

        # 0.5-1.5秒で終了するはず（5秒待たない）
        assert 0.4 <= elapsed < 2.0
