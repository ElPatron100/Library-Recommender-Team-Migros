import streamlit as st
import pandas as pd
from collections import Counter
import requests
import urllib.parse
import re
import time

# --- Page Configuration ---
st.set_page_config(page_title="Library Dashboard", layout="wide")
st.title("📚 Library User Dashboard")

# --- 1. Data Loading ---
@st.cache_data
def load_data():
    try:
        read_file_url = "https://raw.githubusercontent.com/ElPatron100/Library-Recommender-Team-Migros/main/interactions_train.csv" 
        rec_file_url = "https://raw.githubusercontent.com/ElPatron100/Library-Recommender-Team-Migros/main/sample_submission.csv"
        items_file_url = "https://raw.githubusercontent.com/ElPatron100/Library-Recommender-Team-Migros/main/items.csv"
        
        df_read = pd.read_csv(read_file_url)
        df_rec = pd.read_csv(rec_file_url)
        df_items = pd.read_csv(items_file_url)

        df_items.columns = df_items.columns.str.strip()
        df_read.columns = df_read.columns.str.strip()
        df_read = df_read.rename(columns={'u': 'user_id', 'i': 'item_id'})
        df_items = df_items.rename(columns={'i': 'item_id', 'Title': 'title'})

        # TITLE CLEANER: Removes "/" and trailing whitespace perfectly
        df_items['title'] = df_items['title'].str.split('/').str[0].str.strip()

        # ISBN CLEANER: Finds the first 10 or 13-digit sequence
        def clean_isbn(x):
            if pd.isna(x): return ""
            match = re.search(r'\b(\d{13}|\d{10})\b', str(x))
            return match.group(0) if match else "".join(filter(str.isdigit, str(x)))[:13]

        df_items['isbn'] = df_items['ISBN Valid'].apply(clean_isbn)
        df_items['Author'] = df_items['Author'].fillna("Unknown Author")

        df_read['user_id'] = df_read['user_id'].astype(str)
        df_read['item_id'] = df_read['item_id'].astype(str)
        df_rec['user_id'] = df_rec['user_id'].astype(str)
        df_items['item_id'] = df_items['item_id'].astype(str)
        
        item_mapping = dict(zip(df_items['item_id'], df_items['title']))
        isbn_mapping = dict(zip(df_items['item_id'], df_items['isbn']))
        author_mapping = dict(zip(df_items['item_id'], df_items['Author']))
        
        return df_read, df_rec, item_mapping, isbn_mapping, author_mapping
    except Exception as e:
        return None, None, None, None, str(e)

with st.spinner("🔄 Loading Global Library Data..."):
    df_read, df_rec, item_mapping, isbn_mapping, author_mapping = load_data()

# --- 2. Advanced API Fetcher ---
# Removed @st.cache_data to prevent permanent caching of rate-limit failures
def fetch_poster_url(isbn):
    if not isbn or len(isbn) < 8: 
        return None
    
    # Initialize dictionary in session state if it doesn't exist
    if 'poster_cache' not in st.session_state:
        st.session_state.poster_cache = {}
        
    # Return from cache immediately if we already successfully searched this ISBN
    if isbn in st.session_state.poster_cache:
        return st.session_state.poster_cache[isbn]
        
    # YOUR API KEY
    API_KEY = "AIzaSyBiQlaEe0ZsJIWkfRQB5jiekhF5Qu_RNag"
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": f"isbn:{isbn}", "key": API_KEY}
    
    try:
        # 0.1s delay prevents hitting Google's burst rate limits (429 errors)
        time.sleep(0.1) 
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if "items" in data:
                img_links = data["items"][0].get("volumeInfo", {}).get("imageLinks", {})
                img_url = img_links.get("thumbnail") or img_links.get("smallThumbnail")
                if img_url:
                    secure_url = img_url.replace("http:", "https:")
                    st.session_state.poster_cache[isbn] = secure_url # Cache the success
                    return secure_url
            
            # If we get a 200 OK but no items, the book cover genuinely doesn't exist.
            # Cache the 'None' so we don't waste time querying it again.
            st.session_state.poster_cache[isbn] = None
            return None
            
        elif response.status_code == 429:
            # Rate limit hit! Do NOT cache this, so the app retries next time it loads.
            return None
            
    except Exception:
        # Network error or timeout. Do NOT cache this failure.
        pass
        
    return None

# --- 3. Grid Display Logic ---
def display_book_grid(book_ids, section_title):
    if not book_ids:
        st.write("No books to display.")
        return

    st.subheader(section_title)
    rows = [book_ids[i:i + 5] for i in range(0, len(book_ids), 5)]
    
    for row in rows:
        cols = st.columns(5)
        for i, item_id in enumerate(row):
            with cols[i]:
                title = item_mapping.get(str(item_id), "Unknown")
                isbn = isbn_mapping.get(str(item_id), "")
                author = author_mapping.get(str(item_id), "Unknown Author")
                
                poster_url = fetch_poster_url(isbn)
                
                # Dynamic Placeholder
                safe_title = urllib.parse.quote_plus(title[:35])
                placeholder = f"https://placehold.co/128x192/2e3440/d8dee9?text={safe_title}"
                
                display_url = poster_url if poster_url else placeholder
                
                st.markdown(
                    f'''
                    <div style="min-height: 270px; margin-bottom: 10px;">
                        <img src="{display_url}" 
                             onerror="this.onerror=null;this.src='{placeholder}';" 
                             style="width:100%; border-radius:10px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                    </div>
                    ''', 
                    unsafe_allow_html=True
                )
                st.write(f"**{title}**")
                st.caption(f"✍️ {author}")
                st.caption(f"🆔 {isbn}")

# --- 4. Main Dashboard UI ---
if df_read is None:
    st.error("Connection Error: Check GitHub source.")
else:
    user_id = st.sidebar.text_input("🔑 User Login (ID):")

    if user_id:
        if user_id in df_read['user_id'].values:
            # THE WELCOME MESSAGE
            st.success(f"Welcome back, User {user_id}!")
            
            tab1, tab2 = st.tabs(["📊 My Dashboard", "👥 Friend Recommendations"])

            with tab1:
                # History
                history = df_read[df_read['user_id'] == user_id]['item_id'].tolist()
                display_book_grid(history[-10:], "📖 Your Recent Reads")
                
                st.divider()
                
                # Recommendations
                r_col = df_rec.columns[1]
                r_str = df_rec[df_rec['user_id'] == user_id][r_col].values[0]
                r_list = [b.strip() for b in str(r_str).replace(',', ' ').split() if b.strip()]
                display_book_grid(r_list[:10], "⭐ Personalized Recommendations")
        else:
            st.warning("User ID not found in system.")