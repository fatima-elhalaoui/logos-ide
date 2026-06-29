"""
Pronunciation engine for Logos IDE.

System text-to-speech voices (read through NVDA / JAWS) cannot pronounce
polytonic Greek script. The trick — pioneered in the original prototype — is to
transliterate Greek into a *phonetic spelling* using the orthography of the
user's interface language, so that a normal Spanish or English voice reads it
approximately the way the chosen scholarly scheme intends.

Four schemes are supported, each available with Spanish ("es") or English
("en") target orthography:

    * ``erasmian``        – academic classroom pronunciation (default)
    * ``modern``          – contemporary Greek (iotacism, fricatives)
    * ``restored-attic``  – reconstructed 5th-century Attic
    * ``erasmian`` + es   – the Spanish-school Erasmian taught in Spain

The renderer is table-driven so the (linguistically verified) mapping tables in
``PRONUNCIATION_TABLES`` can be refined independently of the algorithm.
"""

import unicodedata

# Combining diacritics we care about (NFD code points).
ACUTE = "́"
GRAVE = "̀"
CIRCUMFLEX = "͂"
SMOOTH = "̓"
ROUGH = "̔"
IOTA_SUB = "ͅ"
DIAERESIS = "̈"
_ACCENTS = {ACUTE, GRAVE, CIRCUMFLEX}

SCHEMES = ("erasmian", "modern", "restored-attic")
DEFAULT_SCHEME = "erasmian"

# Human-readable scheme names per UI language (for the Settings dialog).
SCHEME_LABELS = {
    "en": {
        "erasmian": "Erasmian (academic)",
        "modern": "Modern Greek",
        "restored-attic": "Restored Attic",
    },
    "es": {
        "erasmian": "Erasmiana (académica)",
        "modern": "Griego moderno",
        "restored-attic": "Ática restituida",
    },
}

_ES_ACUTE = {"a": "á", "e": "é", "i": "í", "o": "ó", "u": "ú"}


def _base_consonants_vowels(lang):
    """Spelling of the plain (unaccented) Greek alphabet, shared starting point."""
    if lang == "es":
        return {
            "vowels": {"α": "a", "ε": "e", "η": "e", "ι": "i", "ο": "o", "υ": "u", "ω": "o"},
            "consonants": {
                "β": "b", "γ": "g", "δ": "d", "ζ": "ds", "θ": "z", "κ": "k", "λ": "l",
                "μ": "m", "ν": "n", "ξ": "x", "π": "p", "ρ": "r", "σ": "s", "ς": "s",
                "τ": "t", "φ": "f", "χ": "j", "ψ": "ps", "ϲ": "s",
            },
        }
    return {
        "vowels": {"α": "a", "ε": "e", "η": "ay", "ι": "i", "ο": "o", "υ": "u", "ω": "oh"},
        "consonants": {
            "β": "b", "γ": "g", "δ": "d", "ζ": "zd", "θ": "th", "κ": "k", "λ": "l",
            "μ": "m", "ν": "n", "ξ": "x", "π": "p", "ρ": "r", "σ": "s", "ς": "s",
            "τ": "t", "φ": "f", "χ": "ch", "ψ": "ps", "ϲ": "s",
        },
    }


def _table_erasmian(lang):
    t = _base_consonants_vowels(lang)
    if lang == "es":
        t["diphthongs"] = {
            "αι": "ai", "ει": "ei", "οι": "oi", "υι": "ui",
            "αυ": "au", "ευ": "eu", "ου": "u", "ηυ": "eu",
        }
        t["rough"] = "j"   # Spanish has no /h/; "j" makes the voice aspirate
    else:
        t["diphthongs"] = {
            "αι": "eye", "ει": "ay", "οι": "oy", "υι": "wee",
            "αυ": "ow", "ευ": "eh-oo", "ου": "oo", "ηυ": "ay-oo",
        }
        t["rough"] = "h"
    return t


