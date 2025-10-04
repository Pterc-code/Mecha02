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
    praises.clear()
    with open("cogs/PraiseFiles/praises.txt", "r") as file:
        for line in file:
            stripped_line = line.strip()
            praises.append(stripped_line.split('||')[0])


# Helper function to get list of friends
def _get_all_friends() -> list:
    """
    Returns a list of all players in your friends list as LeaguePlayer objects
    """
    metadata = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)
    players = []
    for user in metadata.json()['allPlayers']:
        if user['summonerName'] in Monkeys:
            players.append(LeaguePlayer.Player(user['summonerName']))
    return players


# Helper function to generate a praise
def _generate_praise(name) -> str:
    return f'{name}, {random.choice(praises)}, also, stop dying!'


class LeagueGameStatus(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.player_death_count = None

    @commands.command()
    async def monitor(self, ctx):
        """
        During a game of league of legends, if any of your friends die: give them a praise!
        """
        try:
            voice_client = ctx.voice_client
            if voice_client is None or not voice_client.is_connected():
                await ctx.send("I'm not connected to a voice channel. Use `!join` before starting the monitor.")
                return
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
