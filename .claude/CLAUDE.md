# Workflow Guidelines

Additional guidelines for working in this repository.

## Core Principles

- Never use mock data, results, or workarounds - implement complete working code
- Implement tests after every checkpoint and verify all tests pass
- Only create progress files and project plans in `.claude_plans/`
- Update `projectplan.md` after completing each stage
- Keep files organized - regularly clean up orphan or unneeded files

## File Boundaries

**Safe to modify**: `src/`, `frontend/src/`, `tests/`, `frontend/src/components/`

**Never modify**: `node_modules/`, `.git/`, `dist/`, `build/`, `venv/`, `.env` files

## Code Style

**Python**: snake_case variables/functions, PascalCase classes, SCREAMING_SNAKE_CASE constants

**TypeScript**: camelCase variables/functions, PascalCase classes/components, SCREAMING_SNAKE_CASE constants
