"""
魏世芬聲音教練｜後台管理系統 v2
Streamlit + 自訂 HTML 元件，黑金質感
"""
import streamlit as st
import streamlit.components.v1 as components
import requests, json
from datetime import datetime
import pandas as pd

# ── 頁面設定 ──────────────────────────────────────────────────
st.set_page_config(
    page_title="魏世芬聲音教練｜管理後台",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 全域 CSS：只改 Streamlit 結構，視覺由 html() 負責 ──────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Noto+Serif+TC:wght@400;500;600&family=Noto+Sans+TC:wght@300;400;500&display=swap');

html,body,[class*="css"]{ font-family:'Noto Sans TC',sans-serif; }
#MainMenu,footer,header{ visibility:hidden; }
.block-container{ padding:1.2rem 1.5rem 2rem !important; max-width:100% !important; }

/* ── 強制黑底 ── */
.stApp{ background:#0C0C0C !important; }
.main .block-container{ background:#0C0C0C !important; }
[data-testid="stAppViewContainer"]{ background:#0C0C0C !important; }
[data-testid="stAppViewBlockContainer"]{ background:#0C0C0C !important; }

/* ── 所有文字預設亮色（全覆蓋）── */
.stApp *, .stApp p, .stApp span, .stApp label,
.stApp div, .stMarkdown *, .stMarkdown p,
[data-testid="stMarkdownContainer"] *,
[data-testid="stMarkdownContainer"] p{ color:#F7F2E8 !important; }

/* selectbox 文字 */
.stSelectbox [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] div,
.stSelectbox [data-baseweb="select"] input{ color:#F7F2E8 !important; background:#1a1a1a !important; }

/* st.info / st.success / st.error — 自帶淺底，文字要深色 */
[data-testid="stAlert"]{ border-radius:10px !important; }
[data-testid="stAlert"] *{ color:#1a1a1a !important; }

/* st.error 紅底時文字白色 */
[data-testid="stAlert"][data-baseweb="notification"][kind="error"] *{ color:#fff !important; }

/* section header / expander 標題 */
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span{ color:#F7F2E8 !important; }

/* caption */
[data-testid="stCaptionContainer"] p,
.stCaption p{ color:#555048 !important; }

/* tab label */
.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] span{ color:inherit !important; }

/* radio label text */
[data-testid="stSidebar"] .stRadio label p,
[data-testid="stSidebar"] .stRadio label span{ color:inherit !important; }

/* checkbox label */
.stCheckbox label p,
.stCheckbox label span{ color:#8A7F70 !important; }

/* form submit / download btn 文字 */
.stFormSubmitButton button p,
.stFormSubmitButton button span,
[data-testid="stDownloadButton"] button p,
[data-testid="stDownloadButton"] button span{ color:inherit !important; }

/* Tab panel 黑底 */
.stTabs [data-baseweb="tab-panel"]{ background:#0C0C0C !important; padding:16px 0 !important; }

/* Expander 內部黑底 */
[data-testid="stExpander"] details{ background:#1a1a1a !important; }
[data-testid="stExpander"] summary{ color:#F7F2E8 !important; }
[data-testid="stExpander"] summary:hover{ color:#E2C26A !important; }

/* Caption 文字 */
.stCaptionContainer, [data-testid="stCaptionContainer"]{ color:#555048 !important; }

/* Dataframe 深色 */
[data-testid="stDataFrame"] th{ background:#252525 !important; color:#8A7F70 !important; }
[data-testid="stDataFrame"] td{ background:#1a1a1a !important; color:#F7F2E8 !important; }

/* Sidebar */
section[data-testid="stSidebar"]{
    background:#111 !important;
    border-right:1px solid rgba(201,168,76,0.15) !important;
    min-width:220px !important; max-width:220px !important;
}
section[data-testid="stSidebar"] > div{ padding:0 !important; }

/* Radio 導覽 */
[data-testid="stSidebar"] .stRadio > div{ gap:2px !important; }
[data-testid="stSidebar"] .stRadio label{
    background:transparent !important;
    border-radius:8px !important;
    padding:9px 14px !important;
    color:#8A7F70 !important;
    font-size:0.86rem !important;
    cursor:pointer !important;
    transition:all .2s !important;
    border:none !important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked){
    background:rgba(201,168,76,0.1) !important;
    color:#E2C26A !important;
}
[data-testid="stSidebar"] .stRadio label:hover:not(:has(input:checked)){
    background:rgba(255,255,255,0.04) !important;
    color:#C9A84C !important;
}
[data-testid="stSidebar"] .stRadio input{ display:none !important; }

/* 按鈕 */
.stButton>button{
    background:linear-gradient(135deg,#C9A84C,#E2C26A) !important;
    color:#0C0C0C !important; font-weight:600 !important;
    border:none !important; border-radius:8px !important;
    font-family:'Noto Sans TC',sans-serif !important;
}
/* 次要按鈕 */
.stButton>button[kind="secondary"]{
    background:rgba(255,255,255,0.05) !important;
    color:#8A7F70 !important;
    border:1px solid rgba(255,255,255,0.1) !important;
}

/* Form */
[data-testid="stForm"]{
    background:#1a1a1a !important;
    border:1px solid rgba(201,168,76,0.1) !important;
    border-radius:12px !important; padding:16px !important;
}

/* Input / Select */
.stTextInput input,.stNumberInput input,.stTextArea textarea,.stSelectbox>div>div{
    background:#1a1a1a !important;
    border:1px solid rgba(201,168,76,0.2) !important;
    border-radius:8px !important;
    color:#F7F2E8 !important;
    font-family:'Noto Sans TC',sans-serif !important;
}
.stTextInput input:focus,.stTextArea textarea:focus{
    border-color:rgba(201,168,76,0.5) !important;
    box-shadow:none !important;
}

/* Tab */
.stTabs [data-baseweb="tab-list"]{
    background:transparent !important;
    border-bottom:1px solid rgba(201,168,76,0.12) !important;
    gap:0 !important;
}
.stTabs [data-baseweb="tab"]{
    background:transparent !important;
    color:#555048 !important; font-size:0.85rem !important;
    padding:10px 20px !important;
    border-bottom:2px solid transparent !important;
}
.stTabs [aria-selected="true"]{
    color:#E2C26A !important;
    border-bottom-color:#C9A84C !important;
    background:transparent !important;
}

/* Expander */
[data-testid="stExpander"]{
    background:#1a1a1a !important;
    border:1px solid rgba(201,168,76,0.1) !important;
    border-radius:10px !important;
}
[data-testid="stExpander"] summary{ color:#F7F2E8 !important; }

/* Dataframe */
[data-testid="stDataFrame"]{ border-radius:10px !important; }

/* Download btn */
[data-testid="stDownloadButton"]>button{
    background:transparent !important;
    border:1px solid rgba(201,168,76,0.35) !important;
    color:#E2C26A !important;
}
hr{ border-color:rgba(201,168,76,0.1) !important; }
.stCheckbox label{ color:#8A7F70 !important; }
[data-testid="column"]{ background:transparent !important; }
.stNumberInput button{ background:#252525 !important; border:1px solid rgba(201,168,76,.2) !important; color:#E2C26A !important; }
[data-baseweb="popover"] [role="listbox"]{ background:#1E1E1E !important; border:1px solid rgba(201,168,76,.2) !important; }
[data-baseweb="popover"] [role="option"]{ color:#F7F2E8 !important; }
[data-baseweb="popover"] [role="option"]:hover{ background:rgba(201,168,76,.1) !important; }
</style>
""", unsafe_allow_html=True)

# ── 設定 ──────────────────────────────────────────────────────
GAS_URL     = st.secrets.get("GAS_URL", "")
ADMIN_TOKEN = st.secrets.get("ADMIN_TOKEN", "changeme")

# ── API ───────────────────────────────────────────────────────
def api(action, payload=None):
    if not GAS_URL:
        return {"ok": False, "msg": "尚未設定 GAS_URL（請在 secrets.toml 設定）"}
    try:
        r = requests.post(GAS_URL, json={
            "action": action, "token": ADMIN_TOKEN, "payload": payload or {}
        }, timeout=30)
        return r.json()
    except Exception as e:
        return {"ok": False, "msg": str(e)}

@st.cache_data(ttl=60)
def get_dashboard(): return api("getDashboard")
@st.cache_data(ttl=30)
def get_orders(status=None, courseId=None, keyword=None):
    return api("getOrders", {"status":status,"courseId":courseId,"keyword":keyword})
@st.cache_data(ttl=30)
def get_courses(): return api("getCourses")
@st.cache_data(ttl=30)
def get_payments(): return api("getPayments")

def clear_cache():
    get_dashboard.clear(); get_orders.clear()
    get_courses.clear();   get_payments.clear()

# ── 自訂 HTML 元件工具 ────────────────────────────────────────
FONT_IMPORT = """
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Noto+Serif+TC:wght@400;500;600&family=Noto+Sans+TC:wght@300;400;500&display=swap" rel="stylesheet">
"""

BASE_CSS = """
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:transparent;font-family:'Noto Sans TC',sans-serif;color:#F7F2E8;}
:root{
  --black:#0C0C0C;--card:#1E1E1E;--graphite:#252525;
  --gold:#C9A84C;--gold-lt:#E2C26A;--cream:#F7F2E8;
  --warm:#8A7F70;--muted:#555048;
  --green:#A5D6A7;--yellow:#E2C26A;--red:#EF9A9A;--blue:#90CAF9;
}
.pill{display:inline-flex;align-items:center;gap:5px;padding:3px 10px;border-radius:20px;font-size:.7rem;font-weight:600;}
.pill::before{content:'';width:5px;height:5px;border-radius:50%;background:currentColor;}
.pill-g{background:rgba(165,214,167,.12);color:var(--green);border:1px solid rgba(165,214,167,.2);}
.pill-y{background:rgba(226,194,106,.12);color:var(--yellow);border:1px solid rgba(226,194,106,.22);}
.pill-r{background:rgba(239,154,154,.1);color:var(--red);border:1px solid rgba(239,154,154,.2);}
.pill-b{background:rgba(144,202,249,.1);color:var(--blue);border:1px solid rgba(144,202,249,.2);}
</style>
"""

def html_block(content, height=None):
    full = FONT_IMPORT + BASE_CSS + content
    if height:
        components.html(full, height=height, scrolling=False)
    else:
        components.html(full, scrolling=False)

# ── KPI 卡片 ──────────────────────────────────────────────────
def kpi_cards(items):
    """items = list of {label, value, sub, color}"""
    cols_html = ""
    for item in items:
        color = item.get("color","var(--gold-lt)")
        sub   = item.get("sub","")
        cols_html += f"""
        <div style="flex:1;background:var(--card);border:1px solid rgba(201,168,76,.15);
                    border-radius:14px;padding:22px 24px;position:relative;overflow:hidden;">
          <div style="position:absolute;bottom:0;left:0;right:0;height:2px;
                      background:linear-gradient(90deg,var(--gold),transparent);"></div>
          <div style="font-size:.68rem;letter-spacing:.12em;text-transform:uppercase;
                      color:var(--warm);margin-bottom:12px;">{item['label']}</div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:2.2rem;
                      font-weight:600;color:{color};line-height:1;">{item['value']}</div>
          {'<div style="font-size:.72rem;color:var(--muted);margin-top:8px;">'+sub+'</div>' if sub else ''}
        </div>"""
    html_block(f"""
    <div style="display:flex;gap:16px;padding:4px 2px;">
      {cols_html}
    </div>
    """, height=120)

# ── 狀態 pill ─────────────────────────────────────────────────
STATUS_PILL = {
    "待付款": ('<span class="pill pill-r">⏳ 待付款</span>',),
    "待對帳": ('<span class="pill pill-y">🔄 待對帳</span>',),
    "已付款": ('<span class="pill pill-g">✅ 已付款</span>',),
    "待核對": ('<span class="pill pill-y">🔄 待核對</span>',),
    "已核對": ('<span class="pill pill-g">✅ 已核對</span>',),
    "異常":   ('<span class="pill pill-r">⚠️ 異常</span>',),
}
def pill(status):
    return STATUS_PILL.get(status, (f'<span class="pill pill-b">{status}</span>',))[0]

# ── 章節標題 ──────────────────────────────────────────────────
def page_header(icon, title, sub=""):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
      <div style="width:4px;height:24px;background:var(--gold,#C9A84C);border-radius:2px;flex-shrink:0;"></div>
      <div style="font-family:'Noto Serif TC',serif;font-size:1.4rem;font-weight:500;color:#F7F2E8;">{icon} {title}</div>
    </div>
    {'<div style="font-size:.78rem;color:#555048;margin-bottom:20px;padding-left:16px;">'+sub+'</div>' if sub else '<div style="margin-bottom:20px;"></div>'}
    """, unsafe_allow_html=True)

def section_title(text):
    st.markdown(f"""
    <div style="font-family:'Noto Serif TC',serif;font-size:.9rem;font-weight:500;
                color:#F7F2E8;margin:20px 0 12px;display:flex;align-items:center;gap:8px;">
      <span style="width:3px;height:14px;background:#C9A84C;border-radius:2px;display:inline-block;"></span>
      {text}
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:28px 20px 22px;border-bottom:1px solid rgba(201,168,76,0.12);">
      <div style="font-size:2rem;filter:drop-shadow(0 0 10px rgba(201,168,76,0.6));">🎤</div>
      <div style="font-family:'Noto Serif TC',serif;font-size:1.1rem;color:#fff;margin-top:10px;line-height:1.3;">
        魏世芬<br><span style="color:#C9A84C;">聲音教練</span>
      </div>
      <div style="font-size:.68rem;color:#3A3530;margin-top:6px;letter-spacing:.08em;">管理後台 · Admin</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    page = st.radio(
        "nav",
        ["📊  收費總覽", "📋  訂單管理", "✅  對帳核對", "🎓  課程設定", "📤  匯出報表"],
        label_visibility="collapsed"
    )

    st.markdown("<div style='margin-top:auto;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    if st.button("🔄 重新整理", use_container_width=True):
        clear_cache(); st.rerun()

    st.markdown("""
    <div style="padding:16px 20px;font-size:.68rem;color:#2A2520;letter-spacing:.06em;border-top:1px solid rgba(201,168,76,0.06);margin-top:12px;">
      voicefen.com · Vocal Coach 13年
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  PAGE 1：收費總覽
# ════════════════════════════════════════════════════════════
if page == "📊  收費總覽":
    page_header("📊", "收費總覽", "即時掌握課程收費狀況")

    res = get_dashboard()
    if not res.get("ok"):
        st.error(res.get("msg","資料載入失敗"))
        st.info("💡 請在 `.streamlit/secrets.toml` 設定 GAS_URL 與 ADMIN_TOKEN")
        st.stop()

    d = res["data"]

    # ── KPI ──
    kpi_cards([
        {"label":"本月訂單數",  "value": d.get("monthOrders",0),
         "sub":"本月新增報名", "color":"#F7F2E8"},
        {"label":"累計已收款",  "value": f"${d.get('totalRevenue',0):,.0f}",
         "sub":"已核對付款總額","color":"#E2C26A"},
        {"label":"待收款金額",  "value": f"${d.get('pendingAmount',0):,.0f}",
         "sub":f"{d.get('pendingCount',0)} 筆未完成","color":"#EF9A9A"},
        {"label":"對帳完成率",  "value": f"{d.get('verifyRate',0)}%",
         "sub":"已核對 / 總訂單","color":"#A5D6A7"},
    ])

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    col_l, col_r = st.columns([3,2], gap="medium")

    # ── 趨勢圖（自訂 SVG bar chart）──
    with col_l:
        trend = d.get("trend", [])
        if trend:
            max_rev = max((t.get("revenue",0) for t in trend), default=1) or 1
            bars = ""
            labels = ""
            n = len(trend)
            w = 460
            pad = 40
            bar_w = int((w - pad*2) / n * 0.45)
            for i, t in enumerate(trend):
                x = pad + int((w-pad*2) * i / n) + int((w-pad*2)/n/2)
                h = int(t.get("revenue",0) / max_rev * 130)
                h = max(h, 2)
                bars += f'<rect x="{x-bar_w//2}" y="{140-h}" width="{bar_w}" height="{h}" rx="3" fill="url(#gold_grad)" opacity=".88"/>'
                mo = str(t.get("month",""))[-2:].lstrip("0") or "0"
                labels += f'<text x="{x}" y="158" text-anchor="middle" font-size="11" fill="#555048">{mo}月</text>'

            html_block(f"""
            <div style="background:#1E1E1E;border:1px solid rgba(201,168,76,.12);border-radius:14px;padding:22px 24px 14px;">
              <div style="font-size:.8rem;color:#F7F2E8;font-family:'Noto Serif TC',serif;margin-bottom:4px;
                          display:flex;align-items:center;gap:8px;">
                <span style="width:3px;height:12px;background:#C9A84C;border-radius:1px;display:inline-block;"></span>
                月收費趨勢
              </div>
              <div style="font-size:.68rem;color:#555048;margin-bottom:14px;">近 6 個月 · 已收款金額</div>
              <svg viewBox="0 0 500 170" style="width:100%;height:170px;">
                <defs>
                  <linearGradient id="gold_grad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#E2C26A"/>
                    <stop offset="100%" stop-color="#C9A84C" stop-opacity=".7"/>
                  </linearGradient>
                </defs>
                <line x1="40" y1="10" x2="40" y2="142" stroke="rgba(201,168,76,.1)" stroke-width="1"/>
                <line x1="40" y1="142" x2="465" y2="142" stroke="rgba(201,168,76,.1)" stroke-width="1"/>
                {bars}
                {labels}
              </svg>
            </div>
            """, height=260)

    # ── 未完成清單 ──
    with col_r:
        r2 = get_orders(status="待付款")
        r3 = get_orders(status="待對帳")
        pending = []
        for r in [r2,r3]:
            if r.get("ok"): pending.extend(r.get("data",[]))

        items_html = ""
        for o in pending[:5]:
            amt = int(o.get("應付金額",0))
            items_html += f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:12px 0;border-bottom:1px solid rgba(255,255,255,.04);">
              <div>
                <div style="font-size:.85rem;color:#F7F2E8;">{o.get('姓名','')}</div>
                <div style="font-size:.72rem;color:#555048;margin-top:2px;">{o.get('課程名稱','')}</div>
              </div>
              <div style="text-align:right;">
                <div style="font-size:.88rem;color:#EF9A9A;font-family:'Cormorant Garamond',serif;">
                  NT${amt:,}
                </div>
                {pill(o.get('訂單狀態',''))}
              </div>
            </div>"""

        if not items_html:
            items_html = """<div style="text-align:center;padding:30px;color:#555048;font-size:.82rem;">
                🎉 所有訂單對帳完成！</div>"""

        html_block(f"""
        <div style="background:#1E1E1E;border:1px solid rgba(201,168,76,.12);border-radius:14px;
                    padding:22px 24px;height:100%;">
          <div style="font-size:.8rem;color:#F7F2E8;font-family:'Noto Serif TC',serif;margin-bottom:4px;
                      display:flex;align-items:center;gap:8px;">
            <span style="width:3px;height:12px;background:#C9A84C;border-radius:1px;display:inline-block;"></span>
            待收款清單
          </div>
          <div style="font-size:.68rem;color:#555048;margin-bottom:12px;">
            共 {len(pending)} 筆待處理
          </div>
          {items_html}
        </div>
        """, height=260)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── 課程分布 ──
    section_title("課程報名分布")
    bycourse = d.get("bycourse", [])
    if bycourse:
        max_c = max((b.get("count",0) for b in bycourse), default=1) or 1
        bars2 = ""
        labels2 = ""
        vals2 = ""
        n2 = len(bycourse)
        for i, b in enumerate(bycourse):
            x = 60 + int(560 * i / n2) + int(560/n2/2)
            h = int(b.get("count",0) / max_c * 80)
            h = max(h, 2)
            bars2 += f'<rect x="{x-30}" y="{90-h}" width="60" height="{h}" rx="4" fill="url(#gold2)" opacity=".85"/>'
            nm = b.get("name","")[:6]
            vals2 += f'<text x="{x}" y="{84-h}" text-anchor="middle" font-size="12" fill="#E2C26A" font-weight="600">{b.get("count",0)}</text>'
            labels2 += f'<text x="{x}" y="108" text-anchor="middle" font-size="11" fill="#555048">{nm}</text>'

        html_block(f"""
        <div style="background:#1E1E1E;border:1px solid rgba(201,168,76,.12);border-radius:14px;padding:22px 24px 14px;">
          <svg viewBox="0 0 680 120" style="width:100%;height:120px;">
            <defs>
              <linearGradient id="gold2" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#E2C26A"/>
                <stop offset="100%" stop-color="#C9A84C" stop-opacity=".6"/>
              </linearGradient>
            </defs>
            {bars2}{vals2}{labels2}
          </svg>
        </div>
        """, height=150)

# ════════════════════════════════════════════════════════════
#  PAGE 2：訂單管理
# ════════════════════════════════════════════════════════════
elif page == "📋  訂單管理":
    page_header("📋", "訂單管理", "查看所有報名記錄，手動更新訂單狀態")

    fc1, fc2, fc3 = st.columns([2,2,3])
    with fc1: f_status  = st.selectbox("狀態", ["全部","待付款","待對帳","已付款"])
    with fc2:
        rc = get_courses()
        c_opts = {"全部課程": None}
        if rc.get("ok"):
            for c in rc.get("data",[]):
                c_opts[c.get("課程名稱","")] = c.get("課程ID")
        f_course = st.selectbox("課程", list(c_opts.keys()))
    with fc3: f_kw = st.text_input("搜尋", placeholder="姓名 / 手機 / 訂單編號")

    res = get_orders(
        status=None if f_status=="全部" else f_status,
        courseId=c_opts.get(f_course),
        keyword=f_kw.strip() or None
    )
    orders = res.get("data",[]) if res.get("ok") else []

    # 自訂表格 HTML
    if orders:
        rows_html = ""
        for o in orders:
            pay = o.get("payment") or {}
            amt = int(o.get("應付金額",0))
            p_act = int(pay.get("實付金額",0)) if pay.get("實付金額") else 0
            ts = str(o.get("報名時間",""))[:16]
            oid = o.get("訂單編號","")
            rows_html += f"""
            <tr>
              <td style="font-size:.72rem;color:#555048;font-family:monospace;">{oid}</td>
              <td style="font-size:.76rem;color:#8A7F70;">{ts}</td>
              <td style="font-weight:500;">{o.get('姓名','')}</td>
              <td style="color:#8A7F70;font-size:.78rem;">{o.get('手機','')}</td>
              <td><span style="background:rgba(144,202,249,.1);color:#90CAF9;border:1px solid rgba(144,202,249,.2);
                               padding:2px 8px;border-radius:20px;font-size:.7rem;">{o.get('課程名稱','')}</span></td>
              <td style="color:#E2C26A;font-family:'Cormorant Garamond',serif;font-size:1rem;">
                ${amt:,}</td>
              <td style="color:#8A7F70;font-size:.78rem;">{pay.get('付款方式','—')}</td>
              <td style="font-family:monospace;color:#E2C26A;font-size:.82rem;">
                {pay.get('帳號後5碼','—')}</td>
              <td>{pill(o.get('訂單狀態',''))}</td>
            </tr>"""

        html_block(f"""
        <div style="background:#1E1E1E;border:1px solid rgba(201,168,76,.1);border-radius:14px;overflow:hidden;">
          <div style="padding:14px 20px;border-bottom:1px solid rgba(201,168,76,.08);
                      display:flex;justify-content:space-between;align-items:center;">
            <span style="font-family:'Noto Serif TC',serif;font-size:.88rem;color:#F7F2E8;">
              訂單列表
            </span>
            <span style="font-size:.72rem;color:#555048;">共 {len(orders)} 筆</span>
          </div>
          <div style="overflow-x:auto;">
          <table style="width:100%;border-collapse:collapse;font-size:.82rem;color:#F7F2E8;">
            <thead>
              <tr style="border-bottom:1px solid rgba(201,168,76,.08);">
                {''.join(f'<th style="padding:10px 14px;text-align:left;font-size:.66rem;letter-spacing:.12em;color:#555048;font-weight:400;text-transform:uppercase;white-space:nowrap;">{h}</th>'
                  for h in ['訂單編號','時間','姓名','手機','課程','應付','付款方式','帳號後5碼','狀態'])}
              </tr>
            </thead>
            <tbody>
              {rows_html}
            </tbody>
          </table>
          </div>
        </div>
        """, height=min(80 + len(orders)*48, 520))
    else:
        st.info("查無訂單記錄")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    section_title("手動更新訂單")
    with st.form("update_order"):
        u1,u2,u3 = st.columns([2,2,3])
        with u1: upd_id   = st.text_input("訂單編號")
        with u2: upd_st   = st.selectbox("更新狀態",["待付款","待對帳","已付款"])
        with u3: upd_note = st.text_input("備註")
        if st.form_submit_button("更新訂單"):
            if upd_id:
                r = api("updateOrder",{"orderId":upd_id,"status":upd_st,"note":upd_note})
                if r.get("ok"): st.success("✅ 已更新"); clear_cache(); st.rerun()
                else: st.error(r.get("msg","更新失敗"))

# ════════════════════════════════════════════════════════════
#  PAGE 3：對帳核對
# ════════════════════════════════════════════════════════════
elif page == "✅  對帳核對":
    page_header("✅", "對帳核對", "核對學員付款資料，確認收款完成")

    res  = get_payments()
    pays = res.get("data",[]) if res.get("ok") else []
    res_o = get_orders()
    orders_map = {o["訂單編號"]: o for o in (res_o.get("data",[]) if res_o.get("ok") else [])}

    pending_pays = [p for p in pays if p.get("核對狀態") != "已核對"]
    done_pays    = [p for p in pays if p.get("核對狀態") == "已核對"]

    tab1, tab2 = st.tabs([f"⏳ 待核對（{len(pending_pays)}）", f"✅ 已核對（{len(done_pays)}）"])

    with tab1:
        if not pending_pays:
            html_block("""
            <div style="background:#1E1E1E;border:1px solid rgba(165,214,167,.2);border-radius:14px;
                        padding:40px;text-align:center;">
              <div style="font-size:2rem;margin-bottom:12px;">🎉</div>
              <div style="font-family:'Noto Serif TC',serif;font-size:1rem;color:#A5D6A7;">
                目前沒有待核對的付款記錄！
              </div>
            </div>
            """, height=140)
        else:
            for p in pending_pays:
                oid = p.get("訂單編號","")
                o   = orders_map.get(oid, {})
                exp = int(o.get("應付金額",0) or 0)
                act = int(p.get("實付金額",0) or 0)
                match_ok = exp > 0 and act > 0 and exp == act
                match_html = (
                    '<span style="color:#A5D6A7;font-size:.78rem;">✅ 金額吻合</span>' if match_ok
                    else f'<span style="color:#EF9A9A;font-size:.78rem;">⚠️ 差額 ${abs(exp-act):,}</span>'
                    if (exp and act) else ""
                )

                with st.expander(
                    f"📌 {oid}　{o.get('姓名','')}　{p.get('付款方式','')}　NT${act:,}",
                    expanded=False
                ):
                    html_block(f"""
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;padding:4px;">
                      <div style="display:flex;flex-direction:column;gap:10px;">
                        {''.join(f'<div><span style="font-size:.68rem;color:#555048;">{k}　</span><span style="font-size:.83rem;">{v}</span></div>'
                          for k,v in [('學員',o.get('姓名','')),('課程',o.get('課程名稱','')),
                                      ('手機',o.get('手機','')),('報名',str(o.get('報名時間',''))[:16])])}
                      </div>
                      <div style="display:flex;flex-direction:column;gap:10px;">
                        {''.join(f'<div><span style="font-size:.68rem;color:#555048;">{k}　</span><span style="font-size:.83rem;">{v}</span></div>'
                          for k,v in [('付款方式',p.get('付款方式','')),
                                      ('帳號後5碼',f"<span style='font-family:monospace;color:#E2C26A'>{p.get('帳號後5碼','—')}</span>"),
                                      ('應付',f"NT${exp:,}"),('實付',f"NT${act:,}")])}
                        {match_html}
                      </div>
                    </div>
                    <div style="margin-top:12px;font-size:.78rem;color:#8A7F70;">
                      備註：{p.get('備註','—')}
                    </div>
                    """, height=160)

                    with st.form(f"verify_{p.get('付款ID','')}"):
                        v1,v2 = st.columns([2,3])
                        with v1: v_st   = st.selectbox("核對結果",["已核對","異常"])
                        with v2: v_note = st.text_input("備註", placeholder="金額正確，對帳完成")
                        if st.form_submit_button("✅ 確認核對"):
                            r = api("verifyPayment",{"payId":p.get("付款ID",""),"status":v_st,"note":v_note})
                            if r.get("ok"): st.success("核對完成！"); clear_cache(); st.rerun()
                            else: st.error(r.get("msg","核對失敗"))

    with tab2:
        if done_pays:
            rows_h = ""
            for p in done_pays:
                act = int(p.get("實付金額",0) or 0)
                rows_h += f"""<tr>
                  <td style="font-family:monospace;font-size:.72rem;color:#555048;">{p.get('付款ID','')}</td>
                  <td style="font-size:.72rem;color:#555048;font-family:monospace;">{p.get('訂單編號','')}</td>
                  <td style="font-size:.76rem;color:#8A7F70;">{str(p.get('付款時間',''))[:16]}</td>
                  <td>{p.get('付款方式','')}</td>
                  <td style="font-family:monospace;color:#E2C26A;">{p.get('帳號後5碼','—')}</td>
                  <td style="color:#A5D6A7;font-family:'Cormorant Garamond',serif;font-size:1rem;">NT${act:,}</td>
                  <td>{pill('已核對')}</td>
                  <td style="font-size:.76rem;color:#8A7F70;">{p.get('核對備註','')}</td>
                </tr>"""
            html_block(f"""
            <div style="background:#1E1E1E;border:1px solid rgba(201,168,76,.1);border-radius:14px;overflow:hidden;">
              <div style="overflow-x:auto;">
              <table style="width:100%;border-collapse:collapse;font-size:.82rem;color:#F7F2E8;">
                <thead><tr style="border-bottom:1px solid rgba(201,168,76,.08);">
                  {''.join(f'<th style="padding:10px 14px;text-align:left;font-size:.66rem;color:#555048;font-weight:400;letter-spacing:.1em;text-transform:uppercase;">{h}</th>'
                    for h in ['付款ID','訂單編號','付款時間','方式','帳號後5碼','實付','狀態','備註'])}
                </tr></thead>
                <tbody>{rows_h}</tbody>
              </table>
              </div>
            </div>
            """, height=min(80+len(done_pays)*44,420))
        else:
            st.info("尚無已核對記錄")

# ════════════════════════════════════════════════════════════
#  PAGE 4：課程設定
# ════════════════════════════════════════════════════════════
elif page == "🎓  課程設定":
    page_header("🎓", "課程設定", "新增、編輯、停用課程，前台即時更新")

    res = get_courses()
    courses = res.get("data",[]) if res.get("ok") else []

    section_title("目前課程")
    if courses:
        for c in courses:
            is_open  = c.get("是否開放") is True
            is_feat  = c.get("精選標記") is True
            price    = int(c.get("單價",0))
            status_t = "🟢 開放中" if is_open else "🔴 已停用"

            with st.expander(f"{c.get('圖示','')}  {c.get('課程名稱','')}　｜　${price:,} / {c.get('計費單位','')}　｜　{status_t}"):
                html_block(f"""
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:4px 0 8px;">
                  <div style="display:flex;flex-direction:column;gap:8px;">
                    {''.join(f'<div><span style="font-size:.68rem;color:#555048;letter-spacing:.08em;">{k}　</span><span style="font-size:.82rem;color:#F7F2E8;">{v}</span></div>'
                      for k,v in [('課程ID',c.get('課程ID','')),('類型',c.get('課程類型','')),
                                  ('計費單位',c.get('計費單位','')),
                                  ('精選',('⭐ 是' if is_feat else '否'))])}
                  </div>
                  <div>
                    <div style="font-size:.68rem;color:#555048;margin-bottom:6px;letter-spacing:.08em;">課程說明</div>
                    <div style="font-size:.8rem;color:#8A7F70;line-height:1.6;">{c.get('課程說明','')}</div>
                  </div>
                </div>
                """, height=120)

                with st.form(f"edit_{c.get('課程ID','')}"):
                    r1,r2 = st.columns(2)
                    with r1:
                        e_name  = st.text_input("課程名稱", value=c.get("課程名稱",""))
                        e_type  = st.text_input("英文類型", value=c.get("課程類型",""))
                        e_icon  = st.text_input("圖示 Emoji", value=c.get("圖示",""))
                    with r2:
                        e_price = st.number_input("單價", value=price, step=100)
                        e_unit  = st.text_input("計費單位", value=c.get("計費單位",""))
                        e_open  = st.checkbox("開放報名", value=is_open)
                        e_feat  = st.checkbox("標記精選", value=is_feat)
                    e_desc = st.text_area("課程說明", value=c.get("課程說明",""), height=72)
                    b1,b2 = st.columns(2)
                    with b1:
                        if st.form_submit_button("💾 儲存變更"):
                            r = api("saveCourse",{"id":c.get("課程ID"),"name":e_name,"type":e_type,
                                "desc":e_desc,"icon":e_icon,"price":e_price,"unit":e_unit,
                                "open":e_open,"featured":e_feat})
                            if r.get("ok"): st.success("✅ 已儲存"); clear_cache(); st.rerun()
                            else: st.error(r.get("msg","儲存失敗"))
                    with b2:
                        if st.form_submit_button("🗑️ 刪除課程", type="secondary"):
                            r = api("deleteCourse",{"id":c.get("課程ID")})
                            if r.get("ok"): st.success("已刪除"); clear_cache(); st.rerun()
                            else: st.error(r.get("msg"))
    else:
        st.info("尚無課程，請新增")

    st.markdown("---")
    section_title("新增課程")
    with st.form("add_course"):
        a1,a2 = st.columns(2)
        with a1:
            a_name  = st.text_input("課程名稱 *", placeholder="例：一對一私人課程")
            a_type  = st.text_input("英文類型 *", placeholder="例：One-on-One")
            a_icon  = st.text_input("圖示 Emoji", value="🎤")
        with a2:
            a_price = st.number_input("單價 *", min_value=0, step=100, value=3000)
            a_unit  = st.text_input("計費單位 *", value="堂")
            a_open  = st.checkbox("立即開放報名", value=True)
            a_feat  = st.checkbox("標記為精選", value=False)
        a_desc = st.text_area("課程說明 *", placeholder="描述課程內容與特色...", height=80)
        if st.form_submit_button("➕ 新增課程"):
            if not all([a_name,a_type,a_price,a_unit,a_desc]):
                st.error("請填寫所有必填欄位（*）")
            else:
                r = api("saveCourse",{"name":a_name,"type":a_type,"desc":a_desc,
                    "icon":a_icon,"price":a_price,"unit":a_unit,"open":a_open,"featured":a_feat})
                if r.get("ok"): st.success(f"✅ 新增成功！ID：{r.get('id','')}"); clear_cache(); st.rerun()
                else: st.error(r.get("msg","新增失敗"))

# ════════════════════════════════════════════════════════════
#  PAGE 5：匯出報表
# ════════════════════════════════════════════════════════════
elif page == "📤  匯出報表":
    page_header("📤", "匯出報表", "下載訂單、付款明細 CSV 報表")

    c1,c2 = st.columns(2,gap="medium")

    with c1:
        section_title("訂單報表")
        res = get_orders()
        orders = res.get("data",[]) if res.get("ok") else []
        if orders:
            rows = [{"訂單編號":o.get("訂單編號",""),"報名時間":str(o.get("報名時間",""))[:16],
                     "姓名":o.get("姓名",""),"手機":o.get("手機",""),"Email":o.get("Email",""),
                     "課程":o.get("課程名稱",""),"應付金額":o.get("應付金額",""),
                     "付款方式":(o.get("payment") or {}).get("付款方式",""),
                     "帳號後5碼":(o.get("payment") or {}).get("帳號後5碼",""),
                     "實付金額":(o.get("payment") or {}).get("實付金額",""),
                     "核對狀態":(o.get("payment") or {}).get("核對狀態",""),
                     "訂單狀態":o.get("訂單狀態",""),"備註":o.get("備註","")} for o in orders]
            df_o = pd.DataFrame(rows)
            st.dataframe(df_o, height=280, use_container_width=True, hide_index=True)
            st.download_button("⬇ 下載訂單 CSV", df_o.to_csv(index=False,encoding="utf-8-sig").encode("utf-8-sig"),
                f"訂單_{datetime.now().strftime('%Y%m%d')}.csv","text/csv")
        else:
            st.info("尚無訂單資料")

    with c2:
        section_title("付款明細報表")
        res2 = get_payments()
        pays = res2.get("data",[]) if res2.get("ok") else []
        if pays:
            df_p = pd.DataFrame([{"付款ID":p.get("付款ID",""),"訂單編號":p.get("訂單編號",""),
                "付款時間":str(p.get("付款時間",""))[:16],"付款方式":p.get("付款方式",""),
                "帳號後5碼":p.get("帳號後5碼",""),"實付金額":p.get("實付金額",""),
                "核對狀態":p.get("核對狀態",""),"核對時間":str(p.get("核對時間",""))[:16],
                "核對備註":p.get("核對備註","")} for p in pays])
            st.dataframe(df_p, height=280, use_container_width=True, hide_index=True)
            st.download_button("⬇ 下載付款明細 CSV", df_p.to_csv(index=False,encoding="utf-8-sig").encode("utf-8-sig"),
                f"付款_{datetime.now().strftime('%Y%m%d')}.csv","text/csv")
        else:
            st.info("尚無付款記錄")

    st.markdown("---")
    section_title("月份統計摘要")
    res3 = get_dashboard()
    if res3.get("ok"):
        trend = res3["data"].get("trend",[])
        if trend:
            df_t = pd.DataFrame(trend)
            df_t.columns = ["月份","訂單數","已收款金額"]
            st.dataframe(df_t, use_container_width=True, hide_index=True)
            st.download_button("⬇ 下載月份統計 CSV", df_t.to_csv(index=False,encoding="utf-8-sig").encode("utf-8-sig"),
                f"月統計_{datetime.now().strftime('%Y%m%d')}.csv","text/csv")
