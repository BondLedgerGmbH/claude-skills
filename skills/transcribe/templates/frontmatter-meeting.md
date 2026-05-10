{{!--
Frontmatter block for meeting mode (transcript, timestamped, summary).

Required placeholders:
- SOURCE: original input filename (basename, no path).
- MEETING_DATE: MMDDYYYY extracted from the filename if a date pattern is present, else today's date.
- TRANSCRIBED_ON: today's date in MMDDYYYY.
- DURATION: human-readable duration, e.g. "32 min 14 sec".
- QUALITY: High | Medium | Low.
- DICTIONARY_APPLIED: true | false.
- EXTRA_LINES: optional extra YAML lines (e.g., "format: timestamped" for timestamped variant). Empty string if none.
--}}
---
source: {{SOURCE}}
meeting_date: {{MEETING_DATE}}
transcribed_on: {{TRANSCRIBED_ON}}
duration: {{DURATION}}
model: whisper.cpp medium
language: en
quality: {{QUALITY}}
dictionary_applied: {{DICTIONARY_APPLIED}}
{{EXTRA_LINES}}---
