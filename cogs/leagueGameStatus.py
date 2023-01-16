import asyncio

from staticFunctions import _get_player_death_count, play_in_vc

import requests
from leaguePlayer import Player
import urllib3

import time
from discord.ext import commands

urllib3.disable_warnings()

# Monkeys
Monkeys = {
    'Mecha 01': 'Daniel',
    'Horse In Bush': 'Bobby',
    'AshX': 'Ash',
    'Ka1m': 'Brad',
    'Rizzard H Choi': 'Ricky',
    'Badman1884': 'York'
}

class leagueGameStatus(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.player_death_count = None

    @commands.command()
    async def monitor(self, ctx):
        player = Player(ctx.message.content[9:])
        await ctx.send(f'Monitoring {ctx.message.content[9:]}')
        player.get_player_index()
        player.get_death_count()
        try:
            while True:
                did_die = await player.update_death_count()
                if did_die:
                    await play_in_vc(ctx, ctx.voice_client, f'Stop dying you monkey', 'en')
        except (requests.exceptions.ConnectionError, KeyError):
            print('fdasfdsa')
            return 1


        # try:
        #     request = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)
        #     player_index = None
        #     for i in range(len(request.json()['allPlayers'])):
        #         if request.json()['allPlayers'][i]['summonerName'] == f'{player_name}':
        #             player_index = i
        #
        #     if player_index is not None:
        #         self.player_death_count = await _get_player_death_count(player_index)
        #         while True:
        #             if await _get_player_death_count(player_index) > self.player_death_count:
        #                 self.player_death_count = await _get_player_death_count(player_index)
        #                 await play_in_vc(ctx, ctx.voice_client, f'{Monkeys[player_name]} Stop dying you monkey', 'en')
        #             await asyncio.sleep(1)
        #     else:
        #         await ctx.send(f'did not find the player with name: {player_name}')
        # except (requests.exceptions.ConnectionError, KeyError):
        #     return 1


def setup(client):
    client.add_cog(leagueGameStatus(client))
