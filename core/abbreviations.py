"""
Expand dense lexicon abbreviations so a screen reader speaks real words.

LSJ-style definitions are full of abbreviations ("indecl.", "q.v.", "Att.",
"sqq.") that are unintelligible when read aloud. This module expands a curated,
verified set on demand. The data lives in ``core/data/abbreviations.json``
(generated/verified separately) with a small built-in fallback so the feature
works even before that file is present.

Expansion is conservative: only exact, period-terminated tokens are replaced,
so ordinary words are never touched.
"""

import json
import os
import re

_DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "abbreviations.json")

# Minimal built-in fallback (the JSON file supersedes/extends this).
_FALLBACK = {
    "indecl.": {"en": "indeclinable", "es": "indeclinable"},
    "pl.": {"en": "plural", "es": "plural"},
    "sg.": {"en": "singular", "es": "singular"},
    "gen.": {"en": "genitive", "es": "genitivo"},
    "dat.": {"en": "dative", "es": "dativo"},
    "acc.": {"en": "accusative", "es": "acusativo"},
    "voc.": {"en": "vocative", "es": "vocativo"},
    "nom.": {"en": "nominative", "es": "nominativo"},
    "masc.": {"en": "masculine", "es": "masculino"},
    "fem.": {"en": "feminine", "es": "femenino"},
    "neut.": {"en": "neuter", "es": "neutro"},
    "aor.": {"en": "aorist", "es": "aoristo"},
    "impf.": {"en": "imperfect", "es": "imperfecto"},
    "fut.": {"en": "future", "es": "futuro"},
    "pf.": {"en": "perfect", "es": "perfecto"},
    "subj.": {"en": "subjunctive", "es": "subjuntivo"},
    "opt.": {"en": "optative", "es": "optativo"},
    "imper.": {"en": "imperative", "es": "imperativo"},
    "part.": {"en": "participle", "es": "participio"},
    "inf.": {"en": "infinitive", "es": "infinitivo"},
    "med.": {"en": "middle", "es": "media"},
    "pass.": {"en": "passive", "es": "pasiva"},
    "Att.": {"en": "Attic", "es": "ático"},
    "Ion.": {"en": "Ionic", "es": "jónico"},
    "Dor.": {"en": "Doric", "es": "dórico"},
    "Ep.": {"en": "Epic", "es": "épico"},
    "q.v.": {"en": "which see", "es": "véase"},
    "cf.": {"en": "compare", "es": "compárese"},
    "sc.": {"en": "namely", "es": "a saber"},
    "v.l.": {"en": "variant reading", "es": "variante textual"},
    "f.l.": {"en": "false reading", "es": "lectura errónea"},
    "sqq.": {"en": "and following", "es": "y siguientes"},
    "esp.": {"en": "especially", "es": "especialmente"},
    "usu.": {"en": "usually", "es": "usualmente"},
    "abs.": {"en": "absolute", "es": "absoluto"},
    "metaph.": {"en": "metaphorically", "es": "metafóricamente"},
    "Lat.": {"en": "Latin", "es": "latín"},
}


def _load():
    table = dict(_FALLBACK)
    try:
        with open(_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Accept either {abbr: {en, es}} or [{abbr, en, es}, ...].
        if isinstance(data, list):
            for e in data:
                if e.get("abbr"):
                    table[e["abbr"]] = {"en": e.get("en", ""), "es": e.get("es", "")}
        elif isinstance(data, dict):
            for k, v in data.items():
                table[k] = v
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return table


_TABLE = _load()
# Longest abbreviations first so "op.cit." wins over "cit.".
_KEYS_SORTED = sorted(_TABLE.keys(), key=len, reverse=True)
_PATTERN = re.compile(
    "(?<![\\w.])(" + "|".join(re.escape(k) for k in _KEYS_SORTED) + ")(?![\\w])"
)


def expand(text, lang="en"):
    """Return *text* with known abbreviations expanded for the given language."""
    if not text:
        return text

    def _sub(m):
        entry = _TABLE.get(m.group(1))
        if not entry:
            return m.group(1)
        return entry.get(lang) or entry.get("en") or m.group(1)

    return _PATTERN.sub(_sub, text)


def lookup(abbr, lang="en"):
    """Return the expansion of a single abbreviation, or None."""
    entry = _TABLE.get(abbr)
    if not entry:
        return None
    return entry.get(lang) or entry.get("en")


def all_entries():
    return _TABLE
