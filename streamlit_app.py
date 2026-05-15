import streamlit as st
import pandas as pd
from collections import Counter
import requests
import urllib.parse
import re
import time
import hashlib
import base64

# --- Page Configuration ---
st.set_page_config(
    page_title="Migros Library",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# 1. CUSTOM CSS — Migros × Netflix Hybrid
# ─────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap');

    /* ── Reset & Base ── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: #F7F6F2 !important;
        font-family: 'DM Sans', sans-serif !important;
        color: #1a1a1a !important;
    }

    /* Hide Streamlit chrome */
    #MainMenu, header[data-testid="stHeader"], footer,
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }

    [data-testid="stSidebar"] { display: none !important; }

    /* Remove default padding to fix top space issue */
    .main .block-container, [data-testid="stMainBlockContainer"] {
        padding: 0 !important;
        padding-top: 0rem !important; /* Forces top alignment */
        max-width: 100% !important;
    }

    /* ── Sticky Header ── */
    .mig-header {
        position: sticky;
        top: 0;
        z-index: 9999;
        background: #fff;
        border-bottom: 2px solid #FF6600;
        padding: 0 2.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 64px;
        box-shadow: 0 2px 20px rgba(0,0,0,0.08);
    }
    .mig-logo {
        font-family: 'Sora', sans-serif;
        font-weight: 800;
        font-size: 1.6rem;
        color: #FF6600;
        letter-spacing: -0.5px;
    }
    .mig-logo span { color: #1a1a1a; }
    .mig-nav-title {
        font-family: 'Sora', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: #555;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .mig-user-pill {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        background: #FFF3EB;
        border: 1.5px solid #FF6600;
        border-radius: 50px;
        padding: 0.4rem 1rem 0.4rem 0.6rem;
    }
    .mig-avatar {
        width: 38px; height: 38px;
        background: #FFF3EB;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.35rem;
        line-height: 1;
        border: 2px solid #FF6600;
    }
    .mig-user-info { line-height: 1.2; }
    .mig-cumulus-num { font-size: 0.7rem; color: #888; font-weight: 500; }
    .mig-points { font-size: 0.85rem; font-weight: 700; color: #FF6600; }
    
    .mig-logout-btn {
        font-family: 'Sora', sans-serif !important;
        font-weight: 600 !important; font-size: 0.8rem !important;
        color: #ffffff !important; border: 1.5px solid #FF6600 !important;
        border-radius: 8px !important; padding: 0.42rem 1rem !important;
        text-decoration: none !important; white-space: nowrap !important;
        transition: all 0.2s !important; background: #FF6600 !important;
        display: inline-block !important;
    }
    .mig-logout-btn:hover, .mig-logout-btn:visited, .mig-logout-btn:active { 
        background: #e05500 !important; color: #ffffff !important; 
        border-color: #e05500 !important; text-decoration: none !important; 
    }

    /* ── Page Wrapper ── */
    /* Minimal top padding to close the gap */
    .mig-page { padding: 0.5rem 2.5rem 4rem; }

    /* ── Hero Section ── */
    .mig-hero {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d1f00 40%, #FF6600 100%);
        border-radius: 20px;
        padding: 2.5rem 3rem;
        margin-top: 0.5rem; /* Pulled up close to header */
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .mig-hero::before {
        content: '';
        position: absolute;
        top: -50%; right: -10%;
        width: 500px; height: 500px;
        background: radial-gradient(circle, rgba(255,102,0,0.3) 0%, transparent 70%);
    }
    .mig-hero h1 {
        font-family: 'Sora', sans-serif;
        font-size: 2rem; font-weight: 800;
        color: #fff; margin-bottom: 0.3rem;
        position: relative;
    }
    .mig-hero p { color: rgba(255,255,255,0.65); font-size: 0.95rem; position: relative; }
    .mig-hero .points-badge {
        position: absolute; right: 3rem; top: 50%; transform: translateY(-50%);
        background: rgba(255,255,255,0.1);
        border: 1.5px solid rgba(255,102,0,0.5);
        border-radius: 16px;
        padding: 1rem 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .mig-hero .points-badge .pts-num {
        font-family: 'Sora', sans-serif;
        font-size: 2.2rem; font-weight: 800; color: #ffffff !important;
        display: block; line-height: 1;
    }
    .mig-hero .points-badge .pts-label { 
        color: #ffffff !important; 
        font-size: 0.85rem !important; 
        margin-top: 0.2rem !important; 
        display: block !important; 
        font-weight: 500 !important; 
    }

    /* ── Tabs ── */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 2px solid #e8e8e8 !important;
        gap: 0 !important;
        margin-bottom: 1.5rem;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        font-family: 'Sora', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        color: #888 !important;
        padding: 0.75rem 1.5rem !important;
        border-bottom: 3px solid transparent !important;
        background: transparent !important;
        border-radius: 0 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        transition: all 0.2s !important;
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        color: #FF6600 !important;
        border-bottom-color: #FF6600 !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab-panel"] {
        background: transparent !important;
        padding: 0.5rem 1.5rem 2rem 1.5rem !important; 
    }

    /* ── Book Cards Grid ── */
    .book-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 1.5rem;
    }
    .book-card {
        background: #fff;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        cursor: pointer;
        position: relative;
        margin-bottom: 0.8rem !important;
    }
    .book-card:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 12px 32px rgba(255,102,0,0.18);
    }
    .book-cover {
        width: 100%; height: 240px;
        object-fit: cover;
        display: block;
    }
    .book-info { padding: 0.9rem 1rem 1rem; }
    .book-title-text {
        font-family: 'Sora', sans-serif;
        font-weight: 700; font-size: 0.85rem;
        color: #1a1a1a; margin-bottom: 0.25rem;
        display: -webkit-box; -webkit-line-clamp: 2;
        -webkit-box-orient: vertical; overflow: hidden;
        line-height: 1.3;
    }
    .book-author-link {
        font-size: 0.75rem; color: #FF6600;
        font-weight: 500; text-decoration: none;
        display: block; margin-bottom: 0.3rem;
    }
    .book-author-link:hover { text-decoration: underline; }
    .book-subject {
        font-size: 0.7rem; color: #999;
        background: #F7F6F2; border-radius: 20px;
        padding: 0.2rem 0.6rem; display: inline-block;
        margin-bottom: 0.5rem;
    }
    .book-desc {
        font-size: 0.72rem; color: #666; line-height: 1.4;
        display: -webkit-box; -webkit-line-clamp: 3;
        -webkit-box-orient: vertical; overflow: hidden;
        margin-bottom: 0.7rem;
    }
    .read-badge {
        display: inline-flex; align-items: center; gap: 0.3rem;
        background: #E8F5E9; color: #2E7D32;
        font-size: 0.7rem; font-weight: 600;
        border-radius: 20px; padding: 0.25rem 0.65rem;
        margin-bottom: 0.5rem;
    }

    /* ── Mark as Read Button ── */
    .stButton > button {
        font-family: 'Sora', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        border-radius: 8px !important;
        border: 1.5px solid #FF6600 !important;
        color: #FF6600 !important;
        background: transparent !important;
        padding: 0.35rem 0.9rem !important;
        transition: all 0.2s !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background: #FF6600 !important;
        color: #fff !important;
    }

    /* ── Section Headers ── */
    .section-header {
        font-family: 'Sora', sans-serif;
        font-weight: 800; font-size: 1.4rem;
        color: #1a1a1a; margin-bottom: 1.25rem;
        display: flex; align-items: center; gap: 0.5rem;
    }
    .section-header .accent { color: #FF6600; }

    /* ── Leaderboard ── */
    .leaderboard-row {
        display: flex; align-items: center;
        background: #fff; border-radius: 12px;
        padding: 1rem 1.25rem; margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .leaderboard-row:hover { transform: translateX(4px); }
    
    .rank-num {
        font-family: 'Sora', sans-serif;
        font-weight: 800; font-size: 1.4rem;
        min-width: 50px; 
        white-space: nowrap; 
        flex-shrink: 0;
        color: #ddd;
    }
    .rank-num.gold { color: #FFD700; }
    .rank-num.silver { color: #C0C0C0; }
    .rank-num.bronze { color: #CD7F32; }
    .rank-avatar {
        width: 42px; height: 42px;
        border-radius: 50%; background: #FF6600;
        display: flex; align-items: center; justify-content: center;
        font-family: 'Sora', sans-serif; font-weight: 700;
        color: #fff; font-size: 0.9rem; margin-right: 1rem;
    }
    .rank-user { flex: 1; }
    .rank-name { font-weight: 600; font-size: 0.9rem; }
    .rank-id { font-size: 0.75rem; color: #999; }
    .rank-pts {
        font-family: 'Sora', sans-serif;
        font-weight: 800; font-size: 1.1rem; color: #FF6600;
    }
    .rank-pts span { font-size: 0.7rem; color: #aaa; font-weight: 400; margin-left: 0.2rem; }

    /* ── Friends / Book Club ── */
    .friend-card {
        background: #fff; border-radius: 14px;
        padding: 1.25rem 1.5rem; margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border-left: 4px solid #FF6600;
    }
    .friend-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; }
    .friend-avatar {
        width: 48px; height: 48px; border-radius: 50%;
        background: linear-gradient(135deg, #FF6600, #ff9a44);
        display: flex; align-items: center; justify-content: center;
        font-family: 'Sora', sans-serif; font-weight: 700;
        color: #fff; font-size: 1.5rem;
    }
    .friend-name { font-family: 'Sora', sans-serif; font-weight: 700; font-size: 1rem; }
    .friend-mutual { font-size: 0.78rem; color: #888; }
    .shared-book-chip {
        display: inline-flex; align-items: center; gap: 0.3rem;
        background: #FFF3EB; border: 1px solid #FFD4B2;
        border-radius: 20px; padding: 0.3rem 0.8rem;
        font-size: 0.75rem; font-weight: 500; color: #CC4400;
        margin: 0.25rem 0.25rem 0 0;
    }

    /* ── Top 10 ── */
    .top10-item {
        display: flex; align-items: center; gap: 1rem;
        background: #fff; border-radius: 12px;
        padding: 0.9rem 1.2rem; margin-bottom: 0.6rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .top10-rank {
        font-family: 'Sora', sans-serif;
        font-weight: 800; font-size: 1.3rem; color: #eee;
        min-width: 45px; 
        text-align: center;
        white-space: nowrap;
        flex-shrink: 0;
    }
    .top10-rank.highlight { color: #FF6600; }
    .top10-info { flex: 1; }
    .top10-title { font-weight: 600; font-size: 0.88rem; color: #1a1a1a; }
    .top10-author { font-size: 0.75rem; color: #888; }
    .top10-reads { font-family: 'Sora', sans-serif; font-weight: 700; color: #FF6600; font-size: 0.9rem; }
    .top10-reads span { font-size: 0.68rem; color: #aaa; font-weight: 400; }

    /* ── Author filter banner ── */
    .author-filter-banner {
        background: linear-gradient(135deg, #FFF3EB, #FFE4CC);
        border: 1.5px solid #FFD4B2;
        border-radius: 12px; padding: 0.9rem 1.25rem;
        margin-bottom: 1.5rem;
        display: flex; align-items: center; justify-content: space-between;
    }
    .author-filter-text { font-size: 0.9rem; font-weight: 600; color: #CC4400; }

    /* ── Empty state ── */
    .empty-state {
        text-align: center; padding: 4rem 2rem;
        color: #bbb;
    }
    .empty-state .empty-icon { font-size: 3rem; margin-bottom: 1rem; }
    .empty-state p { font-size: 0.95rem; }

    /* Streamlit form inputs */
    [data-testid="stTextInput"] input {
        border: 2px solid #eee !important;
        border-radius: 10px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.95rem !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #FF6600 !important;
        box-shadow: 0 0 0 3px rgba(255,102,0,0.1) !important;
    }
    [data-testid="stTextInput"] label {
        font-family: 'Sora', sans-serif !important;
        font-weight: 600 !important; font-size: 0.82rem !important;
        color: #555 !important;
    }

    /* Selectbox */
    [data-testid="stSelectbox"] { display: none; }

    /* Alert / info */
    [data-testid="stAlert"] {
        border-radius: 10px !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* Spinner */
    [data-testid="stSpinner"] { color: #FF6600 !important; }

    /* Login page */
    .login-only-mode [data-testid="stVerticalBlock"] > div:empty { display: none !important; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #F7F6F2; }
    ::-webkit-scrollbar-thumb { background: #FF6600; border-radius: 3px; }
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        read_file_url  = "https://raw.githubusercontent.com/ElPatron100/Library-Recommender-Team-Migros/main/interactions_train.csv"
        rec_file_url   = "https://raw.githubusercontent.com/ElPatron100/Library-Recommender-Team-Migros/main/sample_submission.csv"
        items_file_url = "https://raw.githubusercontent.com/ElPatron100/Library-Recommender-Team-Migros/main/items.csv"

        df_read  = pd.read_csv(read_file_url)
        df_rec   = pd.read_csv(rec_file_url)
        df_items = pd.read_csv(items_file_url)

        df_items.columns = df_items.columns.str.strip()
        df_read.columns  = df_read.columns.str.strip()

        df_read  = df_read.rename(columns={'u': 'user_id', 'i': 'item_id'})
        df_items = df_items.rename(columns={'i': 'item_id', 'Title': 'title'})

        df_items['title']  = df_items['title'].str.split('/').str[0].str.strip()
        df_items['Author'] = df_items['Author'].fillna("Unknown Author")

        if 'Subjects' in df_items.columns:
            df_items['Subjects'] = df_items['Subjects'].fillna("General")
        else:
            df_items['Subjects'] = "General"

        def clean_isbn(x):
            if pd.isna(x): return ""
            match = re.search(r'\b(\d{13}|\d{10})\b', str(x))
            return match.group(0) if match else "".join(filter(str.isdigit, str(x)))[:13]

        df_items['isbn'] = df_items['ISBN Valid'].apply(clean_isbn) if 'ISBN Valid' in df_items.columns else ""

        df_read['user_id']  = df_read['user_id'].astype(str)
        df_read['item_id']  = df_read['item_id'].astype(str)
        df_items['item_id'] = df_items['item_id'].astype(str)

        # ── Robust rec parsing ──────────────────────────────────────────────
        df_rec.columns = df_rec.columns.str.strip()
        df_rec['user_id'] = df_rec['user_id'].astype(str).str.strip()

        non_user_cols = [c for c in df_rec.columns if c.lower() not in ('user_id', 'userid')]

        if len(non_user_cols) == 1:
            col = non_user_cols[0]
            sample_val = str(df_rec[col].dropna().iloc[0]) if not df_rec[col].dropna().empty else ""
            if ' ' in sample_val and not sample_val.replace(' ', '').isdigit() is False:
                rows = []
                for _, row in df_rec.iterrows():
                    uid = str(row['user_id'])
                    for iid in str(row[col]).split():
                        iid = iid.strip()
                        if iid and iid not in ('nan', ''):
                            rows.append({'user_id': uid, 'item_id': iid})
                df_rec = pd.DataFrame(rows)
            else:
                df_rec = df_rec.rename(columns={col: 'item_id'})
                df_rec['item_id'] = df_rec['item_id'].astype(str).str.strip()
        else:
            rows = []
            for _, row in df_rec.iterrows():
                uid = str(row['user_id'])
                for col in non_user_cols:
                    val = str(row[col]).strip()
                    if val and val not in ('nan', ''):
                        rows.append({'user_id': uid, 'item_id': val})
            df_rec = pd.DataFrame(rows)

        df_rec = df_rec.dropna(subset=['item_id'])
        df_rec = df_rec[df_rec['item_id'].astype(str).str.strip().ne('')]
        df_rec['user_id'] = df_rec['user_id'].astype(str)
        df_rec['item_id'] = df_rec['item_id'].astype(str).str.strip()

        item_mapping   = dict(zip(df_items['item_id'], df_items['title']))
        isbn_mapping   = dict(zip(df_items['item_id'], df_items['isbn']))
        author_mapping = dict(zip(df_items['item_id'], df_items['Author']))

        return df_read, df_rec, item_mapping, isbn_mapping, author_mapping, df_items
    except Exception as e:
        return None, None, None, None, None, str(e)

# ─────────────────────────────────────────────
# 3. GOOGLE BOOKS API
# ─────────────────────────────────────────────
def fetch_book_data(isbn, title="", author=""):
    cache_key = isbn or f"{title}_{author}"
    if not cache_key:
        return None, None

    if 'book_cache' not in st.session_state:
        st.session_state.book_cache = {}

    if cache_key in st.session_state.book_cache:
        return st.session_state.book_cache[cache_key]

    API_KEY = "AIzaSyBiQlaEe0ZsJIWkfRQB5jiekhF5Qu_RNag"
    url = "https://www.googleapis.com/books/v1/volumes"

    queries = []
    if isbn and len(isbn) >= 8:
        queries.append(f"isbn:{isbn}")
    if title:
        queries.append(f"intitle:{title}")

    cover_url = None
    description = None

    for q in queries:
        try:
            time.sleep(0.05)
            resp = requests.get(url, params={"q": q, "key": API_KEY, "maxResults": 1}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if "items" in data:
                    vi = data["items"][0].get("volumeInfo", {})
                    img = vi.get("imageLinks", {})
                    img_url = img.get("thumbnail") or img.get("smallThumbnail")
                    if img_url:
                        cover_url = img_url.replace("http:", "https:")
                    description = vi.get("description", "")
                    if description:
                        description = description[:200] + ("…" if len(description) > 200 else "")
                    if cover_url:
                        break
        except Exception:
            pass

    result = (cover_url, description)
    st.session_state.book_cache[cache_key] = result
    return result

# ─────────────────────────────────────────────
# 4. ROBUST BASE64 PLACEHOLDER COVER GENERATOR
# ─────────────────────────────────────────────
COVER_THEMES = [
    ("#FF9A44", "#FC6076"), ("#00C9FF", "#92FE9D"), ("#f12711", "#f5af19"),
    ("#654ea3", "#eaafc8"), ("#FF416C", "#FF4B2B"), ("#00B4DB", "#0083B0"),
    ("#8E2DE2", "#4A00E0"), ("#F09819", "#EDDE5D"), ("#1D976C", "#93F9B9"),
    ("#EB3349", "#F45C43")
]

def get_placeholder_html(title, author=""):
    title_str = str(title) if title else ""
    idx = int(hashlib.md5(title_str.encode()).hexdigest(), 16) % len(COVER_THEMES)
    bg1, bg2 = COVER_THEMES[idx]

    words = title_str.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if len(test) <= 18:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
        if len(lines) == 3 and cur:
            lines.append(cur[:16] + ("…" if len(cur) > 16 else ""))
            cur = ""
            break
    if cur and len(lines) < 4:
        lines.append(cur)
    lines = lines[:4]

    title_start_y = max(90, 130 - len(lines) * 14)
    
    # Fully secure XML escaper to prevent quotes from breaking SVG parsing
    def safe_xml(s): return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace("'",'&#39;')
    
    tspans = "".join(f'<tspan x="100" dy="{0 if i == 0 else 24}">{safe_xml(l)}</tspan>' for i, l in enumerate(lines))

    # Raw SVG string
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="240" viewBox="0 0 200 240"><defs><linearGradient id="cvbg{idx}" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="{bg1}"/><stop offset="100%" stop-color="{bg2}"/></linearGradient></defs><rect width="200" height="240" fill="url(#cvbg{idx})"/><path d="M30 180 Q 100 150 170 180 L 170 60 Q 100 30 30 60 Z" fill="rgba(255,255,255,0.15)"/><path d="M100 45 L 100 165" stroke="rgba(255,255,255,0.3)" stroke-width="2"/><text x="100" y="{title_start_y}" text-anchor="middle" font-family="Sora, sans-serif" font-size="14" font-weight="700" fill="#ffffff" letter-spacing="0.5">{tspans}</text></svg>'
    
    # CRITICAL FIX: Encode SVG to Base64 to bypass Streamlit's aggressive markdown HTML stripper
    b64_svg = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    img_src = f"data:image/svg+xml;base64,{b64_svg}"
    
    return f'<img class="book-cover" src="{img_src}" alt="Placeholder Cover">'

# ─────────────────────────────────────────────
# 5. SESSION STATE INIT
# ─────────────────────────────────────────────
def init_session():
    defaults = {
        'logged_in': False,
        'user_id': None,
        'cumulus_number': None,
        'read_books': set(),
        'cumulus_points': 0,
        'author_filter': None,
        'book_cache': {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ─────────────────────────────────────────────
# 6. HELPERS
# ─────────────────────────────────────────────
def get_cumulus_points():
    return len(st.session_state.read_books) * 50

def subject_short(subj_str, n=1):
    if not subj_str or subj_str == "General":
        return "General"
    parts = re.split(r'[;,|/]', str(subj_str))
    return parts[0].strip()[:30] if parts else "General"

def wiki_url(author):
    return f"https://en.wikipedia.org/wiki/Special:Search?search={urllib.parse.quote_plus(str(author))}"

# ─────────────────────────────────────────────
# 7. HEADER
# ─────────────────────────────────────────────
ANIMALS = ["🦊","🐻","🦁","🐯","🐼","🦝","🐨","🦄","🐸","🦋",
           "🐺","🦉","🦚","🦜","🐙","🦈","🐬","🦩","🦦","🐧",
           "🦔","🦥","🦘","🐲","🦕","🐳","🦭","🐆","🦓","🦏"]

def get_animal(uid):
    idx = int(hashlib.md5(str(uid).encode()).hexdigest(), 16) % len(ANIMALS)
    return ANIMALS[idx]

def render_header():
    uid = st.session_state.cumulus_number or st.session_state.user_id or "—"
    pts = get_cumulus_points()
    animal = get_animal(uid)

    params = st.query_params
    if params.get("logout") == "1":
        st.query_params.clear()
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    st.markdown(f"""
    <div class="mig-header">
        <div style="display:flex;align-items:center;gap:1.5rem;">
            <div class="mig-logo">MIGROS <span>Library</span></div>
            <div class="mig-nav-title">Recommender Dashboard</div>
        </div>
        <div style="display:flex;align-items:center;gap:0.75rem;">
            <div class="mig-user-pill">
                <div class="mig-avatar">{animal}</div>
                <div class="mig-user-info">
                    <div class="mig-cumulus-num">#{uid}</div>
                    <div class="mig-points">⭐ {pts:,} pts</div>
                </div>
            </div>
            <a href="?logout=1" class="mig-logout-btn">Logout</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 8. BOOK CARD RENDERER
# ─────────────────────────────────────────────
def render_book_card(item_id, df_items, show_read_btn=True, context_key="", show_author_filter=False):
    row = df_items[df_items['item_id'] == str(item_id)]
    if row.empty:
        return

    r       = row.iloc[0]
    title   = str(r.get('title', 'Unknown Title'))
    author  = str(r.get('Author', 'Unknown Author'))
    isbn    = str(r.get('isbn', ''))
    subject = subject_short(r.get('Subjects', 'General'))
    is_read = item_id in st.session_state.read_books

    cover_url, description = fetch_book_data(isbn, title, author)

    if description:
        description = re.sub(r'<[^>]+>', '', str(description)).strip()
        description = description[:200] + ("…" if len(description) > 200 else "")

    def he(s): return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace("'",'&#39;')

    desc_html  = f'<div class="book-desc">{he(description)}</div>' if description else ""
    read_badge = '<div class="read-badge">✓ Read · +50 pts</div>' if is_read else ""
    author_href = wiki_url(author)

    if cover_url:
        cover_html = f'<img class="book-cover" src="{cover_url}" alt="{he(title)}" onerror="this.style.display=\'none\'">'
    else:
        cover_html = get_placeholder_html(title, author)

    html_content = f'<div class="book-card">{cover_html}<div class="book-info"><div class="book-title-text">{he(title)}</div><a class="book-author-link" href="{author_href}" target="_blank" title="Search Wikipedia for {he(author)}">{he(author)}</a><div class="book-subject">{he(subject)}</div>{desc_html}{read_badge}</div></div>'
    
    st.markdown(html_content, unsafe_allow_html=True)

    if show_author_filter:
        filter_key = f"filt_{item_id}_{context_key}"
        if st.button(f"🔍 Books by {author[:20]}", key=filter_key):
            st.session_state.author_filter = author
            st.rerun()

    if show_read_btn and not is_read:
        read_key = f"read_{item_id}_{context_key}"
        if st.button("✓ Mark as Read  +50 pts", key=read_key):
            st.session_state.read_books.add(item_id)
            st.rerun()
    elif is_read:
        st.markdown('<p style="font-size:0.72rem;color:#2E7D32;text-align:center;margin-top:0.3rem;">✅ In your reading history</p>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 9. LOGIN PAGE
# ─────────────────────────────────────────────
def render_login(df_read):
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d1f00 50%, #FF6600 100%) !important;
        min-height: 100vh;
    }
    .main .block-container {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 2rem !important;
    }
    .login-box {
        background: #fff;
        border-radius: 24px;
        padding: 3rem 2.5rem 2.5rem;
        width: 100%;
        box-shadow: 0 30px 80px rgba(0,0,0,0.4);
    }
    </style>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.6, 1])
    with center:
        st.markdown("""
        <div class="login-box">
            <div style="text-align:center;font-family:Sora,sans-serif;font-weight:800;font-size:2.2rem;color:#FF6600;margin-bottom:0.2rem;">MIGROS</div>
            <div style="text-align:center;font-family:Sora,sans-serif;font-weight:700;font-size:1rem;color:#1a1a1a;margin-bottom:0.4rem;">Library</div>
            <div style="text-align:center;color:#aaa;font-size:0.82rem;margin-bottom:2rem;">Sign in with your Cumulus Number to access your dashboard</div>
        </div>
        """, unsafe_allow_html=True)

        cumulus_input = st.text_input("Cumulus Number", placeholder="e.g. 1042", key="login_cumulus")
        password_input = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pw")
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if st.button("Sign In →", key="login_btn", use_container_width=True):
            if not cumulus_input.strip():
                st.error("Please enter your Cumulus Number.")
            elif not password_input.strip():
                st.error("Please enter your password.")
            else:
                uid = cumulus_input.strip()
                valid_users = df_read['user_id'].unique().tolist() if df_read is not None else []
                if uid in valid_users:
                    for k in ['login_cumulus', 'login_pw']:
                        if k in st.session_state:
                            del st.session_state[k]
                    st.session_state.logged_in = True
                    st.session_state.user_id = uid
                    st.session_state.cumulus_number = uid
                    user_reads = df_read[df_read['user_id'] == uid]['item_id'].tolist()
                    st.session_state.read_books = set(user_reads)
                    st.rerun()
                else:
                    st.error(f"Cumulus Number '{uid}' not found. Please check and try again.")

        st.markdown("""
        <div style="text-align:center;color:#ccc;font-size:0.72rem;margin-top:1.5rem;">
            © 2024 Migros · Library Recommender · Team Migros
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 10. TAB: RECOMMENDATIONS
# ─────────────────────────────────────────────
def tab_recommendations(df_rec, df_items):
    uid = st.session_state.user_id
    user_recs = df_rec[df_rec['user_id'] == uid]

    if 'item_id' in user_recs.columns:
        rec_ids = user_recs['item_id'].astype(str).tolist()
    else:
        rec_ids = []

    if st.session_state.author_filter:
        af = st.session_state.author_filter
        st.markdown(f"""
        <div class="author-filter-banner">
            <div class="author-filter-text">📚 Showing books by: <strong>{af}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✕ Clear filter", key="clear_author_filter"):
            st.session_state.author_filter = None
            st.rerun()
        af_ids = df_items[df_items['Author'] == af]['item_id'].tolist()
        display_ids = [i for i in rec_ids if i in af_ids] or af_ids[:20]
    else:
        display_ids = rec_ids

    if not display_ids:
        st.markdown('<div class="empty-state"><div class="empty-icon">📭</div><p>No recommendations found for this user.</p></div>', unsafe_allow_html=True)
        return

    st.markdown(f'<div class="section-header">Your <span class="accent">Picks</span> &nbsp;<span style="font-size:0.9rem;color:#999;font-weight:400">{len(display_ids)} books</span></div>', unsafe_allow_html=True)

    cols = st.columns(5)
    for idx, iid in enumerate(display_ids[:20]):
        with cols[idx % 5]:
            render_book_card(iid, df_items, show_read_btn=True, context_key=f"rec{idx}", show_author_filter=True)

# ─────────────────────────────────────────────
# 11. TAB: MY READING HISTORY
# ─────────────────────────────────────────────
def tab_reading_history(df_items):
    read_ids = list(st.session_state.read_books)

    if not read_ids:
        st.markdown('<div class="empty-state"><div class="empty-icon">📖</div><p>You haven\'t marked any books as read yet.</p></div>', unsafe_allow_html=True)
        return

    pts = get_cumulus_points()
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#FFF3EB,#FFE4CC);border-radius:14px;padding:1.25rem 1.5rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:1rem;">
        <div style="font-size:2rem;">⭐</div>
        <div>
            <div style="font-family:Sora,sans-serif;font-weight:800;font-size:1.3rem;color:#FF6600;">{pts:,} Cumulus Points</div>
            <div style="color:#888;font-size:0.82rem;">{len(read_ids)} books read · {len(read_ids)} × 50 pts</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-header">Reading <span class="accent">History</span></div>', unsafe_allow_html=True)

    cols = st.columns(5)
    for idx, iid in enumerate(read_ids):
        with cols[idx % 5]:
            render_book_card(iid, df_items, show_read_btn=False, context_key=f"hist{idx}")

# ─────────────────────────────────────────────
# 12. TAB: TOP 10 POPULAR
# ─────────────────────────────────────────────
def tab_top10(df_read, df_rec, df_items):
    counts = Counter(df_read['item_id'].tolist())
    if 'item_id' in df_rec.columns:
        for iid in df_rec['item_id']:
            counts[str(iid)] += 1

    top10 = counts.most_common(10)

    st.markdown('<div class="section-header">📈 Top <span class="accent">10</span> Most Popular</div>', unsafe_allow_html=True)

    for rank, (item_id, cnt) in enumerate(top10, 1):
        row = df_items[df_items['item_id'] == str(item_id)]
        if row.empty:
            continue
        r = row.iloc[0]
        title  = str(r.get('title', 'Unknown'))[:60]
        author = str(r.get('Author', 'Unknown'))

        hl = "highlight" if rank <= 3 else ""
        st.markdown(f"""
        <div class="top10-item">
            <div class="top10-rank {hl}">#{rank}</div>
            <div class="top10-info">
                <div class="top10-title">{title}</div>
                <div class="top10-author">{author}</div>
            </div>
            <div class="top10-reads">{cnt:,}<span> reads</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-header" style="margin-top: 2rem;">Visual <span class="accent">Showcase</span></div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for idx, (item_id, _) in enumerate(top10[:10]):
        with cols[idx % 5]:
            render_book_card(str(item_id), df_items, show_read_btn=True, context_key=f"top{idx}")

# ─────────────────────────────────────────────
# 13. TAB: BOOK CLUB
# ─────────────────────────────────────────────
def tab_friends(df_rec, df_items):
    uid = st.session_state.user_id

    if 'item_id' not in df_rec.columns:
        st.info("Recommendation data format not supported for friend matching.")
        return

    my_recs = set(df_rec[df_rec['user_id'] == uid]['item_id'].astype(str).tolist())

    if not my_recs:
        st.markdown('<div class="empty-state"><div class="empty-icon">👥</div><p>No recommendations found to match friends.</p></div>', unsafe_allow_html=True)
        return

    other_users = df_rec[df_rec['user_id'] != uid]
    overlap_scores = []
    for other_uid, grp in other_users.groupby('user_id'):
        their_recs = set(grp['item_id'].astype(str).tolist())
        shared = my_recs & their_recs
        if shared:
            overlap_scores.append((other_uid, shared, len(shared)))

    overlap_scores.sort(key=lambda x: -x[2])
    top_friends = overlap_scores[:5]

    if not top_friends:
        st.markdown('<div class="empty-state"><div class="empty-icon">🔍</div><p>No friends with matching recommendations found yet.</p></div>', unsafe_allow_html=True)
        return

    st.markdown('<div class="section-header">👥 Book <span class="accent">Club</span></div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#888;font-size:0.85rem;margin-bottom:1.5rem;">Readers who share your recommended books — read them together!</p>', unsafe_allow_html=True)

    for friend_uid, shared_ids, count in top_friends:
        animal_icon = get_animal(friend_uid)

        st.markdown(f"""
        <div class="friend-card" style="margin-bottom: 0.5rem; border-left: 4px solid #FF6600;">
            <div class="friend-header" style="margin-bottom: 0;">
                <div class="friend-avatar">{animal_icon}</div>
                <div>
                    <div class="friend-name">Reader #{friend_uid}</div>
                    <div class="friend-mutual">{count} book{"s" if count != 1 else ""} in common</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(5)
        for idx, iid in enumerate(list(shared_ids)[:5]):
            with cols[idx % 5]:
                render_book_card(str(iid), df_items, show_read_btn=True, context_key=f"friend_{friend_uid}_{idx}")
                
        st.markdown("<hr style='margin: 1.5rem 0; border-top: 1px solid #e8e8e8;'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 14. TAB: CUMULUS LEADERBOARD
# ─────────────────────────────────────────────
def tab_leaderboard(df_read):
    user_counts = df_read.groupby('user_id').size().reset_index(name='reads')
    user_counts['points'] = user_counts['reads'] * 50

    curr_uid = st.session_state.user_id
    curr_reads = len(st.session_state.read_books)
    curr_points = get_cumulus_points()

    user_counts.loc[user_counts['user_id'] == curr_uid, 'reads'] = curr_reads
    user_counts.loc[user_counts['user_id'] == curr_uid, 'points'] = curr_points

    user_counts = user_counts.sort_values('points', ascending=False).reset_index(drop=True)
    user_counts['rank'] = user_counts.index + 1

    my_row = user_counts[user_counts['user_id'] == curr_uid]
    my_rank = int(my_row['rank'].values[0]) if not my_row.empty else "—"

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1a1a1a,#2d1f00);border-radius:16px;padding:1.5rem 2rem;margin-bottom:2rem;display:flex;align-items:center;gap:2rem;">
        <div style="text-align:center;">
            <div style="font-family:Sora,sans-serif;font-weight:800;font-size:2.5rem;color:#FF6600;">#{my_rank}</div>
            <div style="color:rgba(255,255,255,0.5);font-size:0.75rem;">Your Rank</div>
        </div>
        <div style="width:1px;height:50px;background:rgba(255,255,255,0.1);"></div>
        <div style="text-align:center;">
            <div style="font-family:Sora,sans-serif;font-weight:800;font-size:2.5rem;color:#FFD700;">{curr_points:,}</div>
            <div style="color:rgba(255,255,255,0.5);font-size:0.75rem;">Your Points</div>
        </div>
        <div style="width:1px;height:50px;background:rgba(255,255,255,0.1);"></div>
        <div style="text-align:center;">
            <div style="font-family:Sora,sans-serif;font-weight:800;font-size:2.5rem;color:#fff;">{len(user_counts):,}</div>
            <div style="color:rgba(255,255,255,0.5);font-size:0.75rem;">Total Readers</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">🏆 Cumulus <span class="accent">Leaderboard</span></div>', unsafe_allow_html=True)

    rank_classes = {1: "gold", 2: "silver", 3: "bronze"}

    for _, row in user_counts.head(50).iterrows():
        rank = int(row['rank'])
        uid  = row['user_id']
        pts  = int(row['points'])
        is_me = uid == curr_uid
        animal_ldr = get_animal(uid)
        rank_cls = rank_classes.get(rank, "")

        highlight_style = "border: 2px solid #FF6600;" if is_me else ""
        me_badge = " 👈 <em style='color:#FF6600;font-size:0.7rem;'>You</em>" if is_me else ""

        st.markdown(f"""
        <div class="leaderboard-row" style="{highlight_style}">
            <div class="rank-num {rank_cls}">#{rank}</div>
            <div class="rank-avatar" style="background:{'#FFF3EB' if is_me else '#f5f5f5'};font-size:1.3rem;">{animal_ldr}</div>
            <div class="rank-user">
                <div class="rank-name">Reader #{uid}{me_badge}</div>
                <div class="rank-id">{int(row['reads'])} books read</div>
            </div>
            <div class="rank-pts">{pts:,}<span> pts</span></div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 15. MAIN APP
# ─────────────────────────────────────────────
def main():
    inject_css()
    init_session()

    with st.spinner("Loading Migros Library data…"):
        df_read, df_rec, item_mapping, isbn_mapping, author_mapping, df_items = load_data()

    if df_read is None:
        st.error(f"Failed to load data: {df_items}")
        return

    if not st.session_state.logged_in:
        render_login(df_read)
        st.stop()

    render_header()

    uid = st.session_state.user_id
    pts = get_cumulus_points()
    reads = len(st.session_state.read_books)

    st.markdown('<div class="mig-page">', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="mig-hero">
        <h1>Welcome back, Reader #{uid} 👋</h1>
        <p>Discover your next great read — personalised just for you.</p>
        <div class="points-badge">
            <span class="pts-num">{pts:,}</span>
            <span class="pts-label">⭐ Cumulus Points<br>{reads} books read</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs([
        "📚 Recommendations",
        "📖 My History",
        "🔥 Top 10",
        "👥 Book Club",
        "🏆 Leaderboard"
    ])

    with tabs[0]:
        tab_recommendations(df_rec, df_items)

    with tabs[1]:
        tab_reading_history(df_items)

    with tabs[2]:
        tab_top10(df_read, df_rec, df_items)

    with tabs[3]:
        tab_friends(df_rec, df_items)

    with tabs[4]:
        tab_leaderboard(df_read)

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()