class MusicError(Exception):
    """Base class for user-facing music errors."""


class ResolverError(MusicError):
    """Raised when input cannot be resolved to playable tracks."""


class SpotifyCredentialsError(ResolverError):
    """Raised when Spotify metadata is requested without credentials."""


class PlaybackError(MusicError):
    """Raised when playback cannot start or continue."""


class VoiceDisconnectedError(PlaybackError):
    """Raised when playback stops because the bot is no longer connected to voice."""
