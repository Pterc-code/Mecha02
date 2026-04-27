import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TMP_DIR = BASE_DIR / "tmp"


@dataclass(frozen=True)
class Settings:
    token: str
    command_prefix: str
    extensions: tuple[str, ...]
    data_dir: Path
    tmp_dir: Path
    praise_file: Path
    league_api_url: str
    league_poll_seconds: float
    activity_name: str
    auto_disconnect_when_alone: bool
    auto_disconnect_grace_seconds: float
    auto_disconnect_checks: int
    log_level: str
    spotify_client_id: str
    spotify_client_secret: str
    music_max_playlist_size: int
    music_idle_timeout_seconds: int
    sync_app_commands: bool
    sync_guild_id: int | None


def load_settings() -> Settings:
    load_dotenv(BASE_DIR / ".env")

    extensions = tuple(
        item.strip()
        for item in os.getenv(
            "MECHA_EXTENSIONS",
            "mecha.cogs.admin,mecha.cogs.voice,mecha.cogs.praise,mecha.cogs.league,mecha.cogs.music",
        ).split(",")
        if item.strip()
    )
    if "mecha.cogs.music" not in extensions:
        extensions = (*extensions, "mecha.cogs.music")

    data_dir = Path(os.getenv("MECHA_DATA_DIR", DATA_DIR))
    tmp_dir = Path(os.getenv("MECHA_TMP_DIR", TMP_DIR))

    return Settings(
        token=os.getenv("DISCORD_TOKEN", ""),
        command_prefix=os.getenv("MECHA_COMMAND_PREFIX", "!"),
        extensions=extensions,
        data_dir=data_dir,
        tmp_dir=tmp_dir,
        praise_file=Path(os.getenv("MECHA_PRAISE_FILE", data_dir / "praises.txt")),
        league_api_url=os.getenv(
            "MECHA_LEAGUE_API_URL",
            "https://127.0.0.1:2999/liveclientdata/allgamedata",
        ),
        league_poll_seconds=float(os.getenv("MECHA_LEAGUE_POLL_SECONDS", "0.2")),
        activity_name=os.getenv("MECHA_ACTIVITY_NAME", "Mecha 01"),
        auto_disconnect_when_alone=os.getenv("MECHA_AUTO_DISCONNECT_WHEN_ALONE", "false").lower()
        in {"1", "true", "yes", "on"},
        auto_disconnect_grace_seconds=float(os.getenv("MECHA_AUTO_DISCONNECT_GRACE_SECONDS", "30")),
        auto_disconnect_checks=int(os.getenv("MECHA_AUTO_DISCONNECT_CHECKS", "3")),
        log_level=os.getenv("MECHA_LOG_LEVEL", "INFO"),
        spotify_client_id=os.getenv("SPOTIFY_CLIENT_ID", ""),
        spotify_client_secret=os.getenv("SPOTIFY_CLIENT_SECRET", ""),
        music_max_playlist_size=int(os.getenv("MECHA_MUSIC_MAX_PLAYLIST_SIZE", "100")),
        music_idle_timeout_seconds=int(os.getenv("MECHA_MUSIC_IDLE_TIMEOUT_SECONDS", "300")),
        sync_app_commands=os.getenv("MECHA_SYNC_APP_COMMANDS", "true").lower()
        in {"1", "true", "yes", "on"},
        sync_guild_id=int(os.getenv("MECHA_SYNC_GUILD_ID")) if os.getenv("MECHA_SYNC_GUILD_ID") else None,
    )
