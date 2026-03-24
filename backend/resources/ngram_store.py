"""
Inserting 3GB of n-gram into the RAM can be a fucked up solution. It was needed to improve this, passing from 6.4GB into a 2.4GB RAM consumption.

Basically, we no longer use dicts (hashmaps are not THAT efficient), but to create an sqlite3 database where the ngrams are store and, if needed, retrieved
"""

import os
import sqlite3


def _parse_ngram_line(line, path):
    line = line.strip()
    if not line:
        return None

    if 'wiki' in path:
        pos = line.rfind(' ')
    else:
        pos = line.rfind('\t')

    if pos <= 0 or pos + 1 >= len(line):
        return None

    # Keep original parsing behavior for compatibility with existing model logic.
    key = line[0:pos - 1]
    freq_text = line[pos + 1]
    try:
        freq = int(freq_text)
    except ValueError:
        return None
    return key, freq


class NgramStore:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._total_count = self._read_meta_int('total_count', 1)
        self._max_freq = self._read_meta_int('max_freq', 1)

    def _read_meta_int(self, key, default):
        row = self.conn.execute('SELECT value FROM meta WHERE key = ?', (key,)).fetchone()
        if not row:
            return default
        try:
            return int(row['value'])
        except Exception:
            return default

    @property
    def total_count(self):
        return self._total_count

    @property
    def max_freq(self):
        return self._max_freq

    def __getitem__(self, key):
        row = self.conn.execute('SELECT freq FROM ngrams WHERE key = ?', (key,)).fetchone()
        if row is None:
            raise KeyError(key)
        return int(row['freq'])


def _is_valid_sqlite_db(db_path):
    if not os.path.exists(db_path):
        return False
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ngrams'")
        has_ngrams = cur.fetchone() is not None
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='meta'")
        has_meta = cur.fetchone() is not None
        if not (has_ngrams and has_meta):
            conn.close()
            return False
        cur.execute("SELECT COUNT(*) FROM meta WHERE key IN ('total_count', 'max_freq')")
        meta_count = cur.fetchone()[0]
        conn.close()
        return meta_count == 2
    except Exception:
        return False


def _build_sqlite_from_text(source_path, db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    tmp_db_path = db_path + '.tmp'
    if os.path.exists(tmp_db_path):
        os.remove(tmp_db_path)

    conn = sqlite3.connect(tmp_db_path)
    cur = conn.cursor()
    cur.execute('PRAGMA journal_mode = OFF')
    cur.execute('PRAGMA synchronous = OFF')
    cur.execute('PRAGMA temp_store = MEMORY')
    cur.execute('CREATE TABLE ngrams (key TEXT PRIMARY KEY, freq INTEGER NOT NULL)')
    cur.execute('CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)')

    total_count = 0
    max_freq = 1
    batch = []
    batch_size = 20000

    # insert the data from the .txt into the database
    with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
        for raw_line in f:
            parsed = _parse_ngram_line(raw_line, source_path)
            if not parsed:
                continue
            key, freq = parsed
            total_count += freq
            if freq > max_freq:
                max_freq = freq
            batch.append((key, freq))
            if len(batch) >= batch_size:
                cur.executemany('INSERT OR REPLACE INTO ngrams (key, freq) VALUES (?, ?)', batch)
                conn.commit()
                batch = []

    if batch:
        cur.executemany('INSERT OR REPLACE INTO ngrams (key, freq) VALUES (?, ?)', batch)

    cur.executemany(
        'INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)',
        [('total_count', str(total_count)), ('max_freq', str(max_freq))],
    )
    cur.execute('CREATE INDEX IF NOT EXISTS idx_ngrams_key ON ngrams(key)')
    conn.commit()
    conn.close()

    os.replace(tmp_db_path, db_path)


def load_ngram_resource(source_path, backend='dict'):
    backend = (backend or 'dict').strip().lower()
    if backend != 'sqlite':
        return _load_ngram_dict(source_path)

    db_path = source_path + '.sqlite'
    if not _is_valid_sqlite_db(db_path):
        if os.path.exists(db_path):
            os.remove(db_path)
        _build_sqlite_from_text(source_path, db_path)

    return NgramStore(db_path)


def _load_ngram_dict(path):
    dic = {}
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            parsed = _parse_ngram_line(line, path)
            if not parsed:
                continue
            key, freq = parsed
            dic[key] = freq
    return dic
