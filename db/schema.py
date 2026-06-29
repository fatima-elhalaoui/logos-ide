"""
Dictionary database schema, migration and seed-data builder.

The shipped database has one table, ``words``, mapping inflected/variant Greek
forms to a lemma, an (optional) morphology code and English + Spanish
definitions. For accent-insensitive lookup we add a ``form_norm`` column holding
the normalised key (see :func:`core.greek_utils.normalize_lookup`).

``ensure_dictionary_schema`` is idempotent: it adds the column and index to an
existing 575k-row database exactly once, then is essentially free on later runs.
"""

import os
import sqlite3

from core.greek_utils import normalize_lookup

# Path to the seed DB committed in the repo (the full DB is resolved elsewhere).
SEED_DB_PATH = os.path.join(os.path.dirname(__file__), "logos_dict.seed.db")

CREATE_WORDS = """
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form TEXT NOT NULL,
    form_norm TEXT,
    lemma TEXT NOT NULL,
    morph_code TEXT,
    definition TEXT,
    definition_es TEXT
)
"""


def _column_names(cursor, table):
    cursor.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cursor.fetchall()}


def _index_names(cursor, table):
    cursor.execute(f"PRAGMA index_list({table})")
    return {row[1] for row in cursor.fetchall()}


def ensure_dictionary_schema(conn, progress=None):
    """Ensure ``words`` has ``form_norm`` populated and indexed.

    *progress* is an optional callable ``progress(done, total)`` invoked during a
    first-time backfill so the UI can show "preparing dictionary…".
    Returns True if a (potentially slow) backfill was performed.
    """
    conn.create_function("norm", 1, normalize_lookup, deterministic=True)
    cur = conn.cursor()
    cur.execute(CREATE_WORDS)

    cols = _column_names(cur, "words")
    did_backfill = False
    if "form_norm" not in cols:
        cur.execute("ALTER TABLE words ADD COLUMN form_norm TEXT")
        conn.commit()
        cols.add("form_norm")

    # Backfill any rows whose form_norm is missing.
    cur.execute("SELECT COUNT(*) FROM words WHERE form_norm IS NULL OR form_norm = ''")
    missing = cur.fetchone()[0]
    if missing:
        did_backfill = True
        cur.execute("SELECT COUNT(*) FROM words")
        total = cur.fetchone()[0]
        # Update in a single SQL statement using the registered function.
        cur.execute(
            "UPDATE words SET form_norm = norm(form) "
            "WHERE form_norm IS NULL OR form_norm = ''"
        )
        conn.commit()
        if progress:
            progress(total, total)

    indexes = _index_names(cur, "words")
    if "idx_words_form_norm" not in indexes:
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_words_form_norm ON words(form_norm)"
        )
    if "idx_words_lemma" not in indexes:
        cur.execute("CREATE INDEX IF NOT EXISTS idx_words_lemma ON words(lemma)")
    conn.commit()
    return did_backfill


# ---------------------------------------------------------------------------
# Seed database (committed to git so the app works immediately after clone).
# ---------------------------------------------------------------------------

