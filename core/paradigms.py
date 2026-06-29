"""
Generate regular Greek paradigms (declension / conjugation tables).

This is a study aid covering the *regular* patterns taught first in every Greek
course: the three article-driven noun declensions and the present/imperfect of
the thematic (-ω) verb, plus the verb "to be". It is intentionally honest about
scope — irregular and athematic forms are not invented; instead the generator
reports that it can only show the regular pattern.

Each paradigm is returned as a structured, screen-reader-friendly object:
    {
      "type": "...",
      "title": {"en": "...", "es": "..."},
      "note": {"en": "...", "es": "..."},
      "groups": [
         {"label": {"en": "...", "es": "..."},
          "rows": [{"label": {"en","es"}, "form": "λόγος"}, ...]}
      ]
    }
"""

from core.greek_utils import strip_diacritics

_CASES = [
    ("nom", "Nominative", "Nominativo"),
    ("gen", "Genitive", "Genitivo"),
    ("dat", "Dative", "Dativo"),
    ("acc", "Accusative", "Acusativo"),
    ("voc", "Vocative", "Vocativo"),
]

_PERSONS = [
    ("1s", "1st singular", "1ª singular"),
    ("2s", "2nd singular", "2ª singular"),
    ("3s", "3rd singular", "3ª singular"),
    ("1p", "1st plural", "1ª plural"),
    ("2p", "2nd plural", "2ª plural"),
    ("3p", "3rd plural", "3ª plural"),
]


def _rows(stem, endings_sing, endings_plur):
    rows = []
    for (key, en, es), end in zip(_CASES, endings_sing):
        rows.append({"label": {"en": f"{en} sing.", "es": f"{es} sing."}, "form": stem + end})
    for (key, en, es), end in zip(_CASES, endings_plur):
        rows.append({"label": {"en": f"{en} pl.", "es": f"{es} pl."}, "form": stem + end})
    return rows


def _second_decl_masc(stem):
    return _rows(stem, ["ος", "ου", "ῳ", "ον", "ε"], ["οι", "ων", "οις", "ους", "οι"])


def _second_decl_neut(stem):
    return _rows(stem, ["ον", "ου", "ῳ", "ον", "ον"], ["α", "ων", "οις", "α", "α"])


def _first_decl_eta(stem):
    return _rows(stem, ["η", "ης", "ῃ", "ην", "η"], ["αι", "ων", "αις", "ας", "αι"])


def _first_decl_alpha(stem):
    return _rows(stem, ["α", "ας", "ᾳ", "αν", "α"], ["αι", "ων", "αις", "ας", "αι"])


def _present_active(stem):
    sing = ["ω", "εις", "ει"]
    plur = ["ομεν", "ετε", "ουσι(ν)"]
    rows = []
    forms = sing + plur
    for (key, en, es), end in zip(_PERSONS, forms):
        rows.append({"label": {"en": en, "es": es}, "form": stem + end})
    return rows


def _imperfect_active(stem):
    # augment + stem + endings (regular ε- augment on consonant-initial stems)
    aug = "ἐ" + stem
    sing = ["ον", "ες", "ε(ν)"]
    plur = ["ομεν", "ετε", "ον"]
    rows = []
    for (key, en, es), end in zip(_PERSONS, sing + plur):
        rows.append({"label": {"en": en, "es": es}, "form": aug + end})
    return rows


def _eimi_present():
    forms = ["εἰμί", "εἶ", "ἐστί(ν)", "ἐσμέν", "ἐστέ", "εἰσί(ν)"]
    return [
        {"label": {"en": en, "es": es}, "form": f}
        for (key, en, es), f in zip(_PERSONS, forms)
    ]


def generate_paradigm(lemma):
    """Return a paradigm object for *lemma*, or None if no regular pattern fits."""
    if not lemma:
        return None
    bare = strip_diacritics(lemma)

    # Verb "to be".
    if bare in ("ειμι", "ειμί") or lemma in ("εἰμί", "εἰμι"):
        return {
            "type": "verb-eimi",
            "title": {"en": "εἰμί — present indicative (to be)",
                      "es": "εἰμί — presente de indicativo (ser/estar)"},
            "note": {"en": "Irregular verb; present indicative shown.",
                     "es": "Verbo irregular; se muestra el presente de indicativo."},
            "groups": [{"label": {"en": "Present indicative", "es": "Presente de indicativo"},
                        "rows": _eimi_present()}],
        }

    # Thematic verb in -ω.
    if lemma.endswith("ω") and not lemma.endswith("μι"):
        stem = lemma[:-1]
        return {
            "type": "verb-thematic",
            "title": {"en": f"{lemma} — regular -ω verb",
                      "es": f"{lemma} — verbo regular en -ω"},
            "note": {"en": "Regular thematic pattern (present & imperfect active).",
                     "es": "Patrón temático regular (presente e imperfecto activos)."},
            "groups": [
                {"label": {"en": "Present active indicative",
                           "es": "Presente activo de indicativo"},
                 "rows": _present_active(stem)},
                {"label": {"en": "Imperfect active indicative",
                           "es": "Imperfecto activo de indicativo"},
                 "rows": _imperfect_active(stem)},
            ],
        }

    # Nouns by ending.
    if lemma.endswith("ος"):
        return _noun_paradigm(lemma, lemma[:-2], _second_decl_masc,
                              "2nd declension (masc./fem. -ος)",
                              "2ª declinación (masc./fem. -ος)")
    if lemma.endswith("ον"):
        return _noun_paradigm(lemma, lemma[:-2], _second_decl_neut,
                              "2nd declension neuter (-ον)",
                              "2ª declinación neutra (-ον)")
    if lemma.endswith("η"):
        return _noun_paradigm(lemma, lemma[:-1], _first_decl_eta,
                              "1st declension (-η)", "1ª declinación (-η)")
    if lemma.endswith("α"):
        return _noun_paradigm(lemma, lemma[:-1], _first_decl_alpha,
                              "1st declension (-α)", "1ª declinación (-α)")
    return None


def _noun_paradigm(lemma, stem, builder, title_en, title_es):
    return {
        "type": "noun",
        "title": {"en": f"{lemma} — {title_en}", "es": f"{lemma} — {title_es}"},
        "note": {"en": "Regular declension shown; accent may shift in real forms.",
                 "es": "Se muestra la declinación regular; el acento puede variar."},
        "groups": [{"label": {"en": "Singular & plural", "es": "Singular y plural"},
                    "rows": builder(stem)}],
    }
