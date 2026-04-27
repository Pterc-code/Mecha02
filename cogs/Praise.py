from mecha.cogs.praise import Praise


async def setup(bot):
    await bot.add_cog(Praise(bot))
