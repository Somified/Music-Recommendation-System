"""
FILE: app.py — Melodix · Multi-Vector Music Curation System
Run from /python:  streamlit run app.py
pip install streamlit pandas numpy plotly requests
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os, math, requests, urllib.parse, json

# ── Paths ──────────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
DATA  = _ROOT / "data"
if not DATA.exists(): DATA = Path(os.getcwd()) / "data"
if not DATA.exists(): DATA = Path(os.getcwd()).parent / "data"

# ═══════════════════════════════════════════════════════════════════════════
# PALETTE  — zero blacks, full beige/rose scheme
# ═══════════════════════════════════════════════════════════════════════════
YUCCA      = "#F3EBD8"
OLD_ROSE   = "#C6214E"
BRILL_ROSE = "#ED5F9A"
LIME       = "#B6BB79"
BORDEAUX   = "#4A0E20"
SURFACE    = "#FAF5EA"
SURFACE2   = "#F7EFE0"
BORDER     = "#E2D5BC"
MUTED      = "#9A8B74"
TEXT       = "#3D1A0E"          # deep warm brown — readable, NOT black
ROSE_TINT  = "#FDF0F5"
ROSE_MID   = "#F5C8D8"

# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Melodix", page_icon="🎵",
                   layout="wide", initial_sidebar_state="expanded")

# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL CSS  — no black anywhere
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Base ── */
html,body,[class*="css"]{{
    font-family:'DM Sans',sans-serif;
    background-color:{YUCCA}!important;
    color:{TEXT};
}}
[data-testid="stAppViewContainer"],[data-testid="stMain"],
.main,.stApp{{background-color:{YUCCA}!important;}}
#MainMenu,footer,header{{visibility:hidden;}}
.block-container{{padding:2.5rem 3rem;max-width:1320px;}}

/* ── Sidebar ── */
[data-testid="stSidebar"]{{background-color:{SURFACE}!important;border-right:1.5px solid {BORDER};}}
[data-testid="stSidebar"] *{{color:{TEXT}!important;}}
[data-testid="stSidebar"] .stRadio label{{color:{TEXT}!important;}}

/* ── Typography ── */
.hero-title{{
    font-family:'Playfair Display',serif;font-size:2.8rem;font-weight:700;
    color:{BORDEAUX};line-height:1.15;margin-bottom:0.25rem;
}}
.hero-sub{{
    font-size:0.83rem;color:{MUTED};letter-spacing:0.12em;
    text-transform:uppercase;font-weight:500;margin-bottom:2rem;
}}
.section-title{{
    font-family:'Playfair Display',serif;font-size:1.2rem;font-weight:600;
    color:{BORDEAUX};margin:1.5rem 0 0.8rem;padding-bottom:0.35rem;
    border-bottom:2px solid {BRILL_ROSE};display:inline-block;
}}

/* ── Cards ── */
.card{{background:{SURFACE};border:1.5px solid {BORDER};border-radius:14px;padding:1.4rem 1.6rem;margin-bottom:0.8rem;}}
.card-rose{{border-left:4px solid {OLD_ROSE};}}
.card-lime{{border-left:4px solid {LIME};}}

/* ── Song selection grid ── */
.song-card{{
    background:{SURFACE};border:2px solid {BORDER};border-radius:16px;
    overflow:hidden;cursor:pointer;position:relative;
    transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease;
}}
.song-card:hover{{
    transform:translateY(-5px) scale(1.025);
    border-color:{BRILL_ROSE};
    box-shadow:0 10px 28px rgba(237,95,154,.22);
}}
.song-card.selected{{
    border-color:{OLD_ROSE}!important;
    box-shadow:0 0 0 3px rgba(198,33,78,.22),0 10px 28px rgba(198,33,78,.18)!important;
    transform:translateY(-5px) scale(1.03)!important;
    background:{ROSE_TINT}!important;
}}
.song-card.selected::after{{
    content:'✓';position:absolute;top:8px;right:9px;
    background:{OLD_ROSE};color:{SURFACE};
    border-radius:50%;width:22px;height:22px;line-height:22px;
    text-align:center;font-size:12px;font-weight:700;
    box-shadow:0 2px 6px rgba(74,14,32,.25);
}}
.card-img{{width:100%;aspect-ratio:1/1;object-fit:cover;display:block;background:{ROSE_MID};}}
.card-info{{padding:0.65rem 0.8rem 0.75rem;}}
.card-name{{font-size:0.8rem;font-weight:600;color:{BORDEAUX};line-height:1.2;margin-bottom:0.15rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.card-artist{{font-size:0.7rem;color:{MUTED};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.card-pop{{font-size:0.65rem;color:{BRILL_ROSE};font-weight:600;margin-top:0.25rem;letter-spacing:0.03em;}}

/* ── Rec rows ── */
.rec-row{{
    display:flex;align-items:flex-start;gap:1rem;padding:1rem 1.2rem;
    background:{SURFACE};border:1.5px solid {BORDER};border-radius:12px;margin-bottom:0.6rem;
    transition:border-color .2s,box-shadow .2s;
}}
.rec-row:hover{{border-color:{BRILL_ROSE};box-shadow:0 3px 14px rgba(198,33,78,.09);}}
.rec-rank{{font-family:'Playfair Display',serif;font-size:1.45rem;font-weight:700;color:{OLD_ROSE};min-width:2.2rem;padding-top:.1rem;}}
.rec-body{{flex:1;}}
.rec-name{{font-size:.97rem;font-weight:600;color:{BORDEAUX};margin-bottom:.15rem;}}
.rec-artist{{font-size:.82rem;color:{MUTED};margin-bottom:.3rem;}}
.rec-why{{font-size:.76rem;color:{OLD_ROSE};background:rgba(198,33,78,.07);border-radius:6px;padding:.2rem .6rem;display:inline-block;margin-top:.15rem;}}
.score-pill{{background:linear-gradient(135deg,{OLD_ROSE},{BRILL_ROSE});color:{SURFACE};border-radius:20px;padding:.25rem .8rem;font-size:.78rem;font-weight:600;white-space:nowrap;margin-top:.2rem;}}

/* ── Tags ── */
.tag-lime{{background:rgba(182,187,121,.2);border:1px solid {LIME};color:#4a4f10;border-radius:12px;padding:.15rem .6rem;font-size:.72rem;font-weight:600;display:inline-block;margin-right:.3rem;}}
.tag-rose{{background:rgba(237,95,154,.12);border:1px solid {BRILL_ROSE};color:{OLD_ROSE};border-radius:12px;padding:.15rem .6rem;font-size:.72rem;font-weight:600;display:inline-block;margin-right:.3rem;}}
.seed-chip{{display:inline-block;background:rgba(182,187,121,.18);border:1.5px solid {LIME};color:{BORDEAUX};border-radius:20px;padding:.25rem .8rem;font-size:.8rem;font-weight:500;margin:.2rem;}}

/* ── Metric box ── */
.metric-box{{background:{SURFACE};border:1.5px solid {BORDER};border-radius:12px;padding:.9rem 1.1rem;text-align:center;margin-bottom:.5rem;}}
.metric-val{{font-family:'Playfair Display',serif;font-size:1.8rem;font-weight:700;color:{OLD_ROSE};}}
.metric-label{{font-size:.7rem;color:{MUTED};text-transform:uppercase;letter-spacing:.07em;}}

/* ── LA matrix table ── */
.la-matrix{{width:100%;border-collapse:collapse;font-size:.78rem;font-family:monospace;}}
.la-matrix th{{background:{OLD_ROSE};color:{SURFACE};padding:.4rem .6rem;}}
.la-matrix td{{padding:.35rem .6rem;border-bottom:1px solid {BORDER};color:{TEXT};}}
.la-matrix tr:nth-child(even) td{{background:{SURFACE2};}}
.la-highlight{{color:{OLD_ROSE};font-weight:700;}}

/* ── Streamlit overrides ── */
.stSlider>div>div>div>div{{background:{OLD_ROSE}!important;}}
div[data-testid="stSelectbox"] label,div[data-testid="stMultiSelect"] label,
div[data-testid="stSlider"] label{{color:{TEXT}!important;font-weight:500;}}
.stButton>button{{background:{OLD_ROSE};color:{SURFACE};border:none;border-radius:8px;font-weight:600;padding:.45rem 1.2rem;transition:background .2s;}}
.stButton>button:hover{{background:{BRILL_ROSE};color:{SURFACE};}}
[data-testid="stTextInput"] input{{background:{SURFACE}!important;border:1.5px solid {BORDER}!important;color:{TEXT}!important;border-radius:8px!important;}}
.stTabs [data-baseweb="tab-list"]{{background:{SURFACE};border-radius:10px;border:1.5px solid {BORDER};padding:.3rem;}}
.stTabs [data-baseweb="tab"]{{color:{MUTED}!important;}}
.stTabs [aria-selected="true"]{{background:{OLD_ROSE}!important;color:{SURFACE}!important;border-radius:8px!important;}}
.stExpander{{background:{SURFACE}!important;border:1.5px solid {BORDER}!important;border-radius:12px!important;}}
.stExpander summary{{color:{BORDEAUX}!important;font-weight:600;}}
hr{{border-color:{BORDER}!important;}}
/* Remove any dark/transparent plotly backgrounds that bleed through */
.js-plotly-plot .plotly .modebar{{background:{SURFACE}!important;}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_songs():
    p = DATA / "songs.csv"
    if not p.exists(): st.error(f"songs.csv not found at {p}"); st.stop()
    df = pd.read_csv(p)
    for c in ['track_name','name','title','song']:
        if c in df.columns: df=df.rename(columns={c:'name'}); break
    for c in ['artists','artist','artist_name','track_artist']:
        if c in df.columns: df=df.rename(columns={c:'artist'}); break
    for c in ['track_id','id','spotify_id']:
        if c in df.columns: df=df.rename(columns={c:'track_id'}); break
    for c in ['popularity','Popularity']:
        if c in df.columns: df=df.rename(columns={c:'popularity'}); break
    if 'artist'     not in df.columns: df['artist']     = 'Unknown'
    if 'track_id'   not in df.columns: df['track_id']   = None
    if 'popularity' not in df.columns: df['popularity'] = 50
    feats = [c for c in ['energy','danceability','valence','acousticness',
                          'speechiness','instrumentalness','liveness','tempo']
             if c in df.columns]
    keep = ['name','artist','track_id','popularity']+feats
    df = df[[c for c in keep if c in df.columns]].dropna(subset=['name'])
    df['name']       = df['name'].astype(str).str.strip()
    df['artist']     = df['artist'].astype(str).str.strip()
    df['popularity'] = pd.to_numeric(df['popularity'],errors='coerce').fillna(50)
    df = df.sort_values('popularity',ascending=False).drop_duplicates(subset=['name']).reset_index(drop=True)
    if 'tempo' in feats:
        ti=feats.index('tempo'); col=df['tempo'].values.astype(float)
        rng=col.max()-col.min()
        if rng>0: df['tempo']=(col-col.min())/rng
    return df, feats

@st.cache_data
def load_ratings(n_songs):
    path=DATA/"ratings.csv"
    if not path.exists(): return np.zeros((0,n_songs)),[]
    df=pd.read_csv(path,index_col=0)
    R=df.values.astype(float)
    if R.shape[1]>n_songs: R=R[:,:n_songs]
    elif R.shape[1]<n_songs: R=np.hstack([R,np.zeros((R.shape[0],n_songs-R.shape[1]))])
    return R,list(df.index)

songs_df, FEAT_COLS = load_songs()
S_raw        = songs_df[FEAT_COLS].values.astype(float)
song_names   = songs_df['name'].tolist()
song_artists = songs_df['artist'].tolist()
track_ids    = songs_df['track_id'].tolist()
popularities = songs_df['popularity'].tolist()
R, users     = load_ratings(len(song_names))

# ═══════════════════════════════════════════════════════════════════════════
# ALBUM ART  — iTunes Search API (free, no auth)
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False, ttl=86400)
def fetch_album_art_batch(song_artist_pairs: tuple) -> dict:
    """
    Fetches album art URLs for a batch of (song, artist) pairs via iTunes API.
    Returns dict: (song, artist) -> art_url or ""
    """
    result = {}
    for name, artist in song_artist_pairs:
        query = urllib.parse.quote(f"{name} {artist}")
        try:
            r = requests.get(
                f"https://itunes.apple.com/search?term={query}&entity=song&limit=1",
                timeout=3
            )
            data = r.json()
            if data.get('resultCount', 0) > 0:
                url = data['results'][0].get('artworkUrl100', '')
                result[(name, artist)] = url.replace('100x100bb', '300x300bb')
            else:
                result[(name, artist)] = ""
        except Exception:
            result[(name, artist)] = ""
    return result

# ═══════════════════════════════════════════════════════════════════════════
# AUDIO FINGERPRINT SVG  — fallback when no album art
# ═══════════════════════════════════════════════════════════════════════════
def fingerprint_svg(feat_vals, width=160, height=160):
    n  = len(feat_vals)
    if n == 0:
        return f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"><rect width="{width}" height="{height}" fill="{SURFACE}"/></svg>'
    cx,cy  = width/2, height/2
    r_max  = min(cx,cy)*0.80
    r_min  = r_max*0.22
    val_i  = FEAT_COLS.index('valence')    if 'valence'    in FEAT_COLS else 0
    eng_i  = FEAT_COLS.index('energy')     if 'energy'     in FEAT_COLS else 0
    v_val  = float(feat_vals[val_i])
    e_val  = float(feat_vals[eng_i])

    def lerp(t,c1,c2):
        r1,g1,b1=int(c1[1:3],16),int(c1[3:5],16),int(c1[5:7],16)
        r2,g2,b2=int(c2[1:3],16),int(c2[3:5],16),int(c2[5:7],16)
        return f'#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}'

    bar_col  = lerp(v_val, LIME, BRILL_ROSE)
    bg_col   = lerp(v_val*0.25, SURFACE, ROSE_MID)
    glow_a   = 0.10 + e_val*0.22

    paths = []
    for i,val in enumerate(feat_vals):
        ang  = 2*math.pi*i/n - math.pi/2
        bw   = 2*math.pi/n*0.72
        a1,a2 = ang-bw/2, ang+bw/2
        r_bar = r_min + (r_max-r_min)*float(val)
        def pt(r,a): return (cx+r*math.cos(a), cy+r*math.sin(a))
        x1i,y1i=pt(r_min,a1); x2i,y2i=pt(r_min,a2)
        x1o,y1o=pt(r_bar,a1); x2o,y2o=pt(r_bar,a2)
        lf = 1 if bw>math.pi else 0
        op = 0.50+float(val)*0.48
        paths.append(
            f'<path d="M{x1i:.1f},{y1i:.1f} A{r_min:.1f},{r_min:.1f} 0 {lf},1 {x2i:.1f},{y2i:.1f} '
            f'L{x2o:.1f},{y2o:.1f} A{r_bar:.1f},{r_bar:.1f} 0 {lf},0 {x1o:.1f},{y1o:.1f}Z" '
            f'fill="{bar_col}" opacity="{op:.2f}"/>'
        )
    return (
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
        f'<rect width="{width}" height="{height}" fill="{bg_col}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r_max*0.92:.1f}" fill="{bar_col}" opacity="{glow_a:.2f}"/>'
        + ''.join(paths)
        + f'<circle cx="{cx}" cy="{cy}" r="{r_min*0.7:.1f}" fill="{SURFACE}" opacity="0.92"/>'
        f'</svg>'
    )

def norm01(idx):
    row=S_raw[idx].copy(); mn,mx=S_raw.min(0),S_raw.max(0)
    rng=mx-mn; rng[rng==0]=1; return (row-mn)/rng

# ═══════════════════════════════════════════════════════════════════════════
# LA ENGINE
# ═══════════════════════════════════════════════════════════════════════════
def zscore(S):
    mu=S.mean(0); sig=S.std(0); sig[sig==0]=1
    return (S-mu)/sig, mu, sig

def per_feat_match(song_z, centroid_z):
    return 1.0/(1.0+np.abs(song_z-centroid_z))

def geo_mean_score(per_feat):
    return np.exp(np.sum(np.log(per_feat+1e-9),axis=1)/per_feat.shape[1])

def cosine_sim_vec(q, S):
    qn=np.linalg.norm(q)
    if qn==0: return np.zeros(len(S))
    Sn=np.linalg.norm(S,axis=1); Sn[Sn==0]=1
    return np.clip((S@q)/(Sn*qn),0,None)

def euc_sim_vec(q, S):
    return 1.0/(1.0+np.linalg.norm(S-q,axis=1))

def minmax_scale(scores_dict, base=60, top=100):
    vals = np.array(list(scores_dict.values()), dtype=float)
    mn, mx = vals.min(), vals.max()
    if mx - mn < 1e-9:
        return {k: float(base + (top-base)/2) for k in scores_dict}
    return {k: float(base + (top-base)*(v-mn)/(mx-mn)) for k,v in scores_dict.items()}

def get_recommendations(seed_indices, alpha, beta, gamma, top_n=10, div_w=0.15):
    S_z,_,_ = zscore(S_raw)
    centroid = S_z[seed_indices].mean(axis=0)

    pf  = per_feat_match(S_z, centroid)
    geo = geo_mean_score(pf)
    cos = cosine_sim_vec(centroid, S_z)
    euc = euc_sim_vec(centroid, S_z)
    # weights: cosine 0.5 · euclidean 0.3 · geometric-mean 0.2
    p1  = 0.50*cos + 0.30*euc + 0.20*geo
    if p1.max()>0: p1/=p1.max()

    p3 = np.zeros(len(song_names))
    if R.shape[0]>0 and R.sum()>0:
        p3 = np.clip(R.mean(1,keepdims=True)+R.mean(0,keepdims=True)-R.mean(),0,1).mean(0)
        if p3.max()>0: p3/=p3.max()

    final = alpha*p1 + beta*p1 + gamma*p3

    # ── Zero all seeds ─────────────────────────────────────────────────────
    seed_names = {song_names[i] for i in seed_indices}
    for i, sn in enumerate(song_names):
        if sn in seed_names: final[i] = -1.0

    # Diversity penalty
    top_cands = np.argsort(final)[::-1][:top_n*4]
    for cidx in top_cands:
        if final[cidx] < 0: continue
        dists   = np.linalg.norm(S_z[seed_indices]-S_z[cidx],axis=1)
        penalty = max(0,(dists.mean()-dists.min())/(1.5+1e-6))
        final[cidx] = max(0, final[cidx]-div_w*penalty)

    # ── Deduplicate by name ────────────────────────────────────────────────
    seen_names = set(seed_names)
    rec_idx    = []
    for idx in np.argsort(final)[::-1]:
        if final[idx] <= 0: continue
        if song_names[idx] in seen_names: continue
        seen_names.add(song_names[idx])
        rec_idx.append(idx)
        if len(rec_idx) >= top_n: break

    # ── Min-max scale to 60-100 for display ───────────────────────────────
    raw_map    = {idx: float(final[idx]) for idx in rec_idx}
    scaled_pct = minmax_scale(raw_map, base=60, top=100)

    # ── Rich why: top-3 matching features per song ────────────────────────
    why = []
    for idx in rec_idx:
        pf_row = per_feat_match(S_z[idx], centroid)
        top3_i = np.argsort(pf_row)[::-1][:3]
        why.append({
            "top3":    [(FEAT_COLS[i], float(pf_row[i])) for i in top3_i],
            "euc_d":   float(np.linalg.norm(S_z[idx]-centroid)),
            "pf_row":  pf_row,
            "cos":     float(cos[idx]),
            "euc_sim": float(euc[idx]),
            "geo":     float(geo[idx]),
        })

    return rec_idx, final, scaled_pct, p1, p3, centroid, S_z, why

def compute_corr():
    if R.shape[0]<2 or R.sum()==0: return None,None,None,None
    rated_idxs = np.where(R.sum(axis=0)>=2)[0]
    if len(rated_idxs)<2: return None,None,None,None
    R_sub     = R[:,rated_idxs]
    sub_names = [song_names[i] for i in rated_idxs]
    with np.errstate(invalid='ignore',divide='ignore'):
        C_s = np.nan_to_num(np.corrcoef(R_sub.T))
        C_u = np.nan_to_num(np.corrcoef(R))
    return C_s,C_u,sub_names,users

# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════
def spotify_embed(track_id, h=80):
    if not track_id or str(track_id).lower() in ('nan','none',''): return ""
    return (f'<iframe style="border-radius:10px;margin-top:.5rem;" '
            f'src="https://open.spotify.com/embed/track/{track_id}?utm_source=generator&theme=0" '
            f'width="100%" height="{h}" frameBorder="0" allowfullscreen="" '
            f'allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" '
            f'loading="lazy"></iframe>')

def img_tag(url, fallback_svg, name):
    if url:
        return f'<img src="{url}" class="card-img" alt="{name}" onerror="this.style.display=\'none\'">'
    svg_b64 = "data:image/svg+xml;charset=utf-8," + fallback_svg.replace('#','%23').replace('"',"'")
    return f'<img src="{svg_b64}" class="card-img" alt="{name}">'

# ═══════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════
if 'selected_songs' not in st.session_state:
    st.session_state.selected_songs = []
if 'page' not in st.session_state:
    st.session_state.page = "🎵 Select Songs"

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='padding:1rem 0 .2rem'>
        <div style='font-family:Playfair Display,serif;font-size:1.9rem;font-weight:700;color:{BORDEAUX};letter-spacing:-.01em;'>Melodix</div>
        <div style='font-size:.7rem;color:{MUTED};letter-spacing:.1em;text-transform:uppercase;'>Linear Algebra · Music Curation</div>
    </div><hr>""", unsafe_allow_html=True)

    page = st.radio("",
        ["🎵 Select Songs","🎯 Your Playlist","🔬 Correlation Analysis","📐 LA Concepts"],
        label_visibility="collapsed",
        index=["🎵 Select Songs","🎯 Your Playlist","🔬 Correlation Analysis","📐 LA Concepts"]
               .index(st.session_state.page)
    )
    st.session_state.page = page

    sel_count = len(st.session_state.selected_songs)
    if sel_count > 0:
        st.markdown(f"""
        <div style='background:{ROSE_TINT};border:1.5px solid {ROSE_MID};
                    border-radius:10px;padding:.8rem 1rem;margin:.8rem 0;'>
            <div style='font-size:.72rem;color:{MUTED};text-transform:uppercase;letter-spacing:.06em;margin-bottom:.4rem;'>Seeds selected</div>
            {"".join(f"<div style='font-size:.8rem;color:{BORDEAUX};font-weight:500;margin:.15rem 0;'>🎵 {s[:24]}</div>" for s in st.session_state.selected_songs)}
        </div>""", unsafe_allow_html=True)
        if st.button("✕  Clear all seeds"):
            st.session_state.selected_songs = []
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    if page == "🎯 Your Playlist":
        st.markdown(f"<div style='font-size:.75rem;color:{MUTED};font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:.7rem;'>Score Fusion Weights</div>", unsafe_allow_html=True)
        alpha = st.slider("α  P1 · Similarity", 0.0, 1.0, 0.5, 0.05)
        beta  = st.slider("β  P2 · Taste",      0.0, 1.0, 0.3, 0.05)
        gamma = st.slider("γ  P3 · Ratings",    0.0, 1.0, 0.2, 0.05)
        total = alpha+beta+gamma
        if abs(total-1.0)>0.01:
            st.warning(f"Sum={total:.2f} — auto-normalised.")
            alpha/=total; beta/=total; gamma/=total
        st.session_state.weights = (alpha,beta,gamma)
    else:
        st.session_state.setdefault('weights',(0.5,0.3,0.2))

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='metric-box'><div class='metric-val'>{len(song_names):,}</div><div class='metric-label'>Songs</div></div>
    <div class='metric-box'><div class='metric-val'>{len(users)}</div><div class='metric-label'>Classmates</div></div>
    <div class='metric-box'><div class='metric-val'>{len(FEAT_COLS)}</div><div class='metric-label'>Audio Features</div></div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 1 — SELECT SONGS
