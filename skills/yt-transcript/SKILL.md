---
name: yt-transcript
description: >
  Extracts YouTube video transcripts and produces structured summaries with key takeaways.
  Use this skill whenever the user provides a YouTube link and asks for a transcript, summary,
  takeaways, or analysis of a YouTube video. Also trigger when the user says things like
  "summarise this video", "what does this video say", "get me the transcript",
  "key points from this YouTube video", or pastes a YouTube/youtu.be URL with any request
  to extract or analyse its content. Handles non-English videos by fetching EN translations.
  Requires network access (pip install + YouTube API calls).
---

# YouTube Video Summariser

Extracts transcripts from YouTube videos using the `youtube-transcript-api` Python library and produces:

1. **Summary file** (`.md` + `.pdf`) - structured analysis with context, key arguments, takeaways, and notable quotes
2. **Transcript file** (`.md` + `.pdf`) - full timestamped transcript in English
3. **Executive summary** - displayed directly in chat after processing

## Requirements

- **Claude Code environment** - this skill requires network access to install dependencies and fetch data from YouTube. It will not work in Claude.ai or other network-restricted environments.
- Python 3.x
- `youtube-transcript-api` (installed automatically by the skill)
- `fpdf2` (installed automatically by the skill, used for PDF generation)

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `output_dir` | `output/yt-transcripts` | Relative path (from project root) where transcript and summary files are saved. Created automatically if it doesn't exist. Change this value to redirect output to a different location. |

## Inputs

| Parameter | Required | Description |
|-----------|----------|-------------|
| YouTube URL | Yes | Any valid YouTube link (`youtube.com/watch?v=`, `youtu.be/`, etc.) |
| Output directory | No | Where to save the files. Default: `output/yt-transcripts/` subfolder inside the current project directory (see Configuration above). User can override per-invocation by specifying a different path. |

## Workflow

### Step 1: Install dependency

```bash
pip install youtube-transcript-api fpdf2 --break-system-packages
```

### Step 2: Extract the video ID

Parse the YouTube URL to extract the video ID. Handle these formats:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://youtube.com/watch?v=VIDEO_ID&t=123` (strip extra params)

### Step 3: Fetch transcript

Run the transcript extraction script:

```bash
python {base_directory}/scripts/fetch_transcript.py VIDEO_ID [--output-dir OUTPUT_DIR]
```

The default `--output-dir` should be `output/yt-transcripts/` inside the current project directory (as configured in the Configuration section above). Create the folder if it doesn't exist. For example: `--output-dir /path/to/project/output/yt-transcripts`

The script handles:
- Fetching available transcript languages
- Preferring manual EN transcripts over auto-generated ones
- Falling back to auto-generated EN transcripts
- For non-English videos: fetching the original transcript and translating to EN
- Outputting a clean timestamped transcript

The script writes a JSON file with the transcript data. If the script fails (e.g. no transcript available, video is private), report the error clearly to the user.

### Step 4: Generate the transcript markdown file

Read the JSON output and create a markdown file named:
`{video_id}_transcript.md`

Format:
```markdown
# Transcript: {Video Title}

**Source:** {YouTube URL}
**Date extracted:** {current date}
**Language:** {original language} → English (if translated)

---

[00:00] First line of transcript text here.
[00:15] Next line continues here.
[01:02] And so on through the entire video.
```

Timestamps should use `[MM:SS]` format for videos under 1 hour, `[HH:MM:SS]` for longer videos.

Once the transcript markdown file has been successfully written, delete the intermediate JSON file (`{video_id}_transcript.json`) — it is no longer needed.

### Step 5: Generate the summary markdown file

Read the full transcript and produce a structured summary named:
`{video_id}_summary.md`

Use this structure:

```markdown
# Summary: {Video Title}

**Source:** {YouTube URL}
**Date:** {current date}

## Context

Brief description of the video: who is speaking, what the setting is (interview, lecture, panel, solo commentary), and the core topic. 2-3 sentences max.

## Key Arguments

The main claims, positions, or ideas presented in the video. Each argument as a separate paragraph. Use direct references to what was said. Aim for 3-7 key arguments depending on video length/density.

## Takeaways

The actionable or memorable points distilled from the content. Write as short, direct statements. 5-10 takeaways depending on content density.

## Notable Quotes

Direct quotes from the transcript that capture key moments or strong statements. Include the approximate timestamp. Select 3-6 quotes that represent the most important or distinctive points made.

> "Quote text here." — Speaker (if identifiable) [MM:SS]

## Summary

A concise 2-4 paragraph synthesis of the entire video content. This should stand alone as a useful overview for someone who hasn't watched the video.
```

**Writing guidelines for the summary:**
- Write in clear, functional prose. No filler, no hedging.
- Use simple connectors: "also", "as well", "instead".
- Ground claims in specifics from the transcript (names, numbers, examples mentioned).
- If multiple speakers are identifiable, attribute arguments to them.
- Do not invent or infer content not present in the transcript.
- If the transcript quality is poor (auto-generated, lots of errors), note this at the top of the summary.

### Step 6: Generate PDF versions

Convert both markdown files to PDF using the conversion script:

```bash
python {base_directory}/scripts/md_to_pdf.py {video_id}_summary.md
python {base_directory}/scripts/md_to_pdf.py {video_id}_transcript.md
```

This produces `{video_id}_summary.pdf` and `{video_id}_transcript.pdf` in the same output directory. The PDFs should be plain black and white, reflecting markdown formatting only — no colours, backgrounds, or visual effects. Do NOT open the PDF files after creation — the user will open them manually.

### Step 7: Output executive summary and file paths in chat

After all files are saved, output an executive summary directly in the chat. This is the only user-facing output from the skill. Use this format:

```
## Executive Summary: {Video Title}

**Duration:** ~{duration} | **Speakers:** {speaker names} | **Setting:** {brief setting}

{2-3 paragraph synthesis of the video's core thesis, key arguments, and actionable takeaways. Keep it tight — aim for ~150-250 words. Ground claims in specifics from the transcript. This should give the user enough context to decide whether to read the full summary or watch the video.}

**Key picks/recommendations mentioned:** {if applicable, list specific tickers, assets, names, or actionable items mentioned by speakers}

**Files saved:**
- `{path}/{video_id}_summary.md` + `.pdf`
- `{path}/{video_id}_transcript.md` + `.pdf`
```

Do NOT open any files, launch any viewers, or run any commands beyond file creation. The skill's job ends with writing files and outputting the summary above.

## Error Handling

| Error | Action |
|-------|--------|
| No transcript available | Tell the user. Some videos have transcripts disabled. |
| Video is private/unavailable | Tell the user the video cannot be accessed. |
| Network not available | Tell the user to enable network access in their settings. |
| Non-English, no translation available | Provide the original language transcript and note the limitation. |
| Very long video (>3hrs) | Proceed normally but warn the user the summary may be less precise for very long content. |
