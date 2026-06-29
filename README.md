# Logos IDE

**An accessible Ancient & Koine Greek study environment for blind and low‑vision students.**

🇬🇧 English · [🇪🇸 Español](README.es.md)

Logos IDE lets a blind student **read, write, hear and study** ancient Greek
entirely from the keyboard, with full **NVDA** and **JAWS** support. It aims to
be for Greek what [EDICO](https://www.once.es) is for science: not a demo, but a
complete daily study tool — and a fair, ethical companion in the exam room.

---

## Why this exists

Studying Greek is unusually hard without sight:

- **Polytonic script** stacks breathings, accents, iota subscripts and diaereses
  onto each vowel. Sighted students glance at them; a screen reader normally just
  says "alpha" and the diacritics are lost.
- **System voices cannot pronounce Greek.** A Spanish or English TTS voice reads
  Greek letters by name or mangles them.
- **Paper dictionaries and morphology tables are visual** and effectively
  inaccessible.

Logos IDE solves each of these directly.

## What it does

- **Type Greek from a Latin keyboard.** `a`→α, `q`→θ, `w`→ω. Add accents and
  breathings *after* the vowel: `a)/` → ἄ, `w|` → ῳ. Invalid combinations are
  rejected so you never produce malformed Greek.
- **Hear correct pronunciation.** A transliteration engine renders Greek into a
  phonetic spelling your screen‑reader voice can actually say, in four switchable
  schemes: **Spanish‑style Erasmian** (default), **English/academic Erasmian**,
  **Modern Greek**, and **Restored Attic**.
- **Instant dictionary + morphology.** Put the cursor on a word and its
  Liddell‑Scott‑Jones entry appears (575,000+ forms). Lookup is
  accent‑insensitive, abbreviations are expanded for clean speech ("indecl." →
  "indeclinable"), and parsing codes become plain language.
- **"Describe this character"** speaks every accent and breathing on the current
  glyph — `Ctrl+;` → "alpha with smooth breathing and acute accent".
- **Read on demand**: current word, line, selection, or the whole document, with
  no redundant double‑speech over your screen reader.
- **Study tools**: notes/annotations, vocabulary **flashcards with spaced
  repetition**, Anki/CSV export, word history, and on‑demand **paradigm tables**
  for regular declensions and conjugations.
- **Import** Greek texts from PDF, EPUB or plain text.
- **Exam mode** disables the dictionary, morphology and notes so the same tool a
  student writes and reads with every day can be used fairly in an assessment.
- **Fully bilingual** Spanish / English interface, switchable at any time.

See the **[User Guide](docs/USER_GUIDE.en.md)** for the complete keyboard reference.

## Accessibility

- Designed and tested for **NVDA** and **JAWS** on Windows.
- 100% keyboard operable; no mouse or numpad required.
- Speaks through your *own* screen‑reader voice and rate via `accessible_output2`,
  with an offline `pyttsx3` fallback.
- Deliberately **avoids redundant speech** — the app never echoes what your
  screen reader already says.
- Adjustable editor font size for low‑vision users.

## Installation

### Option A — run from source

Requires **Python 3.11+**.

```bash
git clone https://github.com/<your-account>/logos-ide.git
cd logos-ide
python -m venv venv
venv\Scripts\activate            # Windows
pip install -r requirements.txt
python run_logos.py
```

On first launch the app uses a small **built‑in starter dictionary** so it works
immediately. For the full 575k‑form dictionary, install the **data pack** (see
below).

### Option B — packaged app (no Python needed)

Download the latest release for your platform from the
[Releases page](../../releases), unzip it and run `LogosIDE`. The full dictionary
is bundled.

### The full dictionary data pack

The complete dictionary database is ~300 MB — too large for the git repository.
Download `logos_dict.db` from the [Releases page](../../releases) and place it in
your user data folder:

- **Windows:** `%LOCALAPPDATA%\LogosIDE\LogosIDE\logos_dict.db`

or point the `LOGOS_DB` environment variable at it. You can also rebuild it from
source with `scripts/build_database.py` (see [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md)).

## Quick start

1. Launch the app. The cursor starts in the Greek editor.
2. Type `a)nqrwpos` → ἄνθρωπος.
3. Press **F8** to hear the dictionary entry, or **F6** to read the dictionary panel.
4. Press **Ctrl+R** to hear a selection; **Ctrl+;** to describe a character.
5. Press **F1** at any time for the full typing guide.

## Project status

Version **1.0.0** — feature‑complete and ready for testing. Feedback from blind
and sighted Greek students alike is very welcome; please open an
[issue](../../issues).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Good first issues are labelled
`good first issue`.

## License

Code: **MIT** (see [LICENSE](LICENSE)).
Dictionary data: derived from the Perseus Digital Library LSJ lexicon and
morphology, **CC BY‑SA 3.0** — see [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md).
