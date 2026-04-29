"""ARQYVMediaEngine — custom media layer.

Built entirely on OS-native APIs via Qt Multimedia (zero external installs)
plus pure-Python subsystems for format detection, subtitles, and playlists.

  engine.core          → ARQYVMediaEngine  (the single authoritative object)
  engine.format        → magic-byte format detector
  engine.subtitle      → SRT / ASS / VTT parser + Qt overlay renderer
  engine.playlist      → playlist with shuffle, repeat, smart resume
  engine.audio_dsp     → volume normalisation, peak metering, EQ hints
"""
