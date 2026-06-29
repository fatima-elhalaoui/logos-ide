# Changelog

All notable changes to Logos IDE are documented here.

## [1.0.0] — 2026

The first complete release. Logos IDE grew from a read‑only prototype into a full
study environment.

### Added
- **Pronunciation engine** with four switchable schemes: Spanish‑style Erasmian
  (default), English/academic Erasmian, Modern Greek and Restored Attic, each
  rendered in Spanish or English orthography for the screen‑reader voice.
- **Fully bilingual** Spanish / English interface, switchable at runtime.
- **Preferences dialog** (language, pronunciation scheme, speech rate, font size,
  auto‑speak, exam mode, dictionary panel).
- **Exam mode** that ethically disables the dictionary, morphology, paradigms and
  notes while keeping writing and reading aloud.
- **Annotations / notes** anchored to text, with view, jump and delete.
- **Vocabulary flashcards** with Leitner spaced repetition, plus CSV and Anki
  export, and a word‑history log.
- **Paradigm generator** for the regular noun declensions, the thematic ‑ω verb,
  and εἰμί.
- **"Describe character"** command that speaks every accent and breathing.
- **On‑demand reading** of word, line, selection and whole document.
- **Lexicon abbreviation expander** (149 entries) for clean speech.
- **Accent‑insensitive dictionary lookup** via a normalised key, with English
  fallback when a Spanish definition is missing.
- **Find / Find next / Go to line**, adjustable font size, and a Greek‑input
  on/off toggle for mixed‑language documents.
- Rotating **logging**, per‑user data directory, a bundled **seed dictionary**,
  a headless **test suite**, and **PyInstaller** packaging.

### Fixed
- Changing the interface language no longer pops up the keyboard‑guide dialog.
- "Not found" lookups now give a clear spoken message instead of failing silently
  (the old missing `error_dict` key).
- The editor no longer self‑voices over the screen reader (no more double speech);
  navigation echo is left to NVDA/JAWS.
- Diacritic composition now validates the result and rejects impossible
  combinations (e.g. a consonant with a circumflex, a Latin letter with an accent).
- The TTS worker survives transient speech errors instead of dying permanently.
- Document‑import cancellation is now cooperative (no unsafe `terminate()`),
  preventing file‑handle leaks.
- Heavy transliteration moved off the GUI thread.
- Windows file paths handled with `os.path.basename` instead of `split('/')`.
- `requirements.txt` is now valid UTF‑8.

### Known limitations
- The shipped full dictionary has empty morphology codes; cursor‑on‑word *parsing*
  requires the optional morphology data pack (see `scripts/import_morphology.py`).
- Spanish definitions are machine‑translated; a regeneration pipeline
  (`scripts/regenerate_spanish.py`) repairs them progressively.
