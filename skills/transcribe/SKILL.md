---
name: transcribe
description: Transcribe audio or video files (or YouTube/podcast URLs) using whisper.cpp with the medium model on Apple Silicon. Routes output between meeting mode (private recordings) and source-material mode (public videos / podcasts / lectures), each with its own downstream artifact (meeting summary vs article-style write-up). Optionally generates a spoken audio summary via Piper TTS.
argument-hint: [file-path(s) | URL(s)] [--meeting | --source-material] [--topic <topic>] [--audio]
disable-model-invocation: true
allowed-tools: Bash, Read, Write, Glob, Edit, Agent, AskUserQuestion
---

# Transcribe Media Files

Transcribe audio/video inputs (local files or URLs) with whisper.cpp, then produce a downstream artifact tailored to the source: a meeting summary for private recordings, or an article-style write-up for public videos / podcasts. Optionally narrate the meeting summary as a WAV via Piper.

## Configuration

- **Whisper binary**: `whisper-cli` (homebrew, typically `/opt/homebrew/bin/whisper-cli`).
- **Model**: `~/.claude/models/ggml-medium.bin`.
- **URL downloader**: `yt-dlp`. If your installer ships with a python ≥3.10 shebang it will run directly; if you see "unsupported version of Python", invoke explicitly via your homebrew python: `/opt/homebrew/bin/python3 $(which yt-dlp) ...`.
- **Language**: default `-l en`. Use `-l <code>` if specified; only `-l auto` if explicitly requested.
- **Dictionary**: if `transcribe-output/transcription_dictionary.md` exists in the project, load it for post-processing corrections (see Post-Processing).
- **Templates**: all output documents are rendered from files in `templates/` next to this SKILL.md. Edit those files to change formatting; do not embed templates inline in SKILL.md.
- **Piper TTS** (optional, for `--audio`): `~/.local/bin/piper` wrapping the piper-tts venv at `~/.local/share/piper-venv/`. Voice: `~/.local/share/piper-voices/en_US-amy-medium.onnx`.

## Modes

The skill has two output modes. They differ in destination, filename convention, frontmatter, and downstream artifact.

| | `meeting` mode | `source-material` mode |
|---|---|---|
| Use case | private recordings (Teams/Zoom/Meet calls, voice memos) | public videos, podcasts, lectures, conference talks |
| Output base | `transcribe-output/<MMDDYYYY>/meetings/` | `transcribe-output/<MMDDYYYY>/source-material/` |
| Filename pattern | `<sanitized_input>_transcript.md`, `..._transcript_timestamped.md`, `..._summary.md` | `<YYYY-MM-DD>_<source_type>_<slug>_transcript.md`, `..._timestamped.md`, `<YYYY-MM-DD>_<source_type>_<slug>.md` (article: no `_article` suffix) |
| Frontmatter template | `templates/frontmatter-meeting.md` | `templates/frontmatter-source-material.md` |
| Downstream template | `templates/meeting-summary.md` | `templates/article.md` |
| Transcript template | `templates/transcript.md` (both modes) | `templates/transcript.md` (both modes) |
| Timestamped template | `templates/transcript-timestamped.md` (both modes) | `templates/transcript-timestamped.md` (both modes) |
| `--audio` supported? | yes (narrates the summary) | no (articles are read material, not voice content) |

## Source kinds

Orthogonal to mode: each input is either a **local file** or a **URL**. URLs require a download step (see step 2).

## Process

### Step 0. Parse arguments and resolve mode + topic

1. Split `$ARGUMENTS` into a list of inputs (file paths and/or URLs) plus optional flags. Recognised flags:
   - `--meeting` — force meeting mode for all inputs.
   - `--source-material` — force source-material mode for all inputs.
   - `--topic <topic>` — set a topic value to write into the source-material frontmatter (only meaningful in source-material mode).
   - `--audio` — generate a spoken summary (meeting mode only). Ignored in source-material mode.
2. If no inputs are provided, ask the user.
3. **Resolve mode for each input**:
   - If `--meeting` or `--source-material` is set, use it for all inputs.
   - Else infer:
     - URL → tentatively `source-material`.
     - Local file with `Meeting Recording` / `Teams` / `Zoom` / `GoogleMeet` markers in the filename → tentatively `meeting`.
     - Anything else → ambiguous.
   - If any input is ambiguous, **ask the user** via `AskUserQuestion`. Do not guess. Cache the answer for the rest of the batch (ask once per batch unless inputs are genuinely heterogeneous).