def _table_modern(lang):
    # Iotacism: η ι υ ει οι υι all -> "i"; fricatives; av/af, ev/ef.
    if lang == "es":
        t = {
            "vowels": {"α": "a", "ε": "e", "η": "i", "ι": "i", "ο": "o", "υ": "i", "ω": "o"},
            "consonants": {
                "β": "v", "γ": "g", "δ": "d", "ζ": "s", "θ": "z", "κ": "k", "λ": "l",
                "μ": "m", "ν": "n", "ξ": "x", "π": "p", "ρ": "r", "σ": "s", "ς": "s",
                "τ": "t", "φ": "f", "χ": "j", "ψ": "ps", "ϲ": "s",
            },
            "diphthongs": {
                "αι": "e", "ει": "i", "οι": "i", "υι": "i",
                "αυ": "av", "ευ": "ev", "ου": "u",
            },
        }
    else:
        t = {
            "vowels": {"α": "ah", "ε": "eh", "η": "ee", "ι": "ee", "ο": "oh", "υ": "ee", "ω": "oh"},
            "consonants": {
                "β": "v", "γ": "gh", "δ": "th", "ζ": "z", "θ": "th", "κ": "k", "λ": "l",
                "μ": "m", "ν": "n", "ξ": "x", "π": "p", "ρ": "r", "σ": "s", "ς": "s",
                "τ": "t", "φ": "f", "χ": "kh", "ψ": "ps", "ϲ": "s",
            },
            "diphthongs": {
                "αι": "eh", "ει": "ee", "οι": "ee", "υι": "ee",
                "αυ": "av", "ευ": "ev", "ου": "oo",
            },
        }
    t["rough"] = ""  # rough breathing is silent in Modern Greek
    return t


def _table_restored(lang):
    # Reconstructed Attic: vowel length + aspirated stops; rendered as best a
    # modern voice can approximate.
    if lang == "es":
        t = {
            "vowels": {"α": "a", "ε": "e", "η": "ee", "ι": "i", "ο": "o", "υ": "u", "ω": "oo"},
            "consonants": {
                "β": "b", "γ": "g", "δ": "d", "ζ": "sd", "θ": "tj", "κ": "k", "λ": "l",
                "μ": "m", "ν": "n", "ξ": "x", "π": "p", "ρ": "r", "σ": "s", "ς": "s",
                "τ": "t", "φ": "pj", "χ": "kj", "ψ": "ps", "ϲ": "s",
            },
            "diphthongs": {
                "αι": "ai", "ει": "ee", "οι": "oi", "υι": "ui",
                "αυ": "au", "ευ": "eu", "ου": "uu",
            },
            "rough": "j",
        }
    else:
        t = {
            "vowels": {"α": "a", "ε": "e", "η": "eh", "ι": "i", "ο": "o", "υ": "ew", "ω": "aw"},
            "consonants": {
                "β": "b", "γ": "g", "δ": "d", "ζ": "zd", "θ": "t-h", "κ": "k", "λ": "l",
                "μ": "m", "ν": "n", "ξ": "x", "π": "p", "ρ": "r", "σ": "s", "ς": "s",
                "τ": "t", "φ": "p-h", "χ": "k-h", "ψ": "ps", "ϲ": "s",
            },
            "diphthongs": {
                "αι": "ai", "ει": "ay", "οι": "oy", "υι": "wee",
                "αυ": "ow", "ευ": "eh-oo", "ου": "oo",
            },
            "rough": "h",
        }
    return t


def _build_tables():
    tables = {}
    for lang in ("es", "en"):
        tables[("erasmian", lang)] = _table_erasmian(lang)
        tables[("modern", lang)] = _table_modern(lang)
        tables[("restored-attic", lang)] = _table_restored(lang)
    return tables


