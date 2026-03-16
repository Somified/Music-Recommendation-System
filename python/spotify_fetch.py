import os
import spotipy
import pandas as pd
import numpy as np
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

# ── LOAD CREDENTIALS FROM .env ────────────────────────────────────────
# load_dotenv() reads the .env file and makes those values available
# via os.getenv(). This way credentials never appear in your code.
load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))
# ─────────────────────────────────────────────────────────────────────


# ── SONG LIST ─────────────────────────────────────────────────────────
# Add artist name after the song title for more accurate search results.
# Spotify's search is fuzzy — adding the artist avoids wrong matches
# e.g. "Stay With Me" returns Sam Smith not some random cover.
SONGS = [
    "Blinding Lights The Weeknd",
    "Shape of You Ed Sheeran",
    "Bohemian Rhapsody Queen",
    "Levitating Dua Lipa",
    "Hotel California Eagles",
    "Starboy The Weeknd",
    "Bad Guy Billie Eilish",
    "Watermelon Sugar Harry Styles",
    "Smells Like Teen Spirit Nirvana",
    "Stay With Me Sam Smith",
    "As It Was Harry Styles",
    "Peaches Justin Bieber",
    "Golden Hour JVKE",
    "Anti-Hero Taylor Swift",
    "Flowers Miley Cyrus",
    "Cruel Summer Taylor Swift",
    "Heat Waves Glass Animals",
    "Shivers Ed Sheeran",
    "Believer Imagine Dragons",
    "Unstoppable Sia",
]
# ─────────────────────────────────────────────────────────────────────


def search_track(song_query):
    """
    Search Spotify for a song and return its track ID and display info.

    sp.search() hits the Spotify search endpoint — same as typing
    in the Spotify search bar. We take limit=1 (top result only).

    Returns a dict with id, name, artist — or None if not found.
    """
    results = sp.search(q=song_query, type='track', limit=1)
    items   = results['tracks']['items']

    if not items:
        return None

    track = items[0]
    return {
        'id':     track['id'],
        'name':   track['name'],
        'artist': track['artists'][0]['name'],
    }


def get_audio_features(track_id):
    """
    Fetch Spotify's audio analysis for a track by its ID.

    sp.audio_features() hits the /audio-features endpoint.
    Spotify computes these by running signal processing on the
    actual audio waveform — they are not metadata, they are
    mathematically derived from the sound itself.

    We extract 5 features for the song feature vector (Pillars 1+2)
    and popularity for the rating proxy (Pillar 3).
    """
    features = sp.audio_features(track_id)[0]
    if not features:
        return None

    return {
        # ── Feature vector components (all naturally 0–1) ─────────────
        'energy':        features['energy'],
        # Detected from beat regularity and rhythm patterns
        'danceability':  features['danceability'],
        # Perceptual positivity — cheerful vs dark
        'valence':       features['valence'],
        # Confidence of no electronic amplification
        'acousticness':  features['acousticness'],
        # BPM divided by 200 to normalise into [0,1] range
        # Raw BPM would dominate cosine similarity unfairly
        'tempo':         round(features['tempo'] / 200.0, 4),
    }


def get_popularity(track_id):
    """
    Fetch the popularity score for a track (0–100).

    Spotify recalculates this regularly based on total plays
    and how recent those plays are — it decays over time.
    We bucket it into 1–5 to use as a rating in Pillar 3.

    Bucketing logic:
      0–20  → 1 star
      21–40 → 2 stars
      41–60 → 3 stars
      61–80 → 4 stars
      81–100 → 5 stars
    """
    track = sp.track(track_id)
    raw   = track['popularity']            # integer 0–100
    rating = int(np.ceil(raw / 20))        # scale to 1–5
    rating = max(1, min(5, rating))        # clamp to valid range
    return raw, rating


def fetch_all(song_list):
    """
    Main loop — fetch everything for every song in the list.
    Returns a list of dicts, one per successfully fetched song.
    """
    rows = []

    for query in song_list:
        print(f"Searching: {query}")

        # ── Step 1: find the track on Spotify ─────────────────────────
        track_info = search_track(query)
        if track_info is None:
            print(f"  Not found — skipping\n")
            continue

        print(f"  Found:  {track_info['name']} by {track_info['artist']}")

        # ── Step 2: get audio features ─────────────────────────────────
        audio = get_audio_features(track_info['id'])
        if audio is None:
            print(f"  No audio features — skipping\n")
            continue

        # ── Step 3: get popularity → rating ───────────────────────────
        popularity, rating = get_popularity(track_info['id'])

        # ── Assemble the row ───────────────────────────────────────────
        row = {
            'name':          track_info['name'],
            'artist':        track_info['artist'],
            'energy':        audio['energy'],
            'danceability':  audio['danceability'],
            'valence':       audio['valence'],
            'acousticness':  audio['acousticness'],
            'tempo':         audio['tempo'],
            'popularity':    popularity,
            'rating':        rating,
        }
        rows.append(row)

        print(f"  energy={audio['energy']}  dance={audio['danceability']}  "
              f"valence={audio['valence']}  tempo={audio['tempo']}  "
              f"popularity={popularity}  rating={rating}/5\n")

    return rows


def save(rows):
    """
    Split the fetched data into two CSV files:

    songs.csv   → name, artist + 5 audio features
                  MATLAB reads this for Pillars 1 and 2
                  Each row = one song vector in R^5

    ratings.csv → name, popularity, rating
                  MATLAB reads this for Pillar 3
                  rating column becomes the R matrix values
    """
    df = pd.DataFrame(rows)

    # songs.csv — feature vectors only
    songs_df = df[['name', 'artist', 'energy', 'danceability',
                   'valence', 'acousticness', 'tempo']]
    songs_path = os.path.join('..', 'data', 'songs.csv')
    songs_df.to_csv(songs_path, index=False)
    print(f"Saved {songs_path}  ({len(songs_df)} songs × 5 features)")

    # ratings.csv — popularity-derived ratings
    ratings_df = df[['name', 'artist', 'popularity', 'rating']]
    ratings_path = os.path.join('..', 'data', 'ratings.csv')
    ratings_df.to_csv(ratings_path, index=False)
    print(f"Saved {ratings_path}  ({len(ratings_df)} songs)")

    # Print a clean summary table
    print("\n── Final dataset ─────────────────────────────────────────")
    print(df[['name', 'energy', 'danceability', 'valence',
              'acousticness', 'tempo', 'rating']].to_string(index=False))


if __name__ == "__main__":
    rows = fetch_all(SONGS)

    if rows:
        save(rows)
        print(f"\nDone. {len(rows)} songs fetched.")
        print("Hand data/songs.csv and data/ratings.csv to MATLAB.")
    else:
        print("No songs fetched — check your credentials in .env")