4. **Resolve topic** (source-material mode only):
   - If `--topic` is set, use it.
   - Otherwise ask the user once via `AskUserQuestion`. Suggest options derived from past topic values used in `transcribe-output/` (look across existing date folders for prior `topic:` frontmatter values), plus an "Other" entry.
   - Never default silently. Ambiguity on topic always becomes a question.

### Step 1. Pre-flight checks

- `whisper-cli`, `ffmpeg`, `ffprobe` must be on PATH.
- Model file `~/.claude/models/ggml-medium.bin` must exist.
- If any URL inputs are present, `yt-dlp` must be runnable.
- If `--audio` and meeting mode: also verify Piper binary and voice model exist; on missing tools, warn and skip audio (do not fail the whole run).
- Report missing tools with the install command from "Error handling" below.

### Step 2. Acquire audio for each input

- **Local file**: keep the existing path; jump to step 3.
- **URL**: download with yt-dlp:
  ```bash
  yt-dlp --print "%(title)s|||%(channel)s|||%(uploader)s|||%(duration)s|||%(id)s" "<url>"
  yt-dlp -x --audio-format m4a -o "/tmp/yt_<id>.%(ext)s" "<url>"
  ```
  Capture title, channel/uploader, duration, video id. Sanitize the title into a filename slug per "Filename sanitization".

### Step 3. Extract metadata with ffprobe

```bash
ffprobe -v quiet -show_entries format=duration -of csv=p=0 "<input_or_downloaded_file>"
```
Convert to human-readable form ("32 min 14 sec"). Warn if duration > 2 hours.

### Step 4. Detect silent segments

```bash
ffmpeg -i "<input>" -af silencedetect=noise=-30dB:d=30 -f null - 2>&1 | grep "silence_start\|silence_end"
```
Store these timestamps for use in step 9e (cross-reference with transcript to flag likely hallucinations).

### Step 5. Resolve dates

- **Meeting mode**: extract a meeting date from the filename if present (`YYYYMMDD`, `YYYY-MM-DD`, `DD-MM-YYYY`, `DDMMYYYY`). Fall back to today's date and note it in the summary.
- **Source-material mode**: `captured` field is always today's date in `YYYY-MM-DD`. Source's own publish date can go in a `published` frontmatter field if known.

### Step 6. Create output directories

All outputs live under the **current working directory** (the active project folder). Use today's date in `MMDDYYYY` for the bucket folder.

- **Meeting mode**:
  ```bash
  mkdir -p "transcribe-output/$(date +%m%d%Y)/meetings"
  ```
- **Source-material mode**:
  ```bash
  mkdir -p "transcribe-output/$(date +%m%d%Y)/source-material"
  ```

### Step 7. Convert to 16 kHz mono WAV

```bash
ffmpeg -i "<input>" -ar 16000 -ac 1 -c:a pcm_s16le "/tmp/whisper_<sanitized_name>.wav" -y
```

### Step 8. Run whisper-cli

```bash
whisper-cli -m ~/.claude/models/ggml-medium.bin -l en -otxt -osrt \
  -of "/tmp/whisper_output_<sanitized_name>" \
  -f "/tmp/whisper_<sanitized_name>.wav"
```
Produces `/tmp/whisper_output_<name>.txt` and `/tmp/whisper_output_<name>.srt`.

For long recordings (>30 min) or multi-input batches, run in background and notify on completion. Process inputs in parallel.

### Step 9. Hallucination detection and quality validation

Read the raw `.txt` and run all checks below, then assign a quality rating.

**9a. Consecutive repetition** — split into lines, normalize (lowercase, strip whitespace, remove punctuation). If any normalized line appears >5 times consecutively, truncate the run and insert `[... hallucination detected and truncated — ~N repeated lines removed ...]`.

**9b. Global repeated phrase ratio** — if any normalized line accounts for >10% of total lines, prepend a quality warning: `> ⚠️ Quality warning: The phrase "<phrase>" appears <N> times (<X>% of lines), which may indicate hallucination.`

**9c. Word density** — `expected_min = duration_minutes * 80`, `expected_max = duration_minutes * 200`. Flag if outside.

**9d. Trailing garbage** — last 20% of lines: if unique-line ratio < 0.3, truncate from where repetition begins and insert `[... trailing hallucination detected and truncated — last ~N lines removed ...]`.