def _merge_verified(tables):
    """Overlay the linguistically-verified vowel/consonant/diphthong maps
    (core/data/pronunciation_tables.json) onto the baseline. The algorithm's own
    rough-breathing and gamma-nasal handling are preserved."""
    import json
    import os
    path = os.path.join(os.path.dirname(__file__), "data", "pronunciation_tables.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return tables
    for entry in data:
        key = (entry.get("scheme"), entry.get("lang"))
        if key not in tables:
            continue
        for field in ("vowels", "consonants", "diphthongs"):
            verified = entry.get(field)
            if isinstance(verified, dict):
                tables[key][field].update(
                    {k: v for k, v in verified.items() if isinstance(v, str) and v}
                )
    return tables


PRONUNCIATION_TABLES = _merge_verified(_build_tables())

# Greek capital -> lowercase, so a single mapping table covers both cases.
_CAP = {
    "Α": "α", "Β": "β", "Γ": "γ", "Δ": "δ", "Ε": "ε", "Ζ": "ζ", "Η": "η", "Θ": "θ",
    "Ι": "ι", "Κ": "κ", "Λ": "λ", "Μ": "μ", "Ν": "ν", "Ξ": "ξ", "Ο": "ο", "Π": "π",
    "Ρ": "ρ", "Σ": "σ", "Τ": "τ", "Υ": "υ", "Φ": "φ", "Χ": "χ", "Ψ": "ψ", "Ω": "ω",
}
_GAMMA_NASAL_FOLLOWERS = {"γ", "κ", "ξ", "χ"}


def _add_spanish_acute(s):
    for i, ch in enumerate(s):
        if ch in _ES_ACUTE:
            return s[:i] + _ES_ACUTE[ch] + s[i + 1:]
        if ch in _ES_ACUTE.values():
            return s  # already accented
    return s


def _tokenize(text):
    """Split into [base_char, {combining marks}] tokens (NFD-aware)."""
    decomposed = unicodedata.normalize("NFD", text)
    tokens = []
    for c in decomposed:
        if unicodedata.combining(c):
            if tokens:
                tokens[-1][1].add(c)
        else:
            tokens.append([c, set()])
    return tokens


def get_table(scheme, lang):
    if lang not in ("es", "en"):
        lang = "en"
    if scheme not in SCHEMES:
        scheme = DEFAULT_SCHEME
    return PRONUNCIATION_TABLES[(scheme, lang)]


def transliterate(text, scheme=DEFAULT_SCHEME, lang="es"):
    """Render Greek *text* as a target-language phonetic spelling."""
    if not text:
        return ""
    tbl = get_table(scheme, lang)
    mark_stress = (lang == "es")
    tokens = _tokenize(text)
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        base, marks = tokens[i]
        is_upper = base.isupper()
        lower = _CAP.get(base, base.lower())

        # γ before a velar -> nasal "n".
        if lower == "γ" and i + 1 < n:
            nxt = tokens[i + 1][0]
            if _CAP.get(nxt, nxt.lower()) in _GAMMA_NASAL_FOLLOWERS:
                rendered = "N" if is_upper else "n"
                out.append(rendered)
                i += 1
                continue

        rendered = None
        consumed = 1
        carries_accent = bool(marks & _ACCENTS)
        rough = ROUGH in marks

        # Diphthong (two vowels, no diaeresis on the second).
        if i + 1 < n:
            nb, nm = tokens[i + 1]
            nlow = _CAP.get(nb, nb.lower())
            pair = lower + nlow
            if pair in tbl["diphthongs"] and DIAERESIS not in nm and DIAERESIS not in marks:
                rendered = tbl["diphthongs"][pair]
                consumed = 2
                carries_accent = bool((marks | nm) & _ACCENTS)
                rough = ROUGH in marks  # breathing sits on first element

        if rendered is None:
            rendered = tbl["vowels"].get(lower)
            if rendered is None:
                rendered = tbl["consonants"].get(lower, base)

        if is_upper and rendered:
            rendered = rendered[0].upper() + rendered[1:]

        if rough and tbl.get("rough"):
            rmark = tbl["rough"]
            if is_upper:
                rendered = rmark.upper() + (rendered[0].lower() + rendered[1:] if rendered else "")
            else:
                rendered = rmark + rendered

        if carries_accent and mark_stress:
            rendered = _add_spanish_acute(rendered)

        out.append(rendered)
        i += consumed

    return unicodedata.normalize("NFC", "".join(out))
