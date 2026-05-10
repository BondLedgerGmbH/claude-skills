{{!--
Frontmatter block for source-material mode (transcript, timestamped, article).

Aligns with personal/source-material/README.md.

Required placeholders:
- SOURCE_URL: full URL of the source (YouTube, podcast feed, article, etc.).
- SOURCE_TYPE: youtube | podcast | article | paper | book.
- AUTHOR: channel name, podcast host, article author.
- TITLE: original title of the source.
- CAPTURED: today's date in YYYY-MM-DD.
- TOPIC: matches an existing personal/source-material/transcripts/<topic>/ folder, or a new topic the user approved.
- DURATION: human-readable duration. Empty for non-AV sources.
- QUALITY: High | Medium | Low.
- DICTIONARY_APPLIED: true | false.
- EXTRA_LINES: optional extra YAML lines (e.g., "format: timestamped"). Empty string if none.
--}}
---
source_url: {{SOURCE_URL}}
source_type: {{SOURCE_TYPE}}
author: {{AUTHOR}}
title: {{TITLE}}
captured: {{CAPTURED}}
topic: {{TOPIC}}
duration: {{DURATION}}
model: whisper.cpp medium
language: en
quality: {{QUALITY}}
dictionary_applied: {{DICTIONARY_APPLIED}}
{{EXTRA_LINES}}---