# ═══════════════════════════════════════════════════════════════════════════
if page == "🎵 Select Songs":
    st.markdown(f"""
    <div class='hero-title'>Choose Your<br>Seed Songs.</div>
    <div class='hero-sub'>Pick 3–5 songs · Your taste centroid is computed from these</div>
    """, unsafe_allow_html=True)

    # Controls
    c1, c2, c3 = st.columns([3,1,1])
    search_q = c1.text_input("🔍 Search", placeholder="Song name or artist…", label_visibility="collapsed")
    pop_min  = c2.slider("Min popularity", 0, 100, 60, 5)
    n_show   = c3.select_slider("Show", [12,24,36,48], value=24)

    pool = [
        i for i,(_,a,p) in enumerate(zip(song_names,song_artists,popularities))
        if p >= pop_min and (not search_q or
            search_q.lower() in song_names[i].lower() or
            search_q.lower() in a.lower())
    ]
    if len(pool) < 6:
        pool = sorted(range(len(song_names)), key=lambda i:-popularities[i])[:200]
    pool = sorted(pool, key=lambda i:-popularities[i])[:n_show]

    # Fetch album art for this pool (cached)
    with st.spinner("Loading album covers…"):
        pairs = tuple((song_names[i], song_artists[i]) for i in pool)
        art   = fetch_album_art_batch(pairs)

    # ── Selected song players (shown at top) ─────────────────────────────
    sel = st.session_state.selected_songs
    if sel:
        st.markdown(f"<div class='section-title'>Your Seeds — Spotify Preview</div>",
                    unsafe_allow_html=True)
        pcols = st.columns(min(len(sel), 5))
        for col, sname in zip(pcols, sel):
            if sname not in song_names: continue
            sidx = song_names.index(sname)
            art_url = art.get((sname, song_artists[sidx]),"")
            tid     = str(track_ids[sidx]) if track_ids[sidx] else ""
            with col:
                if art_url:
                    st.image(art_url, use_container_width=True)
                else:
                    fv  = norm01(sidx)
                    svg = fingerprint_svg(fv)
                    b64 = "data:image/svg+xml;charset=utf-8,"+svg.replace('#','%23').replace('"',"'")
                    st.image(b64, use_container_width=True)
                st.markdown(f"<div style='font-size:.78rem;font-weight:600;color:{BORDEAUX};text-align:center;'>{sname[:22]}</div>", unsafe_allow_html=True)
                if tid and tid not in ('nan','None'):
                    st.markdown(spotify_embed(tid,80), unsafe_allow_html=True)

        if len(sel) >= 3:
            st.markdown(f"<br>", unsafe_allow_html=True)
            if st.button("🎯  Generate Playlist →", type="primary"):
                st.session_state.page = "🎯 Your Playlist"
                st.rerun()

    if len(sel) >= 5:
        st.info("Maximum 5 seeds selected. Remove a song to pick another.")

    # ── Card grid ─────────────────────────────────────────────────────────
    st.markdown(f"<div class='section-title'>Browse & Select</div>", unsafe_allow_html=True)

    COLS = 6
    rows = [pool[i:i+COLS] for i in range(0,len(pool),COLS)]

    for row_pool in rows:
        cols = st.columns(len(row_pool))
        for col, idx in zip(cols, row_pool):
            sname  = song_names[idx]
            artist = song_artists[idx]
            pop    = int(popularities[idx])
            is_sel = sname in st.session_state.selected_songs
            art_url= art.get((sname,artist),"")
            fv     = norm01(idx)
            svg    = fingerprint_svg(fv)

            sel_cls = "selected" if is_sel else ""
            with col:
                st.markdown(f"""
                <div class='song-card {sel_cls}'>
                    {img_tag(art_url, svg, sname)}
                    <div class='card-info'>
                        <div class='card-name' title='{sname}'>{sname[:20]}</div>
                        <div class='card-artist'>{artist[:18]}</div>
                        <div class='card-pop'>★ {pop}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                lbl = "✓ Remove" if is_sel else "+ Select"
                if st.button(lbl, key=f"card_{idx}", use_container_width=True):
                    if is_sel:
                        st.session_state.selected_songs.remove(sname)
                    elif len(st.session_state.selected_songs) < 5:
                        st.session_state.selected_songs.append(sname)
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 2 — YOUR PLAYLIST
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🎯 Your Playlist":
    sel = [s for s in st.session_state.selected_songs if s in song_names]
    seed_indices = [song_names.index(s) for s in sel]

    if len(sel) < 3:
        st.warning("Go back to **Select Songs** and choose at least 3 seeds first.")
        st.stop()

    alpha,beta,gamma = st.session_state.get('weights',(0.5,0.3,0.2))

    st.markdown(f"""
    <div class='hero-title'>Your Curated<br>Playlist.</div>
    <div class='hero-sub'>Taste centroid computed across {len(FEAT_COLS)} audio features · Z-score standardised</div>
    """, unsafe_allow_html=True)

    c1,c2 = st.columns([1,1])
    top_n  = c1.select_slider("Playlist length",[5,8,10,12,15],value=10)
    div_w  = c2.slider("Diversity",0.0,0.5,0.15,0.05)

    rec_idx,final_scores,scaled_pct,p1,p3,centroid,S_z,why = get_recommendations(
        seed_indices,alpha,beta,gamma,top_n,div_w
    )

    # Seeds display
    chips = "".join(f"<span class='seed-chip'>🎵 {s}</span>" for s in sel)
    st.markdown(f"<div style='margin:.5rem 0 1rem;'>{chips}</div>", unsafe_allow_html=True)

    # Centroid card
    top_feats = sorted(enumerate(centroid), key=lambda x:abs(x[1]),reverse=True)[:4]
    feat_tags = "".join(
        f"<span class='tag-lime'>{FEAT_COLS[i]}: {v:+.2f}σ</span>"
        for i,v in top_feats if abs(v)>0.2
    ) or f"<span style='color:{MUTED};'>Balanced across all features</span>"

    st.markdown(f"""
    <div class='card card-lime'>
        <div style='font-size:.78rem;color:{MUTED};margin-bottom:.4rem;text-transform:uppercase;letter-spacing:.05em;'>
            v̄ = ({' + '.join([f's{i+1}' for i in range(len(seed_indices))])}) / {len(seed_indices)} &nbsp;·&nbsp; {len(FEAT_COLS)}-dimensional z-score space
        </div>
        <div>{feat_tags}</div>
    </div>""", unsafe_allow_html=True)

    with st.expander("📊 Taste Centroid Radar"):
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(
            r=np.clip(centroid,-3,3).tolist()+[centroid[0]],
            theta=FEAT_COLS+[FEAT_COLS[0]], fill='toself',
            fillcolor='rgba(237,95,154,0.15)',
            line=dict(color=OLD_ROSE,width=2.5), name='Taste Centroid'
        ))
        for sidx in seed_indices:
            fig_r.add_trace(go.Scatterpolar(
                r=np.clip(S_z[sidx],-3,3).tolist()+[S_z[sidx][0]],
                theta=FEAT_COLS+[FEAT_COLS[0]], fill='toself',
                fillcolor='rgba(182,187,121,0.08)',
                line=dict(color=LIME,width=1,dash='dot'),
                name=song_names[sidx][:20], opacity=0.7
            ))
        fig_r.update_layout(
            polar=dict(bgcolor=SURFACE,
                       radialaxis=dict(visible=True,range=[-3,3],color=MUTED,gridcolor=BORDER),
                       angularaxis=dict(color=TEXT,gridcolor=BORDER)),
            paper_bgcolor=SURFACE,
            font=dict(color=TEXT,family='DM Sans'),
            height=380,margin=dict(t=30,b=30),showlegend=True,
            legend=dict(font=dict(size=9),bgcolor=SURFACE)
        )
        st.plotly_chart(fig_r,use_container_width=True)

    # Fetch art for recommendations
    with st.spinner("Loading album covers…"):
        rec_pairs = tuple((song_names[i],song_artists[i]) for i in rec_idx)
        rec_art   = fetch_album_art_batch(rec_pairs)

    # Recommendations
    st.markdown(f"<div class='section-title'>Recommended for You</div>", unsafe_allow_html=True)

    for rank, idx in enumerate(rec_idx, 1):
        w        = why[rank-1]
        top3     = w["top3"]           # [(feat, score), (feat, score), (feat, score)]
        euc_d    = w["euc_d"]
        pf_row   = w["pf_row"]
        cos_v    = w["cos"]
        euc_v    = w["euc_sim"]
        geo_v    = w["geo"]
        disp_pct = scaled_pct[idx]

        art_url  = rec_art.get((song_names[idx], song_artists[idx]), "")
        tid      = str(track_ids[idx]) if track_ids[idx] else ""

        # ── "Why this song?" — top-3 features natural language ────────────
        top3_names = [f for f, _ in top3]
        why_text = "Strong match in " + ", ".join(top3_names)

        # ── Feature contribution bars with labels ──────────────────────────
        top3_set = {f for f, _ in top3}
        bar_rows = ""
        for i, feat in enumerate(FEAT_COLS):
            score    = float(pf_row[i])
            fill_pct = int(score * 100)
            is_top   = feat in top3_set
            bar_col  = BRILL_ROSE if is_top else ROSE_MID
            label_col= OLD_ROSE   if is_top else MUTED
            weight   = "600"      if is_top else "400"
            bar_rows += (
                f"<div style='display:flex;align-items:center;gap:.5rem;"
                f"margin:.18rem 0;'>"
                f"<span style='font-size:.68rem;color:{label_col};font-weight:{weight};"
                f"width:90px;text-align:right;flex-shrink:0;'>{feat}</span>"
                f"<div style='flex:1;background:{ROSE_MID};border-radius:4px;height:7px;'>"
                f"<div style='width:{fill_pct}%;background:{bar_col};height:100%;"
                f"border-radius:4px;'></div></div>"
                f"<span style='font-size:.68rem;color:{label_col};font-weight:{weight};"
                f"width:2.5rem;'>{score:.2f}</span>"
                f"</div>"
            )

        embed = spotify_embed(tid) if tid not in ("nan","None","") else ""

        if art_url:
            art_html = f'<img src="{art_url}" style="width:72px;height:72px;border-radius:10px;object-fit:cover;flex-shrink:0;" alt="">'  
        else:
            fv  = norm01(idx)
            svg = fingerprint_svg(fv, 72, 72)
            b64 = "data:image/svg+xml;charset=utf-8," + svg.replace("#", "%23").replace('"', "'")
            art_html = f'<img src="{b64}" style="width:72px;height:72px;border-radius:10px;flex-shrink:0;" alt="">'

        st.markdown(f"""
        <div class='rec-row' style='align-items:flex-start;'>
            <div class='rec-rank'>#{rank}</div>
            {art_html}
            <div class='rec-body' style='flex:1;'>
                <div class='rec-name'>{song_names[idx]}</div>
                <div class='rec-artist'>{song_artists[idx]}</div>
                <div class='rec-why' style='margin:.35rem 0;'>💡 {why_text}</div>
                <details style='margin-top:.4rem;'>
                    <summary style='font-size:.73rem;color:{MUTED};cursor:pointer;
                               list-style:none;'>&rsaquo; Feature contribution</summary>
                    <div style='margin-top:.4rem;'>{bar_rows}</div>
                    <div style='font-size:.68rem;color:{MUTED};margin-top:.4rem;'>
                        cos {cos_v:.3f} · euc {euc_v:.3f} · geo {geo_v:.3f} · dist {euc_d:.2f}σ
                    </div>
                </details>
                {embed}
            </div>
            <div style='padding-top:.1rem;'><span class='score-pill'>{disp_pct:.1f}%</span></div>
        </div>
        """, unsafe_allow_html=True)

    # LA Transparency tabs
    st.markdown(f"<div class='section-title'>🔢 LA Calculation Transparency</div>", unsafe_allow_html=True)
    tab_dp,tab_pf,tab_geo = st.tabs(["Dot Products & Norms","Per-Feature Match Heatmap","Geometric Mean Scores"])

    cn = float(np.linalg.norm(centroid))

    with tab_dp:
        st.markdown(f"`cosine(s, c̄) = (s · c̄) / (‖s‖ × ‖c̄‖)` · ‖centroid‖ = **{cn:.4f}**")
        rows=[]
        for rank,idx in enumerate(rec_idx,1):
            sv=S_z[idx]; dot=float(sv@centroid); sn=float(np.linalg.norm(sv))
            cos=dot/(sn*cn+1e-9); ed=float(np.linalg.norm(sv-centroid))
            rows.append({"#":f"#{rank}","Song":song_names[idx][:26],
                         "s·c̄":f"{dot:+.3f}","‖s‖":f"{sn:.3f}",
                         "Cosine":f"{cos:.3f}","Eucl.dist":f"{ed:.3f}",
                         "Scaled %":f"{scaled_pct.get(idx, final_scores[idx]*100):.1f}%"})
        df_r=pd.DataFrame(rows)
        hdr="".join(f"<th>{c}</th>" for c in df_r.columns)
        bdy="".join(
            "<tr>"+"".join(
                f"<td class='{'la-highlight' if c in ('Cosine','Final %') else ''}'>{v}</td>"
                for c,v in row.items()
            )+"</tr>"
            for _,row in df_r.iterrows()
        )
        st.markdown(f"<div style='overflow-x:auto;'><table class='la-matrix'><thead><tr>{hdr}</tr></thead><tbody>{bdy}</tbody></table></div>",
                    unsafe_allow_html=True)

    with tab_pf:
        st.markdown("`match[f] = 1 / (1 + |z_song[f] − z_centroid[f]|)` · 1.0 = perfect match")
        pf_rows=[{
            "#":rank, "Song":song_names[idx][:22],
            **{f:round(float(per_feat_match(S_z[idx],centroid)[i]),3) for i,f in enumerate(FEAT_COLS)}
        } for rank,idx in enumerate(rec_idx,1)]
        pf_df=pd.DataFrame(pf_rows)
        heat_z=pf_df[FEAT_COLS].values
        heat_y=[f"#{r['#']} {r['Song']}" for r in pf_rows]
        fig_pf=px.imshow(heat_z,x=FEAT_COLS,y=heat_y,
                         color_continuous_scale=[[0,YUCCA],[0.5,BRILL_ROSE],[1.0,BORDEAUX]],
                         zmin=0,zmax=1,aspect='auto',text_auto='.2f')
        fig_pf.update_layout(
            paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
            font=dict(color=TEXT,size=10,family='DM Sans'),
            height=max(280,top_n*38), margin=dict(t=10,b=10,l=180,r=10),
            coloraxis_colorbar=dict(title='Match',tickfont=dict(color=TEXT))
        )
        fig_pf.update_xaxes(tickangle=30,tickfont=dict(color=TEXT))
        fig_pf.update_yaxes(tickfont=dict(color=TEXT))
        st.plotly_chart(fig_pf,use_container_width=True)
        st.caption("Bright rose = feature closely matches your centroid. All features contribute equally — no single feature dominates.")

    with tab_geo:
        st.markdown("`geo = exp( mean(log(match[f])) )` · A song must score well on ALL features.")
        grows=[]
        for rank,idx in enumerate(rec_idx,1):
            pf=per_feat_match(S_z[idx],centroid)
            geo=float(np.exp(np.mean(np.log(pf+1e-9))))
            cs=float(np.dot(S_z[idx],centroid)/(np.linalg.norm(S_z[idx])*cn+1e-9))
            eu=float(1/(1+np.linalg.norm(S_z[idx]-centroid)))
            grows.append({"#":f"#{rank}","Song":song_names[idx][:24],
                           "Geo Mean":f"{geo:.4f}","Cosine":f"{max(cs,0):.4f}",
                           "Eucl.Sim":f"{eu:.4f}","P1":f"{p1[idx]:.4f}","Scaled %":f"{scaled_pct.get(idx, final_scores[idx]*100):.1f}%"})
        gdf=pd.DataFrame(grows)
        hdr="".join(f"<th>{c}</th>" for c in gdf.columns)
        bdy="".join("<tr>"+"".join(
            f"<td class='{'la-highlight' if c in ('Geo Mean','Final %') else ''}'>{v}</td>"
            for c,v in row.items())+"</tr>"
            for _,row in gdf.iterrows())
        st.markdown(f"<div style='overflow-x:auto;'><table class='la-matrix'><thead><tr>{hdr}</tr></thead><tbody>{bdy}</tbody></table></div>",
                    unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 3 — CORRELATION ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🔬 Correlation Analysis":
    st.markdown(f"""
    <div class='hero-title'>Correlation<br>Analysis.</div>
    <div class='hero-sub'>Structural relationships from classmates' listening data</div>
    """, unsafe_allow_html=True)

    C_songs,C_users,sub_names,user_list = compute_corr()
    cs = [[0.0,YUCCA],[0.5,BRILL_ROSE],[1.0,BORDEAUX]]

    if C_songs is None:
        st.warning("No ratings data. Run `python process_form_data.py` first.")
        st.stop()

    tab1,tab2 = st.tabs(["🎵  Song–Song Correlation","👥  User–User Correlation"])

    with tab1:
        st.markdown(f"""
        <div class='card card-rose'>
        <b>Formula:</b> C_songs = corr(Rᵀ) — normalised covariance of song column vectors in R.<br>
        <b>Reading it:</b> C[i,j] near 1.0 → classmates who liked song i also liked song j.<br>
        <b>Colour:</b> {YUCCA} = zero correlation → {BRILL_ROSE} = strong positive correlation.
        </div>""", unsafe_allow_html=True)

        n_r  = len(sub_names)
        top_k = st.slider("Songs to display",5,min(40,n_r),min(20,n_r))
        cnts  = np.array([C_songs[i,:].sum() for i in range(n_r)])
        ti    = np.argsort(cnts)[::-1][:top_k]
        C_d   = C_songs[np.ix_(ti,ti)]
        lbls  = [sub_names[i][:22] for i in ti]
        assert C_d.shape==(len(lbls),len(lbls))

        fig_cs = px.imshow(C_d,x=lbls,y=lbls,color_continuous_scale=cs,
                           zmin=-1,zmax=1,aspect='auto',text_auto='.2f')
        fig_cs.update_layout(
            paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
            font=dict(color=TEXT,size=9,family='DM Sans'),
            height=620,margin=dict(t=10,b=80,l=140),
            coloraxis_colorbar=dict(title='Corr.',tickfont=dict(color=TEXT),tickvals=[-1,-0.5,0,0.5,1])
        )
        fig_cs.update_xaxes(tickangle=45,tickfont=dict(size=8,color=TEXT))
        fig_cs.update_yaxes(tickfont=dict(size=8,color=TEXT))
        st.plotly_chart(fig_cs,use_container_width=True)
        st.caption(f"Top {top_k} most-liked songs. Each cell = corr(Rᵀ)[i,j].")

    with tab2:
        st.markdown(f"""
        <div class='card card-rose'>
        <b>Formula:</b> C_users = corr(R) — pairwise correlation of user row vectors.<br>
        <b>Reading it:</b> C[i,j] ≈ 1.0 → nearly identical music taste between two classmates.
        </div>""", unsafe_allow_html=True)

        ulabels=[str(u)[:14] for u in user_list]
        fig_cu=px.imshow(C_users,x=ulabels,y=ulabels,
                          color_continuous_scale=cs,zmin=-1,zmax=1,aspect='auto')
        fig_cu.update_layout(
            paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
            font=dict(color=TEXT,size=9,family='DM Sans'),
            height=640,margin=dict(t=10,b=80,l=140),
            coloraxis_colorbar=dict(tickfont=dict(color=TEXT))
        )
        fig_cu.update_xaxes(tickangle=45,tickfont=dict(size=8,color=TEXT))
        st.plotly_chart(fig_cu,use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 4 — LA CONCEPTS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📐 LA Concepts":
    st.markdown(f"""
    <div class='hero-title'>The Linear Algebra<br>Behind Melodix.</div>
    <div class='hero-sub'>Every recommendation is a sequence of matrix operations</div>
    """, unsafe_allow_html=True)

    concepts=[
        ("Vectors","p1","Each song is a point in audio feature space.",
         "s = [energy, danceability, valence, acousticness, …]  ∈ ℝⁿ",
         "All similarity calculations operate on these vectors. The feature matrix S has shape (n_songs × n_features)."),
        ("Z-Score Standardisation","all","Equalises all features before similarity — prevents any one dimension dominating.",
         "z[f] = (x[f] − μ[f]) / σ[f]   per column of S",
         "Without this, features with large absolute range (e.g. tempo 60–200 BPM) drown out features bounded in [0,1]."),
        ("Taste Centroid","p2","Mean of your seed vectors — your musical centre of gravity.",
         "v̄ = (s₁ + s₂ + … + sₙ) / n",
         "Vector addition + scalar multiplication. This is the textbook definition of a linear combination."),
        ("Per-Feature Match Score","p1","Proximity on each feature dimension independently.",
         "match[f] = 1 / (1 + | z_song[f] − z_centroid[f] |)",
         "Produces n scores (one per feature). Close to centroid on that feature → score near 1.0."),
        ("Geometric Mean (Balance)","p1","Forces multi-feature balance — no single feature can carry the playlist.",
         "geo = exp( (1/n) Σ log(match[f]) )",
         "A song 0.9 on energy but 0.1 on valence scores ~0.3. A song 0.65 on all features scores 0.65. Balance wins."),
        ("Cosine Similarity","p1","Direction match between song vector and taste centroid.",
         "sim(s, v̄) = (s · v̄) / ( ‖s‖ · ‖v̄‖ )",
         "Captures directional alignment. Combined with geometric mean: 50% balance + 30% direction + 20% distance."),
        ("Euclidean Distance","p1","Straight-line gap in z-score feature space.",
         "d(s, v̄) = ‖s − v̄‖ = √( Σ (s[f] − v̄[f])² )",
         "Used in the 'Why' analysis. The dominant feature is the dimension with smallest absolute gap to the centroid."),
        ("Rating Matrix","p3","Binary users × songs matrix from the Google Form responses.",
         "R ∈ ℝᵐˣⁿ,   R[i,j] = 1  if user i liked song j",
         f"Shape = ({len(users)} classmates × {len(song_names)} songs). The entire survey dataset in one matrix."),
        ("Score Fusion — Linear Combination","all","Final score is a weighted sum of all three pillars.",
         "score = α·P₁ + β·P₂ + γ·P₃,   α + β + γ = 1",
         "This IS the textbook definition of a linear combination. Weights are tunable in real-time via the sidebar."),
        ("Correlation Matrix","p3","Pairwise structural relationships between songs or users.",
         "C_songs = corr(Rᵀ),   C_users = corr(R),   entries ∈ [−1, 1]",
         "C[i,j] ≈ 1 → songs i,j are consistently liked together. Visible on the Correlation Analysis page."),
    ]

    plab={'p1':'Pillar 1','p2':'Pillar 2','p3':'Pillar 3','all':'All Pillars'}
    ptag={'p1':'tag-rose','p2':'tag-lime','p3':'tag-rose','all':'tag-lime'}

    for title,pillar,what,formula,why in concepts:
        st.markdown(f"""
        <div class='card' style='margin-bottom:.9rem;'>
            <div style='display:flex;align-items:center;gap:.7rem;margin-bottom:.5rem;'>
                <span style='font-family:Playfair Display,serif;font-size:1.05rem;font-weight:700;color:{BORDEAUX};'>{title}</span>
                <span class='{ptag[pillar]}'>{plab[pillar]}</span>
            </div>
            <div style='color:{MUTED};font-size:.88rem;margin-bottom:.5rem;'>{what}</div>
            <div style='background:{YUCCA};border:1.5px solid {BORDER};border-radius:8px;
                        padding:.55rem 1rem;font-family:monospace;color:{OLD_ROSE};
                        font-size:.9rem;margin-bottom:.5rem;'>{formula}</div>
            <div style='font-size:.82rem;color:{TEXT};'>{why}</div>
        </div>
        """, unsafe_allow_html=True)