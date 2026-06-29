"""
Greek text utilities shared across Logos IDE.

Centralises Unicode normalisation so that dictionary lookup, audio and the
editor all agree on what "the same word" means. Ancient Greek is written with
polytonic diacritics (breathings, accents, iota subscript, diaeresis); students
frequently type a word without every mark, so accent-insensitive matching is
essential for the tool to feel responsive.
"""

import unicodedata

# Punctuation that clings to words and should be trimmed before lookup.
WORD_PUNCTUATION = ".,;:?!·()[]{}'\"«»—–…"


def strip_diacritics(text: str) -> str:
    """Return *text* with every combining diacritic removed (keeps base letters)."""
    decomposed = unicodedata.normalize("NFD", text)
    out = [c for c in decomposed if not unicodedata.combining(c)]
    return unicodedata.normalize("NFC", "".join(out))


def normalize_lookup(word: str) -> str:
    """
    Produce the canonical key used for accent-insensitive dictionary lookup.

    Lower-cases, strips surrounding punctuation, removes all diacritics and
    folds final sigma into medial sigma so that "logos" written with or without
    accents and with either sigma form collapses to the same key.
    """
    if not word:
        return ""
    word = word.strip().strip(WORD_PUNCTUATION).strip()
    word = strip_diacritics(word)
    word = word.lower()
    word = word.replace("ς", "σ")  # final sigma -> medial sigma
    return word


def clean_word(word: str) -> str:
    """Trim surrounding punctuation/whitespace but keep diacritics and case."""
    if not word:
        return ""
    return word.strip().strip(WORD_PUNCTUATION).strip()


def has_greek(text: str) -> bool:
    """True if *text* contains at least one Greek letter."""
    for c in text:
        if "GREEK" in unicodedata.name(c, ""):
            return True
    return False


def is_greek_letter(c: str) -> bool:
    return "GREEK" in unicodedata.name(c, "") and unicodedata.category(c).startswith("L")
