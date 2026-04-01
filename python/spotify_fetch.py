import pandas as pd
from pathlib import Path

data_dir    = Path(__file__).resolve().parent.parent / 'data'
kaggle_path = data_dir / 'spotify_kaggle.csv'

df = pd.read_csv(kaggle_path)

print(f"Loaded Kaggle dataset: {len(df)} songs")
print(f"Columns: {list(df.columns)}\n")

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


def find_song(df: pd.DataFrame, name: str, artist: str) -> pd.Series | None:
    name_lower   = name.lower()
    artist_lower = artist.lower()

    mask = (
        (df['track_name'].str.lower() == name_lower) &
        (df['artists'].str.lower().str.contains(artist_lower, regex=False))
    )
    results = df[mask]

    if results.empty:
        mask = (
            df['track_name'].str.lower().str.contains(name_lower, regex=False) &
            df['artists'].str.lower().str.contains(artist_lower, regex=False)
        )
        results = df[mask]

    if results.empty:
        return None

    return results.loc[results['popularity'].idxmax()]


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
            'energy':       round(float(row['energy']),        4),
            'danceability': round(float(row['danceability']),  4),
            'valence':      round(float(row['valence']),       4),
            'acousticness': round(float(row['acousticness']),  4),
            'tempo':        round(float(row['tempo']) / 200.0, 4),
            'popularity':   int(row['popularity']),
            'rating':       max(1, min(5, int(row['popularity']) // 20 + 1)),
        })

    if not rows:
        print("\nNo songs found — check that spotify_kaggle.csv is present.")
        return

    result_df = pd.DataFrame(rows)

    result_df = (
        result_df
        .sort_values('popularity', ascending=False)
        .drop_duplicates(subset='name', keep='first')
        .reset_index(drop=True)
    )

    songs_df = result_df[['name', 'artist', 'energy', 'danceability',
                           'valence', 'acousticness', 'tempo']]
    songs_df.to_csv(data_dir / 'songs.csv', index=False)
    print(f"\nSaved songs.csv  ({len(songs_df)} songs)")

    ratings_df = result_df[['name', 'artist', 'popularity', 'rating']]
    ratings_df.to_csv(data_dir / 'ratings.csv', index=False)
    print(f"Saved ratings.csv  ({len(ratings_df)} songs)")

    print("\nFull dataset:")
    print(result_df[['name', 'energy', 'danceability',
                      'valence', 'acousticness', 'tempo', 'rating']
                    ].to_string(index=False))


if __name__ == "__main__":
    main()