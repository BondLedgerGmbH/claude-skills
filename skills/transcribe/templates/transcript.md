{{!--
Template: plain transcript file (works for both meeting and source-material modes).

Required placeholders:
- FRONTMATTER_BLOCK: full YAML frontmatter block including the leading and trailing `---` lines (mode-specific; see frontmatter-meeting.md / frontmatter-source-material.md).
- TITLE: human-readable title (meeting name or video/podcast title).
- SOURCE_LINE: short line identifying the source (e.g. "Source: <url>" for source-material; "Source File: <filename>" for meeting).
- SIBLING_LINKS_BLOCK: blockquote lines linking siblings. For meeting mode, include `Summary:` link. For source-material mode, include `Article:` link. Always include `Timestamped:` link if a timestamped sibling exists.
- QUALITY: High | Medium | Low.
- QUALITY_NOTE: optional one-line reason if not High; otherwise empty string.
- BODY: cleaned transcript content (paragraphs preserved; hallucinations removed; dictionary corrections applied).
--}}
{{FRONTMATTER_BLOCK}}

# Transcript: {{TITLE}}

> {{SOURCE_LINE}}
{{SIBLING_LINKS_BLOCK}}
> Quality: **{{QUALITY}}**{{QUALITY_NOTE}}

{{BODY}}
