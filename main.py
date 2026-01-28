"""
YouTube配信監視システム - メインエントリーポイント

Composition Root: 依存性の注入を行う
"""

import logging
from pathlib import Path

from config.settings import Settings
from infrastructure.logging.logger_config import setup_logging

# Domain (interfaces only - no imports from infrastructure)
from application.use_cases.monitor_streams_use_case import MonitorStreamsUseCase
from application.services.stream_change_detector import StreamChangeDetector

# Infrastructure (concrete implementations)
from infrastructure.youtube.youtube_stream_repository import YouTubeStreamRepository
from infrastructure.discord.discord_notification_gateway import DiscordNotificationGateway
from infrastructure.persistence.json_state_repository import JsonStateRepository

# Presentation
from presentation.cli.monitor_controller import MonitorController

logger = logging.getLogger(__name__)


def main():
    """メイン処理"""
    try:
        # 1. 設定読み込み
        settings = Settings.load("config/config.json")

        # 2. ロギング設定
        setup_logging(settings.log_level, "logs/monitor.log")

        logger.info("YouTube配信監視システムを起動します")

        # 3. Infrastructure層のインスタンス生成（具象実装）
        stream_repository = YouTubeStreamRepository(settings.youtube_api_key)
        notification_gateway = DiscordNotificationGateway(color=settings.notification_color)
        state_repository = JsonStateRepository("data/state.json")

        # 4. Application層のサービス生成
        change_detector = StreamChangeDetector()

        # 5. Use Case生成（依存性注入）
        # ポイント: Use Caseは抽象（インターフェース）のみを知っている
        use_case = MonitorStreamsUseCase(
            stream_repository=stream_repository,  # StreamRepository型として注入
            notification_gateway=notification_gateway,  # NotificationGateway型として注入
            state_repository=state_repository,  # StateRepository型として注入
            change_detector=change_detector,
        )

        # 6. Presentation層（Controller）生成
        controller = MonitorController(
            use_case=use_case, channels=settings.channels, check_interval=settings.check_interval
        )

        # 7. 監視開始
        controller.start()

    except ValueError as e:
        print(f"設定エラー: {e}")
        print("config.jsonと.envファイルを確認してください")
        return 1

    except KeyboardInterrupt:
        logger.info("ユーザーによる中断")
        return 0

    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        return 1

    finally:
        logger.info("システム終了")

    return 0


if __name__ == "__main__":
    exit(main())
