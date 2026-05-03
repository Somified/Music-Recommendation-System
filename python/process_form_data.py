"""
FILE: process_form_data.py
Run from /python folder:
    python process_form_data.py
"""

import pandas as pd
import numpy as np
import re
import os
from pathlib import Path

# ── Load .env ─────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
except ImportError:
    pass

# ── Paths ─────────────────────────────────────────────────────────────────
BASE          = Path(__file__).parent.parent / "data"
FORM_CSV      = BASE / "form_responses.csv"
SONGS_CSV     = BASE / "songs.csv"
OUT_RATINGS   = BASE / "ratings.csv"
OUT_USERNAMES = BASE / "usernames.csv"
OUT_UNMATCHED = BASE / "unmatched_songs.csv"

# ── Step 1: Load songs.csv and auto-detect the song name column ───────────
songs_df = pd.read_csv(SONGS_CSV)

print(f"songs.csv columns: {list(songs_df.columns)}")

# Try common column names for song title (Kaggle uses 'track_name')
POSSIBLE_NAME_COLS = ['track_name', 'name', 'title', 'song', 'song_name', 'track']
SONGS_NAME_COL = None
for col in POSSIBLE_NAME_COLS:
    if col in songs_df.columns:
        SONGS_NAME_COL = col
        break

if SONGS_NAME_COL is None:
    # Last resort: just use the first string column
    for col in songs_df.columns:
        if songs_df[col].dtype == object:
            SONGS_NAME_COL = col
            break

if SONGS_NAME_COL is None:
    raise ValueError(f"Cannot find a song name column in songs.csv. Columns are: {list(songs_df.columns)}")

print(f"Using song name column: '{SONGS_NAME_COL}'\n")

# Also detect feature columns for later use
FEATURE_COLS = []
for col in ['tempo', 'energy', 'danceability', 'valence', 'acousticness', 'speechiness']:
    if col in songs_df.columns:
        FEATURE_COLS.append(col)
print(f"Feature columns found: {FEATURE_COLS}")

song_names       = songs_df[SONGS_NAME_COL].tolist()
song_names_clean = [str(n).encode('ascii','ignore').decode('ascii').strip().lower() for n in song_names]
print(f"Loaded {len(song_names)} songs from songs.csv\n")

# ── Step 2: Smart CSV loading ─────────────────────────────────────────────
def find_header_row(csv_path):
    for i in range(5):
        try:
            df = pd.read_csv(csv_path, header=i, nrows=2, encoding='utf-8-sig')
            cols = " ".join(str(c).lower() for c in df.columns)
            if any(kw in cols for kw in ['name', 'song', 'fav', 'favourite', 'music', 'give']):
                print(f"Header row detected at index {i}")
                return i
        except Exception:
            continue
    return 0

header_row = find_header_row(FORM_CSV)
form_df    = pd.read_csv(FORM_CSV, header=header_row, encoding='utf-8-sig')
print(f"Form shape: {form_df.shape}")
print(f"Columns: {list(form_df.columns)}\n")

# ── Step 3: Identify name + song columns ─────────────────────────────────
def find_name_col(df):
    for i, col in enumerate(df.columns):
        if any(kw in str(col).lower() for kw in ['name', 'your name', 'give']):
            return i
    return 0

def find_song_cols(df, name_idx):
    idxs = []
    for i, col in enumerate(df.columns):
        if i == name_idx:
            continue
        col_l = str(col).lower()
        if any(kw in col_l for kw in ['timestamp', 'time', 'email']):
            continue
        idxs.append(i)
    return idxs[:10]

name_col_idx  = find_name_col(form_df)
song_col_idxs = find_song_cols(form_df, name_col_idx)
print(f"Name column : [{name_col_idx}] '{form_df.columns[name_col_idx]}'")
print(f"Song columns: {[form_df.columns[i] for i in song_col_idxs]}\n")

# ── Step 4: Clean user names ──────────────────────────────────────────────
SKIP_KW = ['name if you', 'your name', 'fav song', 'favourite', 'song 1',
           'enter your', 'column', 'unnamed', 'fav song']

def clean_username(raw):
    n = str(raw).strip()
    if not n or n.lower() in ('nan', 'n/a', 'na', '-', 'none', ''):
        return 'Anonymous'
    if any(kw in n.lower() for kw in SKIP_KW):
        return None
    return n

raw_names  = form_df.iloc[:, name_col_idx].tolist()
users      = []
valid_rows = []
anon_count = 0

for i, raw in enumerate(raw_names):
    u = clean_username(raw)
    if u is None:
        continue
    if u == 'Anonymous':
        anon_count += 1
        users.append(f'Anonymous_{anon_count}')
    else:
        users.append(u)
    valid_rows.append(i)

