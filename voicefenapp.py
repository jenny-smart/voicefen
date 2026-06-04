import streamlit as st

st.set_page_config(
    page_title="魏世芬聲音教練｜課程收費系統",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

from pages_admin import render_admin
from pages_student import render_student
from styles import inject_styles

inject_styles()

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="brand-icon">🎤</div>
        <div class="brand-name">魏世芬<br>聲音教練</div>
        <div class="brand-tagline">帶你找回自己的聲音</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    mode = st.radio(
        "選擇模式",
        ["🎵 學員報名 / 查詢", "🔐 管理後台"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-footer">
        <div>voicefen.com</div>
        <div style="font-size:0.72rem;margin-top:4px;opacity:0.5;">Vocal Coach · 13年</div>
    </div>
    """, unsafe_allow_html=True)

# ── 路由 ──────────────────────────────────────────────────
if mode == "🔐 管理後台":
    render_admin()
else:
    render_student()
