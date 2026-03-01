# Claude Skills

A curated collection of skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — Anthropic's official CLI for Claude.

## What are Claude Code Skills?

Skills are reusable instruction sets that extend Claude Code's capabilities. Each skill is a directory containing a `SKILL.md` file (with optional reference files and scripts) that Claude Code auto-discovers from `~/.claude/skills/`.

When you ask Claude Code to perform a task that matches a skill's trigger, it loads the skill's instructions and follows them — giving Claude domain-specific expertise it wouldn't otherwise have.

## Available Skills

| Skill | Description |
|-------|-------------|
| [skill-security-scanner](skills/skill-security-scanner/) | Scans AI skill packages for security risks, vulnerabilities, backdoors, and prompt injection. Acts as a Senior Security Engineer. |

## Installation

### Install a single skill

Copy the skill directory into your Claude Code skills folder:

```bash
# Clone the repo
git clone https://github.com/xjarko123/claude-skills.git /tmp/claude-skills

# Copy the skill you want
cp -r /tmp/claude-skills/skills/skill-security-scanner ~/.claude/skills/

# Clean up
rm -rf /tmp/claude-skills
```

### Install all skills

```bash
git clone https://github.com/xjarko123/claude-skills.git /tmp/claude-skills
cp -r /tmp/claude-skills/skills/* ~/.claude/skills/
rm -rf /tmp/claude-skills
```

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
