# AGENTS.md

## Project Role

This repository is the measurement-stage predecessor of the larger K1 velocity compensation and navigation safety project.

## Language Rules

- README.md must be Chinese-first.
- English technical terms may be included in parentheses.
- README.en.md may contain the English version.
- Keep README.md and README.en.md technically consistent.

## Development Rules

1. Do not implement real robot movement before command topics are verified.
2. Do not hard-code unverified ROS2 topic names.
3. Do not commit secrets, tokens, SSH keys, robot passwords, or `.env` files.
4. Do not mix measurement logic with compensation logic.
5. Keep measurement outputs compatible with downstream compensation modules.
6. Prefer small, testable Python functions.
7. Add or update tests when changing metric calculation logic.
8. Keep README.md Chinese-first.

## Safety Rules

Any file that may send movement commands must include:

- manual confirmation
- velocity limit check
- emergency-stop reminder
- dry-run mode by default

## Review Guidelines

Flag the following as high-priority issues:

- code that can move the robot without explicit safety confirmation
- unverified ROS2 topic names treated as final
- missing tests for metrics
- schema-breaking changes to processed_environment_profile.json
- secrets or local environment files committed to Git
- README.md becoming English-first
