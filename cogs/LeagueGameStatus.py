import asyncio
import random
from datetime import datetime
import requests
from cogs.LeagueGameStatusFiles import LeaguePlayer
import urllib3
from cogs.TextToSpeechFiles.TextToSpeech import vocalizeText
from discord.ext import commands

urllib3.disable_warnings()

# Monkeys
Monkeys = {
    'Mecha 01': 'Daniel',
    'Horse In Bush': 'Bobby',
    'AshX': 'Ash',
    'Ka1m': 'Brad',
    'Badman1884': 'York',
    'PumpkinEater': 'Peter'
}

praises = []


# Load PraiseFiles
async def loadPraise():
    file = open("cogs/PraiseFiles/praises.txt", "r")

    for line in file:
        stripped_line = line.strip()
        praises.append(stripped_line.split('||')[0])

    file.close()


def _get_all_friends() -> list:
    metadata = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)
    players = []
    for user in metadata.json()['allPlayers']:
        if user['summonerName'] in Monkeys:
            players.append(LeaguePlayer.Player(user['summonerName']))
    return players


def _generate_praise(name) -> str:
    return f'{name}, {random.choice(praises)}, also, stop dying!'


class LeagueGameStatus(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.player_death_count = None

    @commands.command()
    async def monitor(self, ctx):
        try:
            await loadPraise()
            friends = _get_all_friends()

            await ctx.channel.send(f'Monitoring game at {datetime.now()}!')

            while True:
                await asyncio.sleep(0.2)
                for friend in friends:
                    if friend.deathDetected():
                        await vocalizeText(ctx, _generate_praise(Monkeys[friend.user_name]), 'en')
        except (requests.exceptions.ConnectionError, KeyError):
            await ctx.channel.send('Game Ended!')


async def setup(client):
    await client.add_cog(LeagueGameStatus(client))
