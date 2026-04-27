from mecha.cogs.league import League


async def setup(bot):
    await bot.add_cog(League(bot))
