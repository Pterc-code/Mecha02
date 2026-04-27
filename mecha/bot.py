import logging

import discord
from discord.ext import commands

from mecha.config import Settings, load_settings
from mecha.services.audio_player import AudioPlayer


def create_bot(settings: Settings | None = None) -> commands.Bot:
    settings = settings or load_settings()
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix=settings.command_prefix, intents=intents, help_command=None)
    bot.settings = settings
    bot.audio_player = AudioPlayer()
    return bot


async def load_extensions(bot: commands.Bot, settings: Settings) -> None:
    for extension in settings.extensions:
        await bot.load_extension(extension)


async def run() -> None:
    settings = load_settings()
    if not settings.token:
        raise RuntimeError("DISCORD_TOKEN is required. Add it to .env or your environment.")

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger("discord.voice_client").setLevel(logging.DEBUG)
    logging.getLogger("discord.player").setLevel(logging.DEBUG)

    bot = create_bot(settings)
    async with bot:
        await load_extensions(bot, settings)
        await bot.start(settings.token)
