# Imports
import os
import re

import discord
from gtts import gTTS
from discord import ClientException
from discord.opus import OpusNotLoaded


# Helper function to vocalize text
async def vocalizeText(ctx, text, language) -> None:
    """
    Play the text in the designated voice_client in the prompted language
    """
    folder_path = "cogs/TextToSpeechFiles"
    os.makedirs(folder_path, exist_ok=True)

    tts = gTTS(text=text, lang=language)

    file_path = os.path.join(folder_path, "tts.mp3")
    tts.save(file_path)
    try:
        ctx.voice_client.play(discord.FFmpegPCMAudio('cogs/TextToSpeechFiles/tts.mp3'))
        print(f"Finished playing: {tts.text}")
    except ClientException as e:
        await ctx.send(f"A client exception occured:\n`{e}`")
    except TypeError as e:
        await ctx.send(f"TypeError exception:\n`{e}`")
    except OpusNotLoaded as e:
        await ctx.send(f"OpusNotLoaded exception: \n`{e}`")


# Helper to determine whether text is in chinese
def is_chinese(text) -> bool:
    """
    If text contains chinese then return TRUE
    """
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    return bool(chinese_pattern.search(text))
