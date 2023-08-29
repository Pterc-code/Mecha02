# Imports
import discord

from gtts import gTTS
from discord import ClientException
from discord.opus import OpusNotLoaded

import requests





async def _get_player_death_count(player_index) -> int:
    """
    Given the player_index in the game return the number of deaths the player has
    """
    try:
        request = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)
        return request.json()['allPlayers'][player_index]['scores']['deaths']
    except (requests.exceptions.ConnectionError, KeyError):
        return -1
