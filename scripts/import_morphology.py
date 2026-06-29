"""
Optional morphology data pack: populate ``morph_code`` so cursor-on-word parsing
works for inflected forms.

The shipped LSJ-derived database maps forms to lemmas and definitions but has no
morphology codes. This script fills them from **MorphGNT/SBLGNT** — a freely
available, fully parsed Greek New Testament (Koine) — converting MorphGNT's parse
strings into the Robinson-style codes that :mod:`core.morph_translator` already
understands (e.g. ``N-NSF``, ``V-PAI-3S``).

It is a great first data pack because it is small, reliable and gives real
parses for the high-frequency Koine vocabulary students read most.

Usage:
    python scripts/import_morphology.py            # download + import
    python scripts/import_morphology.py --limit 5  # first few books only (test)

For Classical coverage, the larger Perseus/Morpheus treebank can be imported the
same way; see docs/DATA_SOURCES.md.
"""

import argparse
import os
import sqlite3
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.greek_utils import normalize_lookup  # noqa: E402

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "logos_dict.db")
BASE = "https://raw.githubusercontent.com/morphgnt/sblgnt/master/"

# 66 book files, e.g. 61-Mt-morphgnt.txt … 27-Re-morphgnt.txt
BOOKS = [
    "61-Mt", "62-Mk", "63-Lk", "64-Jn", "65-Ac", "66-Ro", "67-1Co", "68-2Co",
    "69-Ga", "70-Eph", "71-Php", "72-Col", "73-1Th", "74-2Th", "75-1Ti", "76-2Ti",
    "77-Tit", "78-Phm", "79-Heb", "80-Jas", "81-1Pe", "82-2Pe", "83-1Jn", "84-2Jn",
    "85-3Jn", "86-Jud", "87-Re",
]

# MorphGNT POS -> Robinson head.
_POS = {
    "N-": "N", "A-": "A", "RA": "T", "RP": "P", "RR": "P", "RD": "P", "RI": "P",
    "C-": "CONJ", "D-": "D", "P-": "PREP", "X-": "PRT", "I-": "INJ", "V-": "V",
    "ADV": "D",
}
_TENSE = {"P": "P", "I": "I", "F": "F", "A": "A", "X": "X", "Y": "Y"}
_VOICE = {"A": "A", "M": "M", "P": "P", "E": "E"}
_MOOD = {"I": "I", "S": "S", "O": "O", "D": "M", "N": "N", "P": "P"}


def morphgnt_to_robinson(pos, parse):
    """parse = 8 chars: person tense voice mood case number gender degree."""
    head = _POS.get(pos, pos.strip("-") or "X")
    person, tense, voice, mood, case, number, gender, degree = (
        parse[0], parse[1], parse[2], parse[3], parse[4], parse[5], parse[6], parse[7]
    )
    if head == "V":
        t = _TENSE.get(tense, "")
        v = _VOICE.get(voice, "")
        m = _MOOD.get(mood, "")
        code = f"V-{t}{v}{m}"
        if person in "123" and number in "SP":
            code += f"-{person}{number}"
        return code
    if head in ("N", "A", "T", "P"):
        if case in "NGDAV" and number in "SP" and gender in "MFN":
            return f"{head}-{case}{number}{gender}"
        return head
    return head


def fetch_book(book):
    url = f"{BASE}{book}-morphgnt.txt"
    req = urllib.request.Request(url, headers={"User-Agent": "LogosIDE/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="only first N books")
    ap.add_argument("--db", default=DB_PATH)
    args = ap.parse_args()

    if not os.path.exists(args.db):
        print(f"Database not found: {args.db}. Run build_database.py first.")
        return 1

    conn = sqlite3.connect(args.db, timeout=60)
    conn.execute("PRAGMA busy_timeout=60000")
    cur = conn.cursor()

    # form_norm -> robinson code (first/most common wins per form).
    mapping = {}
    books = BOOKS[: args.limit] if args.limit else BOOKS
    for i, book in enumerate(books, 1):
        try:
            text = fetch_book(book)
        except Exception as e:
            print(f"  skip {book}: {e}")
            continue
        for line in text.splitlines():
            cols = line.split()
            if len(cols) < 7:
                continue
            pos, parse, _word, _text, normalized, lemma = (
                cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]
            )
            key = normalize_lookup(normalized)
            if key and key not in mapping:
                mapping[key] = morphgnt_to_robinson(pos, parse)
        print(f"  [{i}/{len(books)}] {book}: {len(mapping)} forms collected")

    print(f"Applying {len(mapping)} morphology codes…")
    updated = 0
    for key, code in mapping.items():
        cur.execute(
            "UPDATE words SET morph_code = ? WHERE form_norm = ? AND (morph_code IS NULL OR morph_code = '')",
            (code, key),
        )
        updated += cur.rowcount
    conn.commit()
    conn.close()
    print(f"Done. Updated {updated} rows with morphology codes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
