from mecha.config import load_settings
from mecha.services.audio_player import AudioPlayer
from mecha.services.tts_service import TTSService, is_chinese


async def vocalizeText(ctx, text, language) -> None:
    bot = getattr(ctx, "bot", None)
    settings = getattr(bot, "settings", None) or load_settings()
    audio_player = getattr(bot, "audio_player", None) or AudioPlayer()
    service = TTSService(settings.tmp_dir / "tts", audio_player)
    await service.vocalize(ctx, text, language)
