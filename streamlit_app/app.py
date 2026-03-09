import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# ── Page Config ────────────────────────────────────────────
st.set_page_config(
    page_title="🎮 Video Game Analytics",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0f0f1a; }
    section[data-testid="stSidebar"] { background-color: #1a1a2e; }
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #7c83fd44;
        border-radius: 12px;
        padding: 16px !important;
    }
    [data-testid="stMetricLabel"] { color: #aaaacc !important; font-size: 13px !important; }
    [data-testid="stMetricValue"] { color: #7c83fd !important; font-size: 26px !important; font-weight: 700 !important; }
    h1 { color: #7c83fd !important; font-weight: 800 !important; }
    h2 { color: #ffffff !important; font-weight: 700 !important; }
    h3 { color: #ccccff !important; font-weight: 600 !important; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a2e; color: #aaaacc;
        border-radius: 8px 8px 0 0; padding: 10px 20px; font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background-color: #7c83fd !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ── Plotly Template ────────────────────────────────────────
PALETTE = ["#7c83fd","#fd7c7c","#7cfdcb","#fdd97c","#fd7cf0","#7ccffd","#fdaa7c","#b07cfd"]

pio.templates["gaming"] = go.layout.Template({
    "layout": {
        "paper_bgcolor": "#0f0f1a", "plot_bgcolor": "#1a1a2e",
        "font": {"color": "#ccccff"},
        "xaxis": {"gridcolor": "#2a2a4a", "linecolor": "#444466"},
        "yaxis": {"gridcolor": "#2a2a4a", "linecolor": "#444466"},
        "colorway": PALETTE,
        "legend": {"bgcolor": "#1a1a2e", "bordercolor": "#444466"},
    }
})
pio.templates.default = "gaming"

# ── Load Data ──────────────────────────────────────────────
@st.cache_data
def load_data():
    games   = pd.read_csv("cleaned_data/cleaned_games.csv")
    vgsales = pd.read_csv("cleaned_data/cleaned_vgsales.csv")
    merged  = pd.read_csv("cleaned_data/merged_data.csv")
    matched = merged[merged["Global_Sales"] > 0].copy()
    return games, vgsales, merged, matched

games, vgsales, merged, matched = load_data()

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎮 Video Game Analytics")
    st.markdown("---")
    page = st.radio("📌 Navigate", [
        "🏠 Overview",
        "⭐ Ratings & Engagement",
        "💰 Sales Analysis",
        "🧩 Genre Analysis",
        "🕹️ Platform & Publisher",
        "📅 Yearly Trends",
        "🔍 Game Explorer"
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### 🔧 Filters")
    all_genres = sorted(games["Primary_Genre"].dropna().unique())
    sel_genres = st.multiselect("Genres", all_genres, default=all_genres[:8])
    year_range = st.slider("Year Range", 1980, 2020, (1995, 2016))

    st.markdown("---")
    st.markdown("""
    <div style='color:#666688;font-size:12px;'>
    📊 Dataset<br>• 1,099 unique games<br>• 16,593 sales records<br>
    • 469 matched games<br>• 31 platforms • 19 genres
    </div>""", unsafe_allow_html=True)

# ── Filtered Data ──────────────────────────────────────────
games_f   = games[games["Primary_Genre"].isin(sel_genres)] if sel_genres else games
vgsales_f = vgsales[(vgsales["Year"] >= year_range[0]) & (vgsales["Year"] <= year_range[1])]
matched_f = matched[matched["Primary_Genre"].isin(sel_genres)] if sel_genres else matched

# ══════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.title("🎮 Video Game Sales & Engagement Analytics")
    st.markdown("##### Comprehensive analysis of game ratings, engagement metrics, and global sales")
    st.markdown("---")

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("🎮 Unique Games",  f"{len(games):,}")
    c2.metric("📊 Sales Records", f"{len(vgsales):,}")
    c3.metric("🔗 Matched Games", f"{len(matched):,}")
    c4.metric("⭐ Avg Rating",    f"{games['Rating'].mean():.2f}/5.0")
    c5.metric("💰 Total Sales",   f"{vgsales['Global_Sales'].sum():.0f}M")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        top_plays = games.nlargest(10, "Plays")
        fig = px.bar(top_plays.sort_values("Plays"),
            x="Plays", y="Game_Title", orientation="h",
            color="Rating", color_continuous_scale="Plasma",
            title="🕹️ Top 10 Most Played Games",
            text=top_plays.sort_values("Plays")["Plays"].apply(lambda x: f"{x/1000:.0f}K"),
            labels={"Game_Title":"","Plays":"Total Plays"})
        fig.update_traces(textposition="outside")
        fig.update_layout(height=420, showlegend=False, yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        top_sales = vgsales.groupby("Game_Title")["Global_Sales"].sum().nlargest(10).reset_index()
        fig = px.bar(top_sales.sort_values("Global_Sales"),
            x="Global_Sales", y="Game_Title", orientation="h",
            color="Global_Sales", color_continuous_scale="Viridis",
            title="💰 Top 10 Best-Selling Games",
            text=top_sales.sort_values("Global_Sales")["Global_Sales"].apply(lambda x: f"{x:.1f}M"),
            labels={"Game_Title":"","Global_Sales":"Global Sales (M)"})
        fig.update_traces(textposition="outside")
        fig.update_layout(height=420, showlegend=False, yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        gc = games["Primary_Genre"].value_counts().reset_index()
        gc.columns = ["Genre","Count"]
        fig = px.pie(gc, values="Count", names="Genre",
            title="🧩 Genre Distribution",
            color_discrete_sequence=PALETTE, hole=0.4)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        regions = {"North America": vgsales["NA_Sales"].sum(),
                   "Europe": vgsales["EU_Sales"].sum(),
                   "Japan": vgsales["JP_Sales"].sum(),
                   "Rest of World": vgsales["Other_Sales"].sum()}
        fig = px.pie(values=list(regions.values()), names=list(regions.keys()),
            title="🌍 Regional Sales Market Share",
            color_discrete_sequence=PALETTE, hole=0.4)
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 2 — RATINGS & ENGAGEMENT
# ══════════════════════════════════════════════════════════
elif page == "⭐ Ratings & Engagement":
    st.title("⭐ Ratings & Engagement Analysis")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📊 Rating Distribution", "🎮 Engagement Metrics", "🏆 Top Games"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(games_f, x="Rating", nbins=30,
                title="Rating Distribution", color_discrete_sequence=[PALETTE[0]],
                labels={"Rating":"User Rating","count":"Games"})
            fig.add_vline(x=games_f["Rating"].mean(), line_dash="dash", line_color=PALETTE[1],
                         annotation_text=f"Mean: {games_f['Rating'].mean():.2f}")
            fig.add_vline(x=games_f["Rating"].median(), line_dash="dot", line_color=PALETTE[2],
                         annotation_text=f"Median: {games_f['Rating'].median():.2f}")
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.box(games_f[games_f["Primary_Genre"].notna()],
                x="Primary_Genre", y="Rating", color="Primary_Genre",
                title="Rating by Genre", color_discrete_sequence=PALETTE,
                labels={"Primary_Genre":"Genre","Rating":"Rating"})
            fig.update_layout(height=380, showlegend=False, xaxis={"tickangle":45})
            st.plotly_chart(fig, use_container_width=True)

        def rate_tier(r):
            if r >= 4.0: return "High (4+)"
            if r >= 3.0: return "Medium (3-4)"
            return "Low (<3)"
        tier_df = games_f["Rating"].dropna().apply(rate_tier).value_counts().reset_index()
        tier_df.columns = ["Tier","Count"]
        fig = px.bar(tier_df, x="Tier", y="Count", color="Tier",
            color_discrete_map={"High (4+)":PALETTE[0],"Medium (3-4)":PALETTE[3],"Low (<3)":PALETTE[1]},
            title="Games by Rating Tier", text="Count")
        fig.update_traces(textposition="outside")
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            eng_genre = games_f.groupby("Primary_Genre")[["Plays","Wishlist","Backlogs"]].mean().reset_index()
            fig = px.bar(eng_genre.sort_values("Plays", ascending=False),
                x="Primary_Genre", y="Plays", color="Plays",
                color_continuous_scale="Plasma", title="🎮 Avg Plays by Genre",
                labels={"Primary_Genre":"Genre","Plays":"Avg Plays"})
            fig.update_layout(height=380, xaxis={"tickangle":45})
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.scatter(games_f.dropna(subset=["Plays","Wishlist","Rating"]),
                x="Plays", y="Wishlist", color="Rating",
                size="Backlogs", hover_name="Game_Title",
                color_continuous_scale="Plasma",
                title="Plays vs Wishlist (size=Backlogs)",
                log_x=True, log_y=True)
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)

        eng_heatmap = games_f.groupby("Primary_Genre")[["Plays","Wishlist","Backlogs","Playing"]].mean().round(0)
        fig = px.imshow(eng_heatmap.T, color_continuous_scale="Viridis",
            title="📊 Engagement Heatmap by Genre", aspect="auto")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        top_n = st.slider("Top N Games", 5, 30, 15)
        col1, col2 = st.columns(2)
        with col1:
            top_rated = games_f[games_f["Plays"] >= 1000].nlargest(top_n, "Rating")
            fig = px.bar(top_rated.sort_values("Rating"),
                x="Rating", y="Game_Title", orientation="h", color="Primary_Genre",
                title=f"🌟 Top {top_n} Highest Rated Games",
                color_discrete_sequence=PALETTE, labels={"Game_Title":"","Rating":"Rating"})
            fig.update_layout(height=500, yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            top_wish = games_f.nlargest(top_n, "Wishlist")
            fig = px.bar(top_wish.sort_values("Wishlist"),
                x="Wishlist", y="Game_Title", orientation="h", color="Primary_Genre",
                title=f"💫 Top {top_n} Most Wishlisted",
                color_discrete_sequence=PALETTE, labels={"Game_Title":"","Wishlist":"Wishlist"})
            fig.update_layout(height=500, yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 3 — SALES ANALYSIS
# ══════════════════════════════════════════════════════════
elif page == "💰 Sales Analysis":
    st.title("💰 Sales Analysis")
    st.markdown("---")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🌍 Total Global", f"{vgsales_f['Global_Sales'].sum():.0f}M")
    c2.metric("🇺🇸 NA Sales",    f"{vgsales_f['NA_Sales'].sum():.0f}M")
    c3.metric("🇪🇺 EU Sales",    f"{vgsales_f['EU_Sales'].sum():.0f}M")
    c4.metric("🇯🇵 JP Sales",    f"{vgsales_f['JP_Sales'].sum():.0f}M")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🌍 Regional", "🔝 Top Games", "📊 Distribution"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            regions = {"North America":vgsales_f["NA_Sales"].sum(),
                       "Europe":vgsales_f["EU_Sales"].sum(),
                       "Japan":vgsales_f["JP_Sales"].sum(),
                       "Rest of World":vgsales_f["Other_Sales"].sum()}
            fig = px.pie(values=list(regions.values()), names=list(regions.keys()),
                title="🌍 Market Share by Region",
                color_discrete_sequence=PALETTE, hole=0.45)
            fig.update_traces(textinfo="percent+label")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            genre_reg = vgsales_f.groupby("Genre")[["NA_Sales","EU_Sales","JP_Sales"]].sum()
            genre_reg = genre_reg[genre_reg.sum(axis=1) > 10]
            fig = px.imshow(genre_reg, color_continuous_scale="Viridis",
                title="🌐 Regional Sales Heatmap by Genre", aspect="auto")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        yearly_r = vgsales_f.groupby("Year")[["NA_Sales","EU_Sales","JP_Sales"]].sum().reset_index()
        fig = px.line(yearly_r, x="Year", y=["NA_Sales","EU_Sales","JP_Sales"],
            title="📈 Regional Sales Trends", markers=True,
            labels={"value":"Sales (M)","variable":"Region"},
            color_discrete_sequence=PALETTE)
        fig.update_layout(height=340)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        top_n_s = st.slider("Top N", 5, 25, 10)
        col1, col2 = st.columns(2)
        with col1:
            tgs = vgsales_f.groupby("Game_Title")["Global_Sales"].sum().nlargest(top_n_s).reset_index()
            fig = px.bar(tgs.sort_values("Global_Sales"),
                x="Global_Sales", y="Game_Title", orientation="h",
                color="Global_Sales", color_continuous_scale="Viridis",
                title=f"🏆 Top {top_n_s} Best-Sellers",
                text=tgs.sort_values("Global_Sales")["Global_Sales"].apply(lambda x: f"{x:.1f}M"),
                labels={"Game_Title":"","Global_Sales":"Global Sales (M)"})
            fig.update_traces(textposition="outside")
            fig.update_layout(height=500, showlegend=False, yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            top_names = vgsales_f.groupby("Game_Title")["Global_Sales"].sum().nlargest(top_n_s).index
            treg = vgsales_f[vgsales_f["Game_Title"].isin(top_names)]\
                .groupby("Game_Title")[["NA_Sales","EU_Sales","JP_Sales","Other_Sales"]].sum()\
                .reset_index().sort_values("NA_Sales")
            fig = px.bar(treg,
                x=["NA_Sales","EU_Sales","JP_Sales","Other_Sales"], y="Game_Title",
                orientation="h", title=f"🌍 Regional Breakdown Top {top_n_s}",
                labels={"value":"Sales (M)","variable":"Region","Game_Title":""},
                color_discrete_sequence=PALETTE)
            fig.update_layout(height=500, yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(vgsales_f[vgsales_f["Global_Sales"] < 5],
                x="Global_Sales", nbins=50,
                title="Sales Distribution (<5M)", color_discrete_sequence=[PALETTE[2]],
                labels={"Global_Sales":"Sales (M)","count":"Games"})
            fig.update_layout(height=360)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            def s_tier(v):
                if v >= 5: return "Blockbuster (5M+)"
                if v >= 1: return "Hit (1-5M)"
                return "Mid-Tier (<1M)"
            stier = vgsales_f["Global_Sales"].apply(s_tier).value_counts().reset_index()
            stier.columns = ["Tier","Count"]
            fig = px.bar(stier, x="Tier", y="Count", color="Tier",
                color_discrete_sequence=PALETTE, title="Sales Tier Distribution", text="Count")
            fig.update_traces(textposition="outside")
            fig.update_layout(height=360, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 4 — GENRE ANALYSIS
# ══════════════════════════════════════════════════════════
elif page == "🧩 Genre Analysis":
    st.title("🧩 Genre Analysis")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        gc = games_f["Primary_Genre"].value_counts().reset_index()
        gc.columns = ["Genre","Count"]
        fig = px.bar(gc, x="Genre", y="Count", color="Count",
            color_continuous_scale="Plasma", title="🎮 Games per Genre", text="Count")
        fig.update_traces(textposition="outside")
        fig.update_layout(height=380, xaxis={"tickangle":45}, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        gr = games_f.groupby("Primary_Genre")["Rating"].mean().sort_values(ascending=False).reset_index()
        fig = px.bar(gr, x="Primary_Genre", y="Rating",
            color="Rating", color_continuous_scale="RdYlGn",
            title="⭐ Avg Rating by Genre",
            text=gr["Rating"].apply(lambda x: f"{x:.2f}"))
        fig.add_hline(y=games_f["Rating"].mean(), line_dash="dash", line_color="white",
                     annotation_text="Overall Mean")
        fig.update_traces(textposition="outside")
        fig.update_layout(height=380, xaxis={"tickangle":45}, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        genre_sales = vgsales_f.groupby("Genre")["Global_Sales"].sum().sort_values(ascending=False).reset_index()
        fig = px.pie(genre_sales.head(12), values="Global_Sales", names="Genre",
            title="💰 Genre Market Share (Sales)",
            color_discrete_sequence=PALETTE, hole=0.4)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        ge = games_f.groupby("Primary_Genre")[["Plays","Wishlist","Backlogs"]].mean().reset_index()
        fig = px.scatter(ge, x="Plays", y="Wishlist", size="Backlogs",
            color="Primary_Genre", hover_name="Primary_Genre",
            title="🎯 Plays vs Wishlist by Genre",
            color_discrete_sequence=PALETTE)
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Radar chart
    st.markdown("### 🕸️ Genre Engagement Radar")
    sel_g = st.selectbox("Select Genre for Radar", sorted(games_f["Primary_Genre"].dropna().unique()))
    cats = ["Plays","Wishlist","Backlogs","Playing","Rating"]
    gdata   = games_f[games_f["Primary_Genre"]==sel_g][cats].mean()
    overall = games_f[cats].mean()
    maxv    = games_f[cats].max()
    gn = (gdata / maxv * 100).fillna(0)
    on = (overall / maxv * 100).fillna(0)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=list(gn)+[gn.iloc[0]], theta=cats+[cats[0]],
        fill="toself", name=sel_g, line_color=PALETTE[0], fillcolor="rgba(124,131,253,0.25)"))
    fig.add_trace(go.Scatterpolar(r=list(on)+[on.iloc[0]], theta=cats+[cats[0]],
        fill="toself", name="Overall", line_color=PALETTE[1], fillcolor="rgba(253,124,124,0.25)"))
    fig.update_layout(
        polar=dict(bgcolor="#1a1a2e",
            radialaxis=dict(visible=True, range=[0,100], gridcolor="#2a2a4a"),
            angularaxis=dict(gridcolor="#2a2a4a")),
        paper_bgcolor="#0f0f1a", font_color="#ccccff", height=420,
        title=f"Engagement: {sel_g} vs Overall Average")
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 5 — PLATFORM & PUBLISHER
# ══════════════════════════════════════════════════════════
elif page == "🕹️ Platform & Publisher":
    st.title("🕹️ Platform & Publisher Analysis")
    st.markdown("---")

    tab1, tab2 = st.tabs(["🕹️ Platforms", "🏢 Publishers"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            ps = vgsales_f.groupby("Platform")["Global_Sales"].sum().nlargest(15).reset_index()
            fig = px.bar(ps.sort_values("Global_Sales"),
                x="Global_Sales", y="Platform", orientation="h",
                color="Global_Sales", color_continuous_scale="Viridis",
                title="🏆 Top 15 Platforms by Sales",
                text=ps.sort_values("Global_Sales")["Global_Sales"].apply(lambda x: f"{x:.0f}M"),
                labels={"Platform":"","Global_Sales":"Sales (M)"})
            fig.update_traces(textposition="outside")
            fig.update_layout(height=500, showlegend=False, yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            top_p = vgsales_f.groupby("Platform")["Global_Sales"].sum().nlargest(12).index
            pr = vgsales_f[vgsales_f["Platform"].isin(top_p)]\
                .groupby("Platform")[["NA_Sales","EU_Sales","JP_Sales","Other_Sales"]].sum()\
                .reset_index().sort_values("NA_Sales")
            fig = px.bar(pr, x=["NA_Sales","EU_Sales","JP_Sales","Other_Sales"], y="Platform",
                orientation="h", title="🌍 Regional Sales by Platform",
                labels={"value":"Sales (M)","variable":"Region","Platform":""},
                color_discrete_sequence=PALETTE)
            fig.update_layout(height=500, yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        pt = vgsales_f.groupby("Platform")["Game_Title"].nunique().nlargest(15).reset_index()
        pt.columns = ["Platform","Titles"]
        fig = px.bar(pt.sort_values("Titles", ascending=False),
            x="Platform", y="Titles", color="Titles",
            color_continuous_scale="Plasma", title="📚 Titles per Platform", text="Titles")
        fig.update_traces(textposition="outside")
        fig.update_layout(height=320, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            pubs = vgsales_f[vgsales_f["Publisher"]!="Unknown"]\
                .groupby("Publisher")["Global_Sales"].sum().nlargest(15).reset_index()
            fig = px.bar(pubs.sort_values("Global_Sales"),
                x="Global_Sales", y="Publisher", orientation="h",
                color="Global_Sales", color_continuous_scale="Magma",
                title="🏢 Top 15 Publishers by Sales",
                text=pubs.sort_values("Global_Sales")["Global_Sales"].apply(lambda x: f"{x:.0f}M"),
                labels={"Publisher":"","Global_Sales":"Sales (M)"})
            fig.update_traces(textposition="outside")
            fig.update_layout(height=500, showlegend=False, yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            pe = vgsales_f[vgsales_f["Publisher"]!="Unknown"]\
                .groupby("Publisher").agg(Titles=("Game_Title","nunique"),
                    Total=("Global_Sales","sum")).reset_index()
            pe = pe[pe["Titles"] >= 10]
            pe["Avg"] = pe["Total"] / pe["Titles"]
            pe = pe.nlargest(15,"Avg")
            fig = px.scatter(pe, x="Titles", y="Avg", size="Total",
                color="Total", hover_name="Publisher",
                color_continuous_scale="Viridis",
                title="📈 Publisher Efficiency (Avg Sales/Title)",
                labels={"Titles":"Number of Titles","Avg":"Avg Sales per Title (M)"})
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 6 — YEARLY TRENDS
# ══════════════════════════════════════════════════════════
elif page == "📅 Yearly Trends":
    st.title("📅 Yearly Trends")
    st.markdown("---")

    yearly = vgsales_f.groupby("Year").agg(
        games_released=("Game_Title","nunique"),
        global_sales=("Global_Sales","sum"),
        na_sales=("NA_Sales","sum"),
        eu_sales=("EU_Sales","sum"),
        jp_sales=("JP_Sales","sum"),
    ).reset_index()
    yearly = yearly[(yearly["Year"] >= 1990) & (yearly["Year"] <= 2016)]
    yearly["avg_per_game"] = yearly["global_sales"] / yearly["games_released"]

    col1, col2 = st.columns(2)
    with col1:
        fig = px.area(yearly, x="Year", y="games_released",
            title="🎮 Games Released per Year",
            color_discrete_sequence=[PALETTE[0]], markers=True,
            labels={"games_released":"Titles","Year":"Year"})
        fig.update_layout(height=340)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.area(yearly, x="Year", y="global_sales",
            title="💰 Global Sales per Year (M)",
            color_discrete_sequence=[PALETTE[1]], markers=True,
            labels={"global_sales":"Sales (M)","Year":"Year"})
        fig.update_layout(height=340)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig = px.line(yearly, x="Year", y=["na_sales","eu_sales","jp_sales"],
            title="🌍 Regional Sales Trends",
            color_discrete_sequence=PALETTE, markers=True,
            labels={"value":"Sales (M)","variable":"Region"})
        newnames = {"na_sales":"NA","eu_sales":"EU","jp_sales":"JP"}
        fig.for_each_trace(lambda t: t.update(name=newnames.get(t.name,t.name)))
        fig.update_layout(height=340)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        fig = px.bar(yearly, x="Year", y="avg_per_game",
            color="avg_per_game", color_continuous_scale="Viridis",
            title="📊 Avg Sales per Game per Year",
            labels={"avg_per_game":"Avg Sales (M)"})
        fig.update_layout(height=340, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Decade heatmap
    st.markdown("### 🔥 Genre Evolution by Decade")
    dg = vgsales_f.copy()
    dg["Decade"] = (dg["Year"] // 10 * 10).astype(str) + "s"
    dgp = dg.groupby(["Decade","Genre"])["Global_Sales"].sum()\
        .reset_index().pivot(index="Genre", columns="Decade", values="Global_Sales").fillna(0)
    fig = px.imshow(dgp, color_continuous_scale="Viridis",
        title="Genre Sales by Decade (Millions)", aspect="auto")
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 7 — GAME EXPLORER
# ══════════════════════════════════════════════════════════
elif page == "🔍 Game Explorer":
    st.title("🔍 Game Explorer")
    st.markdown("Search, filter and explore individual games")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1: search = st.text_input("🔎 Search Title", placeholder="e.g. Zelda, Mario...")
    with col2: gf = st.selectbox("Genre", ["All"] + sorted(games["Primary_Genre"].dropna().unique()))
    with col3: sb = st.selectbox("Sort by", ["Rating","Plays","Wishlist","Backlogs"])

    df = games.copy()
    if search: df = df[df["Game_Title"].str.contains(search, case=False, na=False)]
    if gf != "All": df = df[df["Primary_Genre"] == gf]
    df = df.sort_values(sb, ascending=False)

    st.markdown(f"**{len(df)} games found**")
    show = ["Game_Title","Primary_Genre","Rating","Plays","Wishlist","Backlogs","Playing","Release Year"]
    show = [c for c in show if c in df.columns]
    st.dataframe(df[show].head(50).reset_index(drop=True), use_container_width=True, height=400)

    if len(df) > 0:
        st.markdown("---")
        st.markdown("### 📊 Game Deep Dive")
        sel = st.selectbox("Select a Game", df["Game_Title"].tolist())
        row = df[df["Game_Title"] == sel].iloc[0]

        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("⭐ Rating",   f"{row['Rating']:.1f}/5.0")
        c2.metric("🎮 Plays",    f"{int(row['Plays']):,}" if pd.notna(row['Plays']) else "N/A")
        c3.metric("💫 Wishlist", f"{int(row['Wishlist']):,}" if pd.notna(row['Wishlist']) else "N/A")
        c4.metric("📦 Backlogs", f"{int(row['Backlogs']):,}" if pd.notna(row['Backlogs']) else "N/A")
        rel_yr = row.get('Release Year') if hasattr(row, 'get') else (row['Release Year'] if 'Release Year' in row.index else None)
        c5.metric('🗓️ Year', f'{int(rel_yr)}' if rel_yr is not None and pd.notna(rel_yr) else 'N/A')

        sales_row = vgsales[vgsales["Game_Title"].str.lower() == sel.lower()]
        if len(sales_row) > 0:
            st.markdown("#### 💰 Sales Data")
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("🌍 Global", f"{sales_row['Global_Sales'].sum():.2f}M")
            c2.metric("🇺🇸 NA",    f"{sales_row['NA_Sales'].sum():.2f}M")
            c3.metric("🇪🇺 EU",    f"{sales_row['EU_Sales'].sum():.2f}M")
            c4.metric("🇯🇵 JP",    f"{sales_row['JP_Sales'].sum():.2f}M")

            # Platform breakdown
            plat_data = sales_row.groupby("Platform")["Global_Sales"].sum().reset_index()
            fig = px.bar(plat_data.sort_values("Global_Sales"),
                x="Global_Sales", y="Platform", orientation="h",
                color="Global_Sales", color_continuous_scale="Viridis",
                title=f"Sales by Platform — {sel}",
                labels={"Platform":"","Global_Sales":"Sales (M)"})
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("💡 No sales data found for this game in vgsales dataset.")

# ── Footer ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#444466;font-size:12px;padding:8px;'>
    🎮 Video Game Sales & Engagement Analytics Dashboard
</div>""", unsafe_allow_html=True)
