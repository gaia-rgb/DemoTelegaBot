import os
import time
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
_model = None


def get_model():
    global _model
    if _model is None:
        import whisper
        model_name = os.getenv("WHISPER_MODEL", "small")
        logger.info("Loading Whisper model: %s", model_name)
        _model = whisper.load_model(model_name)
        logger.info("Whisper model loaded")
    return _model


async def transcribe_voice(ogg_bytes: bytes) -> str:
    """Convert OGG voice bytes to text using local Whisper."""
    import ffmpeg

    with tempfile.TemporaryDirectory() as tmp:
        ogg_path = Path(tmp) / "voice.ogg"
        wav_path = Path(tmp) / "voice.wav"
        ogg_path.write_bytes(ogg_bytes)

        try:
            (
                ffmpeg.input(str(ogg_path))
                      .output(str(wav_path), ar=16000, ac=1)
                      .overwrite_output()
                      .run(quiet=True)
            )
        except Exception as e:
            logger.error("ffmpeg conversion failed: %s", e)
            raise RuntimeError("Не удалось обработать голосовое сообщение") from e

        t0 = time.perf_counter()
        result = get_model().transcribe(str(wav_path), language="ru", fp16=False)
        elapsed = time.perf_counter() - t0
        text = result["text"].strip()
        logger.info("Transcribed in %.2fs: %r", elapsed, text[:80])
        return text