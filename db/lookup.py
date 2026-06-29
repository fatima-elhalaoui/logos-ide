"""
Background dictionary + morphology lookup.

Runs SQLite queries off the GUI thread via a queue so rapid typing never freezes
the screen reader. Lookups are accent-insensitive (via ``form_norm``), expand
LSJ abbreviations for clean speech, and fall back to the English definition when
a Spanish one is missing.
"""

import json
import queue
import sqlite3

from PyQt6.QtCore import QThread, pyqtSignal

from core import abbreviations
from core.data_paths import dictionary_db_path
from core.greek_utils import normalize_lookup
from core.logger import get_logger
from core.morph_translator import translate_morph_code
from db import schema

log = get_logger(__name__)

_MAX_RESULTS = 12


def quick_lookup(word, language="en"):
    """Synchronous single-word lookup (for flashcards/history). Returns the best
    entry dict or None. Opens a short-lived connection; cheap for occasional use."""
    norm = normalize_lookup(word)
    if not norm:
        return None
    try:
        conn = sqlite3.connect(dictionary_db_path())
    except sqlite3.Error:
        return None
    row = None
    try:
        row = conn.execute(
            "SELECT lemma, morph_code, definition, definition_es "
            "FROM words WHERE form_norm = ? OR lemma = ? "
            "ORDER BY (lemma = form) DESC, "
            "(morph_code IS NOT NULL AND morph_code != '') DESC, id LIMIT 1",
            (norm, norm),
        ).fetchone()
    except sqlite3.Error:
        row = None
    finally:
        conn.close()
    if not row:
        return None
    lemma, morph, def_en, def_es = row
    active = def_es if (language == "es" and def_es) else (def_en or def_es or "")
    return {
        "lemma": lemma,
        "morphology": translate_morph_code(morph, language) if morph else "",
        "raw_morph": morph or "",
        "definition": abbreviations.expand(active, language),
    }


class DictionaryLookupWorker(QThread):
    """Serves dictionary lookups; emits a JSON-encoded result list."""

    lookup_completed = pyqtSignal(str)
    status_changed = pyqtSignal(str)  # e.g. "preparing dictionary…"

    def __init__(self, parent=None, language="en"):
        super().__init__(parent)
        self.word_queue = queue.Queue()
        self.is_running = True
        self.language = language
        self._last_norm = None

    def set_language(self, lang):
        self.language = lang
        self._last_norm = None  # force refresh on next identical word

    def search_word(self, word):
        """Enqueue a search (called on the GUI thread on every cursor move)."""
        norm = normalize_lookup(word)
        if norm and norm != self._last_norm:
            self._last_norm = norm
            self.word_queue.put((word, norm))

    def stop(self):
        self.is_running = False
        self.word_queue.put(None)  # unblock the queue
        self.wait(3000)

    # ------------------------------------------------------------------
    def run(self):
        try:
            conn = sqlite3.connect(dictionary_db_path())
        except sqlite3.Error as e:
            log.error("Could not open dictionary DB: %s", e)
            self.lookup_completed.emit(json.dumps([{"error": str(e)}]))
            return

        try:
            self.status_changed.emit("preparing")
            schema.ensure_dictionary_schema(conn)
            self.status_changed.emit("ready")
        except sqlite3.Error as e:
            log.warning("Schema preparation issue: %s", e)

        cursor = conn.cursor()
        while self.is_running:
            try:
                item = self.word_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            if item is None or not self.is_running:
                break

            # Coalesce: if the user kept typing, jump to the most recent word.
            while not self.word_queue.empty():
                nxt = self.word_queue.get_nowait()
                if nxt is None:
                    item = None
                    break
                item = nxt
            if item is None:
                break

            original, norm = item
            try:
                results = self._query(cursor, norm)
                self.lookup_completed.emit(json.dumps(results, ensure_ascii=False))
            except sqlite3.Error as e:
                log.error("Lookup error for %r: %s", original, e)
                self.lookup_completed.emit(
                    json.dumps([{"error": f"database error: {e}"}], ensure_ascii=False)
                )

        conn.close()

    # ------------------------------------------------------------------
    def _query(self, cursor, norm):
        rank = ("ORDER BY (lemma = form) DESC, "
                "(morph_code IS NOT NULL AND morph_code != '') DESC, id")
        cursor.execute(
            "SELECT lemma, morph_code, definition, definition_es "
            f"FROM words WHERE form_norm = ? {rank} LIMIT ?",
            (norm, _MAX_RESULTS),
        )
        rows = cursor.fetchall()
        if not rows:
            # Fall back to matching the lemma itself (helps when the cursor is on
            # a headword without an inflected entry).
            cursor.execute(
                "SELECT lemma, morph_code, definition, definition_es "
                f"FROM words WHERE form_norm = ? OR lemma = ? {rank} LIMIT ?",
                (norm, norm, _MAX_RESULTS),
            )
            rows = cursor.fetchall()
        if not rows:
            return [{"not_found": norm}]

        # De-duplicate identical (lemma, morph, def) tuples.
        seen = set()
        out = []
        for lemma, morph, def_en, def_es in rows:
            key = (lemma, morph, def_en)
            if key in seen:
                continue
            seen.add(key)

            if self.language == "es" and def_es:
                active = def_es
            else:
                active = def_en or def_es or ""
            active = abbreviations.expand(active, self.language)

            out.append({
                "lemma": lemma,
                "morphology": translate_morph_code(morph, self.language) if morph else "",
                "raw_morph": morph or "",
                "definition": active,
                "definition_en": def_en or "",
                "definition_es": def_es or "",
            })
        return out
