import urllib.request
import json
import sqlite3
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.greek_utils import normalize_lookup  # noqa: E402
from db.schema import CREATE_WORDS  # noqa: E402

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "logos_dict.db")

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def download_data():
    url = "https://raw.githubusercontent.com/perseids-project/lsj-js/master/vendor/lsj.json"
    print(f"Downloading from {url}...")
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = response.read()
    except Exception as e:
        print(f"Error downloading: {e}")
        return
        
    print("Download complete. Parsing JSON...")
    try:
        parsed_data = json.loads(data)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return
        
    print(f"Loaded {len(parsed_data)} dictionary entries.")
    
    # Connect to DB
    print(f"Connecting to database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure the table exists, then clear it.
    cursor.execute(CREATE_WORDS)
    print("Clearing existing data...")
    cursor.execute("DELETE FROM words")
    
    records_to_insert = []
    
    print("Preparing records...")
    for idx, (lemma, info) in enumerate(parsed_data.items()):
        # Basic progress indicator
        if idx > 0 and idx % 20000 == 0:
            print(f"Processed {idx} / {len(parsed_data)} lemmas...")
            
        definition = clean_html(info.get("d", ""))
        morph_code = "" # LSJ does not have POS tags in a simple field
        
        # LSJ json maps lemmas to definitions.
        # We will add the lemma itself as a form.
        forms_to_add = set()
        
        # Strip trailing numeric markers common in LSJ keys
        clean_lemma = lemma.split(' ')[0] if ' ' in lemma else lemma
        forms_to_add.add(clean_lemma)
        
        # Add any alternate forms
        for g_form in info.get("g", []):
            if g_form:
                forms_to_add.add(g_form.split(' ')[0] if ' ' in g_form else g_form)
        for m_form in info.get("m", []):
            if m_form:
                forms_to_add.add(m_form.split(' ')[0] if ' ' in m_form else m_form)
                
        for f in forms_to_add:
            # Replaces any special HTML entities like &nbsp;
            final_def = definition.replace('&nbsp;', ' ')
            records_to_insert.append((f, normalize_lookup(f), clean_lemma, morph_code, final_def))

    print(f"Inserting {len(records_to_insert)} records into database. This might take a few seconds...")

    cursor.executemany('''
        INSERT INTO words (form, form_norm, lemma, morph_code, definition)
        VALUES (?, ?, ?, ?, ?)
    ''', records_to_insert)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_words_form_norm ON words(form_norm)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_words_lemma ON words(lemma)")
    conn.commit()
    conn.close()
    
    print("Database population complete!")

if __name__ == "__main__":
    download_data()
