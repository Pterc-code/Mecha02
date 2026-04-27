import os
import re
import uuid
from pathlib import Path

import discord
from discord import ClientException
from discord.opus import OpusNotLoaded
from gtts import gTTS

from mecha.services.audio_player import AudioPlayer


class TTSService:
    def __init__(self, tmp_dir: Path, audio_player: AudioPlayer | None = None) -> None:
        self.tmp_dir = tmp_dir
        self.audio_player = audio_player or AudioPlayer()

    async def vocalize(self, ctx, text: str, language: str) -> None:
        voice_client = getattr(ctx, "voice_client", None)
        if voice_client is None or not voice_client.is_connected():
            await ctx.send("I'm not connected to a voice channel. Please summon me with `!join` first.")
            return

        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.tmp_dir / f"tts_{uuid.uuid4().hex}.mp3"
        source = None

        try:
            tts = gTTS(text=text, lang=language)
            tts.save(file_path)
            source = discord.FFmpegPCMAudio(str(file_path))
            await self.audio_player.play_and_wait(ctx, source)
            print(f"Finished playing: {tts.text}")
        except ClientException as error:
            await ctx.send(f"A client exception occurred:\n`{error}`")
        except TypeError as error:
            await ctx.send(f"TypeError exception:\n`{error}`")
        except OpusNotLoaded as error:
            await ctx.send(f"OpusNotLoaded exception: \n`{error}`")
        finally:
            if source is not None:
                source.cleanup()
            try:
                os.remove(file_path)
            except OSError:
                pass


def is_chinese(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]+", text))
