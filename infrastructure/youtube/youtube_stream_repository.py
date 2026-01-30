"""YouTube Data API v3を使用した配信情報取得実装

StreamRepositoryインターフェースの具象実装

コスト最適化版:
- search.list (100 units) → playlistItems.list (1 unit) + videos.list (1 unit)
- 合計コスト: 2 units/回（1/50に削減）
"""

from typing import Optional, List, Callable, TypeVar
import logging
import time
from datetime import datetime, timezone, timedelta
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


class QuotaExceededError(Exception):
    """YouTube APIクォータ超過エラー"""

    pass


T = TypeVar("T")


class YouTubeStreamRepository(StreamRepository):
    """YouTube APIを使用した配信情報取得の実装（コスト最適化版）"""

    # 最新何件の動画をチェックするか
    MAX_RECENT_VIDEOS = 20

    # リトライ設定
    MAX_RETRIES = 3
    RETRY_BACKOFF_BASE = 2  # 秒

    def __init__(self, api_key: str):
        """
        Args:
            api_key: YouTube Data API v3のAPIキー
        """
        self._api_key = api_key
        self._youtube = build("youtube", "v3", developerKey=api_key)

    @staticmethod
    def _calculate_wait_until_jst_18() -> int:
        """
        JST 18:00までの待機時間（秒）を計算

        Returns:
            JST 18:00までの秒数
        """
        # 現在のJST時刻を取得
        jst = timezone(timedelta(hours=9))
        now_jst = datetime.now(jst)

        # 今日のJST 18:00
        today_18_jst = now_jst.replace(hour=18, minute=0, second=0, microsecond=0)

        # 既に18:00を過ぎている場合は明日の18:00
        if now_jst >= today_18_jst:
            reset_time = today_18_jst + timedelta(days=1)
        else:
            reset_time = today_18_jst

        # 待機時間を計算
        wait_seconds = int((reset_time - now_jst).total_seconds())
        return wait_seconds

    def _retry_on_error(self, func: Callable[[], T], operation_name: str) -> T:
        """
        エラー時に指数バックオフでリトライする

        Args:
            func: 実行する関数
            operation_name: 操作名（ログ用）

        Returns:
            関数の実行結果

        Raises:
            QuotaExceededError: クォータ超過エラーの場合
            RepositoryError: その他のエラーでリトライ回数を超えた場合
        """
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                return func()
            except HttpError as e:
                # クォータ超過エラーをチェック
                if e.resp.status == 403:
                    error_details = e.error_details if hasattr(e, "error_details") else []
                    for error in error_details:
                        if error.get("reason") == "quotaExceeded":
                            # クォータ超過エラー
                            wait_seconds = self._calculate_wait_until_jst_18()
                            logger.error(
                                f"YouTube APIクォータ超過を検出しました。"
                                f"JST 18:00まで待機します（約{wait_seconds // 3600}時間{(wait_seconds % 3600) // 60}分）"
                            )
                            raise QuotaExceededError(
                                f"クォータ超過。JST 18:00まで{wait_seconds}秒待機が必要です"
                            )

                    # クォータ以外の403エラー（権限エラーなど）
                    raise RepositoryError(f"YouTube API エラー ({operation_name}): {e}") from e

                # 400 (bad request) や 404 はリトライしない
                if e.resp.status in [400, 404]:
                    raise RepositoryError(f"YouTube API エラー ({operation_name}): {e}") from e

                # 500番台エラーはリトライ対象
                last_error = e
                wait_time = self.RETRY_BACKOFF_BASE**attempt
                logger.warning(
                    f"{operation_name} 失敗 (試行 {attempt + 1}/{self.MAX_RETRIES}): {e}. "
                    f"{wait_time}秒後にリトライします..."
                )
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(wait_time)
            except Exception as e:
                # その他の例外もリトライ対象
                last_error = e
                wait_time = self.RETRY_BACKOFF_BASE**attempt
                logger.warning(
                    f"{operation_name} で予期しないエラー (試行 {attempt + 1}/{self.MAX_RETRIES}): {e}. "
                    f"{wait_time}秒後にリトライします..."
                )
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(wait_time)

        # 全リトライ失敗
        raise RepositoryError(
            f"{operation_name} が{self.MAX_RETRIES}回のリトライ後も失敗しました: {last_error}"
        ) from last_error

    def _get_uploads_playlist_id(self, channel_id: str) -> str:
        """
        チャンネルIDからアップロードプレイリストIDを生成

        YouTubeの仕様: チャンネルID "UC..." → アップロードプレイリストID "UU..."
        (最初の'C'を'U'に置換)

        Args:
            channel_id: YouTubeチャンネルID

        Returns:
            アップロードプレイリストID
        """
        if channel_id.startswith("UC"):
            return "UU" + channel_id[2:]
        else:
            # 非標準的なチャンネルIDの場合はエラー
            raise RepositoryError(f"非標準的なチャンネルID形式: {channel_id}")

    def get_current_stream(self, channel: Channel) -> Optional[Stream]:
        """
        チャンネルの現在の配信を取得

        コスト最適化版:
        1. playlistItems.list で最新N件の動画IDを取得 (1 unit)
        2. videos.list で一括取得してliveBroadcastContent='live'をチェック (1 unit)
        合計: 2 units/回
        """
        try:
            # Step 1: アップロードプレイリストIDを取得
            uploads_playlist_id = self._get_uploads_playlist_id(str(channel.id))

            # Step 2: playlistItems.listで最新N件の動画IDを取得 (1 unit) - リトライ付き
            def fetch_playlist_items():
                playlist_request = self._youtube.playlistItems().list(
                    part="contentDetails",
                    playlistId=uploads_playlist_id,
                    maxResults=self.MAX_RECENT_VIDEOS,
                )
                return playlist_request.execute()

            playlist_response = self._retry_on_error(
                fetch_playlist_items, f"playlistItems.list ({channel.name})"
            )

            items = playlist_response.get("items", [])
            if not items:
                logger.debug(f"動画なし: {channel.name}")
                return None

            # 動画IDのリストを作成
            video_ids = [item["contentDetails"]["videoId"] for item in items]

            # Step 3: videos.listで一括取得 (1 unit) - リトライ付き
            def fetch_videos():
                videos_request = self._youtube.videos().list(
                    part="snippet,liveStreamingDetails,status", id=",".join(video_ids)
                )
                return videos_request.execute()

            videos_response = self._retry_on_error(fetch_videos, f"videos.list ({channel.name})")

            # Step 4: liveBroadcastContent='live'の動画を探す
            for video in videos_response.get("items", []):
                snippet = video["snippet"]
                status = video.get("status", {})
                live_broadcast_content = snippet.get("liveBroadcastContent", "none")

                if live_broadcast_content == "live":
                    # 配信中の動画を発見
                    video_id = video["id"]
                    title = snippet.get("title", "")
                    privacy_status = status.get("privacyStatus", "unknown")
                    made_for_kids = status.get("madeForKids", False)

                    # デバッグログ: プライバシー情報を出力
                    logger.info(
                        f"配信検出: {title} (ID: {video_id}) - "
                        f"Privacy: {privacy_status}, MadeForKids: {made_for_kids}"
                    )

                    # TODO: メンバー限定配信の判定ロジック（Phase 2で検討）
                    # if privacy_status == "unlisted" or ... :
                    #     logger.warning(f"メンバー限定配信の可能性: {title}")

                    # liveStreamingDetailsから実際の開始時刻を取得
                    live_details = video.get("liveStreamingDetails", {})
                    actual_start_time = live_details.get("actualStartTime")

                    if actual_start_time:
                        started_at = datetime.fromisoformat(
                            actual_start_time.replace("Z", "+00:00")
                        )
                    else:
                        # フォールバック: 公開日時を使用
                        started_at = datetime.fromisoformat(
                            snippet["publishedAt"].replace("Z", "+00:00")
                        )

                    stream = Stream(
                        video_id=video_id,
                        title=title,
                        thumbnail_url=snippet["thumbnails"]["high"]["url"],
                        started_at=started_at,
                        status=StreamStatus.LIVE,
                    )

                    logger.debug(f"配信中: {channel.name} - {stream.title}")
                    return stream

            # 配信中の動画がない
            logger.debug(f"配信なし: {channel.name}")
            return None

        except QuotaExceededError:
            # クォータ超過エラーはそのまま再送出
            raise

        except RepositoryError:
            # _retry_on_error から投げられたエラーはそのまま再送出
            raise

        except Exception as e:
            logger.error(f"予期しないエラー ({channel.name}): {e}", exc_info=True)
            raise RepositoryError(f"配信情報取得エラー: {e}") from e
