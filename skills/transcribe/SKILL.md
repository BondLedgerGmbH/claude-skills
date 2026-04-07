---
name: transcribe
description: Transcribe audio or video files to text using whisper.cpp with the medium model on Apple Silicon. Use when the user wants to transcribe, get a transcript, or extract speech from any media file (mp4, mp3, wav, m4a, webm, ogg, flac, aac, wma, mkv, avi, mov, etc). Optionally generate an audio summary using Piper text-to-speech.
argument-hint: [file-path(s)] [--audio]
disable-model-invocation: true
allowed-tools: Bash, Read, Write, Glob, Edit, Agent
---

# Transcribe Media Files

Transcribe audio/video files using whisper.cpp (Apple Silicon optimized) with the medium GGML model for high accuracy. Then generate a meeting summary with key takeaways, decisions, and follow-up items.

## Configuration

- **Whisper binary**: `whisper-cli` (installed via homebrew at `/opt/homebrew/bin/whisper-cli`)
- **Model**: `~/.claude/models/ggml-medium.bin`
- **Language**: Default to `-l en`. If the user specifies a different language, use that instead. Only use `-l auto` if the user explicitly requests auto-detection.
- **Dictionary**: If `transcribe-output/transcription_dictionary.md` exists in the project, load it for post-processing corrections (see Post-Processing section).
- **Piper TTS binary**: `~/.local/bin/piper` (wrapper script invoking the piper-tts venv at `~/.local/share/piper-venv/`)
- **Piper voice model**: `~/.local/share/piper-voices/en_US-amy-medium.onnx` (US English, Amy, medium quality, 22050 Hz mono)

## Output Structure

All output goes into the **current working directory** (the active project folder):

