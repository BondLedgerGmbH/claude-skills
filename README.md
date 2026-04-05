# Claude Skills

A curated collection of skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — Anthropic's official CLI for Claude.

## What are Claude Code Skills?

Skills are reusable instruction sets that extend Claude Code's capabilities. Each skill is a directory containing a `SKILL.md` file (with optional reference files and scripts) that Claude Code auto-discovers from `~/.claude/skills/`.

When you ask Claude Code to perform a task that matches a skill's trigger, it loads the skill's instructions and follows them — giving Claude domain-specific expertise it wouldn't otherwise have.

## Available Skills

| Skill | Description |
|-------|-------------|
| [skill-security-scanner](skills/skill-security-scanner/) | Scans AI skill packages for security risks, vulnerabilities, backdoors, and prompt injection. Acts as a Senior Security Engineer. |
| [yt-transcript](skills/yt-transcript/) | Extracts YouTube video transcripts and produces structured summaries with key takeaways. Handles non-English videos via auto-translation. Outputs markdown + PDF. |
| [portfolio-analyse](skills/portfolio-analyse/) | Analyses a portfolio (IB accounts + off-platform holdings) against a thesis, YouTube video, market scan, or comparison of two views. Runs a 4-subagent pipeline (market research, opportunity scoring, impact analysis, recommendations). |

## Installation

### Install a single skill

Copy the skill directory into your Claude Code skills folder:

```bash
# Clone the repo
git clone https://github.com/BondLedgerGmbH/claude-skills.git /tmp/claude-skills

# Copy the skill you want
cp -r /tmp/claude-skills/skills/skill-security-scanner ~/.claude/skills/

# Clean up
rm -rf /tmp/claude-skills
```

### Install all skills

```bash
git clone https://github.com/BondLedgerGmbH/claude-skills.git /tmp/claude-skills
cp -r /tmp/claude-skills/skills/* ~/.claude/skills/
rm -rf /tmp/claude-skills
```

### Install portfolio-analyse (additional steps)

The portfolio analysis skill uses four subagents that need to be placed in `~/.claude/agents/`:

```bash
git clone https://github.com/BondLedgerGmbH/claude-skills.git /tmp/claude-skills

# Copy the skill
cp -r /tmp/claude-skills/skills/portfolio-analyse ~/.claude/skills/

# Copy the subagents
mkdir -p ~/.claude/agents
cp /tmp/claude-skills/skills/portfolio-analyse/agents/*.md ~/.claude/agents/

# Clean up
rm -rf /tmp/claude-skills
```

Then configure the skill:

1. **Set paths:** Open `~/.claude/skills/portfolio-analyse/SKILL.md` and replace all `[YOUR_PROJECT_DIR]` with the absolute path to your Claude Code project directory (e.g., `/home/user/projects/my-project`)
2. **Set investor profile:** Open `~/.claude/skills/portfolio-analyse/references/investor-context.md` and replace all `[PLACEHOLDER]` values with your actual data (age, location, accounts, holdings, theses)
3. **Configure account names:** The skill references IB accounts by their names in the ib-connect MCP server config. Make sure the account names in `investor-context.md` match those in your `ib-connect` configuration.

The skill will not work without valid paths and will not produce accurate results without a properly configured `investor-context.md`. See the file itself for detailed comments on each section.

**Requirements:**
- [ib-connect](https://github.com/BondLedgerGmbH/mcp) MCP server configured with your IB accounts
- `yt-transcript` skill installed (for YouTube mode)

### Verify installation

```bash
ls ~/.claude/skills/
```

Skills are auto-discovered by Claude Code — no restart or configuration needed.

## Skill Structure

Each skill follows this structure:

```
skill-name/
├── SKILL.md              # Main skill file (YAML frontmatter + instructions)
├── references/           # Optional: detailed reference docs
│   └── *.md
├── scripts/              # Optional: helper scripts
│   └── *.sh
└── docs/                 # Optional: implementation guides, design docs
    └── *.md
```

The `SKILL.md` file must include YAML frontmatter with at minimum:

```yaml
---
name: Skill Name
description: What this skill does
---
```

## Contributing

To add a new skill:

1. Create a directory under `skills/` with a descriptive name (prefix with `skill-`)
2. Add a `SKILL.md` with proper YAML frontmatter and clear instructions
3. Include any reference files or helper scripts the skill needs
4. Update the Available Skills table in this README
5. Open a pull request

## License

MIT
