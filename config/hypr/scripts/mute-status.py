#!/usr/bin/env python3
import json, subprocess, sys
if len(sys.argv) > 1 and sys.argv[1] == 'toggle':
    subprocess.run(['wpctl', 'set-mute', '@DEFAULT_AUDIO_SINK@', 'toggle'], check=True)
result = subprocess.run(['wpctl', 'get-volume', '@DEFAULT_AUDIO_SINK@'], capture_output=True, text=True)
if result.returncode:
    print(json.dumps({'text': '󰖁', 'tooltip': 'Audio device unavailable', 'class': 'unavailable'}))
else:
    muted = '[MUTED]' in result.stdout
    print(json.dumps({'text': '󰖁' if muted else '󰕾', 'tooltip': 'Unmute' if muted else 'Mute', 'class': 'muted' if muted else 'unmuted'}, ensure_ascii=False))
