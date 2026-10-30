#!/bin/sh
# Create the admin account if needed, then run the MUD server
set -e
python /app/deploy/create_admin.py
exec python -m tale.main --game /app/LlamaTale/stories/hallow_mud --mode mud
