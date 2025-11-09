# Contributing to Scriptly

Thanks for your interest in contributing! This document contains practical guidelines for contributing code, themes, documentation, and bug reports.

## Quick start

1. Fork the repository on GitHub.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Make your changes and commit frequently with clear messages.
4. Push the branch to your fork and open a Pull Request against the `main` branch.

## Coding guidelines

- Follow consistent style. We recommend `black` for formatting and `flake8` for lint checks.
- Write readable, well-commented code. Prefer small, focused commits.
- Keep public APIs stable; if you change a public function or class, update the README and any docs.

## Theme contributions

We encourage theme submissions. Please follow these steps when adding a theme:

1. Add a `*.qss` file under `src/core/themes/`.
2. Include a companion `*.json` with color hints for better editor integration. The JSON file is optional but recommended. See `src/core/themes/dark.json` and `modern_dark.json` as examples.
3. Include a short descriptive comment at the top of the QSS file describing the theme.
4. Test the theme locally by running the app.

When opening a PR for a theme:

- Keep the theme self-contained (no external images, unless added to `src/core/themes/` and referenced relatively).
- Keep the QSS focused on Qt widgets. Avoid heavy editor token styling in QSS — use the JSON to give color hints instead.

## Pull request checklist

- [ ] Tests (if applicable) and/or manual verification
- [ ] Code formatted with `black`
- [ ] No obvious lint errors (`flake8`)
- [ ] Documentation updated (README, docs, or CHANGELOG)
- [ ] If adding a theme: include JSON color hints and a short description in the QSS header

## Reporting issues

Please open a GitHub issue with:

- A short, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs or tracebacks (if any)

## Licensing and attribution

When you contribute, by default your contribution will be under the project's license (please ensure a `LICENSE` file is present in the repo). If you include third-party assets (icons, images, etc.), ensure they are compatible with the project's license and add attribution in your PR.

---

If you'd like, I can add a small `scripts/preview_theme.py` helper and a `Makefile` target to preview themes quickly — say the word and I'll add them.