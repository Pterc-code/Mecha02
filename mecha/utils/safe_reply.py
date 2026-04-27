import discord


async def safe_reply(interaction: discord.Interaction, **kwargs) -> None:
    if interaction.response.is_done():
        await interaction.followup.send(**kwargs)
    else:
        await interaction.response.send_message(**kwargs)
