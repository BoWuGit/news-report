# gstack

Use the /browse skill from gstack for all web browsing. Never use mcp__claude-in-chrome__* tools.

If gstack skills aren't working, run `cd .claude/skills/gstack && ./setup` to build the binary and register skills.

## Available Skills

- /office-hours — Brainstorm and validate ideas
- /plan-ceo-review — CEO/founder-mode plan review
- /plan-eng-review — Engineering plan review
- /plan-design-review — Design plan review
- /design-consultation — Create a design system
- /design-shotgun — Explore design variants
- /design-html — Finalize designs into production HTML
- /review — Pre-landing PR review
- /ship — Ship workflow (test, commit, PR)
- /land-and-deploy — Merge PR and deploy
- /canary — Post-deploy monitoring
- /benchmark — Performance regression detection
- /browse — Headless browser for QA and testing
- /connect-chrome — Launch real Chrome with Side Panel
- /qa — QA test and fix bugs
- /qa-only — QA report only (no fixes)
- /design-review — Visual QA and polish
- /setup-browser-cookies — Import cookies for auth
- /setup-deploy — Configure deployment
- /retro — Weekly engineering retrospective
- /investigate — Systematic debugging
- /document-release — Post-ship docs update
- /codex — OpenAI Codex second opinion
- /cso — Security audit
- /autoplan — Run all reviews automatically
- /careful — Safety guardrails for destructive commands
- /freeze — Restrict edits to a directory
- /guard — Full safety mode (careful + freeze)
- /unfreeze — Clear freeze boundary
- /gstack-upgrade — Upgrade gstack
- /learn — Manage project learnings

## Skill routing

When the user's request matches an available skill, ALWAYS invoke it using the Skill
tool as your FIRST action. Do NOT answer directly, do NOT use other tools first.
The skill has specialized workflows that produce better results than ad-hoc answers.

Key routing rules:
- Product ideas, "is this worth building", brainstorming → invoke office-hours
- Bugs, errors, "why is this broken", 500 errors → invoke investigate
- Ship, deploy, push, create PR → invoke ship
- QA, test the site, find bugs → invoke qa
- Code review, check my diff → invoke review
- Update docs after shipping → invoke document-release
- Weekly retro → invoke retro
- Design system, brand → invoke design-consultation
- Visual audit, design polish → invoke design-review
- Architecture review → invoke plan-eng-review
