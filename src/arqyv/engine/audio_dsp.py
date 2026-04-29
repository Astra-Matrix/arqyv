"""Audio DSP utilities: peak metering, loudness normalization hints, EQ.

Uses only numpy (already a transitive dep of sentence-transformers).
Falls back gracefully if numpy is unavailable.

These values are passed as hints to the Qt audio output — they don't
implement a codec or decoder but shape playback behaviour.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field

log = logging.getLogger(__name__)


@dataclass
class EQBand:
    """A single parametric EQ band."""
    freq_hz: float      # center frequency
    gain_db: float = 0.0
    q: float = 1.0      # quality factor (bandwidth)


@dataclass
class AudioDSPSettings:
    """All DSP settings for one playback session."""
    volume: float = 1.0             # 0.0 – 1.0 linear
    normalize: bool = False         # auto-normalize to -14 LUFS
    eq_bands: list[EQBand] = field(default_factory=list)
    mute: bool = False

    def effective_volume(self) -> float:
        return 0.0 if self.mute else self.volume


# ── Peak meter ─────────────────────────────────────────────────────────────

class PeakMeter:
    """Simple peak detector for visualizing audio levels.

    Feed PCM samples via update(); read peak/rms via properties.
    """

    def __init__(self, decay_db_per_sec: float = 20.0, fps: int = 30) -> None:
        self._peak_l = 0.0
        self._peak_r = 0.0
        self._rms_l = 0.0
        self._rms_r = 0.0
        self._decay = 10 ** (-decay_db_per_sec / (fps * 20))

    def update(self, samples_l: "list[float]", samples_r: "list[float] | None" = None) -> None:
        try:
            import numpy as np
            arr_l = np.array(samples_l, dtype=np.float32)
            arr_r = np.array(samples_r if samples_r else samples_l, dtype=np.float32)

            pk_l = float(np.max(np.abs(arr_l)))
            pk_r = float(np.max(np.abs(arr_r)))
            rms_l = float(np.sqrt(np.mean(arr_l ** 2)))
            rms_r = float(np.sqrt(np.mean(arr_r ** 2)))
        except ImportError:
            pk_l = max(abs(s) for s in samples_l) if samples_l else 0
            pk_r = pk_l
            rms_l = rms_r = 0.0

        self._peak_l = max(pk_l, self._peak_l * self._decay)
        self._peak_r = max(pk_r, self._peak_r * self._decay)
        self._rms_l = rms_l
        self._rms_r = rms_r

    def decay(self) -> None:
        self._peak_l *= self._decay
        self._peak_r *= self._decay

    @property
    def peak_db(self) -> tuple[float, float]:
        def to_db(v: float) -> float:
            return 20 * math.log10(max(v, 1e-9))
        return to_db(self._peak_l), to_db(self._peak_r)

    @property
    def rms_db(self) -> tuple[float, float]:
        def to_db(v: float) -> float:
            return 20 * math.log10(max(v, 1e-9))
        return to_db(self._rms_l), to_db(self._rms_r)

    @property
    def peak_linear(self) -> tuple[float, float]:
        return self._peak_l, self._peak_r


# ── Preset EQ configurations ───────────────────────────────────────────────

class EQPreset:
    FLAT = AudioDSPSettings()

    BASS_BOOST = AudioDSPSettings(eq_bands=[
        EQBand(60,   +6.0, 0.8),
        EQBand(120,  +4.0, 1.0),
        EQBand(250,  +2.0, 1.2),
    ])

    VOCAL_BOOST = AudioDSPSettings(eq_bands=[
        EQBand(250,  -2.0, 1.0),
        EQBand(1000, +3.0, 1.5),
        EQBand(3000, +4.0, 1.5),
        EQBand(8000, +2.0, 1.0),
    ])

    CINEMA = AudioDSPSettings(eq_bands=[
        EQBand(80,   +4.0, 0.7),
        EQBand(500,  -2.0, 1.0),
        EQBand(2000, +3.0, 1.5),
        EQBand(8000, +2.0, 1.0),
    ])

    NIGHT_MODE = AudioDSPSettings(volume=0.5, eq_bands=[
        EQBand(60,   -4.0, 0.8),
        EQBand(8000, -3.0, 1.0),
        EQBand(1000, +4.0, 1.5),
        EQBand(3000, +3.0, 1.5),
    ])
