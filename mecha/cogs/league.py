import asyncio
import random
from datetime import datetime

import requests
from discord.ext import commands

from mecha.services.league_client import LeagueClient
from mecha.services.praise_store import PraiseStore
from mecha.services.tts_service import TTSService


TRACKED_PLAYERS = {
    "Mecha 01": "Daniel",
    "Horse In Bush": "Bobby",
    "AshX": "Ash",
    "Ka1m": "Brad",
    "Badman1884": "York",
    "PumpkinEater": "Peter",
}


class League(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.client = LeagueClient(bot.settings.league_api_url)
        self.store = PraiseStore(bot.settings.praise_file)
        self.tts = TTSService(bot.settings.tmp_dir / "tts", bot.audio_player)

    async def _generate_praise(self, name: str) -> str:
        if not self.store.praises:
            await self.store.load()
        return f"{name}, {random.choice(self.store.praises)}, also, stop dying!"

    @commands.command()
    async def monitor(self, ctx) -> None:
        voice_client = ctx.voice_client
        if voice_client is None or not voice_client.is_connected():
            await ctx.send("I'm not connected to a voice channel. Use `!join` before starting the monitor.")
            return

        try:
            await self.store.load()
            friends = await self.client.get_all_friends(TRACKED_PLAYERS)

            await ctx.channel.send(f"Monitoring game at {datetime.now()}!")

            while True:
                await asyncio.sleep(self.bot.settings.league_poll_seconds)
                for friend in friends:
                    if await self.client.death_detected(friend):
                        display_name = TRACKED_PLAYERS[friend.user_name]
                        await self.tts.vocalize(ctx, await self._generate_praise(display_name), "en")
        except (requests.exceptions.ConnectionError, KeyError):
            await ctx.channel.send("Game Ended!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(League(bot))
