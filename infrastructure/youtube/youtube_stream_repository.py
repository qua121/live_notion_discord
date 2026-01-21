"""YouTube Data API v3を使用した配信情報取得実装

StreamRepositoryインターフェースの具象実装
"""

from typing import Optional
import logging
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from domain.entities.channel import Channel
from domain.entities.stream import Stream
from domain.repositories.stream_repository import StreamRepository
from domain.value_objects.stream_status import StreamStatus

logger = logging.getLogger(__name__)


class RepositoryError(Exception):
    """リポジトリエラー"""
    pass


class YouTubeStreamRepository(StreamRepository):
    """YouTube APIを使用した配信情報取得の実装"""

    def __init__(self, api_key: str):
        """
        Args:
            api_key: YouTube Data API v3のAPIキー
        """
        self._api_key = api_key
        self._youtube = build('youtube', 'v3', developerKey=api_key)

    def get_current_stream(self, channel: Channel) -> Optional[Stream]:
        """
        チャンネルの現在の配信を取得

        YouTube Data API v3の search.list エンドポイントを使用
        """
        try:
            # search.listで配信中の動画を検索
            request = self._youtube.search().list(
                part='snippet',
                channelId=str(channel.id),
                eventType='live',
                type='video',
                maxResults=1
            )
            response = request.execute()

            items = response.get('items', [])

            if not items:
                logger.debug(f"配信なし: {channel.name}")
                return None

            # 配信情報を取得
            item = items[0]
            video_id = item['id']['videoId']
            snippet = item['snippet']

            stream = Stream(
                video_id=video_id,
                title=snippet['title'],
                thumbnail_url=snippet['thumbnails']['high']['url'],
                started_at=datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                status=StreamStatus.LIVE
            )

            logger.debug(f"配信中: {channel.name} - {stream.title}")
            return stream

        except HttpError as e:
            if e.resp.status == 403:
                logger.error("YouTube API クォータ超過またはAPIキーエラー")
            raise RepositoryError(f"YouTube API エラー: {e}") from e

        except Exception as e:
            logger.error(f"予期しないエラー: {e}", exc_info=True)
            raise RepositoryError(f"配信情報取得エラー: {e}") from e
