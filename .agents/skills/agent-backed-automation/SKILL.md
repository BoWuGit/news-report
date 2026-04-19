---
name: agent-backed-automation
description: "Runs high-judgment skill steps through a user-provided agent backend such as Codex or Claude Code, with a deterministic local fallback. Use when a workflow should prefer the user's own agent mechanism for better cross-platform portability instead of hard-coding OS-specific scripts."
---

# Agent-Backed Automation

Use this skill when a step is better expressed as "ask an agent to do this" than as a platform-specific script.

The goal is portability:

- Keep `SKILL.md` focused on workflow and decision rules
- Use a small adapter script to normalize input and output
- Let the user supply the real backend command from their environment
- Preserve a deterministic local fallback for offline or unsupported setups

## When To Use

Prefer this pattern for:

- summarization
- drafting notifications or messages
- classification and light reasoning
- transforming loosely structured text into a fixed schema

Do not rely on an external agent for:

- file mutations that must be exact
- parsing where a local parser is available
- validation that must be deterministic
- safety-critical gating

## Contract First

Before calling any backend, define:

1. Input artifact
   Usually a text or JSON file.
2. Output artifact
   Usually JSON or Markdown written to a file.
3. Fallback behavior
   A deterministic local implementation if no backend is available.

This skill ships with [`scripts/run_agent_backend.py`](/Users/bowu/Downloads/news-report/scripts/run_agent_backend.py), which enforces that pattern.

## Backend Selection

The runner supports:

- `auto`: choose the first configured backend
- `codex`: use `CODEX_AGENT_CMD`
- `claude`: use `CLAUDE_AGENT_CMD`
- `fallback`: skip external agents

Important: do not hard-code vendor CLI flags in the skill itself.

Instead, require the user environment to expose one of these variables:

```bash
export CODEX_AGENT_CMD='codex exec --stdin'
export CLAUDE_AGENT_CMD='claude -p'
```

The exact command is environment-specific. The runner passes the prompt on stdin and expects text on stdout.

## Workflow

### Step 1: Prepare a stable prompt

Write the task input to a file. Keep the prompt explicit about:

- objective
- output format
- hard constraints
- what not to do

If the output must be machine-readable, say so plainly and require pure JSON or Markdown with no wrapper text.

### Step 2: Call the adapter

Example:

```bash
python3 scripts/run_agent_backend.py \
  --backend auto \
  --input /tmp/task-prompt.txt \
  --output /tmp/result.md \
  --fallback-text 'Manual attention required.'
```

### Step 3: Validate locally

After the adapter returns:

- verify the output file exists
- validate JSON if JSON was requested
- reject malformed output instead of silently accepting it

### Step 4: Continue with deterministic steps

Use the agent for judgment-heavy work, then return to normal scripts for formatting, validation, persistence, and side effects.

## Notification Example

For a portable "system notification" style step:

1. Ask the agent to draft the short notification text
2. Store the message in a file
3. Use a platform-specific notifier only at the very edge, or surface the text back to the host UI

This separates message generation from OS integration. The message-generation part becomes portable, while notification delivery can be swapped per platform.

## Fallback Guidance

If no configured backend is available:

- use `fallback`
- emit a short deterministic message
- continue the workflow if possible

The workflow should degrade gracefully rather than failing just because a preferred agent backend is absent.
