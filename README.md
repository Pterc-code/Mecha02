# Mecha02

A small Discord sound/music bot with voice helpers, TTS, praise commands, League of Legends live-client monitoring, and a slash-command music system.

## Setup

1. Create a virtual environment.
2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and set `DISCORD_TOKEN`.
4. Run the bot:

   ```powershell
   python main.py
   ```

The default prefix for legacy commands is `!`. Music commands are Discord slash commands.

## Configuration

Runtime config is loaded from `.env`:

- `DISCORD_TOKEN`: Discord bot token. Required.
- `MECHA_COMMAND_PREFIX`: prefix for legacy commands. Defaults to `!`.
- `MECHA_EXTENSIONS`: comma-separated cogs to load at startup.
- `MECHA_PRAISE_FILE`: praise text file. Defaults to `data/praises.txt`.
- `MECHA_TMP_DIR`: generated audio temp directory. Defaults to `tmp`.
- `MECHA_LEAGUE_API_URL`: League live-client endpoint.
- `MECHA_LEAGUE_POLL_SECONDS`: League monitor polling interval.
- `MECHA_AUTO_DISCONNECT_WHEN_ALONE`: whether the legacy voice cog leaves empty voice channels.
- `MECHA_AUTO_DISCONNECT_GRACE_SECONDS`: seconds to wait after joining before auto-leave checks.
- `MECHA_AUTO_DISCONNECT_CHECKS`: repeated empty checks required before leaving.
- `MECHA_MUSIC_MAX_PLAYLIST_SIZE`: maximum YouTube or Spotify playlist items to queue. Defaults to `100`.
- `MECHA_MUSIC_IDLE_TIMEOUT_SECONDS`: seconds before the music player disconnects after the queue ends.
- `MECHA_SYNC_APP_COMMANDS`: sync slash commands on startup. Defaults to `true`.
- `MECHA_SYNC_GUILD_ID`: optional test server ID for faster slash command syncing.
- `SPOTIFY_CLIENT_ID`: Spotify API client ID for metadata lookup.
- `SPOTIFY_CLIENT_SECRET`: Spotify API client secret for metadata lookup.

Spotify links require Spotify credentials. Spotify audio is not played directly; Spotify metadata is resolved to YouTube searches.

## Legacy Commands

General:

- `!ping`
- `!clear <amount>`
- `!load <extension>`
- `!unload <extension>`
- `!reload <extension>`

Voice/TTS/League:

- `!join`
- `!disconnect`
- `!say <text>`
- `!praise <name>`
- `!add <praise>`
- `!showPraises`
- `!monitor`

## Music Slash Commands

- `/play <query_or_url>`
- `/pause`
- `/resume`
- `/skip`
- `/stop`
- `/disconnect`
- `/nowplaying`
- `/queue`
- `/clearqueue`
- `/remove <track_number>`
- `/move <from_position> <to_position>`
- `/shuffle`
- `/loop <off/song/queue>`
- `/volume <value>`

Supported `/play` inputs:

- YouTube video URL
- YouTube playlist URL
- YouTube Music URL when `yt-dlp` can resolve it
- Spotify track URL
- Spotify playlist URL
- Plain search text, for example `/play never gonna give you up`

## Project Layout

```text
main.py                 # entry point
mecha/bot.py            # Discord bot creation and extension loading
mecha/config.py         # environment-backed settings
mecha/cogs/             # Discord command/event adapters
mecha/music/            # music queue, resolvers, playback, embeds, controls
mecha/services/         # TTS, praise, League, shared services
mecha/utils/            # small helpers
data/praises.txt        # editable praise data
tmp/                    # generated runtime files, ignored by git
cogs/                   # legacy compatibility import paths
```

## Notes

The old hard-coded token has been removed. If that token was ever valid, rotate it in the Discord developer portal before running the bot again.
