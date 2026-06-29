"""
Per-user study data: annotations, vocabulary flashcards and lookup history.

Stored in a separate SQLite database in the user-data directory so it survives
app upgrades and never collides with the read-only dictionary. Flashcards use a
simple Leitner spaced-repetition schedule (boxes 0-5).
"""

import csv
import os
import sqlite3
import threading
from datetime import date, datetime, timedelta

from core.data_paths import study_db_path
from core.logger import get_logger

log = get_logger(__name__)

# Days until a card is due again, indexed by Leitner box.
_LEITNER_INTERVALS = [0, 1, 2, 4, 8, 16]


class StudyStore:
    def __init__(self, path=None):
        self.path = path or study_db_path()
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        with self._lock:
            c = self._conn.cursor()
            c.executescript(
                """
                CREATE TABLE IF NOT EXISTS annotations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    start_pos INTEGER NOT NULL,
                    end_pos INTEGER NOT NULL,
                    anchor_text TEXT,
                    note TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_ann_file ON annotations(file_path);

                CREATE TABLE IF NOT EXISTS flashcards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lemma TEXT NOT NULL,
                    front TEXT NOT NULL,
                    back TEXT NOT NULL,
                    morphology TEXT,
                    box INTEGER NOT NULL DEFAULT 0,
                    due TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(lemma, front)
                );

                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lemma TEXT NOT NULL,
                    definition TEXT,
                    looked_at TEXT NOT NULL
                );
                """
            )
            self._conn.commit()

    def close(self):
        with self._lock:
            self._conn.close()

    # ----- annotations -------------------------------------------------
    def add_annotation(self, file_path, start, end, anchor_text, note):
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO annotations (file_path, start_pos, end_pos, anchor_text, note, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (file_path or "", start, end, anchor_text, note, datetime.now().isoformat()),
            )
            self._conn.commit()
            return cur.lastrowid

    def get_annotations(self, file_path):
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM annotations WHERE file_path = ? ORDER BY start_pos",
                (file_path or "",),
            ).fetchall()
            return [dict(r) for r in rows]

    def annotation_at(self, file_path, pos):
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM annotations WHERE file_path = ? AND start_pos <= ? AND end_pos >= ? "
                "ORDER BY (end_pos - start_pos) LIMIT 1",
                (file_path or "", pos, pos),
            ).fetchone()
            return dict(row) if row else None

    def delete_annotation(self, ann_id):
        with self._lock:
            self._conn.execute("DELETE FROM annotations WHERE id = ?", (ann_id,))
            self._conn.commit()

    # ----- flashcards --------------------------------------------------
    def add_flashcard(self, lemma, front, back, morphology=""):
        today = date.today().isoformat()
        with self._lock:
            try:
                cur = self._conn.execute(
                    "INSERT INTO flashcards (lemma, front, back, morphology, box, due, created_at) "
                    "VALUES (?, ?, ?, ?, 0, ?, ?)",
                    (lemma, front, back, morphology, today, datetime.now().isoformat()),
                )
                self._conn.commit()
                return cur.lastrowid
            except sqlite3.IntegrityError:
                return None  # already saved

    def get_flashcards(self):
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM flashcards ORDER BY created_at DESC"
            ).fetchall()
            return [dict(r) for r in rows]

    def due_flashcards(self):
        today = date.today().isoformat()
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM flashcards WHERE due <= ? ORDER BY box, due", (today,)
            ).fetchall()
            return [dict(r) for r in rows]

    def review_flashcard(self, card_id, correct):
        """Advance (correct) or reset (incorrect) the Leitner box and reschedule."""
        with self._lock:
            row = self._conn.execute(
                "SELECT box FROM flashcards WHERE id = ?", (card_id,)
            ).fetchone()
            if not row:
                return
            box = row["box"]
            box = min(box + 1, len(_LEITNER_INTERVALS) - 1) if correct else 0
            due = (date.today() + timedelta(days=_LEITNER_INTERVALS[box])).isoformat()
            self._conn.execute(
                "UPDATE flashcards SET box = ?, due = ? WHERE id = ?", (box, due, card_id)
            )
            self._conn.commit()

    def delete_flashcard(self, card_id):
        with self._lock:
            self._conn.execute("DELETE FROM flashcards WHERE id = ?", (card_id,))
            self._conn.commit()

    def count_flashcards(self):
        with self._lock:
            return self._conn.execute("SELECT COUNT(*) FROM flashcards").fetchone()[0]

    # ----- history -----------------------------------------------------
    def add_history(self, lemma, definition=""):
        with self._lock:
            self._conn.execute(
                "INSERT INTO history (lemma, definition, looked_at) VALUES (?, ?, ?)",
                (lemma, definition, datetime.now().isoformat()),
            )
            # Keep only the most recent 500 entries.
            self._conn.execute(
                "DELETE FROM history WHERE id NOT IN "
                "(SELECT id FROM history ORDER BY id DESC LIMIT 500)"
            )
            self._conn.commit()

    def get_history(self, limit=100):
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def clear_history(self):
        with self._lock:
            self._conn.execute("DELETE FROM history")
            self._conn.commit()

    # ----- export ------------------------------------------------------
    def export_flashcards_csv(self, path, anki=False):
        """Write flashcards to CSV. Anki mode = tab-separated 'front<TAB>back'."""
        cards = self.get_flashcards()
        with open(path, "w", encoding="utf-8", newline="") as f:
            if anki:
                writer = csv.writer(f, delimiter="\t")
                for c in cards:
                    back = c["back"]
                    if c["morphology"]:
                        back = f"{back} [{c['morphology']}]"
                    writer.writerow([c["front"], back])
            else:
                writer = csv.writer(f)
                writer.writerow(["lemma", "front", "back", "morphology", "box", "due"])
                for c in cards:
                    writer.writerow([
                        c["lemma"], c["front"], c["back"],
                        c["morphology"], c["box"], c["due"],
                    ])
        return len(cards)
