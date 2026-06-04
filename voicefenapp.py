"""
魏世芬聲音教練｜後台管理系統
Streamlit + Google Apps Script API
"""
import streamlit as st
import requests, json
from datetime import datetime, date
import pandas as pd

# ── 頁面設定 ──────────────────────────────────────────────────
st.set_page_config(
    page_title="魏世芬聲音教練｜管理後台",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 樣式注入 ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;500;600&family=Noto+Sans+TC:wght@300;400;500&display=swap');

/* 全域基底 */
html, body, [class*="css"] { font-family: 'Noto Sans TC', sans-serif; }

/* 隱藏 Streamlit 預設元素 */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #181818 !important;
    border-right: 1px solid rgba(201,168,76,0.15) !important;
}
section[data-testid="stSidebar"] .stRadio label {
    color: #8A7F70 !important;
    font-size: 0.88rem !important;
}
section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    color: #8A7F70 !important;
}

/* 黑金 metric 卡片 */
[data-testid="metric-container"] {
    background: #1E1E1E;
    border: 1px solid rgba(201,168,76,0.15);
    border-radius: 12px;
    padding: 18px 20px !important;
}
[data-testid="metric-container"] label { color: #8A7F70 !important; font-size: 0.72rem !important; letter-spacing: 0.1em; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #E2C26A !important; font-family: 'Noto Serif TC', serif !important; }
[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 0.75rem !important; }

/* 狀態徽章 */
.badge { display:inline-block; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-weight:600; }
.badge-green  { background:rgba(129,199,132,0.12); color:#A5D6A7; border:1px solid rgba(129,199,132,0.2); }
.badge-yellow { background:rgba(201,168,76,0.12);  color:#E2C26A; border:1px solid rgba(201,168,76,0.22); }
.badge-red    { background:rgba(192,57,43,0.12);   color:#EF9A9A; border:1px solid rgba(192,57,43,0.2); }
.badge-blue   { background:rgba(100,181,246,0.1);  color:#90CAF9; border:1px solid rgba(100,181,246,0.2); }

/* Dataframe 表格 */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* 表單區塊 */
[data-testid="stForm"] { background: #1A1A1A; border: 1px solid rgba(201,168,76,0.1); border-radius: 12px; padding: 16px; }

/* 按鈕 */
.stButton button {
    background: linear-gradient(135deg,#C9A84C,#E2C26A) !important;
    color: #0C0C0C !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
}
.stButton button:hover { opacity: 0.88 !important; }

/* 黃金分割線 */
hr { border-color: rgba(201,168,76,0.12) !important; }

/* 頁面標題 */
.page-title {
    font-family: 'Noto Serif TC', serif;
    font-size: 1.4rem; font-weight: 500;
    color: #F7F2E8;
    margin-bottom: 4px;
    display: flex; align-items: center; gap: 10px;
}
.page-title::before { content:''; width:4px; height:22px; background:#C9A84C; border-radius:2px; display:inline-block; }
.page-sub { font-size: 0.8rem; color: #555048; margin-bottom: 24px; }
</style>
""", unsafe_allow_html=True)

# ── 設定（從 Streamlit Secrets 讀取）─────────────────────────
GAS_URL    = st.secrets.get("GAS_URL", "")
ADMIN_TOKEN= st.secrets.get("ADMIN_TOKEN", "changeme")

# ── GAS API 呼叫 ──────────────────────────────────────────────
def api(action: str, payload: dict = None) -> dict:
    if not GAS_URL:
        return {"ok": False, "msg": "尚未設定 GAS_URL（請在 secrets.toml 設定）"}
    try:
        r = requests.post(GAS_URL, json={
            "action": action,
            "token":  ADMIN_TOKEN,
            "payload": payload or {}
        }, timeout=30)
        return r.json()
    except Exception as e:
        return {"ok": False, "msg": str(e)}

# ── 快取（60 秒）────────────────────────────────────────────────
@st.cache_data(ttl=60)
def get_dashboard():  return api("getDashboard")
@st.cache_data(ttl=30)
def get_orders(status=None, courseId=None, keyword=None):
    return api("getOrders", {"status": status, "courseId": courseId, "keyword": keyword})
@st.cache_data(ttl=30)
def get_courses():    return api("getCourses")
@st.cache_data(ttl=30)
def get_payments():   return api("getPayments")

def clear_cache():
    get_dashboard.clear(); get_orders.clear()
    get_courses.clear();   get_payments.clear()

# ── 狀態徽章 ─────────────────────────────────────────────────
STATUS_MAP = {
    "待付款": ("badge-red",    "⏳ 待付款"),
    "待對帳": ("badge-yellow", "🔄 待對帳"),
    "已付款": ("badge-green",  "✅ 已付款"),
    "已核對": ("badge-green",  "✅ 已核對"),
    "待核對": ("badge-yellow", "🔄 待核對"),
}

def badge(status):
    cls, label = STATUS_MAP.get(status, ("badge-blue", status))
    return f'<span class="badge {cls}">{label}</span>'

# ════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:24px 20px 20px; border-bottom:1px solid rgba(201,168,76,0.12); margin-bottom:8px;">
        <div style="font-size:1.8rem; filter:drop-shadow(0 0 8px rgba(201,168,76,0.5));">🎤</div>
        <div style="font-family:'Noto Serif TC',serif; font-size:1.15rem; color:#fff; margin-top:8px;">魏世芬聲音教練</div>
        <div style="font-size:0.72rem; color:#555048; margin-top:4px; letter-spacing:0.06em;">管理後台 · Admin</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "導覽",
        ["📊 收費總覽", "📋 訂單管理", "✅ 對帳核對", "🎓 課程設定", "📤 匯出報表"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    if st.button("🔄 重新整理資料"):
        clear_cache(); st.rerun()

    st.markdown("""
    <div style="padding:16px 0 0; font-size:0.7rem; color:#3A3530; letter-spacing:0.06em;">
        voicefen.com · Vocal Coach 13年
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  PAGE 1：收費總覽 Dashboard
# ════════════════════════════════════════════════════════════
if page == "📊 收費總覽":
    st.markdown('<div class="page-title">📊 收費總覽</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">即時掌握課程收費狀況</div>', unsafe_allow_html=True)

    res = get_dashboard()
    if not res.get("ok"):
        st.error(res.get("msg", "資料載入失敗"))
        st.info("💡 請先在 `.streamlit/secrets.toml` 設定 GAS_URL 與 ADMIN_TOKEN")
        st.stop()

    d = res["data"]

    # KPI 列
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("本月訂單數",   d.get("monthOrders", 0),   help="本月新增報名數")
    c2.metric("累計已收款",  f"${d.get('totalRevenue',0):,.0f}", help="所有已核對付款總額")
    c3.metric("待收款金額",  f"${d.get('pendingAmount',0):,.0f}", delta=f"-{d.get('pendingCount',0)} 筆未付", delta_color="inverse")
    c4.metric("對帳完成率",  f"{d.get('verifyRate',0)}%", help="已核對 / 總訂單數")

    st.markdown("---")

    col_chart, col_unpaid = st.columns([3, 2])

    with col_chart:
        st.markdown("**📈 近 6 個月收費趨勢**")
        trend = d.get("trend", [])
        if trend:
            df_trend = pd.DataFrame(trend)
            df_trend.columns = ["月份", "訂單數", "已收款"]
            df_trend = df_trend.set_index("月份")
            st.bar_chart(df_trend[["已收款"]], color="#C9A84C", height=220)
        else:
            st.caption("尚無資料")

    with col_unpaid:
        st.markdown("**⚠️ 未完成對帳訂單**")
        res2 = get_orders(status="待付款")
        res3 = get_orders(status="待對帳")
        pending = []
        for r in [res2, res3]:
            if r.get("ok"): pending.extend(r.get("data", []))

        if pending:
            for o in pending[:6]:
                pay = o.get("payment")
                st.markdown(f"""
                <div style="background:#1E1E1E;border:1px solid rgba(201,168,76,.12);border-radius:8px;padding:10px 14px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">
                  <div>
                    <div style="font-size:.85rem;color:#F7F2E8;">{o.get('姓名','')}</div>
                    <div style="font-size:.72rem;color:#555048;">{o.get('課程名稱','')}</div>
                  </div>
                  <div style="text-align:right;">
                    <div style="font-size:.9rem;color:#EF9A9A;">NT${int(o.get('應付金額',0)):,}</div>
                    {badge(o.get('訂單狀態',''))}
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ 所有訂單對帳完成！")

    st.markdown("---")
    st.markdown("**🗂️ 課程報名分布**")
    bycourse = d.get("bycourse", [])
    if bycourse:
        df_bc = pd.DataFrame(bycourse)[["name","count"]]
        df_bc.columns = ["課程名稱","報名人數"]
        st.bar_chart(df_bc.set_index("課程名稱"), color="#C9A84C", height=180)

# ════════════════════════════════════════════════════════════
#  PAGE 2：訂單管理
# ════════════════════════════════════════════════════════════
elif page == "📋 訂單管理":
    st.markdown('<div class="page-title">📋 訂單管理</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">查看所有報名記錄、手動更新訂單狀態</div>', unsafe_allow_html=True)

    # 篩選列
    fc1, fc2, fc3 = st.columns([2,2,3])
    with fc1:
        f_status = st.selectbox("訂單狀態", ["全部","待付款","待對帳","已付款"], index=0)
    with fc2:
        res_c = get_courses()
        course_opts = {"全部課程": None}
        if res_c.get("ok"):
            for c in res_c.get("data", []):
                course_opts[c.get("課程名稱","")] = c.get("課程ID")
        f_course = st.selectbox("課程", list(course_opts.keys()))
    with fc3:
        f_kw = st.text_input("搜尋（姓名 / 手機 / 訂單編號）", placeholder="輸入關鍵字...")

    status_val = None if f_status == "全部" else f_status
    course_val = course_opts.get(f_course)
    kw_val     = f_kw.strip() or None

    res = get_orders(status=status_val, courseId=course_val, keyword=kw_val)
    orders = res.get("data", []) if res.get("ok") else []

    st.caption(f"共 {len(orders)} 筆")

    if orders:
        # 製作顯示用 DataFrame
        rows = []
        for o in orders:
            pay = o.get("payment")
            rows.append({
                "訂單編號":   o.get("訂單編號",""),
                "報名時間":   str(o.get("報名時間",""))[:16],
                "姓名":       o.get("姓名",""),
                "手機":       o.get("手機",""),
                "課程":       o.get("課程名稱",""),
                "應付":       f'${int(o.get("應付金額",0)):,}',
                "付款方式":   pay["付款方式"] if pay else "—",
                "帳號後5碼":  pay["帳號後5碼"] if pay else "—",
                "狀態":       o.get("訂單狀態",""),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True,
                     column_config={
                         "應付": st.column_config.TextColumn(width="small"),
                         "帳號後5碼": st.column_config.TextColumn(width="small"),
                     })

        st.markdown("---")
        st.markdown("**✏️ 手動更新訂單**")
        with st.form("update_order"):
            u1, u2, u3 = st.columns([2,2,3])
            with u1: upd_id = st.text_input("訂單編號")
            with u2: upd_st = st.selectbox("更新狀態", ["待付款","待對帳","已付款"])
            with u3: upd_note = st.text_input("備註")
            if st.form_submit_button("更新訂單"):
                if upd_id:
                    r = api("updateOrder", {"orderId": upd_id, "status": upd_st, "note": upd_note})
                    if r.get("ok"):
                        st.success("✅ 訂單已更新"); clear_cache(); st.rerun()
                    else:
                        st.error(r.get("msg","更新失敗"))
    else:
        st.info("查無訂單記錄")

# ════════════════════════════════════════════════════════════
#  PAGE 3：對帳核對
# ════════════════════════════════════════════════════════════
elif page == "✅ 對帳核對":
    st.markdown('<div class="page-title">✅ 對帳核對</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">核對學員付款資料，確認收款完成</div>', unsafe_allow_html=True)

    res = get_payments()
    pays = res.get("data", []) if res.get("ok") else []

    # 待核對清單
    pending_pays = [p for p in pays if p.get("核對狀態") != "已核對"]
    done_pays    = [p for p in pays if p.get("核對狀態") == "已核對"]

    tab1, tab2 = st.tabs([f"⏳ 待核對（{len(pending_pays)}）", f"✅ 已核對（{len(done_pays)}）"])

    with tab1:
        if not pending_pays:
            st.success("🎉 目前沒有待核對的付款記錄！")
        else:
            res_o = get_orders()
            orders_map = {}
            if res_o.get("ok"):
                for o in res_o.get("data", []):
                    orders_map[o["訂單編號"]] = o

            for p in pending_pays:
                oid = p.get("訂單編號","")
                o   = orders_map.get(oid, {})
                exp = o.get("應付金額", 0)
                act = p.get("實付金額", 0)
                match_ok = int(exp) == int(act) if exp and act else False

                with st.expander(f"📌 {oid} ｜ {o.get('姓名','')} ｜ {p.get('付款方式','')} ｜ ${int(act):,}"):
                    pc1, pc2 = st.columns(2)
                    with pc1:
                        st.markdown(f"**學員**：{o.get('姓名','')}")
                        st.markdown(f"**課程**：{o.get('課程名稱','')}")
                        st.markdown(f"**手機**：{o.get('手機','')}")
                        st.markdown(f"**報名時間**：{str(o.get('報名時間',''))[:16]}")
                    with pc2:
                        st.markdown(f"**付款方式**：{p.get('付款方式','')}")
                        st.markdown(f"**帳號後5碼**：`{p.get('帳號後5碼','—')}`")
                        st.markdown(f"**應付金額**：NT${int(exp):,}" if exp else "**應付金額**：—")
                        st.markdown(f"**實付金額**：NT${int(act):,}" if act else "**實付金額**：—")
                        if match_ok:
                            st.success("✅ 金額吻合")
                        else:
                            st.warning(f"⚠️ 金額差異 ${abs(int(exp)-int(act)):,}")

                    st.markdown(f"**學員備註**：{p.get('備註','—')}")

                    with st.form(f"verify_{p.get('付款ID','')}"):
                        v1, v2 = st.columns([2,3])
                        with v1: v_status = st.selectbox("核對結果", ["已核對","異常"])
                        with v2: v_note   = st.text_input("核對備註", placeholder="金額正確，對帳完成")
                        if st.form_submit_button("✅ 確認核對"):
                            r = api("verifyPayment", {
                                "payId":  p.get("付款ID",""),
                                "status": v_status,
                                "note":   v_note,
                            })
                            if r.get("ok"):
                                st.success("核對完成！"); clear_cache(); st.rerun()
                            else:
                                st.error(r.get("msg","核對失敗"))

    with tab2:
        if done_pays:
            rows = [{
                "付款ID":   p.get("付款ID",""),
                "訂單編號": p.get("訂單編號",""),
                "付款時間": str(p.get("付款時間",""))[:16],
                "付款方式": p.get("付款方式",""),
                "帳號後5碼":p.get("帳號後5碼",""),
                "實付金額": f'${int(p.get("實付金額",0)):,}',
                "核對時間": str(p.get("核對時間",""))[:16],
                "核對備註": p.get("核對備註",""),
            } for p in done_pays]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("尚無已核對記錄")

# ════════════════════════════════════════════════════════════
#  PAGE 4：課程設定
# ════════════════════════════════════════════════════════════
elif page == "🎓 課程設定":
    st.markdown('<div class="page-title">🎓 課程設定</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">新增、編輯、停用課程，前台即時更新</div>', unsafe_allow_html=True)

    res = get_courses()
    courses = res.get("data", []) if res.get("ok") else []

    st.markdown("**📋 目前課程**")
    if courses:
        for c in courses:
            is_open = c.get("是否開放") is True
            status_badge = '🟢 開放中' if is_open else '🔴 已停用'
            with st.expander(f"{c.get('圖示','')} {c.get('課程名稱','')} ｜ ${int(c.get('單價',0)):,} / {c.get('計費單位','')} ｜ {status_badge}"):
                e1, e2 = st.columns(2)
                with e1:
                    st.markdown(f"**課程ID**：`{c.get('課程ID','')}`")
                    st.markdown(f"**類型**：{c.get('課程類型','')}")
                    st.markdown(f"**說明**：{c.get('課程說明','')}")
                with e2:
                    st.markdown(f"**單價**：NT${int(c.get('單價',0)):,}")
                    st.markdown(f"**計費單位**：{c.get('計費單位','')}")
                    st.markdown(f"**精選**：{'⭐ 是' if c.get('精選標記') is True else '否'}")

                with st.form(f"edit_c_{c.get('課程ID','')}"):
                    st.markdown("##### 編輯課程")
                    en1, en2 = st.columns(2)
                    with en1:
                        e_name = st.text_input("課程名稱", value=c.get("課程名稱",""))
                        e_type = st.text_input("英文類型", value=c.get("課程類型",""))
                        e_icon = st.text_input("圖示（Emoji）", value=c.get("圖示",""))
                    with en2:
                        e_price= st.number_input("單價", value=int(c.get("單價",0)), step=100)
                        e_unit = st.text_input("計費單位（堂/期）", value=c.get("計費單位",""))
                        e_open = st.checkbox("開放報名", value=is_open)
                        e_feat = st.checkbox("標記為精選", value=c.get("精選標記") is True)
                    e_desc = st.text_area("課程說明", value=c.get("課程說明",""), height=80)

                    ec1, ec2 = st.columns(2)
                    with ec1:
                        if st.form_submit_button("💾 儲存變更"):
                            r = api("saveCourse", {
                                "id": c.get("課程ID"), "name": e_name, "type": e_type,
                                "desc": e_desc, "icon": e_icon, "price": e_price,
                                "unit": e_unit, "open": e_open, "featured": e_feat
                            })
                            if r.get("ok"):
                                st.success("✅ 已儲存"); clear_cache(); st.rerun()
                            else:
                                st.error(r.get("msg","儲存失敗"))
                    with ec2:
                        if st.form_submit_button("🗑️ 刪除課程", type="secondary"):
                            r = api("deleteCourse", {"id": c.get("課程ID")})
                            if r.get("ok"):
                                st.success("已刪除"); clear_cache(); st.rerun()
                            else:
                                st.error(r.get("msg","刪除失敗"))
    else:
        st.info("尚無課程，請新增第一堂課程")

    st.markdown("---")
    st.markdown("**➕ 新增課程**")
    with st.form("add_course"):
        a1, a2 = st.columns(2)
        with a1:
            a_name = st.text_input("課程名稱 *", placeholder="例：一對一私人課程")
            a_type = st.text_input("英文類型 *", placeholder="例：One-on-One")
            a_icon = st.text_input("圖示（Emoji）", placeholder="🎤", value="🎤")
        with a2:
            a_price= st.number_input("單價 *", min_value=0, step=100, value=3000)
            a_unit = st.text_input("計費單位 *", placeholder="堂 或 期", value="堂")
            a_open = st.checkbox("立即開放報名", value=True)
            a_feat = st.checkbox("標記為精選", value=False)
        a_desc = st.text_area("課程說明 *", placeholder="描述課程內容與特色...", height=80)

        if st.form_submit_button("➕ 新增課程"):
            if not all([a_name, a_type, a_price, a_unit, a_desc]):
                st.error("請填寫所有必填欄位（*）")
            else:
                r = api("saveCourse", {
                    "name": a_name, "type": a_type, "desc": a_desc,
                    "icon": a_icon, "price": a_price, "unit": a_unit,
                    "open": a_open, "featured": a_feat
                })
                if r.get("ok"):
                    st.success(f"✅ 課程已新增！ID：{r.get('id','')}"); clear_cache(); st.rerun()
                else:
                    st.error(r.get("msg","新增失敗"))

# ════════════════════════════════════════════════════════════
#  PAGE 5：匯出報表
# ════════════════════════════════════════════════════════════
elif page == "📤 匯出報表":
    st.markdown('<div class="page-title">📤 匯出報表</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">下載訂單、付款明細 CSV 報表</div>', unsafe_allow_html=True)

    ec1, ec2 = st.columns(2)

    with ec1:
        st.markdown("**📋 訂單報表**")
        res = get_orders()
        orders = res.get("data", []) if res.get("ok") else []
        if orders:
            rows = []
            for o in orders:
                pay = o.get("payment") or {}
                rows.append({
                    "訂單編號":   o.get("訂單編號",""),
                    "報名時間":   str(o.get("報名時間",""))[:16],
                    "姓名":       o.get("姓名",""),
                    "手機":       o.get("手機",""),
                    "Email":      o.get("Email",""),
                    "課程名稱":   o.get("課程名稱",""),
                    "應付金額":   o.get("應付金額",""),
                    "付款方式":   pay.get("付款方式",""),
                    "帳號後5碼":  pay.get("帳號後5碼",""),
                    "實付金額":   pay.get("實付金額",""),
                    "核對狀態":   pay.get("核對狀態",""),
                    "訂單狀態":   o.get("訂單狀態",""),
                    "備註":       o.get("備註",""),
                })
            df_o = pd.DataFrame(rows)
            st.dataframe(df_o, height=240, use_container_width=True, hide_index=True)
            csv = df_o.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                "⬇ 下載訂單報表 CSV",
                data=csv.encode("utf-8-sig"),
                file_name=f"訂單報表_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("尚無訂單資料")

    with ec2:
        st.markdown("**💳 付款明細報表**")
        res2 = get_payments()
        pays = res2.get("data", []) if res2.get("ok") else []
        if pays:
            df_p = pd.DataFrame([{
                "付款ID":   p.get("付款ID",""),
                "訂單編號": p.get("訂單編號",""),
                "付款時間": str(p.get("付款時間",""))[:16],
                "付款方式": p.get("付款方式",""),
                "帳號後5碼":p.get("帳號後5碼",""),
                "實付金額": p.get("實付金額",""),
                "核對狀態": p.get("核對狀態",""),
                "核對時間": str(p.get("核對時間",""))[:16],
                "核對備註": p.get("核對備註",""),
            } for p in pays])
            st.dataframe(df_p, height=240, use_container_width=True, hide_index=True)
            csv2 = df_p.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                "⬇ 下載付款明細 CSV",
                data=csv2.encode("utf-8-sig"),
                file_name=f"付款明細_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("尚無付款記錄")

    st.markdown("---")
    st.markdown("**📊 月份統計摘要**")
    res3 = get_dashboard()
    if res3.get("ok"):
        trend = res3["data"].get("trend", [])
        if trend:
            df_t = pd.DataFrame(trend)
            df_t.columns = ["月份", "訂單數", "已收款金額"]
            st.dataframe(df_t, use_container_width=True, hide_index=True)
            csv3 = df_t.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                "⬇ 下載月份統計 CSV",
                data=csv3.encode("utf-8-sig"),
                file_name=f"月份統計_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
