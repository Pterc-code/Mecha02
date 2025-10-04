# Imports
import asyncio
import os
import re
import uuid
from pathlib import Path
from typing import Optional

import discord
from gtts import gTTS
from discord import ClientException
from discord.opus import OpusNotLoaded

_play_locks: dict[int, asyncio.Lock] = {}


def _get_guild_id(ctx) -> int:
    guild = getattr(ctx, "guild", None)
    if guild is not None:
        return guild.id
    voice_client = getattr(ctx, "voice_client", None)
    if voice_client is not None and voice_client.guild is not None:
        return voice_client.guild.id
    return 0


async def _wait_for_completion(ctx, voice_client: discord.VoiceClient, source: discord.AudioSource) -> None:
    done = asyncio.Event()

    def _after_playback(error: Optional[Exception]) -> None:
        if error:
            print(f"Error while playing audio: {error}")
        loop = getattr(ctx, "loop", None)
        if loop is None and hasattr(ctx, "bot"):
            loop = ctx.bot.loop
        if loop is None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
        if loop is not None:
            loop.call_soon_threadsafe(done.set)

    voice_client.play(source, after=_after_playback)
    await done.wait()


# Helper function to vocalize text
async def vocalizeText(ctx, text, language) -> None:
    """Play the text in the designated voice_client in the prompted language."""
    voice_client = getattr(ctx, "voice_client", None)
    if voice_client is None or not voice_client.is_connected():
        await ctx.send("I'm not connected to a voice channel. Please summon me with `!join` first.")
        return

    folder_path = Path("cogs/TextToSpeechFiles")
    folder_path.mkdir(parents=True, exist_ok=True)

    tts = gTTS(text=text, lang=language)
    file_path = folder_path / f"tts_{uuid.uuid4().hex}.mp3"
    tts.save(file_path)

    guild_id = _get_guild_id(ctx)
    lock = _play_locks.setdefault(guild_id, asyncio.Lock())

    try:
        async with lock:
            voice_client = getattr(ctx, "voice_client", None)
            if voice_client is None or not voice_client.is_connected():
                await ctx.send("I was disconnected before I could speak. Please use `!join` again.")
                return

            while voice_client.is_playing() or voice_client.is_paused():
                await asyncio.sleep(0.05)

            source = discord.FFmpegPCMAudio(str(file_path))
            await _wait_for_completion(ctx, voice_client, source)
            print(f"Finished playing: {tts.text}")
    except ClientException as e:
        await ctx.send(f"A client exception occurred:\n`{e}`")
    except TypeError as e:
        await ctx.send(f"TypeError exception:\n`{e}`")
    except OpusNotLoaded as e:
        await ctx.send(f"OpusNotLoaded exception: \n`{e}`")
    finally:
        if 'source' in locals():
            source.cleanup()
        try:
            os.remove(file_path)
        except OSError:
            pass


# Helper to determine whether text is in chinese
def is_chinese(text) -> bool:
    """
    If text contains chinese then return TRUE
    """
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    return bool(chinese_pattern.search(text))
