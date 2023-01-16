# Imports
import discord

from gtts import gTTS
from discord import ClientException
from discord.opus import OpusNotLoaded

import requests


async def play_in_vc(channel, voice_client, text, lang) -> None:
    """
    Play the text in the designated voice_client in the prompted language
    """
    tts = gTTS(text=text, lang=lang)
    tts.save('tts.mp3')
    try:
        voice_client.play(discord.FFmpegPCMAudio('tts.mp3'))
        print(f"Finished playing: {tts.text}")
    except ClientException as e:
        await channel.send(f"A client exception occured:\n`{e}`")
    except TypeError as e:
        await channel.send(f"TypeError exception:\n`{e}`")
    except OpusNotLoaded as e:
        await channel.send(f"OpusNotLoaded exception: \n`{e}`")


async def _get_player_death_count(player_index) -> int:
    """
    Given the player_index in the game return the number of deaths the player has
    """
    try:
        request = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)
        return request.json()['allPlayers'][player_index]['scores']['deaths']
    except (requests.exceptions.ConnectionError, KeyError):
        return -1
