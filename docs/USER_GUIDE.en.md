# Logos IDE — User Guide

This guide explains everything Logos IDE can do and every keyboard command.
It is written to be read comfortably with a screen reader.

## 1. The basics

When you open Logos IDE the cursor is in the **Greek editor**. Anything you type
is converted from Latin letters into Greek. To the right is the **Dictionary &
Morphology** panel, and there is a menu bar with File, Edit, View, Greek, Audio,
Study, Settings and Help menus.

Switch the whole interface between Spanish and English at any time from
**Settings → Language**, or in Preferences (`Ctrl+,`).

## 2. Writing Greek

Type the Latin letter that matches each Greek letter:

| Type | Get | Type | Get | Type | Get |
|------|-----|------|-----|------|-----|
| a | α | b | β | g | γ |
| d | δ | e | ε | z | ζ |
| h | η | q | θ | i | ι |
| k | κ | l | λ | m | μ |
| n | ν | c | ξ | o | ο |
| p | π | r | ρ | s | σ |
| t | τ | u | υ | f | φ |
| x | χ | y | ψ | w | ω |

- `v` gives the final sigma **ς**. A medial **σ** at the end of a word also
  becomes **ς** automatically when you press space or punctuation.
- A capital Latin letter gives a capital Greek letter (`A` → Α).
- `:` gives the Greek high dot **·** (ano teleia).

### Accents and breathings

Type the modifier **immediately after** the vowel. Modifiers combine.

| Key | Mark | Example |
|-----|------|---------|
| `/` | acute | `a/` → ά |
| `\` | grave | `a\` → ὰ |
| `=` | circumflex | `a=` → ᾶ |
| `)` | smooth breathing | `a)` → ἀ |
| `(` | rough breathing | `a(` → ἁ |
| `\|` | iota subscript | `a\|` → ᾳ |
| `+` | diaeresis | `i+` → ϊ |

Combine them in any order: `a(/` → ἅ, `w|` → ῳ, `h=|` → ῇ. If a combination is
not a real Greek character (for example a consonant with a circumflex), Logos IDE
refuses it instead of producing a broken glyph.

### Greek input on/off

Press **`Ctrl+G`** to turn Greek conversion off, so you can type Spanish or
English notes in the same document, and on again to resume Greek.

## 3. Hearing your text

Your screen reader reads the editor normally as you move around. For correct
ancient pronunciation, use these commands:

| Command | Key |
|---------|-----|
| Read the selected text | `Ctrl+R` |
| Read the current word | `Ctrl+Shift+W` |
| Read the current line | `Ctrl+Shift+L` |
| Read the whole document | `Ctrl+Shift+D` |
| Describe the current character (its accents) | `Ctrl+;` |
| Read the dictionary entry of the current word | `F8` |
| Stop speech | `Ctrl+Space` |

**Pronunciation scheme.** Choose Spanish‑style Erasmian, English Erasmian, Modern
Greek or Restored Attic in **Audio → Pronunciation Scheme** or Preferences. The
spoken pronunciation uses your screen reader's own voice.

By default Logos IDE does **not** speak each letter as you type — your screen
reader already does. If you prefer the app to read each finished Greek word, turn
on **Audio → Speak Greek As I Type**.

## 4. Dictionary and morphology

Move the cursor onto any Greek word and its entry loads automatically into the
Dictionary panel (press **`F6`** to jump there and read it, **`F5`** to return to
the editor). Or press **`F8`** to hear the entry spoken without leaving the editor.

- Lookup ignores accents, so you find a word even if you have not typed every mark.
- Lexicon abbreviations are expanded for clear speech.
- When a word has several possible parses, each is listed as a separate result.

> The built‑in starter dictionary covers high‑frequency vocabulary. Install the
> full data pack (see the README) for the complete 575,000‑form lexicon.

## 5. Study tools

| Tool | How |
|------|-----|
| Add a note to selected text | `Ctrl+Shift+N` |
| View / jump to / delete notes | Study → View Notes |
| Add the current word to flashcards | `Ctrl+D` |
| Review flashcards (spaced repetition) | `Ctrl+Shift+R` |
| Manage / delete flashcards | Study → Manage Flashcards |
| Export flashcards to CSV or Anki | Study → Export… |
| Word history | Study → Word History |
| Show the paradigm of the current word | `Ctrl+Shift+P` |

**Flashcards** use a Leitner schedule: cards you know come back less often, cards
you miss come back sooner. In review, press **Show Answer**, then **I knew it** or
**I missed it**.

**Paradigms** generate the regular declension or conjugation of a word (the three
noun declensions, the regular ‑ω verb, and εἰμί). The dialog is a tree you can
arrow through form by form.

## 6. Exam mode

**Settings → Exam Mode** (`Ctrl+Shift+E`) disables the dictionary, morphology,
paradigms and notes, while keeping writing and reading‑aloud of your own text.
This lets you use the same familiar editor in an assessment without any look‑up
aid — the honest, EDICO‑style way to take an exam.

## 7. Files and documents

| Action | Key |
|--------|-----|
| New tab | `Ctrl+N` |
| Open a text file | `Ctrl+O` |
| Save / Save As | `Ctrl+S` / `Ctrl+Shift+S` |
| Import a PDF / EPUB / text document | `Ctrl+I` |
| Close the current tab | `Ctrl+W` |
| Next / previous tab | `Ctrl+Tab` / `Ctrl+Shift+Tab` |
| Find / Find next | `Ctrl+F` / `F3` |
| Go to line | `Ctrl+L` |
| Quit | `Ctrl+Q` |

## 8. View and comfort

| Action | Key |
|--------|-----|
| Increase font size | `Ctrl+=` |
| Decrease font size | `Ctrl+-` |
| Show/hide dictionary panel | `F4` |
| Focus editor | `F5` |
| Focus dictionary | `F6` |
| Keyboard guide | `F1` |

## 9. Where your data lives

Settings, flashcards, notes and logs are stored in your user data folder
(`%LOCALAPPDATA%\LogosIDE` on Windows), so they are kept safe across updates.

## 10. Getting help

Press **`F1`** for the typing guide, or open **Help → User Guide**. To report a
problem or suggest a feature, open an issue on the project's GitHub page.