1. **Meeting Summary** is saved to `transcribe-output/<current_date>/` where `<current_date>` uses `MMDDYYYY` format with no dashes (today's date, i.e. when the transcription is run).
   - Filename: `<sanitized_input_filename>_summary.md`
   - Example: `transcribe-output/03252026/Discovery_RFQ_20260324_summary.md`
   - If multiple files are transcribed together, create one summary per file unless the user indicates they are from the same meeting (in which case, create a single combined summary).

2. **Transcripts** are saved to `transcribe-output/<current_date>/Transcripts/` as Markdown files (inside the same date folder as the summary).
   - Filename: `<sanitized_input_filename>_transcript.md`
   - Example: `transcribe-output/03252026/Transcripts/Discovery_RFQ_20260324_transcript.md`

3. **Audio Summary** (optional) is saved to `transcribe-output/<current_date>/` alongside the written summary.
   - Filename: `<sanitized_input_filename>_summary.wav`
   - Example: `transcribe-output/03252026/Discovery_RFQ_20260324_summary.wav`
   - Only generated when the `--audio` flag is passed, or when the user confirms they want it (see Audio Summary section).

4. **Cross-linking**: The transcript file must include a link to its summary, and the summary must include a link to its transcript. If an audio summary was generated, the written summary must also link to the audio file.

Create these directories automatically if they don't exist.

## Process

1. **Identify the input file(s)** from `$ARGUMENTS`. If no file is provided, ask the user.

2. **Pre-flight checks**: Verify that `whisper-cli`, `ffmpeg`, and `ffprobe` are available. Verify the model file exists at `~/.claude/models/ggml-medium.bin`. If anything is missing, report the specific error and installation command (see Error Handling).

3. **Extract recording metadata** using ffprobe:
   ```bash
   ffprobe -v quiet -show_entries format=duration -of csv=p=0 "<input_file>"
   ```
   - Parse the duration into human-readable format (e.g., "32 min 14 sec") and store the raw seconds value for later validation.
   - If the recording is longer than 2 hours, warn the user that transcription may take a long time and could hit memory limits.

4. **Detect silent segments** using ffmpeg's silencedetect filter:
   ```bash
   ffmpeg -i "<input_file>" -af silencedetect=noise=-30dB:d=30 -f null - 2>&1 | grep "silence_start\|silence_end"
   ```
   - This identifies silence gaps longer than 30 seconds. Store these timestamps — they will be cross-referenced with the transcript to identify likely hallucination zones (whisper tends to hallucinate during silence).

5. **Extract meeting date from filename** if present. Look for date patterns like `YYYYMMDD`, `YYYY-MM-DD`, `DD-MM-YYYY`, `DDMMYYYY` in the filename. This is the **meeting date** (when the meeting occurred). It is distinct from today's date (when the transcription is run). If no date pattern is found in the filename, use today's date as the meeting date and note this in the summary.

6. **Create output directories**:
   ```bash
   mkdir -p transcribe-output/$(date +%m%d%Y)/Transcripts
   ```

7. **Convert to 16kHz mono WAV** (required by whisper.cpp). Use ffmpeg:
   ```bash
   ffmpeg -i "<input_file>" -ar 16000 -ac 1 -c:a pcm_s16le "/tmp/whisper_<sanitized_name>.wav" -y
   ```
   - Place temp WAV in `/tmp/` prefixed with `whisper_` to avoid clutter.
   - Supported input formats: mp4, mp3, wav, m4a, webm, ogg, flac, aac, wma, mkv, avi, mov, opus, amr, and any format ffmpeg can decode.

8. **Run whisper-cli** for transcription. Generate TWO outputs — plain text and SRT (timestamped):
   ```bash
   whisper-cli -m ~/.claude/models/ggml-medium.bin -l en -otxt -osrt -of "/tmp/whisper_output_<sanitized_name>" -f "/tmp/whisper_<sanitized_name>.wav"
   ```
   - This produces `/tmp/whisper_output_<name>.txt` (plain text) and `/tmp/whisper_output_<name>.srt` (timestamped).
   - For long recordings (>30 min), run in background and notify when done.
   - Process multiple files in parallel.

9. **Hallucination detection and quality validation** — Read the raw `.txt` transcript and run ALL of the following checks:

   ### 9a. Consecutive repetition detection
   - Split the transcript into lines.
   - **Normalize** each line for comparison: lowercase, strip whitespace, remove punctuation.
   - Check for any normalized line that appears more than 5 times consecutively.
   - If detected: truncate the repeated block in the output, insert a marker `[... hallucination detected and truncated — ~N repeated lines removed ...]`.

   ### 9b. Global repeated phrase ratio
   - Count how many times each normalized line appears across the *entire* transcript (not just consecutively).
   - If any single phrase accounts for more than 10% of total transcript lines, flag it as a suspected hallucination even if occurrences are scattered.
   - Insert a warning at the top of the transcript: `> ⚠️ Quality warning: The phrase "<phrase>" appears <N> times (<X>% of lines), which may indicate hallucination.`

   ### 9c. Word density sanity check
   - Calculate expected word count based on duration: typical speech is 100-170 words per minute.
   - `expected_min = duration_minutes * 80` (allowing for pauses/silence)
   - `expected_max = duration_minutes * 200`
   - If actual word count is below `expected_min`: flag as "suspiciously low — may indicate failed transcription or mostly silent recording."
   - If actual word count is above `expected_max`: flag as "suspiciously high — may indicate hallucinated content."

   ### 9d. Trailing garbage detection
   - Take the last 20% of transcript lines.
   - Count unique normalized lines in that segment vs total lines in that segment.
   - If the unique ratio is below 0.3 (i.e., fewer than 30% of lines are unique), the tail is likely hallucinated.
   - Truncate from the point where repetition begins and insert: `[... trailing hallucination detected and truncated — last ~N lines removed ...]`

   ### 9e. Cross-reference with silence map
   - Using the silence timestamps from step 4 and the SRT timestamps from whisper output, check if transcript segments that fall within detected silence windows contain suspicious content (repetitive phrases, off-topic text).
   - If found, insert a marker: `[... segment during detected silence — content may be hallucinated ...]`

   ### 9f. Compute quality score
   Based on the checks above, assign a quality rating:
   - **High**: No hallucinations detected, word density within expected range, no trailing garbage.
   - **Medium**: Minor warnings (e.g., word density slightly outside range, or a few repeated phrases but below thresholds).
   - **Low**: One or more hallucination patterns detected, content was truncated, or word density is significantly off.

   Include this rating in the transcript and summary metadata.

10. **Post-processing: Dictionary corrections**
    - Check if `transcribe-output/transcription_dictionary.md` exists in the current project.
    - If it exists, read it. The file format is a simple Markdown table:
      ```markdown
      | Whisper Output | Correct Term |
      |----------------|--------------|
      | widen | Wyden |
      | soar | SOR |
      | og | OG |
      | ng | NG |
      | luke b | Luka B |
      | look b | Luka B |
      | cassay | Caseis |
      ```
    - Apply case-insensitive whole-word replacements to the transcript text. Be careful not to replace partial words (e.g., "soaring" should not become "SORing").
    - If the dictionary file does not exist, skip this step. On the first run in a new project, create the file with an empty template and tell the user they can populate it for future runs:
      ```markdown
      # Transcription Dictionary
      Add common misrecognitions below. These corrections are applied automatically during transcription.

      | Whisper Output | Correct Term |
      |----------------|--------------|
      | | |
      ```

11. **Write the transcript Markdown file** to `transcribe-output/<MMDDYYYY>/Transcripts/<name>_transcript.md`:
    ```markdown
    ---
    source: <original filename>
    meeting_date: <meeting date extracted from filename, in MMDDYYYY>
    transcribed_on: <today's date in MMDDYYYY>
    duration: <duration from ffprobe, e.g. "32 min 14 sec">
    model: whisper.cpp medium
    language: en
    quality: <High|Medium|Low>
    dictionary_applied: <true|false>
    ---

    # Transcript: <meeting name derived from filename>

    > Summary: [<name>_summary.md](../<name>_summary.md)
    > Quality: **<High|Medium|Low>** <optional: brief reason if not High>

    <transcript content with hallucinations removed and dictionary corrections applied>
    ```

12. **Write the timestamped transcript** to `transcribe-output/<MMDDYYYY>/Transcripts/<name>_transcript_timestamped.md` by reading the `.srt` file and converting it to Markdown format:
    ```markdown
    ---
    source: <original filename>
    meeting_date: <meeting date>
    transcribed_on: <today's date>
    duration: <duration>
    model: whisper.cpp medium
    format: timestamped (from SRT)
    quality: <High|Medium|Low>
    ---

    # Timestamped Transcript: <meeting name>

    **[00:00:00]** First segment of speech...

    **[00:00:15]** Next segment of speech...
    ```
    Apply the same hallucination truncation and dictionary corrections to this file.

13. **Generate a Meeting Summary** by reading the full (cleaned) transcript and creating a structured Markdown document at `transcribe-output/<MMDDYYYY>/<name>_summary.md`. When referencing key points, include approximate timestamps from the SRT data so the user can locate them in the recording:

    ```markdown
    # Meeting Summary: <meeting name>

    | Field | Value |
    |-------|-------|
    | **Meeting Date** | <meeting date from filename or today> |
    | **Transcribed On** | <today's date> |
    | **Duration** | <duration> |
    | **Source File** | <original filename> |
    | **Transcript** | [<name>_transcript.md](Transcripts/<name>_transcript.md) |
    | **Timestamped Transcript** | [<name>_transcript_timestamped.md](Transcripts/<name>_transcript_timestamped.md) |
    | **Quality** | <High\|Medium\|Low> |
    | **Audio Summary** | [<name>_summary.wav](<name>_summary.wav) *(if generated)* |

    ## Overview
    <2-3 sentence summary of what the meeting was about>

    ## Participants
    <List of participants identified from the conversation>

    ## Key Discussion Points
    <Bulleted list of major topics discussed, organized thematically. Include approximate timestamps.>
    - **<Topic>** (~MM:SS) — <brief description>

    ## Decisions Made
    <Bulleted list of explicit decisions or agreements reached during the meeting, with timestamps. If no clear decisions were made, state "No explicit decisions were recorded.">
    - <decision> (~MM:SS)

    ## Key Takeaways
    <Numbered list of the most important conclusions, insights, or implications>

    ## Follow-up Items / Action Items
    <Bulleted checklist of action items with owners, deadlines, and timestamps where identifiable>
    - [ ] <action item> — *Owner: <name if known>* — *Due: <deadline if mentioned>* (~MM:SS)

    ## Open Questions
    <Bulleted list of unresolved questions or topics that need further discussion>

    ## Additional Notes
    <Any other relevant context, risks mentioned, dependencies, or constraints>
    ```

14. **Audio summary generation (optional)** — Generate a spoken audio version of the meeting summary using Piper text-to-speech.

    **Trigger logic**:
    - If `--audio` flag is present in `$ARGUMENTS`: generate the audio summary without asking.
    - If `--audio` flag is NOT present: ask the user — "Would you like an audio summary generated?" If the user declines or does not respond, skip this step entirely.

    **Pre-flight check**: Verify `~/.local/bin/piper` exists and the voice model `~/.local/share/piper-voices/en_US-amy-medium.onnx` is present. If either is missing, report the error and installation instructions (see Error Handling) and skip audio generation — do not fail the entire transcription.

    **Text preparation**: Extract a narration-friendly version of the summary. Strip Markdown formatting (headers, table syntax, bullet markers, checkboxes, links, bold/italic markers). Keep the content structure readable as spoken text — for example, convert "## Key Discussion Points" to "Key Discussion Points." and bullet items to natural sentences. Remove the metadata table entirely. The goal is text that sounds natural when read aloud, not a literal reading of Markdown syntax.

    **Generate audio**:
    ```bash
    echo "<prepared_text>" | ~/.local/bin/piper \
      --model ~/.local/share/piper-voices/en_US-amy-medium.onnx \
      --output_file "transcribe-output/<MMDDYYYY>/<name>_summary.wav"
    ```

    **Verify output**: Confirm the WAV file was created and is non-empty. If generation fails, warn the user but do not fail the overall transcription.

    **Update the summary Markdown**: Add the `Audio Summary` row to the metadata table (see template in step 13) only if the audio file was successfully generated.

15. **Clean up** all temporary files in `/tmp/` (WAV files, `.txt` output, `.srt` output). **IMPORTANT: Do NOT clean up temp files until ALL output files (transcript, timestamped transcript, summary, and audio summary if requested) have been fully written and verified to exist on disk. If using background agents to write files, wait for all agents to complete before deleting temp files.**

16. **Report results** to the user:
    - File locations for transcript, timestamped transcript, summary, and audio summary (if generated)
    - Word count and duration
    - Quality rating with explanation
    - Any hallucination warnings with details on what was detected and truncated
    - Number of dictionary corrections applied (if any)
    - Audio summary status (generated, skipped, or failed with reason)
    - Any other issues encountered

## Multiple files

If multiple files are provided, process them in parallel (parallel ffmpeg conversions, parallel whisper-cli runs). Generate separate transcript and summary files for each, unless the user indicates they belong to the same meeting.

## Filename sanitization

Replace spaces, ampersands, parentheses, and other special characters with underscores. Remove leading/trailing underscores. Collapse consecutive underscores into one. Strip file extensions before sanitizing.

Examples:
- `Discovery RFQ-20260324_115957UTC-Meeting Recording.mp4` → `Discovery_RFQ-20260324_115957UTC-Meeting_Recording`
- `Alice and Bob & Charlie Catch up-20260324_110238-Meeting Recording.mp4` → `Alice_and_Bob_Charlie_Catch_up-20260324_110238-Meeting_Recording`

## Error handling

- If `whisper-cli` is not found: tell the user to install it with `brew install whisper-cpp`
- If the model file is missing: tell the user to download it with:
  ```bash
  mkdir -p ~/.claude/models && curl -L -o ~/.claude/models/ggml-medium.bin "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin"
  ```
- If `ffmpeg` or `ffprobe` is not found: tell the user to install with `brew install ffmpeg`
- If the input file doesn't exist or is unreadable: report the error clearly
- If transcription produces empty output: report the error and suggest checking the audio quality or trying a different format
- If `~/.local/bin/piper` is not found: tell the user to install it with:
  ```bash
  python3 -m venv ~/.local/share/piper-venv && source ~/.local/share/piper-venv/bin/activate && pip install piper-tts
  ```
  Then create the wrapper script:
  ```bash
  printf '#!/bin/zsh\nexec ~/.local/share/piper-venv/bin/piper "$@"\n' > ~/.local/bin/piper && chmod +x ~/.local/bin/piper
  ```
- If the Piper voice model is missing: tell the user to download it with:
  ```bash
  mkdir -p ~/.local/share/piper-voices && curl -L -o ~/.local/share/piper-voices/en_US-amy-medium.onnx "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx" && curl -L -o ~/.local/share/piper-voices/en_US-amy-medium.onnx.json "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json"
  ```
- If Piper audio generation fails: warn the user but do NOT fail the overall transcription — the text outputs are the primary deliverable

## Notes

- The medium model provides good accuracy for meetings, conversations, and general speech.
- whisper.cpp is optimized for Apple Silicon and runs significantly faster than Python whisper.
- Sanitize filenames consistently using the rules in the "Filename sanitization" section.
- The meeting date (from filename) and transcription date (today) are tracked separately for accurate record-keeping.
- The transcription dictionary is project-specific. Each project can have its own domain terms. The dictionary is created automatically on first run if it doesn't exist.
- Piper TTS runs locally via onnxruntime — no network calls or API keys needed. The Amy medium voice produces 22050 Hz mono WAV output.
- Audio summary generation is always optional and never blocks the core transcription workflow.
