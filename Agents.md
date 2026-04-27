# AGENTS.md

## Project
This is a small Discord music/sound bot.

## Coding rules
- Preserve existing bot behavior unless explicitly asked to change it.
- Keep command handlers small.
- Keep Discord setup, command logic, audio playback, queue state, config, and utilities separated.
- Do not expose secrets or tokens.
- Do not over-engineer the project.
- Prefer clear readable code over clever abstractions.

## Verification
After changes, run available checks:
- npm install if dependencies changed
- npm test if tests exist
- npm run lint if linting exists
- npm start or equivalent startup/import check if possible

## Final response format
Always summarize:
1. What changed
2. Files changed
3. How to run
4. What was tested
5. Any remaining risks
