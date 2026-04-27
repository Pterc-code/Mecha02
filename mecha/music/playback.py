import asyncio
import logging

import discord
import yt_dlp

from mecha.music.constants import DEFAULT_VOLUME, MAX_VOLUME, MIN_VOLUME
from mecha.music.errors import PlaybackError
from mecha.music.youtube_resolver import YouTubeResolver

log = logging.getLogger(__name__)

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


class PlaybackFactory:
    def __init__(self, youtube: YouTubeResolver) -> None:
        self.youtube = youtube

    async def create_source(self, track_url: str, volume: float) -> discord.PCMVolumeTransformer:
        try:
            stream_url = await self.youtube.get_stream_url(track_url)
            audio = discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)
            return discord.PCMVolumeTransformer(audio, volume=max(MIN_VOLUME, min(MAX_VOLUME, volume)))
        except (yt_dlp.utils.DownloadError, KeyError, discord.ClientException) as error:
            log.warning("Could not create FFmpeg source for %s: %s", track_url, error)
            raise PlaybackError("I could not create an audio stream for that track.") from error


async def play_source_and_wait(voice_client: discord.VoiceClient, source: discord.AudioSource) -> None:
    done = asyncio.Event()
    loop = asyncio.get_running_loop()

    def after_playback(error: Exception | None) -> None:
        if error:
            log.warning("Audio playback ended with an error: %s", error)
        loop.call_soon_threadsafe(done.set)

    voice_client.play(source, after=after_playback)
    await done.wait()
