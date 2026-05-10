{{!--
Template: meeting summary (mode = meeting only).

Required placeholders:
- TITLE: meeting name derived from filename.
- META_TABLE_ROWS: the rendered rows of the metadata table (see structure below).
- OVERVIEW: 2-3 sentence summary of the meeting.
- PARTICIPANTS: bulleted or comma-separated list inferred from the conversation.
- KEY_TAKEAWAYS: numbered list of the most important conclusions / insights.
- DECISIONS: numbered list of explicit decisions with `(~MM:SS)` timestamps. If none, write "No explicit decisions were recorded."
- DISCUSSION_POINTS: bulleted list grouped thematically with `(~MM:SS)` timestamps.
- ACTION_ITEMS: numbered list of follow-ups with owner / deadline / timestamp.
- OPEN_QUESTIONS: numbered list of unresolved threads.
- ADDITIONAL_NOTES: risks, dependencies, constraints, anything else.
- QUICK_SUMMARY_BLOCK: short Slack/Teams-paste block (no tables, no links, no frontmatter).

Style: never use em dashes. Use commas, periods, semicolons, or parentheses.
--}}
# Meeting Summary: {{TITLE}}

| Field | Value |
|-------|-------|
{{META_TABLE_ROWS}}

## Overview
{{OVERVIEW}}

## Participants
{{PARTICIPANTS}}

## Key Takeaways
{{KEY_TAKEAWAYS}}

## Decisions Made
{{DECISIONS}}

## Key Discussion Points
{{DISCUSSION_POINTS}}

## Follow-up Items / Action Items
{{ACTION_ITEMS}}

## Open Questions
{{OPEN_QUESTIONS}}

## Additional Notes
{{ADDITIONAL_NOTES}}

---

## Quick Summary (copy/paste for Slack or Teams)

{{QUICK_SUMMARY_BLOCK}}
