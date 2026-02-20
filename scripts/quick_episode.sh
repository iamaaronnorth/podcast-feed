#!/bin/bash

# Quick Episode Creator
# Usage: ./quick_episode.sh "Episode Title" ~/path/to/content.md

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PODCAST_DIR="$(dirname "$SCRIPT_DIR")"

echo "🎙️  Creating podcast episode..."

# Run the Python script
python3 "$SCRIPT_DIR/create_episode.py" "$@"

echo ""
echo "🔊 Next steps:"
echo "1. Generate TTS audio: openclaw tts \"\$(cat /tmp/episode_*_script.txt)\""
echo "2. Move audio file to: $PODCAST_DIR/audio/"
echo "3. Test RSS feed: https://iamaaronnorth.github.io/podcast-feed/feed.xml"
echo ""
echo "✅ Episode creation complete!"