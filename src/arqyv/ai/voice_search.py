"""Voice search recorder and transcriber.

Records audio from the default microphone while the user holds the
voice button, then transcribes it using OpenAI Whisper (local model).

Dependencies: sounddevice, soundfile, openai-whisper
"""

from __future__ import annotations

import io
import logging
import queue
import tempfile
from pathlib import Path
from threading import Thread
from typing import Any

log = logging.getLogger(__name__)

_SAMPLE_RATE = 16000
_CHANNELS = 1


class VoiceSearchRecorder:
    """Thread-safe voice recorder. Call start(), then stop_and_transcribe()."""

    def __init__(self, whisper_model: str = "base") -> None:
        self.whisper_model = whisper_model
        self._audio_queue: queue.Queue[Any] = queue.Queue()
        self._frames: list[Any] = []
        self._recording = False
        self._thread: Thread | None = None

    def start(self) -> None:
        self._recording = True
        self._frames = []
        self._thread = Thread(target=self._record, daemon=True)
        self._thread.start()

    def stop_and_transcribe(self) -> str:
        self._recording = False
        if self._thread:
            self._thread.join(timeout=5)

        return self._transcribe()

    def _record(self) -> None:
        try:
            import sounddevice as sd  # type: ignore[import]
            import numpy as np

            with sd.InputStream(
                samplerate=_SAMPLE_RATE,
                channels=_CHANNELS,
                dtype="float32",
            ) as stream:
                while self._recording:
                    data, _ = stream.read(1024)
                    self._frames.append(data)
        except Exception:
            log.exception("Voice recording failed.")

    def _transcribe(self) -> str:
        if not self._frames:
            return ""
        try:
            import numpy as np
            import soundfile as sf  # type: ignore[import]
            import whisper  # type: ignore[import]

            audio = np.concatenate(self._frames, axis=0).flatten()

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = Path(tmp.name)
                sf.write(str(tmp_path), audio, _SAMPLE_RATE)

            model = whisper.load_model(self.whisper_model)
            result = model.transcribe(str(tmp_path), fp16=False, language="en")
            tmp_path.unlink(missing_ok=True)
            return result.get("text", "").strip()
        except ImportError:
            log.warning("sounddevice/soundfile/whisper not installed; voice search unavailable.")
            return ""
        except Exception:
            log.exception("Transcription failed.")
            return ""
