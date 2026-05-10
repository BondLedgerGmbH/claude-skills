{{!--
Template: article-style write-up for a public video / podcast / educational source (mode = source-material).

This is NOT a meeting summary. Do NOT include participants, decisions, or action items. The output should read like a thoughtful blog post that reflects the source content, written so a reader can absorb it without watching the video.

Required placeholders:
- FRONTMATTER_BLOCK: full YAML frontmatter (see frontmatter-source-material.md).
- ARTICLE_TITLE: an article-style title that captures the topic. Often distinct from the raw video title (e.g. video "Stanford CS230 | Lecture 8: Agents, Prompts, and RAG" → article "Beyond the Base Model: A Practical Stack for Building LLM Applications").
- ATTRIBUTION_LINE: italicized one-liner crediting the original creator and linking to the source URL plus the sibling transcript.
- OVERVIEW: 2-4 sentence framing of what the source teaches and why it matters.
- SECTIONS: 3-6 thematic sections, each with a meaningful heading and substantive prose. Multiple paragraphs each. Include specific examples / numbers / names from the source.
- KEY_TAKEAWAYS: 4-7 bulleted insights a reader should walk away with.
- OPEN_THREADS: optional list of questions the source did not fully address. Omit the section if not applicable.

Writing rules (strict):
- Never use em dashes. Use commas, periods, semicolons, parentheses.
- Substance over verbosity. Every paragraph should carry information.
- Write like a domain expert summarizing for thoughtful readers, not like a transcript paraphrase.
- Avoid AI-generated patterns: excessive hedging, hollow summarization, repetitive structure.
- The article should stand on its own.
--}}
{{FRONTMATTER_BLOCK}}

# {{ARTICLE_TITLE}}

{{ATTRIBUTION_LINE}}

## Overview

{{OVERVIEW}}

{{SECTIONS}}

## Key Takeaways

{{KEY_TAKEAWAYS}}

## Open Threads

{{OPEN_THREADS}}
