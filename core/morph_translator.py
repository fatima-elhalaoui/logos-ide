"""
Translate compact morphology codes into plain English / Spanish.

Handles the Robinson-style codes used in Koine corpora (e.g. ``N-GSM``,
``V-PAI-3S``, ``CONJ``, ``PREP``). Unknown codes are returned unchanged so the
panel never shows nothing.
"""

_POS = {
    "en": {
        "N": "Noun", "V": "Verb", "A": "Adjective", "D": "Adverb", "ADV": "Adverb",
        "P": "Pronoun", "R": "Preposition", "PREP": "Preposition", "C": "Conjunction",
        "CONJ": "Conjunction", "I": "Interjection", "INJ": "Interjection",
        "T": "Article", "X": "Particle", "PRT": "Particle",
    },
    "es": {
        "N": "Sustantivo", "V": "Verbo", "A": "Adjetivo", "D": "Adverbio", "ADV": "Adverbio",
        "P": "Pronombre", "R": "Preposición", "PREP": "Preposición", "C": "Conjunción",
        "CONJ": "Conjunción", "I": "Interjección", "INJ": "Interjección",
        "T": "Artículo", "X": "Partícula", "PRT": "Partícula",
    },
}

_CASE = {
    "en": {"N": "Nominative", "G": "Genitive", "D": "Dative", "A": "Accusative", "V": "Vocative"},
    "es": {"N": "Nominativo", "G": "Genitivo", "D": "Dativo", "A": "Acusativo", "V": "Vocativo"},
}
_NUM = {
    "en": {"S": "Singular", "P": "Plural", "D": "Dual"},
    "es": {"S": "Singular", "P": "Plural", "D": "Dual"},
}
_GEN = {
    "en": {"M": "Masculine", "F": "Feminine", "N": "Neuter"},
    "es": {"M": "Masculino", "F": "Femenino", "N": "Neutro"},
}
_TENSE = {
    "en": {"P": "Present", "I": "Imperfect", "F": "Future", "A": "Aorist",
           "X": "Perfect", "Y": "Pluperfect", "2A": "2nd Aorist"},
    "es": {"P": "Presente", "I": "Imperfecto", "F": "Futuro", "A": "Aoristo",
           "X": "Perfecto", "Y": "Pluscuamperfecto", "2A": "Aoristo 2º"},
}
_VOICE = {
    "en": {"A": "Active", "M": "Middle", "P": "Passive", "E": "Middle/Passive",
           "D": "Middle deponent", "O": "Passive deponent", "N": "Middle/Passive deponent"},
    "es": {"A": "Activa", "M": "Media", "P": "Pasiva", "E": "Media/Pasiva",
           "D": "Media deponente", "O": "Pasiva deponente", "N": "Media/Pasiva deponente"},
}
_MOOD = {
    "en": {"I": "Indicative", "S": "Subjunctive", "O": "Optative", "M": "Imperative",
           "N": "Infinitive", "P": "Participle"},
    "es": {"I": "Indicativo", "S": "Subjuntivo", "O": "Optativo", "M": "Imperativo",
           "N": "Infinitivo", "P": "Participio"},
}
_PERSON = {
    "en": {"1": "1st person", "2": "2nd person", "3": "3rd person"},
    "es": {"1": "1ª persona", "2": "2ª persona", "3": "3ª persona"},
}
_NEG = {"en": "negative", "es": "negativa"}


def translate_morph_code(code, language="en"):
    if not code:
        return ""
    lang = "es" if language == "es" else "en"
    code = code.strip()

    parts = code.split("-")
    head = parts[0]
    pos = _POS[lang].get(head, head)
    out = [pos]

    if head in ("CONJ", "PREP", "ADV", "INJ"):
        return pos
    if head == "PRT":
        if len(parts) > 1 and parts[1] == "N":
            out.append(_NEG[lang])
        return ", ".join(out)

    if head in ("N", "A", "T", "P") and len(parts) > 1 and len(parts[1]) == 3:
        p = parts[1]
        out.append(_CASE[lang].get(p[0], p[0]))
        out.append(_NUM[lang].get(p[1], p[1]))
        out.append(_GEN[lang].get(p[2], p[2]))

    elif head == "V" and len(parts) > 1:
        tvm = parts[1]
        if len(tvm) >= 3:
            # allow a 2-char tense prefix like "2A"
            if tvm[0] == "2" and len(tvm) == 4:
                out.append(_TENSE[lang].get(tvm[:2], tvm[:2]))
                rest = tvm[2:]
            else:
                out.append(_TENSE[lang].get(tvm[0], tvm[0]))
                rest = tvm[1:]
            if len(rest) >= 2:
                out.append(_VOICE[lang].get(rest[0], rest[0]))
                out.append(_MOOD[lang].get(rest[1], rest[1]))
        if len(parts) > 2 and len(parts[2]) == 2:
            p2 = parts[2]
            out.append(_PERSON[lang].get(p2[0], ""))
            out.append(_NUM[lang].get(p2[1], p2[1]))

    return ", ".join(t for t in out if t)
