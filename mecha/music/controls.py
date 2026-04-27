import discord

from mecha.music.queue import LoopMode


class MusicControls(discord.ui.View):
    def __init__(self, get_player):
        super().__init__(timeout=180)
        self.get_player = get_player

    @discord.ui.button(label="Pause/Resume", style=discord.ButtonStyle.secondary)
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        player = self.get_player(interaction)
        if player.voice_client and player.voice_client.is_paused():
            await player.resume()
            await interaction.response.send_message("Resumed.", ephemeral=True)
        else:
            await player.pause()
            await interaction.response.send_message("Paused.", ephemeral=True)

    @discord.ui.button(label="Resume", style=discord.ButtonStyle.success)
    async def resume(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.get_player(interaction).resume()
        await interaction.response.send_message("Resumed.", ephemeral=True)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.get_player(interaction).skip()
        await interaction.response.send_message("Skipped.", ephemeral=True)

    @discord.ui.button(label="Shuffle", style=discord.ButtonStyle.secondary)
    async def shuffle(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.get_player(interaction).queue.shuffle()
        await interaction.response.send_message("Queue shuffled.", ephemeral=True)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.get_player(interaction).stop(disconnect=True)
        await interaction.response.send_message("Stopped.", ephemeral=True)

    @discord.ui.button(label="Queue", style=discord.ButtonStyle.secondary)
    async def queue(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        from mecha.music.embeds import queue_embed

        player = self.get_player(interaction)
        await interaction.response.send_message(embed=queue_embed(player.queue, player.current), ephemeral=True)

    @discord.ui.button(label="Loop", style=discord.ButtonStyle.secondary)
    async def loop(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        player = self.get_player(interaction)
        current = player.queue.loop_mode
        if current == LoopMode.OFF:
            player.queue.loop_mode = LoopMode.SONG
        elif current == LoopMode.SONG:
            player.queue.loop_mode = LoopMode.QUEUE
        else:
            player.queue.loop_mode = LoopMode.OFF
        await interaction.response.send_message(f"Loop mode: {player.queue.loop_mode.value}", ephemeral=True)
