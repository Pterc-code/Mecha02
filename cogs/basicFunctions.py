from mecha.cogs.admin import Admin
from mecha.cogs.voice import Voice


async def setup(bot):
    await bot.add_cog(Admin(bot))
    await bot.add_cog(Voice(bot))