# A compact, high-frequency starter vocabulary covering both Classical and
# Koine usage. Format: (form, lemma, morph_code, definition_en, definition_es)
SEED_WORDS = [
    ("λόγος", "λόγος", "N-NSM", "word, speech, account, reason", "palabra, discurso, razón"),
    ("λόγου", "λόγος", "N-GSM", "of a word", "de la palabra"),
    ("λόγῳ", "λόγος", "N-DSM", "to/for a word", "a/para la palabra"),
    ("λόγον", "λόγος", "N-ASM", "word (object)", "palabra (objeto)"),
    ("λόγοι", "λόγος", "N-NPM", "words", "palabras"),
    ("ἀρχή", "ἀρχή", "N-NSF", "beginning, origin, rule, power", "principio, origen, poder"),
    ("ἀρχῇ", "ἀρχή", "N-DSF", "in the beginning", "en el principio"),
    ("θεός", "θεός", "N-NSM", "god, God", "dios, Dios"),
    ("θεοῦ", "θεός", "N-GSM", "of god", "de dios"),
    ("θεόν", "θεός", "N-ASM", "god (object)", "dios (objeto)"),
    ("ἄνθρωπος", "ἄνθρωπος", "N-NSM", "human being, man", "ser humano, hombre"),
    ("ἀνθρώπου", "ἄνθρωπος", "N-GSM", "of a human", "del hombre"),
    ("ἀνθρώπων", "ἄνθρωπος", "N-GPM", "of humans", "de los hombres"),
    ("εἰμί", "εἰμί", "V-PAI-1S", "I am", "soy, estoy"),
    ("ἐστί", "εἰμί", "V-PAI-3S", "he/she/it is", "es, está"),
    ("ἐστίν", "εἰμί", "V-PAI-3S", "he/she/it is", "es, está"),
    ("ἦν", "εἰμί", "V-IAI-3S", "he/she/it was", "era, estaba"),
    ("εἰσί", "εἰμί", "V-PAI-3P", "they are", "son, están"),
    ("λέγω", "λέγω", "V-PAI-1S", "I say, I speak", "digo, hablo"),
    ("λέγει", "λέγω", "V-PAI-3S", "he/she says", "dice"),
    ("εἶπεν", "λέγω", "V-2AAI-3S", "he/she said", "dijo"),
    ("γράφω", "γράφω", "V-PAI-1S", "I write", "escribo"),
    ("ἔχω", "ἔχω", "V-PAI-1S", "I have, I hold", "tengo, sostengo"),
    ("ἔχει", "ἔχω", "V-PAI-3S", "he/she has", "tiene"),
    ("ποιέω", "ποιέω", "V-PAI-1S", "I make, I do", "hago, produzco"),
    ("φέρω", "φέρω", "V-PAI-1S", "I carry, I bear", "llevo, porto"),
    ("ἄγω", "ἄγω", "V-PAI-1S", "I lead, I bring", "conduzco, llevo"),
    ("καί", "καί", "CONJ", "and, also, even", "y, también, incluso"),
    ("δέ", "δέ", "CONJ", "but, and", "pero, y"),
    ("γάρ", "γάρ", "CONJ", "for, because", "pues, porque"),
    ("οὐ", "οὐ", "PRT-N", "not", "no"),
    ("μή", "μή", "PRT-N", "not (with non-indicative)", "no"),
    ("ἐν", "ἐν", "PREP", "in, among (+ dative)", "en, entre (+ dativo)"),
    ("εἰς", "εἰς", "PREP", "into, to (+ accusative)", "hacia, a (+ acusativo)"),
    ("ἐκ", "ἐκ", "PREP", "out of, from (+ genitive)", "desde, de (+ genitivo)"),
    ("πρός", "πρός", "PREP", "to, toward (+ accusative)", "hacia, a (+ acusativo)"),
    ("διά", "διά", "PREP", "through (+gen), because of (+acc)", "a través de, por causa de"),
    ("ὁ", "ὁ", "T-NSM", "the (masculine)", "el (masculino)"),
    ("ἡ", "ὁ", "T-NSF", "the (feminine)", "la (femenino)"),
    ("τό", "ὁ", "T-NSN", "the (neuter)", "lo (neutro)"),
    ("τοῦ", "ὁ", "T-GSM", "of the", "del"),
    ("αὐτός", "αὐτός", "P-NSM", "he, self, same", "él, mismo"),
    ("πᾶς", "πᾶς", "A-NSM", "all, every", "todo, cada"),
    ("μέγας", "μέγας", "A-NSM", "great, large", "grande"),
    ("καλός", "καλός", "A-NSM", "beautiful, good, noble", "hermoso, bueno, noble"),
    ("ἀγαθός", "ἀγαθός", "A-NSM", "good", "bueno"),
    ("πόλις", "πόλις", "N-NSF", "city, city-state", "ciudad, ciudad-estado"),
    ("πόλεως", "πόλις", "N-GSF", "of a city", "de la ciudad"),
    ("ἀνήρ", "ἀνήρ", "N-NSM", "man, husband", "hombre, marido"),
    ("ἀνδρός", "ἀνήρ", "N-GSM", "of a man", "del hombre"),
    ("γυνή", "γυνή", "N-NSF", "woman, wife", "mujer, esposa"),
    ("παῖς", "παῖς", "N-NSM", "child, boy, slave", "niño, muchacho, esclavo"),
    ("ψυχή", "ψυχή", "N-NSF", "soul, life", "alma, vida"),
    ("σῶμα", "σῶμα", "N-NSN", "body", "cuerpo"),
    ("χείρ", "χείρ", "N-NSF", "hand", "mano"),
    ("ἡμέρα", "ἡμέρα", "N-NSF", "day", "día"),
    ("νύξ", "νύξ", "N-NSF", "night", "noche"),
    ("οὐρανός", "οὐρανός", "N-NSM", "heaven, sky", "cielo"),
    ("γῆ", "γῆ", "N-NSF", "earth, land", "tierra"),
    ("ὕδωρ", "ὕδωρ", "N-NSN", "water", "agua"),
    ("πῦρ", "πῦρ", "N-NSN", "fire", "fuego"),
    ("βασιλεύς", "βασιλεύς", "N-NSM", "king", "rey"),
    ("δοῦλος", "δοῦλος", "N-NSM", "slave, servant", "esclavo, siervo"),
    ("φίλος", "φίλος", "N-NSM", "friend; dear", "amigo; querido"),
    ("πατήρ", "πατήρ", "N-NSM", "father", "padre"),
    ("μήτηρ", "μήτηρ", "N-NSF", "mother", "madre"),
    ("ἀδελφός", "ἀδελφός", "N-NSM", "brother", "hermano"),
    ("σοφία", "σοφία", "N-NSF", "wisdom", "sabiduría"),
    ("ἀλήθεια", "ἀλήθεια", "N-NSF", "truth", "verdad"),
    ("ἀγάπη", "ἀγάπη", "N-NSF", "love", "amor"),
    ("εἰρήνη", "εἰρήνη", "N-NSF", "peace", "paz"),
    ("δύναμις", "δύναμις", "N-NSF", "power, ability", "poder, capacidad"),
    ("χρόνος", "χρόνος", "N-NSM", "time", "tiempo"),
    ("κόσμος", "κόσμος", "N-NSM", "world, order, adornment", "mundo, orden"),
    ("ὁδός", "ὁδός", "N-NSF", "road, way, journey", "camino, vía"),
    ("φωνή", "φωνή", "N-NSF", "voice, sound", "voz, sonido"),
    ("ὄνομα", "ὄνομα", "N-NSN", "name", "nombre"),
    ("ἔργον", "ἔργον", "N-NSN", "work, deed", "trabajo, obra"),
    ("βιβλίον", "βιβλίον", "N-NSN", "book, scroll", "libro, rollo"),
    ("γιγνώσκω", "γιγνώσκω", "V-PAI-1S", "I know, I recognise", "conozco, reconozco"),
    ("ὁράω", "ὁράω", "V-PAI-1S", "I see", "veo"),
    ("ἀκούω", "ἀκούω", "V-PAI-1S", "I hear", "oigo, escucho"),
    ("δίδωμι", "δίδωμι", "V-PAI-1S", "I give", "doy"),
    ("λαμβάνω", "λαμβάνω", "V-PAI-1S", "I take, I receive", "tomo, recibo"),
    ("ἔρχομαι", "ἔρχομαι", "V-PNI-1S", "I come, I go", "vengo, voy"),
    ("γίγνομαι", "γίγνομαι", "V-PNI-1S", "I become, I happen", "llego a ser, sucedo"),
    ("βούλομαι", "βούλομαι", "V-PNI-1S", "I wish, I want", "quiero, deseo"),
    ("δύναμαι", "δύναμαι", "V-PNI-1S", "I am able, I can", "puedo"),
]


def build_seed_db(path=SEED_DB_PATH):
    """(Re)create the small seed dictionary committed to the repository."""
    if os.path.exists(path):
        os.remove(path)
    conn = sqlite3.connect(path)
    try:
        cur = conn.cursor()
        cur.execute(CREATE_WORDS)
        rows = [
            (form, normalize_lookup(form), lemma, morph, en, es)
            for (form, lemma, morph, en, es) in SEED_WORDS
        ]
        cur.executemany(
            "INSERT INTO words (form, form_norm, lemma, morph_code, definition, definition_es) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            rows,
        )
        cur.execute("CREATE INDEX idx_words_form_norm ON words(form_norm)")
        cur.execute("CREATE INDEX idx_words_lemma ON words(lemma)")
        conn.commit()
    finally:
        conn.close()
    return path


if __name__ == "__main__":
    p = build_seed_db()
    print(f"Seed database written to {p} with {len(SEED_WORDS)} entries.")
