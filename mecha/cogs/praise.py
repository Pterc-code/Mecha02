import random
from random import choice

from discord.ext import commands

from mecha.services.praise_store import PraiseStore
from mecha.services.tts_service import TTSService, is_chinese


PRAISE_TARGET_IDS = {
    343271388527853579,
    526991910074581003,
    264670780317499403,
}


class Praise(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.store = PraiseStore(bot.settings.praise_file)
        self.tts = TTSService(bot.settings.tmp_dir / "tts", bot.audio_player)

    async def cog_load(self) -> None:
        await self.store.load()

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        if message.author.bot:
            return
        if message.author.id in PRAISE_TARGET_IDS and self.store.praises:
            await message.channel.send(random.choice(self.store.praises))

    @commands.command()
    async def praise(self, ctx, *, name: str = "") -> None:
        voice_client = ctx.voice_client
        if voice_client is None or not voice_client.is_connected():
            await ctx.send("I'm not in a voice channel. Use `!join` first.")
            return

        if not self.store.praises:
            await self.store.load()
        praise = name + " , " + choice(self.store.praises)
        await self.tts.vocalize(ctx, praise, "en")

    @commands.command()
    async def say(self, ctx, *, text: str = "") -> None:
        voice_client = ctx.voice_client
        if voice_client is None or not voice_client.is_connected():
            await ctx.send("I'm not in a voice channel. Use `!join` first.")
            return

        target_language = "zh-CN" if is_chinese(text) else "en"
        await self.tts.vocalize(ctx, text, target_language)

    @commands.command()
    async def add(self, ctx, *, praise: str = "") -> None:
        await self.store.add(praise, ctx.author.name)
        await ctx.channel.send("Added praise: " + praise)

    @commands.command(name="showPraises")
    async def show_praises(self, ctx) -> None:
        for praise in await self.store.formatted_lines():
            await ctx.channel.send(praise)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Praise(bot))
