from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models.song import Song


class SongService:
    def __init__(self, session: AsyncSession):
        self.session = session

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

        self.session.add(song)
        await self.session.commit()
        return song

    async def get_song(self, song_id: int) -> Song | None:
        result = await self.session.execute(
            select(Song).where(Song.id == song_id)
        )
        return result.scalar_one_or_none()