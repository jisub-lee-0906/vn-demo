# 14 audio packaging and looping

Status: scaffold template, not smoke-passed yet.

Purpose:
- Convert generated/imported audio into Ren'Py-friendly `.ogg` assets.
- Normalize volume, trim silence, create loop candidates, and write audio manifests.

Target structure:
```text
game/audio/bgm/*.ogg
game/audio/sfx/*.ogg
```

Recommended ffmpeg commands:
```bash
# Convert to ogg/vorbis
ffmpeg -y -i input.wav -c:a libvorbis -q:a 5 output.ogg

# Trim leading/trailing silence conservatively
ffmpeg -y -i input.wav -af silenceremove=start_periods=1:start_threshold=-50dB:stop_periods=1:stop_threshold=-50dB output_trim.wav

# Peak normalize to about -1 dBFS
ffmpeg -y -i input.wav -af loudnorm=I=-18:TP=-1.5:LRA=11 output_norm.wav
```

Manifest fields:
- semantic_name
- source_file
- output_file
- duration_sec
- sample_rate
- channels
- generation_or_library_source
- license_note
- loopable: true/false
- notes

Ren'Py usage:
```renpy
play music "audio/bgm/bgm_school_day_loop.ogg" fadein 1.0
play sound "audio/sfx/paper_rustle.ogg"
```
