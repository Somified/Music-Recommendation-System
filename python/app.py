"""
FILE: app.py — Melodix · Multi-Vector Music Curation System
Run: streamlit run app.py  (from the /python folder)
pip install streamlit pandas numpy plotly scikit-learn
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os

# ── Paths ──────────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
DATA  = _ROOT / "data"
if not DATA.exists():
    DATA = Path(os.getcwd()) / "data"
if not DATA.exists():
    DATA = Path(os.getcwd()).parent / "data"

# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Melodix",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════
# PALETTE & CSS
# ═══════════════════════════════════════════════════════════════════════════
YUCCA      = "#F3EBD8"
OLD_ROSE   = "#C6214E"
BRILL_ROSE = "#ED5F9A"
LIME       = "#B6BB79"
CHARCOAL   = "#2C2C2C"
BORDEAUX   = "#4A0E20"
SURFACE    = "#FAF5EA"
BORDER     = "#E2D5BC"
MUTED      = "#9A8B74"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {{
    --yucca:      {YUCCA};
    --old-rose:   {OLD_ROSE};
    --brill-rose: {BRILL_ROSE};
    --lime:       {LIME};
    --charcoal:   {CHARCOAL};
    --bordeaux:   {BORDEAUX};
    --surface:    {SURFACE};
    --border:     {BORDER};
    --muted:      {MUTED};
}}

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    background-color: var(--yucca) !important;
    color: var(--charcoal);
}}
[data-testid="stAppViewContainer"], [data-testid="stMain"] {{
    background-color: var(--yucca) !important;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 2.5rem 3rem; max-width: 1300px; }}

/* Sidebar */
[data-testid="stSidebar"] {{
    background-color: var(--surface) !important;
    border-right: 1.5px solid var(--border);
}}
[data-testid="stSidebar"] * {{ color: var(--charcoal) !important; }}

/* Headings */
.hero-title {{
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    font-weight: 700;
    color: var(--bordeaux);
    line-height: 1.15;
    margin-bottom: 0.2rem;
}}
.hero-sub {{
    font-size: 0.85rem;
    color: var(--muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 500;
    margin-bottom: 2rem;
}}
.section-title {{
    font-family: 'Playfair Display', serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--bordeaux);
    margin: 1.5rem 0 0.8rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid var(--brill-rose);
    display: inline-block;
}}

/* Cards */
.card {{
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 0.8rem;
}}
.card-rose {{ border-left: 4px solid var(--old-rose); }}
.card-lime {{ border-left: 4px solid var(--lime); }}

/* Recommendation rows */
.rec-row {{
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem 1.2rem;
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 12px;
    margin-bottom: 0.6rem;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.rec-row:hover {{
    border-color: var(--brill-rose);
    box-shadow: 0 3px 12px rgba(198,33,78,0.08);
}}
.rec-rank {{
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--old-rose);
    min-width: 2.2rem;
    padding-top: 0.1rem;
}}
.rec-body {{ flex: 1; }}
.rec-name {{
    font-size: 0.97rem;
    font-weight: 600;
    color: var(--bordeaux);
    margin-bottom: 0.15rem;
}}
.rec-artist {{ font-size: 0.82rem; color: var(--muted); margin-bottom: 0.3rem; }}
.rec-why {{
    font-size: 0.78rem;
    color: var(--old-rose);
    background: rgba(198,33,78,0.07);
    border-radius: 6px;
    padding: 0.2rem 0.6rem;
    display: inline-block;
    margin-top: 0.15rem;
}}
.score-pill {{
    background: linear-gradient(135deg, var(--old-rose), var(--brill-rose));
    color: white;
    border-radius: 20px;
    padding: 0.25rem 0.8rem;
    font-size: 0.78rem;
    font-weight: 600;
    white-space: nowrap;
    margin-top: 0.2rem;
}}

/* Seed song chip */
.seed-chip {{
    display: inline-block;
    background: rgba(182,187,121,0.2);
    border: 1.5px solid var(--lime);
    color: var(--bordeaux);
    border-radius: 20px;
    padding: 0.25rem 0.8rem;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 0.2rem;
}}

/* Tags */
.tag-lime {{
    background: rgba(182,187,121,0.2);
    border: 1px solid var(--lime);
    color: #5c6020;
    border-radius: 12px;
    padding: 0.15rem 0.6rem;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    display: inline-block;
    margin-right: 0.3rem;
}}
.tag-rose {{
    background: rgba(237,95,154,0.1);
    border: 1px solid var(--brill-rose);
    color: var(--old-rose);
    border-radius: 12px;
    padding: 0.15rem 0.6rem;
    font-size: 0.72rem;
    font-weight: 600;
    display: inline-block;
    margin-right: 0.3rem;
}}

/* Metric box */
.metric-box {{
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    text-align: center;
    margin-bottom: 0.5rem;
}}
.metric-val {{
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--old-rose);
}}
.metric-label {{
    font-size: 0.7rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.07em;
}}

/* Streamlit widget overrides */
.stMultiSelect [data-baseweb="tag"] {{
    background-color: rgba(182,187,121,0.3) !important;
    color: var(--bordeaux) !important;
}}
.stSlider > div > div > div > div {{ background: var(--old-rose) !important; }}
div[data-testid="stSelectbox"] label,
div[data-testid="stMultiSelect"] label,
div[data-testid="stSlider"] label {{ color: var(--charcoal) !important; font-weight: 500; }}
.stButton > button {{
    background: var(--old-rose);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 1.5rem;
    transition: background 0.2s;
}}
.stButton > button:hover {{ background: var(--brill-rose); color: white; }}
.stTabs [data-baseweb="tab-list"] {{
    background: var(--surface);
    border-radius: 10px;
    border: 1.5px solid var(--border);
    padding: 0.3rem;
}}
.stTabs [data-baseweb="tab"] {{ color: var(--muted) !important; }}
.stTabs [aria-selected="true"] {{
    background: var(--old-rose) !important;
    color: white !important;
    border-radius: 8px !important;
}}
hr {{ border-color: var(--border) !important; }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_songs():
    songs_path = DATA / "songs.csv"
    if not songs_path.exists():
        st.error(f"songs.csv not found at: {songs_path}")
        st.stop()

    df = pd.read_csv(songs_path)

    # Auto-detect name column
    for col in ['track_name','name','title','song','song_name']:
        if col in df.columns:
            df = df.rename(columns={col: 'name'})
            break
    # Auto-detect artist column
    for col in ['artists','artist','artist_name','track_artist']:
        if col in df.columns:
            df = df.rename(columns={col: 'artist'})
            break
    if 'artist' not in df.columns:
        df['artist'] = 'Unknown'

    # Auto-detect track_id for Spotify embeds
    for col in ['track_id','id','spotify_id']:
        if col in df.columns:
            df = df.rename(columns={col: 'track_id'})
            break
    if 'track_id' not in df.columns:
        df['track_id'] = None

    # Popularity column
    for col in ['popularity','Popularity','pop']:
        if col in df.columns:
            df = df.rename(columns={col: 'popularity'})
            break
    if 'popularity' not in df.columns:
        df['popularity'] = 50

    feats = [c for c in ['tempo','energy','danceability','valence',
                          'acousticness','speechiness','instrumentalness','liveness']
             if c in df.columns]

    keep = ['name','artist','track_id','popularity'] + feats
    df = df[[c for c in keep if c in df.columns]].dropna(subset=['name'])
    df['name']   = df['name'].astype(str).str.strip()
    df['artist'] = df['artist'].astype(str).str.strip()

    # Deduplicate: keep highest popularity version of each song name
    df = df.sort_values('popularity', ascending=False)
    df = df.drop_duplicates(subset=['name']).reset_index(drop=True)

    return df, feats

@st.cache_data
def load_ratings(n_songs):
    path = DATA / "ratings.csv"
    if not path.exists():
        return np.zeros((0, n_songs)), []
    df    = pd.read_csv(path, index_col=0)
    users = list(df.index)
    # Match column count to n_songs
    R = df.values.astype(float)
    if R.shape[1] > n_songs:
        R = R[:, :n_songs]
    elif R.shape[1] < n_songs:
        R = np.hstack([R, np.zeros((R.shape[0], n_songs - R.shape[1]))])
    return R, users

songs_df, FEAT_COLS = load_songs()
S_raw               = songs_df[FEAT_COLS].values.astype(float)
song_names          = songs_df['name'].tolist()
song_artists        = songs_df['artist'].tolist()
track_ids           = songs_df['track_id'].tolist()
popularities        = songs_df['popularity'].tolist()
R, users            = load_ratings(len(song_names))


# ═══════════════════════════════════════════════════════════════════════════
# LINEAR ALGEBRA ENGINE  (Z-score + multi-seed centroid + diversity penalty)
# ═══════════════════════════════════════════════════════════════════════════

def zscore_standardise(S):
    """Z-score standardisation: (x - μ) / σ per feature column."""
    mu  = S.mean(axis=0)
    sig = S.std(axis=0)
    sig[sig == 0] = 1          # avoid divide-by-zero for constant features
    return (S - mu) / sig, mu, sig

def cosine_sim_matrix(query_vec, S):
    """Cosine similarity of query_vec against every row of S."""
    qn = np.linalg.norm(query_vec)
    if qn == 0:
        return np.zeros(len(S))
    Sn = np.linalg.norm(S, axis=1)
    Sn[Sn == 0] = 1
    return (S @ query_vec) / (Sn * qn)

def taste_centroid(seed_indices, S_z):
    """Mean Taste Vector — linear combination of seed song vectors."""
    vectors = S_z[seed_indices]            # shape: (n_seeds, n_feats)
    return vectors.mean(axis=0)            # centroid in z-score space

def euclidean_dist(a, B):
    """Euclidean distance from vector a to each row of B."""
    return np.linalg.norm(B - a, axis=1)

def diversity_penalty(S_z, seed_indices, candidates, sigma=1.5):
    """
    Penalise candidates that are too close to ONE seed but far from others.
    Encourages breadth matching the full centroid spread.
    sigma: spread tolerance in z-score units
    """
    seed_vecs = S_z[seed_indices]
    # For each candidate, compute min distance to any seed
    penalties = np.zeros(len(candidates))
    for i, cidx in enumerate(candidates):
        dists = euclidean_dist(S_z[cidx], seed_vecs)
        min_d  = dists.min()
        mean_d = dists.mean()
        # If min_d is very small, song is essentially a duplicate of one seed
        # Penalise by how much it deviates from the mean
        penalties[i] = max(0.0, (mean_d - min_d) / (sigma + 1e-6))
    return penalties

def get_dominant_feature(song_vec, centroid_vec, feat_names):
    """Find which feature drives the match (smallest absolute z-score gap)."""
    diffs = np.abs(song_vec - centroid_vec)
    return feat_names[np.argmin(diffs)]

def get_recommendations(seed_indices, alpha, beta, gamma,
                         top_n=10, diversity_weight=0.15):
    """
    Full 3-pillar pipeline with z-score standardisation and diversity penalty.
    seed_indices: list of integer indices into song_names
    """
    S_z, _, _ = zscore_standardise(S_raw)

    # ── Pillar 1: Cosine similarity to taste centroid ─────────────────────
    centroid = taste_centroid(seed_indices, S_z)
    p1 = cosine_sim_matrix(centroid, S_z)
    p1 = np.clip(p1, 0, None)
    if p1.max() > 0:
        p1 /= p1.max()

    # ── Pillar 2: Taste vector similarity (same centroid approach) ─────────
    p2 = cosine_sim_matrix(centroid, S_z)   # same vector, kept separate for weight tuning
    p2 = np.clip(p2, 0, None)
    if p2.max() > 0:
        p2 /= p2.max()

    # ── Pillar 3: Rating matrix ────────────────────────────────────────────
    if R.shape[0] > 0 and R.sum() > 0:
        user_means  = R.mean(axis=1, keepdims=True)
        song_means  = R.mean(axis=0, keepdims=True)
        global_mean = R.mean()
        p3 = np.clip(user_means + song_means - global_mean, 0, 1).mean(axis=0)
        if p3.max() > 0:
            p3 /= p3.max()
    else:
        p3 = np.zeros(len(song_names))

    # ── Score fusion (linear combination) ─────────────────────────────────
    final = alpha * p1 + beta * p2 + gamma * p3

    # ── Zero out seed songs ────────────────────────────────────────────────
    final[seed_indices] = 0

    # ── Diversity penalty on top candidates ───────────────────────────────
    top_candidates = np.argsort(final)[::-1][:top_n * 3]
    penalties      = diversity_penalty(S_z, seed_indices, top_candidates)
    for i, cidx in enumerate(top_candidates):
        final[cidx] = max(0, final[cidx] - diversity_weight * penalties[i])

    # ── Final ranking ──────────────────────────────────────────────────────
    order = np.argsort(final)[::-1][:top_n]

    # ── "Why" analysis ────────────────────────────────────────────────────
    why = []
    for idx in order:
        dom_feat = get_dominant_feature(S_z[idx], centroid, np.array(FEAT_COLS))
        euc_dist = float(euclidean_dist(centroid, S_z[[idx]])[0])
        why.append((dom_feat, euc_dist))

    return order, final, p1, p3, centroid, why

def compute_correlation_matrices():
    """Build correlation matrices with guaranteed dimension alignment."""
    if R.shape[0] < 2 or R.sum() == 0:
        return None, None, None, None

    # Only include songs that were rated by at least 2 users (otherwise corr = NaN)
    rated_mask  = R.sum(axis=0) >= 2
    rated_idxs  = np.where(rated_mask)[0]

    if len(rated_idxs) < 2:
        return None, None, None, None

    R_sub      = R[:, rated_idxs]                        # (n_users, n_rated)
    sub_names  = [song_names[i] for i in rated_idxs]     # len == n_rated

    with np.errstate(invalid='ignore', divide='ignore'):
        C_songs = np.nan_to_num(np.corrcoef(R_sub.T))    # (n_rated, n_rated) ✓
        C_users = np.nan_to_num(np.corrcoef(R))          # (n_users, n_users)

    # Final safety check: assert shape matches labels
    assert C_songs.shape[0] == len(sub_names), \
        f"C_songs shape {C_songs.shape} != sub_names len {len(sub_names)}"

    return C_songs, C_users, sub_names, users


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='padding:1rem 0 0.2rem'>
        <div style='font-family:Playfair Display,serif;font-size:1.8rem;
                    font-weight:700;color:{BORDEAUX};'>Melodix</div>
        <div style='font-size:0.7rem;color:{MUTED};letter-spacing:0.1em;
                    text-transform:uppercase;'>Linear Algebra · Music Curation</div>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    page = st.radio("", ["🎯 Curate Playlist", "📊 Feature Space",
                         "🔬 Correlation Analysis", "📐 LA Concepts"],
                    label_visibility="collapsed")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.75rem;color:{MUTED};font-weight:600;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.8rem;'>Score Fusion Weights</div>", unsafe_allow_html=True)

    alpha = st.slider("α  Pillar 1 · Cosine Similarity", 0.0, 1.0, 0.5, 0.05)
    beta  = st.slider("β  Pillar 2 · Taste Vector",      0.0, 1.0, 0.3, 0.05)
    gamma = st.slider("γ  Pillar 3 · Ratings Matrix",    0.0, 1.0, 0.2, 0.05)

    total = alpha + beta + gamma
    if abs(total - 1.0) > 0.01:
        st.warning(f"Weights sum = {total:.2f} — auto-normalising.")
        alpha /= total; beta /= total; gamma /= total

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='metric-box'><div class='metric-val'>{len(song_names):,}</div><div class='metric-label'>Songs in Dataset</div></div>
    <div class='metric-box'><div class='metric-val'>{len(users)}</div><div class='metric-label'>Classmates' Responses</div></div>
    <div class='metric-box'><div class='metric-val'>{len(FEAT_COLS)}</div><div class='metric-label'>Audio Features</div></div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# HELPER: Spotify embed
# ═══════════════════════════════════════════════════════════════════════════
def spotify_embed(track_id, compact=True):
    if not track_id or str(track_id).lower() in ('nan','none',''):
        return ""
    h = 80 if compact else 152
    return f"""<iframe style="border-radius:8px;margin-top:0.5rem;" 
        src="https://open.spotify.com/embed/track/{track_id}?utm_source=generator" 
        width="100%" height="{h}" frameBorder="0" allowfullscreen="" 
        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
        loading="lazy"></iframe>"""


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 1 — CURATE PLAYLIST
# ═══════════════════════════════════════════════════════════════════════════
if "Curate" in page:
    st.markdown(f"""
    <div class='hero-title'>Curate Your<br>Perfect Playlist.</div>
    <div class='hero-sub'>Select 3–5 seed songs · The system calculates your Taste Centroid</div>
    """, unsafe_allow_html=True)

    # ── Popularity filter ─────────────────────────────────────────────────
    # Default shown outside expander so it's always defined
    pop_threshold = 50
    with st.expander("⚙️ Filter song pool by popularity", expanded=False):
        pop_threshold = st.slider(
            "Minimum popularity score (0–100)",
            0, 100, 50, 5,
            help="Higher = only well-known songs appear in the selection list"
        )

    popular_mask  = [p >= pop_threshold for p in popularities]
    popular_songs = [f"{song_names[i]}  —  {song_artists[i]}"
                     for i in range(len(song_names)) if popular_mask[i]]
    popular_idx   = [i for i in range(len(song_names)) if popular_mask[i]]

    if len(popular_songs) < 10:
        st.warning("Popularity threshold too high — showing all songs.")
        popular_songs = [f"{n}  —  {a}" for n, a in zip(song_names, song_artists)]
        popular_idx   = list(range(len(song_names)))

    # ── Seed song multiselect ─────────────────────────────────────────────
    st.markdown("<div class='section-title'>Choose Your Seed Songs</div>", unsafe_allow_html=True)
    selected_labels = st.multiselect(
        "Pick 3–5 songs you love",
        options=popular_songs,
        max_selections=5,
        help="Select between 3 and 5 songs to define your taste profile"
    )

    if len(selected_labels) < 3:
        st.info("👆 Select at least 3 seed songs to generate your playlist.")
        st.stop()

    # Map selections back to indices
    seed_indices = []
    for label in selected_labels:
        song_part = label.split("  —  ")[0].strip()
        if song_part in song_names:
            seed_indices.append(song_names.index(song_part))

    if not seed_indices:
        st.error("Could not map selections to dataset. Try again.")
        st.stop()

    # ── Display seed chips ────────────────────────────────────────────────
    chips = "".join(f"<span class='seed-chip'>🎵 {song_names[i]}</span>" for i in seed_indices)
    st.markdown(f"<div style='margin:0.5rem 0 1.5rem;'>{chips}</div>", unsafe_allow_html=True)

    # ── Run engine ────────────────────────────────────────────────────────
    top_n   = st.select_slider("Playlist length", [5, 8, 10, 12, 15], value=10)
    div_w   = st.slider("Diversity strength", 0.0, 0.5, 0.15, 0.05,
                         help="Higher = more variety, lower = tighter cluster around centroid")

    rec_idx, final_scores, p1, p3, centroid, why = get_recommendations(
        seed_indices, alpha, beta, gamma, top_n, div_w
    )

    # ── Centroid card ─────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Your Taste Centroid</div>", unsafe_allow_html=True)
    centroid_desc = ", ".join(
        f"<span class='tag-lime'>{f}: {centroid[i]:+.2f}σ</span>"
        for i, f in enumerate(FEAT_COLS)
        if abs(centroid[i]) > 0.3   # only show dominant features
    )
    st.markdown(f"""
    <div class='card card-lime'>
        <div style='font-size:0.8rem;color:{MUTED};text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;'>
            v̄<sub>taste</sub> = mean of {len(seed_indices)} seed vectors (z-score space)
        </div>
        <div>{centroid_desc if centroid_desc else '<span style="color:#9A8B74">All features near zero — very balanced taste profile</span>'}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Centroid radar chart ──────────────────────────────────────────────
    with st.expander("📊 View centroid radar chart"):
        fig_radar = go.Figure(go.Scatterpolar(
            r=np.clip(centroid, -3, 3).tolist() + [centroid[0]],
            theta=FEAT_COLS + [FEAT_COLS[0]],
            fill='toself',
            fillcolor=f'rgba(237,95,154,0.15)',
            line=dict(color=OLD_ROSE, width=2),
            name='Taste Centroid'
        ))
        for sidx in seed_indices:
            s_z, _, _ = zscore_standardise(S_raw)
            fig_radar.add_trace(go.Scatterpolar(
                r=np.clip(s_z[sidx], -3, 3).tolist() + [s_z[sidx][0]],
                theta=FEAT_COLS + [FEAT_COLS[0]],
                fill='toself',
                fillcolor='rgba(182,187,121,0.08)',
                line=dict(color=LIME, width=1, dash='dot'),
                name=song_names[sidx][:20],
                opacity=0.6
            ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor=SURFACE,
                radialaxis=dict(visible=True, range=[-3,3],
                                color=MUTED, gridcolor=BORDER),
                angularaxis=dict(color=CHARCOAL, gridcolor=BORDER)
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=CHARCOAL, family='DM Sans'),
            height=380,
            margin=dict(t=30, b=30),
            showlegend=True,
            legend=dict(font=dict(size=9))
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # ── Recommendations list ──────────────────────────────────────────────
    st.markdown(f"<div class='section-title'>Your Curated Playlist</div>", unsafe_allow_html=True)

    for rank, idx in enumerate(rec_idx, 1):
        dom_feat, euc_d = why[rank - 1]
        score_pct       = final_scores[idx] * 100
        tid             = track_ids[idx]

        embed_html = spotify_embed(tid) if tid and str(tid) not in ('nan','None') else ""

        st.markdown(f"""
        <div class='rec-row'>
            <div class='rec-rank'>#{rank}</div>
            <div class='rec-body'>
                <div class='rec-name'>{song_names[idx]}</div>
                <div class='rec-artist'>{song_artists[idx]}</div>
                <div>
                    <span class='tag-lime'>{dom_feat}</span>
                    <span class='rec-why'>↔ centroid dist: {euc_d:.2f}σ · matched via {dom_feat}</span>
                </div>
                {embed_html}
            </div>
            <div><span class='score-pill'>{score_pct:.1f}%</span></div>
        </div>
        """, unsafe_allow_html=True)

    # ── Pillar breakdown for all recs ─────────────────────────────────────
    with st.expander("📐 Score breakdown across all recommendations"):
        breakdown_df = pd.DataFrame({
            'Song':      [song_names[i][:30] for i in rec_idx],
            'P1 Cosine': [p1[i] for i in rec_idx],
            'P3 Ratings':[p3[i] for i in rec_idx],
            'Final':     [final_scores[i] for i in rec_idx]
        })
        fig_break = px.bar(
            breakdown_df.melt(id_vars='Song', var_name='Pillar', value_name='Score'),
            x='Song', y='Score', color='Pillar', barmode='group',
            color_discrete_map={
                'P1 Cosine': OLD_ROSE,
                'P3 Ratings': LIME,
                'Final': BRILL_ROSE
            }
        )
        fig_break.update_layout(
            plot_bgcolor=SURFACE, paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=CHARCOAL, family='DM Sans'),
            xaxis=dict(tickangle=30, gridcolor=BORDER),
            yaxis=dict(gridcolor=BORDER),
            height=340, margin=dict(t=10, b=60),
            legend=dict(bgcolor='rgba(0,0,0,0)')
        )
        st.plotly_chart(fig_break, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 2 — FEATURE SPACE
# ═══════════════════════════════════════════════════════════════════════════
elif "Feature" in page:
    st.markdown(f"""
    <div class='hero-title'>Feature Space<br>Visualisation.</div>
    <div class='hero-sub'>Songs as vectors · Z-score standardised</div>
    """, unsafe_allow_html=True)

    S_z, _, _ = zscore_standardise(S_raw)

    if len(FEAT_COLS) < 2:
        st.error("Need at least 2 feature columns.")
        st.stop()

    c1, c2, c3 = st.columns(3)
    x_feat   = c1.selectbox("X axis", FEAT_COLS, index=0)
    y_feat   = c2.selectbox("Y axis", FEAT_COLS, index=min(1,len(FEAT_COLS)-1))
    pop_min  = c3.slider("Min popularity", 0, 100, 40)

    xi, yi = FEAT_COLS.index(x_feat), FEAT_COLS.index(y_feat)

    mask   = [p >= pop_min for p in popularities]
    idxs   = [i for i, m in enumerate(mask) if m]
    max_pts = min(3000, len(idxs))
    sample  = idxs[:max_pts]

    plot_df = pd.DataFrame({
        'song':       [song_names[i] for i in sample],
        'artist':     [song_artists[i] for i in sample],
        'x':          S_z[sample, xi],
        'y':          S_z[sample, yi],
        'popularity': [popularities[i] for i in sample]
    })

    fig = px.scatter(
        plot_df, x='x', y='y', color='popularity',
        hover_name='song', hover_data={'artist':True,'popularity':True,'x':False,'y':False},
        color_continuous_scale=[[0, YUCCA],[0.5, BRILL_ROSE],[1.0, BORDEAUX]],
        opacity=0.7,
        labels={'x': f'{x_feat} (z-score)', 'y': f'{y_feat} (z-score)'}
    )
    fig.update_layout(
        plot_bgcolor=SURFACE, paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=CHARCOAL, family='DM Sans'),
        xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
        yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
        coloraxis_colorbar=dict(title='Popularity', tickfont=dict(color=CHARCOAL)),
        height=520, margin=dict(t=20)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Showing {max_pts} songs · popularity ≥ {pop_min} · axes are z-score normalised")

    # Feature distribution
    st.markdown("<div class='section-title'>Feature Distributions</div>", unsafe_allow_html=True)
    feat_sel = st.selectbox("Select feature", FEAT_COLS)
    fig2 = px.histogram(songs_df, x=feat_sel, nbins=50,
                         color_discrete_sequence=[OLD_ROSE])
    fig2.update_layout(
        plot_bgcolor=SURFACE, paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=CHARCOAL, family='DM Sans'),
        xaxis=dict(gridcolor=BORDER), yaxis=dict(gridcolor=BORDER),
        height=280, margin=dict(t=10)
    )
    st.plotly_chart(fig2, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 3 — CORRELATION ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════
elif "Correlation" in page:
    st.markdown(f"""
    <div class='hero-title'>Correlation<br>Analysis.</div>
    <div class='hero-sub'>Structural relationships from classmates' listening data</div>
    """, unsafe_allow_html=True)

    C_songs, C_users, sub_names, user_list = compute_correlation_matrices()

    if C_songs is None:
        st.warning("No ratings data. Run `python process_form_data.py` to generate `data/ratings.csv`.")
        st.stop()

    tab1, tab2 = st.tabs(["🎵  Song–Song Correlation", "👥  User–User Correlation"])

    # ── Song–Song ─────────────────────────────────────────────────────────
    with tab1:
        st.markdown(f"""
        <div class='card card-rose'>
        <b>LA Concept:</b> C = corr(Rᵀ) — normalised covariance of song columns.<br>
        <b>Interpretation:</b> C[i,j] ≈ 1 means classmates who liked song <i>i</i> also liked song <i>j</i>.
        </div>
        """, unsafe_allow_html=True)

        # sub_names and C_songs are already 1-to-1: C_songs[i,j] ↔ sub_names[i], sub_names[j]
        # Just pick the top_k most-liked songs by summing the R columns that were rated
        n_rated = len(sub_names)          # guaranteed == C_songs.shape[0]
        top_k   = st.slider("Songs to display", 5, min(40, n_rated), min(20, n_rated))

        # Build popularity order within the already-filtered sub_names space
        # R columns for rated songs: reconstruct counts directly from C_songs diagonal sum
        rated_counts = np.array([C_songs[i, :].sum() for i in range(n_rated)])
        top_sub_idxs = np.argsort(rated_counts)[::-1][:top_k]

        # Strictly enforce: matrix slice and label list must have identical length
        C_disp = C_songs[np.ix_(top_sub_idxs, top_sub_idxs)]
        labels = [sub_names[i][:22] for i in top_sub_idxs]
        assert C_disp.shape == (len(labels), len(labels)), \
            f"Dimension mismatch: C_disp {C_disp.shape} vs labels {len(labels)}"

        # Yucca White → Brilliant Rose gradient
        colorscale = [[0.0, YUCCA], [0.5, BRILL_ROSE], [1.0, BORDEAUX]]

        fig_cs = px.imshow(
            C_disp, x=labels, y=labels,
            color_continuous_scale=colorscale,
            zmin=-1, zmax=1,
            aspect='auto',
            text_auto='.1f'
        )
        fig_cs.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=CHARCOAL, size=9, family='DM Sans'),
            height=600,
            margin=dict(t=10, b=80, l=130),
            coloraxis_colorbar=dict(
                title='Corr.',
                tickfont=dict(color=CHARCOAL),
                tickvals=[-1,-0.5,0,0.5,1]
            )
        )
        fig_cs.update_xaxes(tickangle=45, tickfont=dict(size=8))
        fig_cs.update_yaxes(tickfont=dict(size=8))
        st.plotly_chart(fig_cs, use_container_width=True)
        st.caption(f"Top {top_k} most-liked songs from classmates' responses.")

    # ── User–User ─────────────────────────────────────────────────────────
    with tab2:
        st.markdown(f"""
        <div class='card card-rose'>
        <b>LA Concept:</b> C = corr(R) — pairwise correlation of user row vectors.<br>
        <b>Interpretation:</b> C[i,j] near 1 = nearly identical music taste between two classmates.
        </div>
        """, unsafe_allow_html=True)

        ulabels = [str(u)[:16] for u in user_list]
        fig_cu  = px.imshow(
            C_users, x=ulabels, y=ulabels,
            color_continuous_scale=[[0.0, YUCCA],[0.5, BRILL_ROSE],[1.0, BORDEAUX]],
            zmin=-1, zmax=1,
            aspect='auto'
        )
        fig_cu.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=CHARCOAL, size=9, family='DM Sans'),
            height=620,
            margin=dict(t=10, b=80, l=130),
            coloraxis_colorbar=dict(tickfont=dict(color=CHARCOAL))
        )
        fig_cu.update_xaxes(tickangle=45, tickfont=dict(size=8))
        st.plotly_chart(fig_cu, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 4 — LA CONCEPTS
# ═══════════════════════════════════════════════════════════════════════════
elif "LA" in page:
    st.markdown(f"""
    <div class='hero-title'>The Linear Algebra<br>Behind Melodix.</div>
    <div class='hero-sub'>Every recommendation is a sequence of matrix operations</div>
    """, unsafe_allow_html=True)

    concepts = [
        ("Vectors", "p1",
         "Each song is a vector in audio feature space.",
         "s = [tempo, energy, danceability, valence, acousticness, ...]",
         "A song is a point in ℝⁿ. All similarity calculations operate on these vectors."),
        ("Z-Score Standardisation", "all",
         "Prevents any single feature from dominating the similarity calculation.",
         "z = (x − μ) / σ  per feature column",
         "Without this, high-BPM songs dominate cosine similarity. Z-scoring puts all features on equal footing."),
        ("Taste Centroid (Mean Vector)", "p2",
         "The average of your seed song vectors — your musical 'centre of gravity'.",
         "v̄_taste = (s₁ + s₂ + ... + sₙ) / n",
         "Vector addition + scalar multiplication. This is the definition of a linear combination."),
        ("Cosine Similarity", "p1",
         "Measures angle between two vectors — direction, not magnitude.",
         "sim(a, b) = (a · b) / (‖a‖ · ‖b‖)",
         "Used to find songs pointing in the same direction as your taste centroid."),
        ("Dot Product", "p1",
         "Numerator of cosine similarity — measures alignment.",
         "a · b = Σ aᵢbᵢ",
         "High dot product = song shares the same audio profile direction as your centroid."),
        ("Euclidean Distance", "p1",
         "Measures how close a song is to your taste centroid in z-score space.",
         "d(a, b) = ‖a − b‖ = √(Σ(aᵢ − bᵢ)²)",
         "Used in the 'Why' analysis — the dominant feature is the dimension with smallest gap to the centroid."),
        ("Rating Matrix", "p3",
         "R is the binary users × songs matrix from classmates' form data.",
         "R ∈ ℝᵐˣⁿ,   Rᵢⱼ = 1 if user i liked song j",
         "The entire classmate dataset compressed into one matrix."),
        ("Row & Column Operations", "p3",
         "Predict how much a user would like an unrated song.",
         "score(i,j) = rowMean(i) + colMean(j) − globalMean",
         "Row means capture user taste breadth. Column means capture song popularity."),
        ("Score Fusion — Linear Combination", "all",
         "The final recommendation score is a weighted sum of all 3 pillars.",
         "score = α·P₁ + β·P₂ + γ·P₃,   α + β + γ = 1",
         "This IS the textbook definition of a linear combination. The α, β, γ are the scalar coefficients."),
        ("Correlation Matrix", "p3",
         "Measures pairwise structural relationships between songs and users.",
         "C_songs = corr(Rᵀ),   C_users = corr(R)",
         "C[i,j] ≈ 1 means songs i and j are consistently liked together — useful for cluster analysis."),
    ]

    pillar_label = {'p1':'Pillar 1','p2':'Pillar 2','p3':'Pillar 3','all':'All Pillars'}
    tag_class    = {'p1':'tag-rose','p2':'tag-lime','p3':'tag-rose','all':'tag-lime'}

    for title, pillar, what, formula, why in concepts:
        st.markdown(f"""
        <div class='card' style='margin-bottom:0.9rem;'>
            <div style='display:flex;align-items:center;gap:0.7rem;margin-bottom:0.5rem;'>
                <span style='font-family:Playfair Display,serif;font-size:1.05rem;
                             font-weight:700;color:{BORDEAUX};'>{title}</span>
                <span class='{tag_class[pillar]}'>{pillar_label[pillar]}</span>
            </div>
            <div style='color:{MUTED};font-size:0.88rem;margin-bottom:0.5rem;'>{what}</div>
            <div style='background:{YUCCA};border:1.5px solid {BORDER};border-radius:8px;
                        padding:0.55rem 1rem;font-family:monospace;color:{OLD_ROSE};
                        font-size:0.92rem;margin-bottom:0.5rem;'>{formula}</div>
            <div style='font-size:0.82rem;color:{CHARCOAL};'>{why}</div>
        </div>
        """, unsafe_allow_html=True)