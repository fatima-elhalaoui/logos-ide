"""
Greek input transliteration, diacritic composition and character description.

Typing convention (modifiers come *after* the vowel):
    /  acute (oxia)         \\  grave (varia)        =  circumflex (perispomeni)
    )  smooth breathing     (   rough breathing      |  iota subscript
    +  diaeresis            v   final sigma          :  ano teleia (·)

``describe_char`` powers the editor's "explain this character" command — vital
for a blind user who cannot see which accents a glyph carries.
"""

import unicodedata

BASIC_GREEK_MAP = {
    "a": "α", "b": "β", "g": "γ", "d": "δ", "e": "ε", "z": "ζ", "h": "η", "q": "θ",
    "i": "ι", "k": "κ", "l": "λ", "m": "μ", "n": "ν", "c": "ξ", "o": "ο", "p": "π",
    "r": "ρ", "s": "σ", "t": "τ", "u": "υ", "f": "φ", "x": "χ", "y": "ψ", "w": "ω",
    "v": "ς", ":": "·",
    "A": "Α", "B": "Β", "G": "Γ", "D": "Δ", "E": "Ε", "Z": "Ζ", "H": "Η", "Q": "Θ",
    "I": "Ι", "K": "Κ", "L": "Λ", "M": "Μ", "N": "Ν", "C": "Ξ", "O": "Ο", "P": "Π",
    "R": "Ρ", "S": "Σ", "T": "Τ", "U": "Υ", "F": "Φ", "X": "Χ", "Y": "Ψ", "W": "Ω",
    "V": "Σ",
}

DIACRITIC_MAP = {
    "/": "́",   # acute
    "\\": "̀",  # grave
    "=": "͂",   # circumflex (perispomeni)
    ")": "̓",   # smooth breathing (psili)
    "(": "̔",   # rough breathing (dasia)
    "|": "ͅ",   # iota subscript (ypogegrammeni)
    "+": "̈",   # diaeresis (dialytika)
}

# Spoken names of each combining mark.
DIACRITIC_NAMES = {
    "́": {"en": "acute accent", "es": "acento agudo"},
    "̀": {"en": "grave accent", "es": "acento grave"},
    "͂": {"en": "circumflex", "es": "circunflejo"},
    "̓": {"en": "smooth breathing", "es": "espíritu suave"},
    "̔": {"en": "rough breathing", "es": "espíritu áspero"},
    "ͅ": {"en": "iota subscript", "es": "iota suscrita"},
    "̈": {"en": "diaeresis", "es": "diéresis"},
    "̄": {"en": "macron", "es": "macrón"},
    "̆": {"en": "breve", "es": "breve"},
}

_LETTER_NAMES = {
    "α": ("alpha", "alfa"), "β": ("beta", "beta"), "γ": ("gamma", "gamma"),
    "δ": ("delta", "delta"), "ε": ("epsilon", "épsilon"), "ζ": ("zeta", "dseta"),
    "η": ("eta", "eta"), "θ": ("theta", "theta"), "ι": ("iota", "iota"),
    "κ": ("kappa", "kappa"), "λ": ("lambda", "lambda"), "μ": ("mu", "my"),
    "ν": ("nu", "ny"), "ξ": ("xi", "xi"), "ο": ("omicron", "ómicron"),
    "π": ("pi", "pi"), "ρ": ("rho", "rho"), "σ": ("sigma", "sigma"),
    "ς": ("final sigma", "sigma final"), "τ": ("tau", "tau"),
    "υ": ("upsilon", "ípsilon"), "φ": ("phi", "fi"), "χ": ("chi", "ji"),
    "ψ": ("psi", "psi"), "ω": ("omega", "omega"),
}


def translate_char(char):
    return BASIC_GREEK_MAP.get(char, char)


def try_combine_diacritic(base_char, modifier_key):
    """Combine *base_char* with the diacritic for *modifier_key*.

    Returns the combined character only if it forms a single, valid precomposed
    polytonic Greek glyph — otherwise None. This rejects nonsense like a
    consonant with a circumflex, a space with an accent, or a Latin letter with
    a Greek accent (all of which the naive NFD+mark approach would happily
    produce).
    """
    mark = DIACRITIC_MAP.get(modifier_key)
    if not mark or not base_char:
        return None

    decomposed = unicodedata.normalize("NFD", base_char)
    base = decomposed[0]
    # Base must be a Greek letter.
    if "GREEK" not in unicodedata.name(base, ""):
        return None
    # Don't stack the same mark twice.
    if mark in decomposed:
        return None

    precomposed = unicodedata.normalize("NFC", decomposed + mark)
    # A valid polytonic combination collapses to exactly one code point.
    if len(precomposed) == 1:
        return precomposed
    return None


def describe_char(char, language="en"):
    """Return a spoken description of *char*, including any diacritics."""
    lang = "es" if language == "es" else "en"
    if not char:
        return "blank" if lang == "en" else "vacío"
    if char in (" ", "\t"):
        return "space" if lang == "en" else "espacio"
    if char in ("\n", " ", " "):
        return "new line" if lang == "en" else "salto de línea"

    decomposed = unicodedata.normalize("NFD", char)
    base = decomposed[0]
    marks = decomposed[1:]

    is_upper = base.isupper()
    base_lower = base.lower()
    name = _LETTER_NAMES.get(base_lower)
    if name:
        letter = name[0] if lang == "en" else name[1]
        if is_upper:
            letter = (f"capital {letter}" if lang == "en" else f"{letter} mayúscula")
    else:
        letter = unicodedata.name(base, base).lower()

    diac = []
    for m in marks:
        d = DIACRITIC_NAMES.get(m)
        if d:
            diac.append(d[lang])
    if not diac:
        return letter
    joiner = " with " if lang == "en" else " con "
    sep = " and " if lang == "en" else " y "
    return letter + joiner + sep.join(diac)


def letter_name(char, language="en"):
    lang = "es" if language == "es" else "en"
    n = _LETTER_NAMES.get(char.lower())
    if not n:
        return char
    return n[0] if lang == "en" else n[1]
