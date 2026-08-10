import streamlit as st
import pandas as pd
from scraper import scrape_books
from datetime import datetime
import os

st.set_page_config(
    page_title="Product Scraper",
    page_icon="🛒",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px 0;
    }
    .main-header h1 {
        font-size: 42px;
        margin-bottom: 8px;
    }
    .subtitle {
        color: #9a9ab0;
        font-size: 16px;
        margin-bottom: 30px;
    }
    .stat-card {
        background: rgba(108, 99, 255, 0.1);
        border: 1px solid rgba(108, 99, 255, 0.3);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .stat-label {
        font-size: 12px;
        color: #9a9ab0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stat-value {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        margin-top: 4px;
    }
    .footer {
        text-align: center;
        color: #6b6b80;
        font-size: 13px;
        margin-top: 40px;
        padding: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🛒 Product Scraper</h1>
    <p class="subtitle">Extract product information from an e-commerce website and export it as CSV</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("**Target Site:** [books.toscrape.com](https://books.toscrape.com)")
    st.markdown("A demo e-commerce site designed for legal web scraping practice.")

    st.divider()

    num_pages = st.slider(
        "Number of pages to scrape",
        min_value=1,
        max_value=50,
        value=3,
        help="Each page contains ~20 products"
    )

    st.info(f"You will scrape approximately **{num_pages * 20} products**.")

    st.divider()

    start_scrape = st.button("🚀 Start Scraping", type="primary", use_container_width=True)

if "scraped_data" not in st.session_state:
    st.session_state.scraped_data = None
if "scrape_time" not in st.session_state:
    st.session_state.scrape_time = None

if start_scrape:
    progress_bar = st.progress(0, text="Preparing to scrape...")
    status_text = st.empty()

    def update_progress(current, total):
        progress = current / total
        progress_bar.progress(progress, text=f"Scraping page {current} of {total}...")

    try:
        start = datetime.now()
        products = scrape_books(num_pages=num_pages, progress_callback=update_progress)
        end = datetime.now()

        st.session_state.scraped_data = pd.DataFrame(products)
        st.session_state.scrape_time = (end - start).total_seconds()

        progress_bar.progress(1.0, text="✅ Scraping complete!")
        status_text.success(f"Successfully scraped {len(products)} products in {st.session_state.scrape_time:.2f} seconds.")

    except Exception as e:
        progress_bar.empty()
        st.error(f"❌ Scraping failed: {e}")

if st.session_state.scraped_data is not None:
    df = st.session_state.scraped_data

    st.subheader("📊 Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Total Products</div>
            <div class="stat-value">{len(df)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        avg_price = df["Price (£)"].mean()
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Average Price</div>
            <div class="stat-value">£{avg_price:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        avg_rating = df["Rating"].mean()
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Average Rating</div>
            <div class="stat-value">{avg_rating:.1f} ⭐</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        in_stock_count = (df["In Stock"] == "Yes").sum()
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">In Stock</div>
            <div class="stat-value">{in_stock_count}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.subheader("🔍 Filter Results")

    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])

    with filter_col1:
        search_term = st.text_input("Search by name", placeholder="e.g. Python")

    with filter_col2:
        min_rating = st.selectbox("Minimum rating", [0, 1, 2, 3, 4, 5], index=0)

    with filter_col3:
        stock_filter = st.selectbox("Stock status", ["All", "In Stock Only", "Out of Stock Only"])

    filtered = df.copy()
    if search_term:
        filtered = filtered[filtered["Name"].str.contains(search_term, case=False, na=False)]
    if min_rating > 0:
        filtered = filtered[filtered["Rating"] >= min_rating]
    if stock_filter == "In Stock Only":
        filtered = filtered[filtered["In Stock"] == "Yes"]
    elif stock_filter == "Out of Stock Only":
        filtered = filtered[filtered["In Stock"] == "No"]

    st.subheader(f"📋 Products ({len(filtered)} shown)")

    display_df = filtered.copy()
    display_df["Rating"] = display_df["Rating"].apply(lambda x: "⭐" * x if x > 0 else "—")

    st.dataframe(
        display_df,
        use_container_width=True,
        height=500,
        hide_index=True
    )

    st.divider()

    st.subheader("💾 Export Data")

    export_col1, export_col2 = st.columns(2)

    with export_col1:
        csv_data = df.to_csv(index=False).encode("utf-8")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="📥 Download CSV (All Data)",
            data=csv_data,
            file_name=f"products_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with export_col2:
        filtered_csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download CSV (Filtered)",
            data=filtered_csv,
            file_name=f"products_filtered_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True
        )

    os.makedirs("data", exist_ok=True)
    saved_path = f"data/products_{timestamp}.csv"
    if st.button("💾 Save CSV to disk", use_container_width=False):
        df.to_csv(saved_path, index=False)
        st.success(f"Saved to `{saved_path}`")

else:
    st.info("👈 Configure the settings in the sidebar and click **Start Scraping** to begin.")

    st.markdown("### 🎯 How it works")
    st.markdown("""
    1. **Choose** how many pages you want to scrape from the sidebar
    2. **Click** the Start Scraping button
    3. **Wait** while the scraper fetches and parses each page
    4. **View** the results in an interactive table
    5. **Filter** the data by name, rating, or stock status
    6. **Download** the results as a CSV file
    """)

    st.markdown("### 🛠️ Extracted Fields")
    st.markdown("""
    - **Name** — Product title
    - **Price (£)** — Price in British Pounds
    - **Rating** — Star rating from 1 to 5
    - **In Stock** — Availability status
    """)

st.markdown("""
<div class="footer">
    Built by <strong>Harshal Naik</strong> — SkillCraft Technology Internship 2026
</div>
""", unsafe_allow_html=True)