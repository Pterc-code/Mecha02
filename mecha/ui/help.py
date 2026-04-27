import discord


HELP_CATEGORIES = {
    "overview": {
        "label": "Overview",
        "title": "Mecha02 Help",
        "description": "Choose a category below to see commands and usage.",
        "fields": [
            ("Main Help", "`!help` or `/help` opens this menu."),
            ("Music Sources", "YouTube links play directly. Spotify links are converted to YouTube searches using Spotify metadata."),
        ],
    },
    "playback": {
        "label": "Playback",
        "title": "Playback Commands",
        "description": "Start, pause, resume, skip, and stop music.",
        "fields": [
            ("Play", "`/play <query_or_url>` or `!play <query_or_url>`"),
            ("Pause / Resume", "`/pause`, `/resume`, `!pause`, `!resume`"),
            ("Skip / Stop", "`/skip`, `/stop`, `!skip`, `!stop`"),
            ("Now Playing", "`/nowplaying` or `!nowplaying`"),
        ],
    },
    "queue": {
        "label": "Queue",
        "title": "Queue Commands",
        "description": "Inspect and reorder the server music queue.",
        "fields": [
            ("Show Queue", "`/queue [page]` or `!queue [page]`"),
            ("Clear Queue", "`/clearqueue` or `!clearqueue`"),
            ("Remove", "`/remove <track_number>` or `!remove <track_number>`"),
            ("Move", "`/move <from_position> <to_position>` or `!move <from_position> <to_position>`"),
            ("Shuffle", "`/shuffle` or `!shuffle`"),
        ],
    },
    "playlists": {
        "label": "Playlists",
        "title": "Playlist & Source Support",
        "description": "Inputs supported by `/play` and `!play`.",
        "fields": [
            ("YouTube", "Video links, playlist links, and YouTube Music links when `yt-dlp` can resolve them."),
            ("Spotify", "Track and playlist links. Spotify audio is not streamed directly."),
            ("Search", "`/play never gonna give you up` searches YouTube and queues the best playable video."),
            ("Limits", "Playlist size is capped by `MECHA_MUSIC_MAX_PLAYLIST_SIZE`."),
        ],
    },
    "modes": {
        "label": "Modes",
        "title": "Loop & Volume",
        "description": "Playback modes and audio level.",
        "fields": [
            ("Loop", "`/loop off`, `/loop song`, `/loop queue` or `!loop <mode>`"),
            ("Volume", "`/volume <0-200>` or `!volume <0-200>`"),
            ("Disconnect", "`/disconnect`, `!disconnect`, or `/stop` to clear and leave."),
        ],
    },
    "general": {
        "label": "General",
        "title": "General Bot Commands",
        "description": "Non-music utility commands.",
        "fields": [
            ("Basic", "`!ping`, `!clear <amount>`"),
            ("Voice/TTS", "`!join`, `!disconnect`, `!say <text>`, `!praise <name>`"),
            ("Praise", "`!add <praise>`, `!showPraises`"),
            ("League", "`!monitor`"),
            ("Cog Admin", "`!load <extension>`, `!unload <extension>`, `!reload <extension>`"),
        ],
    },
}


def help_embed(category: str = "overview") -> discord.Embed:
    data = HELP_CATEGORIES.get(category, HELP_CATEGORIES["overview"])
    embed = discord.Embed(
        title=data["title"],
        description=data["description"],
        color=discord.Color.blurple(),
    )
    for name, value in data["fields"]:
        embed.add_field(name=name, value=value, inline=False)
    embed.set_footer(text="Use the menu below to switch categories.")
    return embed


class HelpCategorySelect(discord.ui.Select):
    def __init__(self) -> None:
        options = [
            discord.SelectOption(label=data["label"], value=key)
            for key, data in HELP_CATEGORIES.items()
        ]
        super().__init__(placeholder="Choose a help category", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(embed=help_embed(self.values[0]), view=self.view)


class HelpView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=300)
        self.add_item(HelpCategorySelect())
