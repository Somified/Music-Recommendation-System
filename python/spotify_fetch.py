import pandas as pd
from pathlib import Path

# ── LOAD KAGGLE DATASET ───────────────────────────────────────────────
# Download from:
# kaggle.com/datasets/maharshipandya/spotify-tracks-dataset
# Place the downloaded file in your data/ folder as spotify_kaggle.csv
# ─────────────────────────────────────────────────────────────────────

data_dir    = Path(__file__).resolve().parent.parent / 'data'
kaggle_path = data_dir / 'spotify_kaggle.csv'

df = pd.read_csv(kaggle_path)

print(f"Loaded Kaggle dataset: {len(df)} songs")
print(f"Columns: {list(df.columns)}\n")

# ── SONGS WE WANT ─────────────────────────────────────────────────────
SONGS = [
    ("Blinding Lights",        "The Weeknd"),
    ("Shape of You",           "Ed Sheeran"),
    ("Bohemian Rhapsody",      "Queen"),
    ("Levitating",             "Dua Lipa"),
    ("Hotel California",       "Eagles"),
    ("Starboy",                "The Weeknd"),
    ("bad guy",                "Billie Eilish"),
    ("Watermelon Sugar",       "Harry Styles"),
    ("Smells Like Teen Spirit","Nirvana"),
    ("Stay With Me",           "Sam Smith"),
    ("As It Was",              "Harry Styles"),
    ("Peaches",                "Justin Bieber"),
    ("golden hour",            "JVKE"),
    ("Anti-Hero",              "Taylor Swift"),
    ("Flowers",                "Miley Cyrus"),
    ("Cruel Summer",           "Taylor Swift"),
    ("Heat Waves",             "Glass Animals"),
    ("Shivers",                "Ed Sheeran"),
    ("Believer",               "Imagine Dragons"),
    ("Unstoppable",            "Sia"),
]
# ─────────────────────────────────────────────────────────────────────


def find_song(df, name, artist):
    """
    Search the Kaggle dataset for a song by name and artist.
    Case-insensitive match. Returns the first matching row.
    """
    mask = (
        df['track_name'].str.lower()   == name.lower()
    ) & (
        df['artists'].str.lower().str.contains(artist.lower())
    )
    results = df[mask]
    return results.iloc[0] if len(results) > 0 else None


def main():
    rows = []

    for name, artist in SONGS:
        row = find_song(df, name, artist)

        if row is None:
            print(f"  NOT FOUND: {name} — {artist}")
            continue

        print(f"  Found: {row['track_name']} — {row['artists']}")

        rows.append({
            'name':         row['track_name'],
            'artist':       row['artists'],
            # ── Audio features — real Spotify values from Kaggle ──────
            'energy':       round(float(row['energy']),        4),
            'danceability': round(float(row['danceability']),  4),
            'valence':      round(float(row['valence']),       4),
            'acousticness': round(float(row['acousticness']),  4),
            # Normalise tempo: BPM ÷ 200 → [0,1]
            'tempo':        round(float(row['tempo']) / 200.0, 4),
            # Popularity → rating 1–5
            'popularity':   int(row['popularity']),
            'rating':       max(1, min(5, int(row['popularity']) // 20 + 1)),
        })

    result_df = pd.DataFrame(rows)

    # ── Save songs.csv — MATLAB reads this for Pillars 1 and 2 ────────
    songs_df = result_df[['name', 'artist', 'energy', 'danceability',
                           'valence', 'acousticness', 'tempo']]
    songs_df.to_csv(data_dir / 'songs.csv', index=False)
    print(f"\nSaved songs.csv  ({len(songs_df)} songs)")

    # ── Save ratings.csv — MATLAB reads this for Pillar 3 ─────────────
    ratings_df = result_df[['name', 'artist', 'popularity', 'rating']]
    ratings_df.to_csv(data_dir / 'ratings.csv', index=False)
    print(f"Saved ratings.csv  ({len(ratings_df)} songs)")

    print("\nFull dataset:")
    print(result_df[['name', 'energy', 'danceability',
                      'valence', 'acousticness', 'tempo', 'rating']
                    ].to_string(index=False))


if __name__ == "__main__":
    main()