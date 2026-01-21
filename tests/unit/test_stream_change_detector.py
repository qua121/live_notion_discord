"""StreamChangeDetectorのユニットテスト"""

import pytest
from datetime import datetime

from domain.entities.stream import Stream
from domain.value_objects.stream_status import StreamStatus
from application.dto.stream_state_dto import StreamStateDto
from application.services.stream_change_detector import StreamChangeDetector


class TestStreamChangeDetector:
    """StreamChangeDetectorのテスト"""

    def setup_method(self):
        """各テストメソッドの前処理"""
        self.detector = StreamChangeDetector()

    def test_is_stream_started_初回チェックで配信中(self):
        """初回チェックで配信中の場合、配信開始と判定"""
        current_stream = Stream(
            video_id='test123',
            title='テスト配信',
            thumbnail_url='http://example.com/thumb.jpg',
            started_at=datetime.now(),
            status=StreamStatus.LIVE
        )

        result = self.detector.is_stream_started(None, current_stream)

        assert result is True

    def test_is_stream_started_前回未配信で今回配信中(self):
        """前回未配信、今回配信中の場合、配信開始と判定"""
        previous_state = StreamStateDto(
            is_live=False,
            video_id=None,
            last_checked=datetime.now(),
            last_notified=None
        )
        current_stream = Stream(
            video_id='test123',
            title='テスト配信',
            thumbnail_url='http://example.com/thumb.jpg',
            started_at=datetime.now(),
            status=StreamStatus.LIVE
        )

        result = self.detector.is_stream_started(previous_state, current_stream)

        assert result is True

    def test_is_stream_started_配信継続中(self):
        """前回も今回も同じ配信中の場合、配信開始ではない"""
        previous_state = StreamStateDto(
            is_live=True,
            video_id='test123',
            last_checked=datetime.now(),
            last_notified=datetime.now()
        )
        current_stream = Stream(
            video_id='test123',
            title='テスト配信',
            thumbnail_url='http://example.com/thumb.jpg',
            started_at=datetime.now(),
            status=StreamStatus.LIVE
        )

        result = self.detector.is_stream_started(previous_state, current_stream)

        assert result is False

    def test_is_stream_started_video_id変化(self):
        """前回と異なるvideo_idの場合、新しい配信開始と判定"""
        previous_state = StreamStateDto(
            is_live=True,
            video_id='old123',
            last_checked=datetime.now(),
            last_notified=datetime.now()
        )
        current_stream = Stream(
            video_id='new456',
            title='新しい配信',
            thumbnail_url='http://example.com/thumb.jpg',
            started_at=datetime.now(),
            status=StreamStatus.LIVE
        )

        result = self.detector.is_stream_started(previous_state, current_stream)

        assert result is True

    def test_is_stream_started_配信なし(self):
        """現在配信していない場合、配信開始ではない"""
        previous_state = StreamStateDto(
            is_live=False,
            video_id=None,
            last_checked=datetime.now(),
            last_notified=None
        )

        result = self.detector.is_stream_started(previous_state, None)

        assert result is False

    def test_is_stream_ended_配信終了(self):
        """前回配信中で今回未配信の場合、配信終了と判定"""
        previous_state = StreamStateDto(
            is_live=True,
            video_id='test123',
            last_checked=datetime.now(),
            last_notified=datetime.now()
        )

        result = self.detector.is_stream_ended(previous_state, None)

        assert result is True

    def test_is_stream_ended_配信継続中(self):
        """前回も今回も配信中の場合、配信終了ではない"""
        previous_state = StreamStateDto(
            is_live=True,
            video_id='test123',
            last_checked=datetime.now(),
            last_notified=datetime.now()
        )
        current_stream = Stream(
            video_id='test123',
            title='テスト配信',
            thumbnail_url='http://example.com/thumb.jpg',
            started_at=datetime.now(),
            status=StreamStatus.LIVE
        )

        result = self.detector.is_stream_ended(previous_state, current_stream)

        assert result is False

    def test_is_stream_ended_前回状態なし(self):
        """前回の状態がない場合、配信終了ではない"""
        result = self.detector.is_stream_ended(None, None)

        assert result is False