**9e. Cross-reference with silence map** — for transcript segments whose SRT timestamps fall inside detected silence windows, if their content is repetitive or off-topic, insert `[... segment during detected silence — content may be hallucinated ...]`.

**9f. Quality score**:
- **High**: no hallucinations, density in band, no trailing garbage.
- **Medium**: minor warnings.
- **Low**: hallucination patterns detected, content truncated, or density significantly off.

### Step 10. Dictionary post-processing

If `transcribe-output/transcription_dictionary.md` exists, read it and apply case-insensitive whole-word replacements to both the plain and SRT transcripts. Be careful with partial words (don't turn "soaring" into "SORing"). If the file does not exist, on first run create it with an empty template:

```markdown
# Transcription Dictionary

| Whisper Output | Correct Term |
|----------------|--------------|
| | |
```

### Step 11. Render the plain transcript

Load `templates/transcript.md`. Fill placeholders:

- `FRONTMATTER_BLOCK`: render `templates/frontmatter-meeting.md` (meeting mode) or `templates/frontmatter-source-material.md` (source-material mode). Leave `EXTRA_LINES` empty (no `format:` line on the plain transcript).
- `TITLE`: meeting name (meeting mode) or video title (source-material mode).
- `SOURCE_LINE`: `Source File: <filename>` (meeting) or `Source: <url>` (source-material).
- `SIBLING_LINKS_BLOCK`: blockquote lines linking siblings. Use relative paths from the transcript's location to its siblings.
- `QUALITY`, `QUALITY_NOTE`: from step 9f.
- `BODY`: cleaned transcript text (paragraphs preserved; hallucinations removed; dictionary corrections applied).

Write to the path resolved by mode (see Modes table above).

### Step 12. Render the timestamped transcript

Load `templates/transcript-timestamped.md`. Same frontmatter rendering as step 11, but pass `EXTRA_LINES="format: timestamped\n"`. Convert each SRT cue into `**[HH:MM:SS]** segment text` separated by blank lines. Apply hallucination truncation and dictionary corrections.

### Step 13. Render the downstream artifact

- **Meeting mode**: load `templates/meeting-summary.md`. Fill all placeholders. Write to `transcribe-output/<MMDDYYYY>/meetings/<sanitized_input>_summary.md`. Include `(~MM:SS)` timestamps from the SRT for decisions, discussion points, and action items so the user can locate them. Do not invent decisions or action items; if none exist, say so explicitly.
- **Source-material mode**: load `templates/article.md`. Fill all placeholders. Write to `transcribe-output/<MMDDYYYY>/source-material/<YYYY-MM-DD>_<source_type>_<slug>.md`. The article must reflect the source content as a coherent piece of writing, not as a transcript paraphrase. Do NOT include participants, decisions, or action items. Sections should be thematic.

### Step 14. Audio summary (optional, meeting mode only)

If `--audio` is set (or the user said yes to "generate audio summary?"), and mode is `meeting`:

**Pre-flight**: verify `~/.local/bin/piper` and the Amy voice model exist. If missing, warn and skip — do not fail the run.

**Narration text preparation**: read the meeting summary Markdown and convert it to narration-friendly plain text in `/tmp/piper_narration_<sanitized_name>.txt`. Apply all of:
- Remove the metadata table entirely (the `| Field | Value |` block).
- Convert `# Heading`, `## Heading`, `### Heading` to `Heading.`.
- Strip `**`, `*`, `__`, `_` wrapping.
- Convert `[link text](url)` to just the link text. Drop bare URLs.
- Strip leading `> ` from lines.
- Strip `- [ ]` / `- [x]` to plain list items, then strip leading `- `.
- Convert `1.`, `2.`, `3.`, ... to `First.`, `Second.`, `Third.`, ... up to `Tenth.`; beyond, keep numerals.
- Strip `(~MM:SS)` and `(~HH:MM:SS)`.
- Strip code fences (triple backticks).
- Drop pure cross-reference link blocks (e.g. `> Summary: [name](path)`).
- Preserve every name, figure, and conclusion. This is not a re-summary.

**Generate**:
```bash
cat "/tmp/piper_narration_<sanitized_name>.txt" | ~/.local/bin/piper \
  --model ~/.local/share/piper-voices/en_US-amy-medium.onnx \
  --output_file "transcribe-output/<MMDDYYYY>/meetings/<sanitized_name>_summary.wav"
```

**Verify** the WAV was written and is non-empty. On failure, warn but do not fail the overall run.

**Update** the summary Markdown's metadata table to add an `Audio Summary` row only if generation succeeded.

In source-material mode, ignore `--audio`.

### Step 15. Clean up temp files

Delete all `/tmp/whisper_*`, `/tmp/yt_*`, `/tmp/piper_narration_*` files for this batch only AFTER the transcript, timestamped transcript, downstream artifact, and (if requested) audio summary have all been written and verified. If you used parallel agents, wait for all of them before cleanup.

### Step 16. Report

Per file, report:
- Final paths (transcript, timestamped, summary or article, audio if generated)
- Mode and (if source-material) topic
- Word count and duration
- Quality rating with one-line reason if not High
- Hallucination warnings
- Number of dictionary corrections applied
- Audio summary status (generated / skipped / failed with reason), if applicable
- Anything unusual

## Multiple files

Process inputs in parallel. Each input gets its own transcript + timestamped + downstream artifact, unless the user explicitly says they belong together (only meaningful for meetings, where a single combined summary may be appropriate).

## Filename sanitization

Strip the file extension. Replace spaces, ampersands, parentheses, and other special characters with underscores. Remove leading/trailing underscores. Collapse consecutive underscores into one.

For source-material slugs, additionally:
- Lowercase.
- Replace underscores with hyphens (slug style).
- Trim to ~60 chars; prefer keeping recognisable keywords (channel, speaker, topic) over generic words.

Examples (meeting):
- `Discovery RFQ-20260324_115957UTC-Meeting Recording.mp4` → `Discovery_RFQ-20260324_115957UTC-Meeting_Recording`
- `Alice and Bob & Charlie Catch up-20260324_110238-Meeting Recording.mp4` → `Alice_and_Bob_Charlie_Catch_up-20260324_110238-Meeting_Recording`

Examples (source-material slug):
- "Skill Issue: Andrej Karpathy on Code Agents…" → `karpathy-skill-issue-no-priors`
- "Stanford CS230 | Autumn 2025 | Lecture 8: Agents, Prompts, and RAG" → `stanford-cs230-lecture-8-agents-rag`

## Error handling

- `whisper-cli` missing: `brew install whisper-cpp`.
- Model missing:
  ```bash
  mkdir -p ~/.claude/models && curl -L -o ~/.claude/models/ggml-medium.bin \
    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin"
  ```
- `ffmpeg` / `ffprobe` missing: `brew install ffmpeg`.
- `yt-dlp` missing: `pip install -U yt-dlp` (against python ≥3.10) or `brew install yt-dlp`.
- `yt-dlp` failing on python version: invoke via an explicit interpreter, e.g. `/opt/homebrew/bin/python3 $(which yt-dlp) ...`.
- Piper missing:
  ```bash
  python3 -m venv ~/.local/share/piper-venv && source ~/.local/share/piper-venv/bin/activate && pip install piper-tts
  mkdir -p ~/.local/bin
  printf '#!/bin/zsh\nexec ~/.local/share/piper-venv/bin/piper "$@"\n' > ~/.local/bin/piper && chmod +x ~/.local/bin/piper
  ```
- Piper voice model missing:
  ```bash
  mkdir -p ~/.local/share/piper-voices && \
    curl -L -o ~/.local/share/piper-voices/en_US-amy-medium.onnx "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx" && \
    curl -L -o ~/.local/share/piper-voices/en_US-amy-medium.onnx.json "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json"
  ```
- Piper generation failure: warn the user, do not fail the overall transcription. Text outputs are the primary deliverable.
- Input file unreadable: report path and stop for that input only.
- Transcription empty: report and suggest checking audio quality or input format.

## Writing style

- Never use em dashes (`--` or `—`) anywhere in output. Use commas, periods, semicolons, or parentheses.
- Substance over verbosity. Every paragraph carries information.
- No AI-tell patterns: no excessive hedging, no hollow summarisation, no repetitive structure.

## Notes

- Medium model gives good accuracy for meetings, podcasts, and lectures. Switch model only if the user requests it.
- Templates live in `templates/` next to this SKILL.md. Edit those to adjust output format. SKILL.md should not embed templates inline.
- Piper TTS runs locally via onnxruntime (no network calls or API keys). The Amy medium voice produces 22050 Hz mono WAV.
- Audio summaries are always optional and never block the core transcription workflow.
