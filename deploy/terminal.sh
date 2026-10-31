#!/bin/sh
# The old way to play: a terminal in the browser, one single-player (IF) game per tab.
# Each game is its own Python process, so cap the tabs to what the free plan's memory holds.
set -e
exec ttyd --port "${PORT:-8180}" --writable --max-clients "${MAX_PLAYERS:-3}" \
    -t titleFixed="Hallow Mud" \
    -t fontFamily="Martian Mono, Menlo, monospace" \
    -t 'theme={"background":"#10201d","foreground":"#e4e5da","cursor":"#f5b726"}' \
    python -m tale.main --game /app/LlamaTale/stories/hallow_mud --mode if
