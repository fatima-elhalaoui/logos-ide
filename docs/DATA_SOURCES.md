# Data sources and licensing

Logos IDE ships code under the MIT license, but its **dictionary data** comes
from scholarly sources with their own terms. Please respect them when
redistributing the database.

## Dictionary (lexicon)

- **Liddell–Scott–Jones (LSJ) Greek–English Lexicon**, as digitised and published
  by the **Perseus Digital Library**, Tufts University.
- License: **Creative Commons Attribution‑ShareAlike 3.0 (CC BY‑SA 3.0)**.
- The English definitions in `logos_dict.db` are derived from this source.

## Morphology

- Greek morphological analyses derive from the Perseus / Morpheus project data,
  also under **CC BY‑SA 3.0**.
- The optional morphology data pack is built by `scripts/import_morphology.py`.

## Spanish definitions

- The Spanish definitions are **machine translations** of the English LSJ
  definitions and are provided for study convenience only. They are being
  progressively improved by `scripts/regenerate_spanish.py`, which masks the
  inline Greek so it is never mangled by the translator.
- Treat the Spanish text as a derivative of the CC BY‑SA 3.0 source.

## Rebuilding the database from scratch

1. `python scripts/build_database.py` — downloads the LSJ JSON and builds the
   `words` table (forms → lemma → English definition).
2. `python scripts/regenerate_spanish.py` — fills/repairs Spanish definitions
   (online; resumable; no API key required).
3. `python scripts/import_morphology.py` — adds morphology codes (optional).
4. `python -m db.schema` — rebuilds the small committed seed database.

## Attribution requirement

If you redistribute the dictionary database (for example as a release asset),
include this notice and a link to the Perseus Digital Library, and keep the
CC BY‑SA 3.0 license on the data.
