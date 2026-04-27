import asyncio
from collections import defaultdict
from typing import Optional

import discord


class AudioPlayer:
    def __init__(self) -> None:
        self._locks: dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def play_and_wait(self, ctx, source: discord.AudioSource) -> None:
        guild_id = getattr(getattr(ctx, "guild", None), "id", 0)
        async with self._locks[guild_id]:
            voice_client = getattr(ctx, "voice_client", None)
            if voice_client is None or not voice_client.is_connected():
                await ctx.send("I'm not connected to a voice channel. Please summon me with `!join` first.")
                return

            while voice_client.is_playing() or voice_client.is_paused():
                await asyncio.sleep(0.05)

            done = asyncio.Event()

            def after_playback(error: Optional[Exception]) -> None:
                if error:
                    print(f"Error while playing audio: {error}")
                ctx.bot.loop.call_soon_threadsafe(done.set)

            voice_client.play(source, after=after_playback)
            await done.wait()
