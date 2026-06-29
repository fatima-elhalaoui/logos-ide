"""
Regenerate / repair the Spanish dictionary definitions.

The original Spanish column was machine-translated *without protecting the inline
Greek*, so Greek words inside definitions came out mangled ("ἄλφα" → "Ёφα"). This
script fixes that by **masking** every run of Greek with an opaque token before
translation and restoring it afterwards, so the Greek is never touched.

It is:
  * resumable   — a JSON cache records every translation; re-running continues.
  * targeted    — by default it only (re)translates definitions that contain
                  Greek (the ones that were corrupted) or that have no Spanish yet.
  * online      — uses Google Translate via deep-translator (no API key), with an
                  optional offline Argos engine (`--engine argos`).

Usage:
    python scripts/regenerate_spanish.py                 # repair Greek-bearing + missing
    python scripts/regenerate_spanish.py --all           # redo every definition
    python scripts/regenerate_spanish.py --limit 2000    # cap this run
    python scripts/regenerate_spanish.py --engine argos  # offline
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "logos_dict.db")
CACHE_FILE = os.path.join(os.path.dirname(__file__), "spanish_cache.json")

# Greek + Greek Extended ranges.
_GREEK_RUN = re.compile(r"[Ͱ-Ͽἀ-῿̀-ͯ]+")
_TOKEN_RE = re.compile(r"MGZ\s*(\d+)\s*MGZ", re.IGNORECASE)


def mask_greek(text):
    """Replace each Greek run with an opaque token translators leave alone."""
    spans = []

    def repl(m):
        spans.append(m.group(0))
        return f" MGZ{len(spans) - 1}MGZ "

    return _GREEK_RUN.sub(repl, text), spans


def unmask_greek(text, spans):
    def repl(m):
        idx = int(m.group(1))
        return spans[idx] if 0 <= idx < len(spans) else m.group(0)

    return _TOKEN_RE.sub(repl, text)


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(cache):
    tmp = CACHE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)
    os.replace(tmp, CACHE_FILE)


_MAX_CHARS = 4500  # Google Translate's per-request limit is 5000.


def _chunks(text, limit=_MAX_CHARS):
    """Split long text into <=limit pieces at sentence/space boundaries."""
    if len(text) <= limit:
        return [text]
    pieces = []
    remaining = text
    while len(remaining) > limit:
        cut = remaining.rfind(". ", 0, limit)
        if cut < limit // 2:
            cut = remaining.rfind(" ", 0, limit)
        if cut <= 0:
            cut = limit
        pieces.append(remaining[:cut + 1])
        remaining = remaining[cut + 1:]
    if remaining:
        pieces.append(remaining)
    return pieces


def get_translator(engine):
    if engine == "argos":
        import argostranslate.translate as at

        def _t(text):
            return at.translate(text, "en", "es")
    else:
        from deep_translator import GoogleTranslator
        gt = GoogleTranslator(source="en", target="es")

        def _t(text):
            return gt.translate(text)

    def translate(text):
        # Transparently handle definitions longer than the request limit.
        return " ".join(_t(c) or "" for c in _chunks(text))

    return translate


def select_definitions(conn, do_all):
    cur = conn.cursor()
    if do_all:
        cur.execute("SELECT DISTINCT definition FROM words WHERE definition != ''")
    else:
        # Greek-bearing definitions (at risk of corruption) OR missing Spanish.
        cur.execute(
            "SELECT DISTINCT definition FROM words "
            "WHERE definition != '' AND ("
            "  definition_es IS NULL OR definition_es = '' "
            "  OR definition GLOB '*[α-ωΑ-Ω]*'"
            ")"
        )
    return [r[0] for r in cur.fetchall()]


def apply_translations(conn, pairs):
    conn.executemany(
        "UPDATE words SET definition_es = ? WHERE definition = ?",
        [(es, en) for en, es in pairs],
    )
    conn.commit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="redo every definition")
    ap.add_argument("--limit", type=int, default=0, help="max definitions this run")
    ap.add_argument("--engine", choices=["google", "argos"], default="google")
    ap.add_argument("--db", default=DB_PATH)
    args = ap.parse_args()

    if not os.path.exists(args.db):
        print(f"Database not found: {args.db}")
        return 1

    conn = sqlite3.connect(args.db, timeout=60)
    conn.execute("PRAGMA busy_timeout=60000")  # wait, don't fail, on concurrent writes
    # Temporary index so the WHERE definition = ? updates are fast; dropped at end
    # so the shipped database is never bloated with it.
    conn.execute("CREATE INDEX IF NOT EXISTS idx_def_tmp ON words(definition)")
    cache = load_cache()
    translate = get_translator(args.engine)

    defs = select_definitions(conn, args.all)
    pending = [d for d in defs if d not in cache]
    print(f"{len(defs)} candidate definitions, {len(pending)} not yet cached "
          f"({len(cache)} cached). Engine: {args.engine}.")

    # Flush anything already cached straight into the DB first.
    cached_pairs = [(en, cache[en]) for en in defs if en in cache]
    if cached_pairs:
        apply_translations(conn, cached_pairs)
        print(f"Synced {len(cached_pairs)} cached translations to the DB.")

    if args.limit:
        pending = pending[: args.limit]

    done = 0
    batch = []
    try:
        for en in pending:
            masked, spans = mask_greek(en)
            try:
                es = translate(masked) or ""
            except Exception as e:
                print(f"  translate error ({e}); pausing 5s")
                time.sleep(5)
                continue
            es = unmask_greek(es, spans)
            cache[en] = es
            batch.append((en, es))
            done += 1
            if done % 50 == 0:
                save_cache(cache)
                apply_translations(conn, batch)
                batch = []
                print(f"  {done}/{len(pending)} translated…")
            if args.engine == "google":
                time.sleep(0.2)  # be gentle with the free endpoint
    except KeyboardInterrupt:
        print("\nInterrupted; saving progress.")
    finally:
        save_cache(cache)
        if batch:
            apply_translations(conn, batch)
        try:
            conn.execute("DROP INDEX IF EXISTS idx_def_tmp")
            conn.commit()
        except Exception:
            pass
        conn.close()
    print(f"Done. Translated {done} definitions this run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
