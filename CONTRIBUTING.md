# Contributing to Logos IDE

Thank you for helping make Greek study accessible! Contributions of every kind
are welcome — code, documentation, translations, linguistic corrections, and
especially **testing reports from blind and low‑vision students**.

## Reporting bugs and ideas

Open an [issue](../../issues) and include:

- What you were doing and what happened (and what you expected).
- Your operating system, screen reader (NVDA / JAWS) and version.
- Anything from the log file (`%LOCALAPPDATA%\LogosIDE\Logs\logos.log` on Windows).

Accessibility problems are treated as high priority.

## Setting up a development environment

```bash
git clone https://github.com/<your-account>/logos-ide.git
cd logos-ide
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run_logos.py
```

## Running the tests

The logic layer has headless tests that need no display:

```bash
python tests/test_logic.py
# or, if you have pytest:
python -m pytest tests
```

Please run them before opening a pull request, and add a test for any logic you
change.

## Project layout

```
core/    pure logic: pronunciation, normalisation, paradigms, settings, i18n…
db/      dictionary schema/lookup and the user study store
ui/      PyQt6 widgets and dialogs
scripts/ data-pipeline tools (DB build, Spanish regeneration, morphology import)
docs/    user guides and data documentation
tests/   headless logic tests
```

## Accessibility guidelines (please read)

This project lives or dies by its accessibility. When you add UI:

1. **Never duplicate the screen reader.** Do not speak text the screen reader
   already announces. On‑demand reading commands are fine; automatic echo is not.
2. Every interactive widget needs a meaningful `setAccessibleName`.
3. Everything must be reachable and operable **from the keyboard alone** — no
   mouse, no numpad.
4. Set a sensible initial focus in every dialog, and make `Esc`/Close work.
5. Keep both the English and Spanish string tables (`core/i18n.py`) in sync; no
   hard‑coded user‑facing strings.

## Style

- Follow the surrounding code; keep functions small and documented.
- User‑facing strings go through `core/i18n.py`, never inline.

## Good first issues

Look for issues labelled `good first issue`. Adding a missing lexicon
abbreviation, a paradigm pattern, or a Spanish string correction is a great way
to start.
