from pathlib import Path
from loguru import logger

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models.song import Song

from bot.config.settings import settings
from bot.services.storage_service import StorageService

from bot.exceptions import (
    DailyLimitExceededError,
    ProcessingError,
)


class SongService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_song(
        self,
        user_id: int,
        original_file: str,
    ) -> Song:
        song = Song(
            user_id=user_id,
            original_file=original_file,
            status="uploaded",
        )

        self.db_session.add(song)
        await self.db_session.commit()
        return song

    async def get_song(self, song_id: int) -> Song | None:
        result = await self.db_session.execute(
            select(Song).where(Song.id == song_id)
        )
        return result.scalar_one_or_none()
    
    async def handle_voice_upload(self, message, user):
        """
        Processing uploaded voice message:
        - checks the limit
        - downloads the file
        - creates a Song record
        """

        # 1. Check the limit
        if user.telegram_id in settings.ADMIN_IDS:
            daily_limit = 100
        else:
            daily_limit = user.plan.daily_limit

        if user.songs_count >= daily_limit:
            raise DailyLimitExceededError()

        # 2. Get Telegram file info
        try:
            file = await message.bot.get_file(message.voice.file_id)
        except Exception:
            raise ProcessingError("telegram_file_fetch_failed")

        file_path = file.file_path

        # 3. Build local path
        storage_service = StorageService()
        local_filename = storage_service.build_voice_path(
            message.voice.file_id
        )

        # 4. Download the filefrom Telegram to local storage
        try:
            await message.bot.download_file(
                file_path,
                destination=local_filename,
            )
        except Exception:
            raise ProcessingError("telegram_file_download_failed")

        logger.info(
            f"Voice saved | tg_id={user.telegram_id} | file={local_filename}"
        )

        # 5. Create a record in the database
        song = await self.create_song(
            user_id=user.id,
            original_file=str(local_filename),
        )

        # 6. Increase the counter
        user.songs_count += 1
        await self.db_session.commit()

        return song    