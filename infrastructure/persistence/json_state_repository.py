"""JSON形式での状態永続化実装

StateRepositoryインターフェースの具象実装
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict

from domain.value_objects.channel_id import ChannelId
from domain.repositories.state_repository import StateRepository
from application.dto.stream_state_dto import StreamStateDto

logger = logging.getLogger(__name__)


class StateRepositoryError(Exception):
    """状態リポジトリエラー"""

    pass


class JsonStateRepository(StateRepository):
    """JSON形式で状態を永続化する実装"""

    def __init__(self, file_path: str):
        """
        Args:
            file_path: 状態ファイルのパス
        """
        self._file_path = Path(file_path)
        self._state_cache: Dict[str, StreamStateDto] = {}
        self._load_from_file()

    def get_state(self, channel_id: ChannelId) -> Optional[StreamStateDto]:
        """チャンネルの状態を取得"""
        return self._state_cache.get(str(channel_id))

    def save_state(self, channel_id: ChannelId, state: StreamStateDto) -> None:
        """チャンネルの状態を保存"""
        try:
            self._state_cache[str(channel_id)] = state
            self._save_to_file()
            logger.debug(f"状態保存完了: {channel_id}")
        except Exception as e:
            logger.error(f"状態保存エラー: {e}", exc_info=True)
            raise StateRepositoryError(f"状態保存失敗: {e}") from e

    def _load_from_file(self) -> None:
        """ファイルから状態を読み込み"""
        if not self._file_path.exists():
            logger.info("状態ファイルが存在しないため新規作成します")
            self._state_cache = {}
            return

        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._state_cache = {
                channel_id: StreamStateDto.from_dict(state_data)
                for channel_id, state_data in data.items()
            }
            logger.info(f"状態ファイル読み込み完了: {len(self._state_cache)}チャンネル")

        except Exception as e:
            logger.error(f"状態ファイル読み込みエラー: {e}", exc_info=True)
            self._state_cache = {}

    def _save_to_file(self) -> None:
        """状態をファイルに保存"""
        # ディレクトリが存在しない場合は作成
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

        data = {channel_id: state.to_dict() for channel_id, state in self._state_cache.items()}

        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
