{{!--
Template: timestamped transcript file (works for both modes).

Required placeholders:
- FRONTMATTER_BLOCK: full YAML frontmatter block; include `format: timestamped` field.
- TITLE: human-readable title.
- SIBLING_LINKS_BLOCK: blockquote lines linking the plain transcript and the article/summary sibling.
- TIMESTAMPED_BODY: body where each cue from the SRT is rendered as `**[HH:MM:SS]** segment text` separated by blank lines.

Apply hallucination truncation and dictionary corrections to TIMESTAMPED_BODY too.
--}}
{{FRONTMATTER_BLOCK}}

# Timestamped Transcript: {{TITLE}}

{{SIBLING_LINKS_BLOCK}}

{{TIMESTAMPED_BODY}}
