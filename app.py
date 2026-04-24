# ─────────────────────────────────────────────────────────────────────────────
#  Medical Insurance Cost Prediction — Streamlit App
#  Run: streamlit run app.py
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediCost — Insurance Predictor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background-color: #0f1117; }

    .metric-card {
        background: linear-gradient(135deg, #1e2a3a, #162030);
        border: 1px solid #2a3f55;
        border-radius: 14px;
        padding: 20px 24px;
        text-align: center;
        margin-bottom: 8px;
    }
    .metric-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #64748b;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-sub {
        font-size: 11px;
        color: #475569;
        margin-top: 4px;
    }

    .predict-result {
        background: linear-gradient(135deg, #0c2340, #0a1f35);
        border: 2px solid #38bdf8;
        border-radius: 18px;
        padding: 28px;
        text-align: center;
    }
    .predict-amount {
        font-size: 52px;
        font-weight: 800;
        color: #38bdf8;
        letter-spacing: -2px;
    }
    .predict-monthly {
        font-size: 16px;
        color: #64748b;
        margin-top: 4px;
    }

    .risk-high   { background: rgba(248,113,113,0.15); color: #f87171;
                   border: 1px solid rgba(248,113,113,0.4);
                   padding: 4px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; }
    .risk-medium { background: rgba(251,191,36,0.15);  color: #fbbf24;
                   border: 1px solid rgba(251,191,36,0.4);
                   padding: 4px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; }
    .risk-low    { background: rgba(74,222,128,0.15);  color: #4ade80;
                   border: 1px solid rgba(74,222,128,0.4);
                   padding: 4px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; }

    .section-title {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #38bdf8;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid #1e3a52;
    }

    div[data-testid="stMetric"] {
        background: #1a2535;
        border: 1px solid #2a3f55;
        border-radius: 12px;
        padding: 12px 16px;
    }
    div[data-testid="stMetric"] label { color: #64748b !important; font-size: 11px !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #38bdf8 !important; font-size: 22px !important; font-weight: 700 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] { font-size: 11px !important; }

    .stSlider > div > div { background: #38bdf8 !important; }
    .stSelectbox > div { background: #1a2535 !important; }
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9, #0284c7) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 12px 28px !important;
        font-size: 15px !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #38bdf8, #0ea5e9) !important;
        transform: translateY(-1px);
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom-color: #38bdf8 !important;
    }

    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Load & Prepare Data (cached) ──────────────────────────────────────────────
@st.cache_data
def load_and_prepare():
    df = pd.read_csv('medical_insurance.csv')
    df = df.drop_duplicates()

    df_enc = df.copy()
    df_enc['sex']    = df_enc['sex'].map({'male': 1, 'female': 0})
    df_enc['smoker'] = df_enc['smoker'].map({'yes': 1, 'no': 0})
    df_enc = pd.get_dummies(df_enc, columns=['region'], drop_first=True)

    df_fe = df_enc.copy()
    df_fe['bmi_category'] = df_fe['bmi'].apply(
        lambda b: 0 if b < 18.5 else (1 if b < 25 else (2 if b < 30 else 3)))
    df_fe['age_group'] = pd.cut(df_fe['age'],
                                 bins=[17,25,35,45,55,65],
                                 labels=[0,1,2,3,4]).astype(int)
    df_fe['smoker_bmi']   = df_fe['smoker'] * df_fe['bmi']
    df_fe['smoker_age']   = df_fe['smoker'] * df_fe['age']
    df_fe['obese_smoker'] = ((df_fe['bmi'] >= 30) & (df_fe['smoker'] == 1)).astype(int)

    return df, df_enc, df_fe


@st.cache_resource
def train_best_model(df_fe):
    X = df_fe.drop('charges', axis=1)
    y = df_fe['charges']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_train)
    X_te_s = scaler.transform(X_test)

    models = {
        'Linear Regression'  : LinearRegression(),
        'Ridge Regression'   : Ridge(alpha=1.0),
        'Lasso Regression'   : Lasso(alpha=0.5),
        'Decision Tree'      : DecisionTreeRegressor(max_depth=6, random_state=42),
        'Random Forest'      : RandomForestRegressor(n_estimators=200, max_depth=10,
                                                      random_state=42, n_jobs=-1),
        'Gradient Boosting'  : GradientBoostingRegressor(n_estimators=200, learning_rate=0.05,
                                                          max_depth=4, random_state=42),
        'XGBoost'            : XGBRegressor(n_estimators=300, learning_rate=0.05,
                                             max_depth=5, random_state=42,
                                             eval_metric='rmse', verbosity=0),
    }
    linear_names = ['Linear Regression', 'Ridge Regression', 'Lasso Regression']
    results = {}
    for name, m in models.items():
        Xtr = X_tr_s if name in linear_names else X_train
        Xte = X_te_s if name in linear_names else X_test
        m.fit(Xtr, y_train)
        pred = m.predict(Xte)
        results[name] = {
            'R2'  : round(r2_score(y_test, pred), 4),
            'RMSE': round(np.sqrt(mean_squared_error(y_test, pred)), 2),
            'MAE' : round(mean_absolute_error(y_test, pred), 2),
        }

    return models['Linear Regression'], scaler, X.columns.tolist(), results


# ── Load everything ───────────────────────────────────────────────────────────
df, df_enc, df_fe = load_and_prepare()
best_model, scaler, feature_cols, all_results = train_best_model(df_fe)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 MediCost")
    st.markdown("**Medical Insurance Cost Predictor**")
    st.markdown("---")
    st.markdown(f"📦 **Dataset:** {df.shape[0]} records")
    st.markdown(f"🏆 **Best Model:** Linear Regression")
    st.markdown(f"📈 **R² Score:** 0.9108")
    st.markdown(f"💡 **RMSE:** $4,048")
    st.markdown("---")
    st.markdown("**Tech Stack**")
    st.markdown("🐍 Python · Pandas · Sklearn")
    st.markdown("📊 Matplotlib · Seaborn")
    st.markdown("🤖 XGBoost · MLflow")
    st.markdown("🌐 Streamlit")


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🏥 Medical Insurance Cost Prediction")
st.markdown("*End-to-end ML project — EDA · Model Training · Live Prediction*")
st.markdown("---")

# ── KPI Cards ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Records",    f"{df.shape[0]:,}")
c2.metric("Avg Annual Cost",  f"${df['charges'].mean():,.0f}")
c3.metric("Median Cost",      f"${df['charges'].median():,.0f}")
c4.metric("Smoker Rate",      f"{100*df['smoker'].eq('yes').mean():.1f}%")
c5.metric("Avg BMI",          f"{df['bmi'].mean():.1f}")

st.markdown("")

# ── Main Tabs ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  EDA — Overview",
    "🔬  EDA — Deep Dive",
    "🤖  Model Performance",
    "💰  Predict My Cost"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EDA Overview
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Univariate Analysis</div>',
                unsafe_allow_html=True)

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.patch.set_facecolor('#0f1117')
    for ax in axes.flat:
        ax.set_facecolor('#1a2535')
        ax.tick_params(colors='#94a3b8')
        for spine in ax.spines.values():
            spine.set_edgecolor('#2a3f55')

    # 1. Charges distribution
    axes[0,0].hist(df['charges'], bins=40, color='#38bdf8', edgecolor='#0f1117', alpha=0.85)
    axes[0,0].axvline(df['charges'].mean(),   color='#f87171', linestyle='--', lw=2,
                      label=f'Mean: ${df["charges"].mean():,.0f}')
    axes[0,0].axvline(df['charges'].median(), color='#fbbf24', linestyle='--', lw=2,
                      label=f'Median: ${df["charges"].median():,.0f}')
    axes[0,0].set_title('Distribution of Charges', color='#e2e8f0')
    axes[0,0].set_xlabel('Charges ($)', color='#64748b')
    axes[0,0].legend(fontsize=8, facecolor='#1a2535', labelcolor='#94a3b8')

    # 2. Age distribution
    axes[0,1].hist(df['age'], bins=20, color='#4ade80', edgecolor='#0f1117', alpha=0.85)
    axes[0,1].set_title('Age Distribution', color='#e2e8f0')
    axes[0,1].set_xlabel('Age (years)', color='#64748b')

    # 3. Smoker pie
    sc = df['smoker'].value_counts()
    axes[0,2].pie(sc, labels=['Non-Smoker','Smoker'], autopct='%1.1f%%',
                  colors=['#4ade80','#f87171'], startangle=90,
                  wedgeprops={'edgecolor':'#0f1117','linewidth':2},
                  textprops={'color':'#e2e8f0'})
    axes[0,2].set_title('Smoker vs Non-Smoker', color='#e2e8f0')

    # 4. BMI distribution
    axes[1,0].hist(df['bmi'], bins=35, color='#a78bfa', edgecolor='#0f1117', alpha=0.85)
    axes[1,0].axvline(df['bmi'].mean(), color='#f87171', linestyle='--', lw=2,
                      label=f'Mean: {df["bmi"].mean():.1f}')
    axes[1,0].axvline(30, color='#fbbf24', linestyle=':', lw=2, label='Obese (30)')
    axes[1,0].set_title('BMI Distribution', color='#e2e8f0')
    axes[1,0].set_xlabel('BMI', color='#64748b')
    axes[1,0].legend(fontsize=8, facecolor='#1a2535', labelcolor='#94a3b8')

    # 5. Region
    rc = df['region'].value_counts()
    axes[1,1].bar(rc.index, rc.values,
                  color=['#f97316','#38bdf8','#4ade80','#fbbf24'], edgecolor='#0f1117')
    axes[1,1].set_title('Policyholders by Region', color='#e2e8f0')
    axes[1,1].set_xlabel('Region', color='#64748b')
    axes[1,1].set_ylabel('Count', color='#64748b')

    # 6. Children
    cc = df['children'].value_counts().sort_index()
    axes[1,2].bar(cc.index, cc.values, color='#fb7185', edgecolor='#0f1117')
    axes[1,2].set_title('Number of Children', color='#e2e8f0')
    axes[1,2].set_xlabel('Children', color='#64748b')
    axes[1,2].set_ylabel('Count', color='#64748b')

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Key Insights
    st.markdown("")
    st.markdown('<div class="section-title">Key Insights</div>', unsafe_allow_html=True)
    i1, i2, i3, i4 = st.columns(4)
    i1.metric("Smoker Cost Premium",   "+283%",  "Smokers pay 3.8× more")
    i2.metric("Age 18→64 Cost Rise",   "+108%",  "$9k → $18.7k avg")
    i3.metric("Obese Smoker Avg",      "$41,544","vs $8k for healthy")
    i4.metric("Highest Region",        "Southeast","avg $14,735/yr")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — EDA Deep Dive
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Bivariate & Multivariate Analysis</div>',
                unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        # Smoker vs charges boxplot
        fig, ax = plt.subplots(figsize=(7, 4))
        fig.patch.set_facecolor('#0f1117')
        ax.set_facecolor('#1a2535')
        for spine in ax.spines.values(): spine.set_edgecolor('#2a3f55')
        df.boxplot(column='charges', by='smoker', ax=ax,
                   boxprops=dict(color='#38bdf8'),
                   medianprops=dict(color='#f87171', linewidth=2.5),
                   whiskerprops=dict(color='#38bdf8'),
                   capprops=dict(color='#38bdf8'),
                   flierprops=dict(marker='o', color='#f87171', markersize=3, alpha=0.5))
        ax.set_title('Smoker vs Charges', color='#e2e8f0')
        ax.set_xlabel('Smoker', color='#64748b')
        ax.set_ylabel('Charges ($)', color='#64748b')
        ax.tick_params(colors='#94a3b8')
        plt.suptitle('')
        st.pyplot(fig); plt.close()

    with col_r:
        # BMI vs charges scatter
        fig, ax = plt.subplots(figsize=(7, 4))
        fig.patch.set_facecolor('#0f1117')
        ax.set_facecolor('#1a2535')
        for spine in ax.spines.values(): spine.set_edgecolor('#2a3f55')
        colors_sc = df['smoker'].map({'yes':'#f87171','no':'#38bdf8'})
        ax.scatter(df['bmi'], df['charges'], c=colors_sc, alpha=0.4, s=15)
        ax.axvline(30, color='#fbbf24', linestyle='--', lw=1.5, label='BMI=30 (Obese)')
        ax.set_title('BMI vs Charges  (red = smoker)', color='#e2e8f0')
        ax.set_xlabel('BMI', color='#64748b')
        ax.set_ylabel('Charges ($)', color='#64748b')
        ax.tick_params(colors='#94a3b8')
        ax.legend(fontsize=8, facecolor='#1a2535', labelcolor='#94a3b8')
        st.pyplot(fig); plt.close()

    col_l2, col_r2 = st.columns(2)

    with col_l2:
        # Age × Smoking
        fig, ax = plt.subplots(figsize=(7, 4))
        fig.patch.set_facecolor('#0f1117')
        ax.set_facecolor('#1a2535')
        for spine in ax.spines.values(): spine.set_edgecolor('#2a3f55')
        for label, grp in df.groupby('smoker'):
            ax.scatter(grp['age'], grp['charges'],
                       label=f'Smoker: {label}', alpha=0.45, s=15,
                       color='#f87171' if label=='yes' else '#38bdf8')
        ax.set_title('Age × Smoking → Charges', color='#e2e8f0')
        ax.set_xlabel('Age', color='#64748b')
        ax.set_ylabel('Charges ($)', color='#64748b')
        ax.tick_params(colors='#94a3b8')
        ax.legend(fontsize=8, facecolor='#1a2535', labelcolor='#94a3b8')
        st.pyplot(fig); plt.close()

    with col_r2:
        # Correlation heatmap
        fig, ax = plt.subplots(figsize=(7, 4))
        fig.patch.set_facecolor('#0f1117')
        ax.set_facecolor('#1a2535')
        corr = df_enc.corr().round(2)
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
                    center=0, vmin=-1, vmax=1, ax=ax,
                    linewidths=0.5, linecolor='#0f1117',
                    annot_kws={'size': 7},
                    cbar_kws={'shrink': 0.8})
        ax.set_title('Correlation Matrix', color='#e2e8f0')
        ax.tick_params(colors='#94a3b8', labelsize=8)
        st.pyplot(fig); plt.close()

    # Region × Gender
    st.markdown("")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4))
    fig.patch.set_facecolor('#0f1117')
    for ax in axes:
        ax.set_facecolor('#1a2535')
        ax.tick_params(colors='#94a3b8')
        for spine in ax.spines.values(): spine.set_edgecolor('#2a3f55')

    pivot = df.groupby(['region','sex'])['charges'].mean().unstack()
    pivot.plot(kind='bar', ax=axes[0], color=['#38bdf8','#f472b6'], edgecolor='#0f1117', width=0.7)
    axes[0].set_title('Region × Gender → Avg Charges', color='#e2e8f0')
    axes[0].set_xlabel('Region', color='#64748b')
    axes[0].set_ylabel('Avg Charges ($)', color='#64748b')
    axes[0].tick_params(axis='x', rotation=30)
    axes[0].legend(title='Sex', facecolor='#1a2535', labelcolor='#94a3b8')

    children_avg = df.groupby('children')['charges'].mean()
    axes[1].plot(children_avg.index, children_avg.values,
                 marker='o', lw=2.5, color='#fb923c',
                 markersize=8, markerfacecolor='#0f1117', markeredgewidth=2)
    axes[1].fill_between(children_avg.index, children_avg.values, alpha=0.12, color='#fb923c')
    axes[1].set_title('Children vs Avg Charges', color='#e2e8f0')
    axes[1].set_xlabel('Number of Children', color='#64748b')
    axes[1].set_ylabel('Avg Charges ($)', color='#64748b')

    plt.tight_layout()
    st.pyplot(fig); plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Model Performance
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Model Comparison — 7 Algorithms</div>',
                unsafe_allow_html=True)

    results_df = pd.DataFrame(all_results).T.sort_values('R2', ascending=False)
    results_df.index.name = 'Model'
    results_df_display = results_df.copy()
    results_df_display['RMSE'] = results_df_display['RMSE'].apply(lambda x: f'${x:,.2f}')
    results_df_display['MAE']  = results_df_display['MAE'].apply(lambda x: f'${x:,.2f}')
    st.dataframe(results_df_display, use_container_width=True)

    st.markdown("")
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.patch.set_facecolor('#0f1117')
    colors_bar = plt.cm.RdYlGn(np.linspace(0.2, 0.9, len(results_df)))

    for ax, metric in zip(axes, ['R2','RMSE','MAE']):
        ax.set_facecolor('#1a2535')
        ax.tick_params(colors='#94a3b8', labelsize=9)
        for spine in ax.spines.values(): spine.set_edgecolor('#2a3f55')

        vals = results_df[metric].sort_values(ascending=(metric != 'R2'))
        bars = ax.barh(vals.index, vals.values,
                       color=colors_bar[::-1], edgecolor='#0f1117', height=0.6)
        for bar, val in zip(bars, vals.values):
            ax.text(bar.get_width() * 1.01,
                    bar.get_y() + bar.get_height()/2,
                    f'{val:.4f}' if metric=='R2' else f'${val:,.0f}',
                    va='center', fontsize=8, color='#94a3b8')
        ax.set_title(metric, color='#e2e8f0', fontsize=12)
        ax.set_xlabel(metric, color='#64748b')

    plt.tight_layout()
    st.pyplot(fig); plt.close()

    st.markdown("")
    st.markdown('<div class="section-title">Best Model — Actual vs Predicted</div>',
                unsafe_allow_html=True)

    X_all = df_fe.drop('charges', axis=1)
    y_all = df_fe['charges']
    _, X_test_d, _, y_test_d = train_test_split(X_all, y_all, test_size=0.2, random_state=42)
    X_test_s = scaler.transform(X_test_d)
    preds    = best_model.predict(X_test_s)
    residuals = y_test_d.values - preds

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor('#0f1117')
    for ax in axes:
        ax.set_facecolor('#1a2535')
        ax.tick_params(colors='#94a3b8')
        for spine in ax.spines.values(): spine.set_edgecolor('#2a3f55')

    axes[0].scatter(y_test_d, preds, alpha=0.4, color='#38bdf8', s=15)
    mn = min(y_test_d.min(), preds.min())
    mx = max(y_test_d.max(), preds.max())
    axes[0].plot([mn,mx],[mn,mx],'r--', lw=2, label='Perfect Prediction')
    axes[0].set_title('Actual vs Predicted', color='#e2e8f0')
    axes[0].set_xlabel('Actual ($)', color='#64748b')
    axes[0].set_ylabel('Predicted ($)', color='#64748b')
    axes[0].legend(fontsize=9, facecolor='#1a2535', labelcolor='#94a3b8')

    axes[1].hist(residuals, bins=40, color='#4ade80', edgecolor='#0f1117', alpha=0.85)
    axes[1].axvline(0, color='#f87171', linestyle='--', lw=2)
    axes[1].set_title('Residuals Distribution', color='#e2e8f0')
    axes[1].set_xlabel('Residual (Actual − Predicted)', color='#64748b')
    axes[1].set_ylabel('Count', color='#64748b')

    plt.tight_layout()
    st.pyplot(fig); plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Predict My Cost
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Enter Your Health Profile</div>',
                unsafe_allow_html=True)

    form_col, result_col = st.columns([1, 1], gap="large")

    with form_col:
        age      = st.slider("🎂 Age", 18, 64, 35)
        bmi      = st.slider("⚖️ BMI", 15.0, 55.0, 28.0, step=0.1)
        children = st.slider("👶 Number of Children / Dependents", 0, 5, 0)

        col_a, col_b = st.columns(2)
        with col_a:
            sex    = st.selectbox("👤 Sex", ["male", "female"])
            smoker = st.selectbox("🚬 Smoker", ["no", "yes"])
        with col_b:
            region = st.selectbox("📍 Region",
                                  ["northeast","northwest","southeast","southwest"])

        # BMI indicator
        bmi_label = ("Underweight" if bmi < 18.5 else
                     "Normal"      if bmi < 25   else
                     "Overweight"  if bmi < 30   else "Obese")
        bmi_color = ("#60a5fa" if bmi < 18.5 else
                     "#4ade80" if bmi < 25   else
                     "#fbbf24" if bmi < 30   else "#f87171")
        st.markdown(
            f'<div style="background:#1a2535;border:1px solid #2a3f55;border-radius:10px;'
            f'padding:10px 16px;display:flex;justify-content:space-between;margin-top:8px">'
            f'<span style="color:#64748b;font-size:12px">BMI CATEGORY</span>'
            f'<span style="color:{bmi_color};font-weight:700;font-size:13px">{bmi_label}</span>'
            f'</div>', unsafe_allow_html=True)

        st.markdown("")
        predict_clicked = st.button("⚡ Estimate My Insurance Cost")

    with result_col:
        if predict_clicked:
            # Build input
            sex_enc    = 1 if sex == 'male' else 0
            smoker_enc = 1 if smoker == 'yes' else 0

            input_dict = {
                'age'              : age,
                'sex'              : sex_enc,
                'bmi'              : float(bmi),
                'children'         : children,
                'smoker'           : smoker_enc,
                'region_northwest' : region == 'northwest',
                'region_southeast' : region == 'southeast',
                'region_southwest' : region == 'southwest',
                'bmi_category'     : (0 if bmi < 18.5 else
                                      1 if bmi < 25   else
                                      2 if bmi < 30   else 3),
                'age_group'        : (0 if age <= 25 else
                                      1 if age <= 35 else
                                      2 if age <= 45 else
                                      3 if age <= 55 else 4),
                'smoker_bmi'       : smoker_enc * float(bmi),
                'smoker_age'       : smoker_enc * age,
                'obese_smoker'     : int(bmi >= 30 and smoker == 'yes'),
            }

            input_df     = pd.DataFrame([input_dict])[feature_cols]
            input_scaled = scaler.transform(input_df)
            cost         = best_model.predict(input_scaled)[0]
            monthly      = cost / 12

            # Risk level
            if cost < 8000:
                risk, risk_cls = "Low Risk",      "risk-low"
            elif cost < 20000:
                risk, risk_cls = "Medium Risk",   "risk-medium"
            elif cost < 35000:
                risk, risk_cls = "High Risk",     "risk-high"
            else:
                risk, risk_cls = "Very High Risk","risk-high"

            # Result card
            st.markdown(
                f'<div class="predict-result">'
                f'<div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;'
                f'color:#64748b;margin-bottom:8px">Estimated Annual Cost</div>'
                f'<div class="predict-amount">${cost:,.0f}</div>'
                f'<div class="predict-monthly">≈ ${monthly:,.0f} / month</div>'
                f'<div style="margin-top:14px">'
                f'<span class="{risk_cls}">{risk}</span>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown("")

            # Factor breakdown
            st.markdown("**📊 Cost Factor Breakdown**")
            base_cost = 4443   # young healthy non-smoker baseline

            factors = {
                "Age Effect"    : min(100, int((age - 18) / (64-18) * 60)),
                "BMI Effect"    : min(100, int((bmi - 15) / (55-15) * 50)),
                "Smoking"       : 95 if smoker == 'yes' else 5,
                "Obesity+Smoke" : 90 if (bmi >= 30 and smoker == 'yes') else 10,
                "Region"        : 40 if region == 'southeast' else 20,
                "Children"      : min(100, children * 15),
            }

            for fname, fval in factors.items():
                bar_color = "#f87171" if fval > 60 else "#fbbf24" if fval > 30 else "#4ade80"
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">'
                    f'<span style="font-size:11px;color:#64748b;width:110px;flex-shrink:0">{fname}</span>'
                    f'<div style="flex:1;height:6px;background:rgba(255,255,255,0.05);border-radius:3px">'
                    f'<div style="width:{fval}%;height:100%;background:{bar_color};border-radius:3px;'
                    f'transition:width 1s"></div></div>'
                    f'<span style="font-size:11px;color:#475569;width:30px">{fval}%</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.markdown("")
            st.caption("*Prediction based on Linear Regression model (R²=0.91). "
                       "Not financial advice.*")

        else:
            st.markdown(
                '<div style="height:300px;display:flex;flex-direction:column;align-items:center;'
                'justify-content:center;color:#334155;text-align:center">'
                '<div style="font-size:52px;opacity:0.4">🩺</div>'
                '<div style="margin-top:12px;font-size:13px;line-height:1.8">'
                'Fill in your health profile<br>and click <b>Estimate</b> to get<br>'
                'your insurance cost prediction</div>'
                '</div>',
                unsafe_allow_html=True
            )