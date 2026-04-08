import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# Must be the first Streamlit command
st.set_page_config(page_title="Vibe Classifier", layout="wide")

def inject_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    /* Global Typography */
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif !important;
        background-color: #0e1117;
        color: #e6edf3;
    }
    
    /* Clean Monochrome Header */
    .title-clean {
        color: #ffffff;
        font-size: 3.2rem;
        font-weight: 600;
        letter-spacing: -1px;
        margin-bottom: 15px;
    }

    .subtitle-text {
        font-size: 1.1rem;
        color: #8b949e;
        margin-bottom: 40px;
        font-weight: 400;
    }

    /* Minimalist Metric Panel */
    .minimal-panel {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 24px;
        text-align: left;
        transition: all 0.2s ease;
    }
    .val-text {
        font-size: 2.8rem;
        font-weight: 500;
        color: #ffffff;
        margin-bottom: 4px;
        line-height: 1;
    }
    .lbl-text {
        font-size: 0.95rem;
        font-weight: 500;
        color: #8b949e;
        text-transform: capitalize;
    }
    
    /* Streamlit overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 30px;
        border-bottom: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        font-size: 1.05rem;
        font-weight: 500;
        color: #8b949e;
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        border-bottom: 2px solid #ffffff !important;
    }
    
    hr {
        border-top: 1px solid #30363d !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------- DATA PIPELINE -----------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('cleaned_dataset.csv')
        df['Intensity'] = df['Energy'] * df['Danceability']
        df['Vocal_Proxy'] = df['Loudness'] / (df['Energy'] + 0.001)
        df['Depression_Score'] = (100 - df['Happiness']) * (100 - df['Energy'])
        return df
    except Exception as e:
        return None

@st.cache_data
def get_metrics(df):
    try:
        scaler = joblib.load('scaler.pkl')
        model = joblib.load('spotify_vibe_model.pkl')
        
        X = df.drop(['Song Name', 'Vibe'], axis=1)
        y = df['Vibe']
        X_scaled = scaler.transform(X)
        
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)
        preds = model.predict(X_test)
        
        acc = accuracy_score(y_test, preds)
        cm = confusion_matrix(y_test, preds, labels=model.classes_)
        cr = classification_report(y_test, preds, output_dict=True)
        return acc, cm, cr, model.classes_
    except Exception as e:
        return None, None, None, None

# ----------------- UI RENDERING -----------------
def main():
    inject_styles()
    
    st.markdown('<div class="title-clean">Vibe Classifier</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">Advanced Acoustic Analysis & Real-Time Classification Metrics</div>', unsafe_allow_html=True)

    df = load_data()
    if df is None:
        st.error("Critical Error: 'cleaned_dataset.csv' missing. Run `clean_data.py` first.")
        return
        
    acc, cm, cr, classes = get_metrics(df)
    
    tab_overview, tab_viz, tab_model = st.tabs(["Data Overview", "Vibe Visualizations", "Model Architecture & Accuracy"])
    
    # -------- TAB 1: OVERVIEW --------
    with tab_overview:
        st.markdown("### Dataset Integrity")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="minimal-panel"><p class="val-text">{df.shape[0]}</p><p class="lbl-text">Total Tracks</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="minimal-panel"><p class="val-text">{df.shape[1]}</p><p class="lbl-text">Features</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="minimal-panel"><p class="val-text">4</p><p class="lbl-text">Target Classes</p></div>', unsafe_allow_html=True)
        with col4:
            if acc:
                st.markdown(f'<div class="minimal-panel"><p class="val-text">{acc*100:.1f}%</p><p class="lbl-text">Core Accuracy</p></div>', unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### Sample Records Explorer")
        st.dataframe(df.head(100), width=1800)

    # -------- TAB 2: VIZ --------
    with tab_viz:
        st.markdown("### The 3D Vibe Universe")
        st.markdown("An interactive multi-dimensional representation of how vibes occupy distinct feature quadrants.")
        try:
            with open('vibe_graph.html', 'r', encoding='utf-8') as f:
                html_data = f.read()
            st.components.v1.html(html_data, height=600, scrolling=True)
        except:
            st.warning("`vibe_graph.html` not found. Regenerate it using `visualize_data.py`.")
            
        st.markdown("<hr>", unsafe_allow_html=True)
        
        col_box, col_heat = st.columns([1, 1])
        with col_box:
            st.markdown("### Feature Densities (Energy Levels)")
            fig1 = px.box(df, x="Vibe", y="Energy", color="Vibe", 
                         title="Energy Distribution across Categories",
                         template="plotly_dark")
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig1, width=800)
            
        with col_heat:
            st.markdown("### Variable Synergy (Correlation Matrix)")
            numeric_df = df.drop(columns=['Song Name', 'Vibe'], errors='ignore')
            corr = numeric_df.corr()
            fig2 = px.imshow(corr, text_auto=".2f", color_continuous_scale="gray", 
                            title="Pearson Correlation Heatmap",
                            template="plotly_dark")
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, width=800)

    # -------- TAB 3: MODEL METRICS --------
    with tab_model:
        if not acc:
            st.error("Model artifacts missing. Cannot display metrics.")
            return

        st.markdown("### Soft-Voting Ensemble Committee Metrics")
        st.markdown("We combine Random Forest, Gradient Boosting, and SVM predictions to declare a robust verdict.")
        
        met1, met2, met3 = st.columns(3)
        met1.metric(label="Global Accuracy Rate", value=f"{acc*100:.2f}%")
        met2.metric(label="Macro Support F1", value=f"{cr['macro avg']['f1-score']:.3f}")
        met3.metric(label="Class Count", value=f"{len(classes)} Active Sets")

        st.markdown("<br>", unsafe_allow_html=True)
        
        col_cr, col_cm = st.columns([1.2, 1])
        
        with col_cr:
            st.markdown("#### Precision, Recall & F1 Architecture")
            report_df = pd.DataFrame(cr).transpose().round(3)
            # Remove accuracy row as it's not a class
            if 'accuracy' in report_df.index:
                report_df = report_df.drop('accuracy')
            st.dataframe(
                report_df.style.background_gradient(cmap='gray', axis=0).format("{:.3f}"), 
                width=800, height=350
            )
            
        with col_cm:
            st.markdown("#### Confusion Matrix Mapping")
            cm_df = pd.DataFrame(cm, index=classes, columns=classes)
            fig3 = px.imshow(cm_df, text_auto=True, color_continuous_scale="gray",
                             labels=dict(x="Predicted Vibe", y="Actual Truth", color="Frequency"),
                             x=classes, y=classes,
                             template="plotly_dark")
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig3, width=800)

if __name__ == '__main__':
    main()
