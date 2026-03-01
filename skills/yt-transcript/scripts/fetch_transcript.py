#!/usr/bin/env python3
"""
Fetch YouTube video transcript using youtube-transcript-api.
Outputs a JSON file with transcript data, video metadata, and language info.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    print("ERROR: youtube-transcript-api not installed. Run: pip install youtube-transcript-api --break-system-packages", file=sys.stderr)
    sys.exit(1)


def extract_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',  # bare video ID
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url}")


def fetch_transcript(video_id: str) -> dict:
    """
    Fetch transcript for a YouTube video.
    
    Priority:
    1. Manual English transcript
    2. Auto-generated English transcript
    3. Any available transcript, translated to English
    4. Any available transcript in original language (if translation fails)
    
    Returns dict with keys: segments, language, was_translated, error
    """
    ytt = YouTubeTranscriptApi()
    try:
        transcript_list = ytt.list(video_id)
    except Exception as e:
        return {"segments": [], "language": None, "was_translated": False, "error": str(e)}

    # Try manual English first
    try:
        transcript = transcript_list.find_manually_created_transcript(['en', 'en-US', 'en-GB'])
        segments = transcript.fetch()
        return {
            "segments": [{"start": s.start, "duration": s.duration, "text": s.text} for s in segments],
            "language": "en",
            "language_name": "English (manual)",
            "was_translated": False,
            "error": None,
        }
    except Exception:
        pass

    # Try auto-generated English
    try:
        transcript = transcript_list.find_generated_transcript(['en', 'en-US', 'en-GB'])
        segments = transcript.fetch()
        return {
            "segments": [{"start": s.start, "duration": s.duration, "text": s.text} for s in segments],
            "language": "en",
            "language_name": "English (auto-generated)",
            "was_translated": False,
            "error": None,
        }
    except Exception:
        pass

    # Try any available transcript, translate to English
    try:
        for transcript in transcript_list:
            try:
                translated = transcript.translate('en')
                segments = translated.fetch()
                return {
                    "segments": [{"start": s.start, "duration": s.duration, "text": s.text} for s in segments],
                    "language": transcript.language_code,
                    "language_name": f"{transcript.language} → English (translated)",
                    "was_translated": True,
                    "error": None,
                }
            except Exception:
                continue
    except Exception:
        pass

    # Last resort: any transcript in original language
    try:
        for transcript in transcript_list:
            try:
                segments = transcript.fetch()
                return {
                    "segments": [{"start": s.start, "duration": s.duration, "text": s.text} for s in segments],
                    "language": transcript.language_code,
                    "language_name": f"{transcript.language} (original, translation unavailable)",
                    "was_translated": False,
                    "error": None,
                }
            except Exception:
                continue
    except Exception:
        pass

    return {"segments": [], "language": None, "was_translated": False, "error": "No transcripts available for this video."}


def format_timestamp(seconds: float, use_hours: bool = False) -> str:
    """Format seconds into [MM:SS] or [HH:MM:SS]."""
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    if use_hours or hours > 0:
        return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"
    return f"[{minutes:02d}:{secs:02d}]"


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube video transcript")
    parser.add_argument("video_id_or_url", help="YouTube video ID or URL")
    # Default to ~/Desktop if it exists (Claude Code), otherwise /mnt/user-data/outputs/ (Claude.ai)
    parser.add_argument("--output-dir", default=".", help="Directory to write output JSON")
    args = parser.parse_args()

    # Extract video ID
    try:
        video_id = extract_video_id(args.video_id_or_url)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching transcript for video: {video_id}")

    # Fetch transcript
    result = fetch_transcript(video_id)

    if result["error"] and not result["segments"]:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(1)

    # Check if video is longer than 1 hour for timestamp formatting
    max_time = max((s["start"] + s["duration"] for s in result["segments"]), default=0)
    use_hours = max_time >= 3600

    # Add formatted timestamps
    for segment in result["segments"]:
        segment["timestamp"] = format_timestamp(segment["start"], use_hours)

    # Build output
    output = {
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "extracted_at": datetime.now().isoformat(),
        "language": result["language"],
        "language_name": result.get("language_name", result["language"]),
        "was_translated": result["was_translated"],
        "total_segments": len(result["segments"]),
        "duration_seconds": int(max_time) if result["segments"] else 0,
        "segments": result["segments"],
        "warning": result.get("error"),
    }

    # Write output
    os.makedirs(args.output_dir, exist_ok=True)
    output_path = os.path.join(args.output_dir, f"{video_id}_transcript.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Transcript saved to: {output_path}")
    print(f"Language: {output['language_name']}")
    print(f"Segments: {output['total_segments']}")
    print(f"Duration: {format_timestamp(max_time, use_hours)}")


if __name__ == "__main__":
    main()