song_cols = form_df.iloc[valid_rows, song_col_idxs].reset_index(drop=True)
print(f"Valid users : {len(users)}")
print(f"Sample      : {users[:6]}\n")

# ── Step 5: Matching helpers ──────────────────────────────────────────────
def strip_emojis(text):
    return str(text).encode('ascii', 'ignore').decode('ascii').strip()

def split_multiple(raw):
    return [p.strip() for p in re.split(r'[/,&\n]+', str(raw)) if p.strip()]

def extract_candidates(raw):
    raw = strip_emojis(raw).strip()
    if not raw:
        return []
    cands = [raw.lower()]
    for sep in [' - ', ' – ', ' | ', ' by ', ': ']:
        if sep.lower() in raw.lower():
            for p in re.split(re.escape(sep), raw, flags=re.IGNORECASE, maxsplit=1):
                p = p.strip().lower()
                if p and p not in cands:
                    cands.append(p)
    no_feat = re.sub(r'\s*(feat\.|ft\.|featuring)\s*.*', '', raw, flags=re.IGNORECASE).strip().lower()
    if no_feat and no_feat not in cands:
        cands.append(no_feat)
    no_bracket = re.sub(r'[\(\[\{].*?[\)\]\}]', '', raw).strip().lower()
    if no_bracket and no_bracket not in cands:
        cands.append(no_bracket)
    return cands

def match_song(candidate, names_clean):
    c = candidate.strip().lower()
    if not c or len(c) < 2:
        return -1
    if c in names_clean:
        return names_clean.index(c)
    for j, s in enumerate(names_clean):
        if s and s in c:
            return j
    if len(c) >= 4:
        for j, s in enumerate(names_clean):
            if c in s:
                return j
    return -1

# ── Step 6: Build R matrix ────────────────────────────────────────────────
n_users       = len(users)
n_songs       = len(song_names)
R             = np.zeros((n_users, n_songs), dtype=int)
unmatched_log = []

for i, row in song_cols.iterrows():
    for col in song_cols.columns:
        raw = str(row[col]).strip()
        if not raw or raw.lower() in ('nan', 'n/a', ''):
            continue
        for part in split_multiple(raw):
            cands   = extract_candidates(part)
            matched = False
            for cand in cands:
                j = match_song(cand, song_names_clean)
                if j != -1:
                    R[i, j] = 1
                    matched  = True
                    break
            if not matched:
                unmatched_log.append({
                    'user':      users[i],
                    'raw_entry': str(row[col]),
                    'cleaned':   part
                })

# ── Step 7: Correlation matrices ─────────────────────────────────────────
print("\nBuilding correlation matrices...")
if R.sum() > 0:
    # Song-song: how often songs are liked together
    with np.errstate(invalid='ignore', divide='ignore'):
        C_songs = np.corrcoef(R.T)          # n_songs × n_songs
        C_users = np.corrcoef(R)            # n_users × n_users
    C_songs = np.nan_to_num(C_songs)
    C_users = np.nan_to_num(C_users)

    # Save correlation matrices
    pd.DataFrame(C_songs, index=song_names, columns=song_names).to_csv(BASE / "corr_songs.csv")
    pd.DataFrame(C_users, index=users,      columns=users     ).to_csv(BASE / "corr_users.csv")
    print(f"  Song-song correlation: {C_songs.shape}  → saved corr_songs.csv")
    print(f"  User-user correlation: {C_users.shape}  → saved corr_users.csv")
else:
    print("  Skipped (no matches yet — run again after fixing unmatched songs)")

# ── Step 8: Save R matrix + usernames ────────────────────────────────────
print(f"\nR matrix : {n_users} users × {n_songs} songs")
print(f"Matched  : {int(R.sum())} entries")
print(f"Unmatched: {len(unmatched_log)} entries")

ratings_df = pd.DataFrame(R, columns=song_names, index=users)
ratings_df.index.name = 'username'
ratings_df.to_csv(OUT_RATINGS)
print(f"\nSaved: {OUT_RATINGS}")

pd.DataFrame({'username': users}).to_csv(OUT_USERNAMES, index=False)
print(f"Saved: {OUT_USERNAMES}")

if unmatched_log:
    pd.DataFrame(unmatched_log).drop_duplicates(subset=['cleaned']).to_csv(OUT_UNMATCHED, index=False)
    print(f"Saved: {OUT_UNMATCHED}  ← review these")

print("\nDone! Run main.m in MATLAB  or  streamlit run app.py")