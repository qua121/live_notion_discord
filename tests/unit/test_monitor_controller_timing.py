"""MonitorControllerの5分同期タイミング計算のユニットテスト"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import pytz

from presentation.cli.monitor_controller import MonitorController
from application.use_cases.monitor_streams_use_case import MonitorStreamsUseCase


class TestMonitorControllerTiming:
    """5分同期タイミング計算のテスト"""

    @pytest.fixture
    def mock_use_case(self):
        """モックのユースケースを作成"""
        return Mock(spec=MonitorStreamsUseCase)

    @pytest.fixture
    def controller(self, mock_use_case):
        """テスト用のコントローラーを作成"""
        return MonitorController(
            use_case=mock_use_case,
            channels=[],
            check_interval=300
        )

    def test_calculate_wait_at_exact_5min(self, controller):
        """ちょうど5の倍数の分の場合、5分後まで待つ"""
        jst = pytz.timezone("Asia/Tokyo")
        test_time = jst.localize(datetime(2026, 1, 29, 14, 25, 0))  # 14:25:00

        with patch("presentation.cli.monitor_controller.datetime") as mock_datetime:
            mock_datetime.now.return_value = test_time

            wait_seconds = controller._calculate_wait_until_next_5min()

            # 14:25:00 -> 14:30:00 = 300秒
            assert wait_seconds == 300

    def test_calculate_wait_mid_interval(self, controller):
        """5分間隔の途中の場合、次の5の倍数まで待つ"""
        jst = pytz.timezone("Asia/Tokyo")
        test_time = jst.localize(datetime(2026, 1, 29, 14, 23, 45))  # 14:23:45

        with patch("presentation.cli.monitor_controller.datetime") as mock_datetime:
            mock_datetime.now.return_value = test_time

            wait_seconds = controller._calculate_wait_until_next_5min()

            # 14:23:45 -> 14:25:00 = 75秒
            assert wait_seconds == 75

    def test_calculate_wait_one_second_before_5min(self, controller):
        """5の倍数の1秒前の場合、次の5分まで待つ"""
        jst = pytz.timezone("Asia/Tokyo")
        test_time = jst.localize(datetime(2026, 1, 29, 14, 24, 59))  # 14:24:59

        with patch("presentation.cli.monitor_controller.datetime") as mock_datetime:
            mock_datetime.now.return_value = test_time

            wait_seconds = controller._calculate_wait_until_next_5min()

            # 14:24:59 -> 14:25:00 = 1秒
            assert wait_seconds == 1

    def test_calculate_wait_at_55min(self, controller):
        """55分の場合、次の時間の00分まで待つ"""
        jst = pytz.timezone("Asia/Tokyo")
        test_time = jst.localize(datetime(2026, 1, 29, 14, 55, 0))  # 14:55:00

        with patch("presentation.cli.monitor_controller.datetime") as mock_datetime:
            mock_datetime.now.return_value = test_time

            wait_seconds = controller._calculate_wait_until_next_5min()

            # 14:55:00 -> 15:00:00 = 300秒
            assert wait_seconds == 300

    def test_calculate_wait_at_58min_30sec(self, controller):
        """58分30秒の場合、次の時間の00分まで待つ"""
        jst = pytz.timezone("Asia/Tokyo")
        test_time = jst.localize(datetime(2026, 1, 29, 14, 58, 30))  # 14:58:30

        with patch("presentation.cli.monitor_controller.datetime") as mock_datetime:
            mock_datetime.now.return_value = test_time

            wait_seconds = controller._calculate_wait_until_next_5min()

            # 14:58:30 -> 15:00:00 = 90秒
            assert wait_seconds == 90

    def test_calculate_wait_at_00min(self, controller):
        """00分の場合、05分まで待つ"""
        jst = pytz.timezone("Asia/Tokyo")
        test_time = jst.localize(datetime(2026, 1, 29, 14, 0, 0))  # 14:00:00

        with patch("presentation.cli.monitor_controller.datetime") as mock_datetime:
            mock_datetime.now.return_value = test_time

            wait_seconds = controller._calculate_wait_until_next_5min()

            # 14:00:00 -> 14:05:00 = 300秒
            assert wait_seconds == 300

    def test_calculate_wait_at_03min_20sec(self, controller):
        """03分20秒の場合、05分まで待つ"""
        jst = pytz.timezone("Asia/Tokyo")
        test_time = jst.localize(datetime(2026, 1, 29, 14, 3, 20))  # 14:03:20

        with patch("presentation.cli.monitor_controller.datetime") as mock_datetime:
            mock_datetime.now.return_value = test_time

            wait_seconds = controller._calculate_wait_until_next_5min()

            # 14:03:20 -> 14:05:00 = 100秒
            assert wait_seconds == 100

    def test_calculate_wait_various_times(self, controller):
        """様々な時刻でのタイミング計算をテスト"""
        jst = pytz.timezone("Asia/Tokyo")

        test_cases = [
            # (入力時刻, 次のチェック時刻, 待機秒数)
            ((14, 0, 0), (14, 5, 0), 300),
            ((14, 1, 30), (14, 5, 0), 210),
            ((14, 5, 0), (14, 10, 0), 300),
            ((14, 7, 15), (14, 10, 0), 165),
            ((14, 10, 0), (14, 15, 0), 300),
            ((14, 14, 59), (14, 15, 0), 1),
            ((14, 59, 30), (15, 0, 0), 30),
        ]

        for (h, m, s), (next_h, next_m, next_s), expected_wait in test_cases:
            test_time = jst.localize(datetime(2026, 1, 29, h, m, s))

            with patch("presentation.cli.monitor_controller.datetime") as mock_datetime:
                mock_datetime.now.return_value = test_time

                wait_seconds = controller._calculate_wait_until_next_5min()

                assert wait_seconds == expected_wait, (
                    f"時刻 {h:02d}:{m:02d}:{s:02d} -> {next_h:02d}:{next_m:02d}:{next_s:02d} "
                    f"の待機時間は {expected_wait}秒 のはずが {wait_seconds}秒"
                )
