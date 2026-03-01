# Skill: Security Scanner

Scans AI skill packages (Claude Code, Cursor, Copilot, Gemini CLI, etc.) for security risks, vulnerabilities, backdoors, and prompt injection — like having a Senior Security Engineer review every skill you install.

## What it does

- Runs [skscan](https://skvault.dev/) automated checks (29 rules across 5 threat categories)
- Performs 10 manual deep-analysis passes covering prompt injection, hidden content, secrets, dangerous code, data exfiltration, supply chain risks, persistence mechanisms, file analysis, external references, and anti-scanner evasion
- Detects hidden Unicode characters, homoglyphs, base64 payloads, and file type mismatches
- Produces a structured risk report with CRITICAL/HIGH/MEDIUM/LOW/INFO findings
- Assigns a final verdict: SAFE / CAUTION / UNSAFE / DANGEROUS

## Prerequisites

- [Node.js](https://nodejs.org/) (for skscan)
- [pnpm](https://pnpm.io/) (needed to build skscan from source — the npm package has a known packaging bug)
- macOS or Linux (the unicode check script uses `perl` as fallback on macOS)

## Usage

Ask Claude Code to scan any skill:

```
Scan the skill at ~/.claude/skills/some-skill/ for security issues
```

```
Security audit this skill package: https://github.com/someone/their-skill
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill — audit methodology, skscan integration, report format |
| `references/security-checklist.md` | Detailed patterns across 12 threat categories |
| `scripts/unicode_check.sh` | Automated detection (12 checks, macOS-compatible) |
| `scripts/run_skscan.sh` | skscan wrapper — handles npm packaging bug via source build fallback |
| `docs/IMPLEMENTATION_GUIDE.md` | Full rebuild guide with design decisions and rationale |

## Hardening

This skill was adversarially red-teamed across 3 rounds, identifying ~32 bypass vectors. Key defenses include:

- Anti-manipulation directive preventing scanned content from influencing the auditor
- macOS-compatible unicode detection (perl fallback for missing grep -P)
- Write tool intentionally excluded from allowed tools to prevent escalation
- Safe git clone procedure for repository URLs
- Argument sanitization to prevent injection via skill invocation
