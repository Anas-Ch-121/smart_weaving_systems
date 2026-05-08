"""
Smart Weaving Management System
Streamlit Frontend
Connects to Flask backend at http://localhost:5000
"""

import streamlit as st
import requests
import pandas as pd
from datetime import date

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
API = "http://127.0.0.1:5000"

st.set_page_config(
    page_title="Smart Weaving",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS  — Industrial dark theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
}

/* Dark background */
.stApp { background-color: #0d0f14; color: #e0e4ef; }
.stSidebar { background-color: #131720 !important; border-right: 1px solid #2a3050; }

/* Header banner */
.top-banner {
    background: linear-gradient(135deg, #1a1f35 0%, #0d1428 100%);
    border: 1px solid #2a3a6e;
    border-radius: 8px;
    padding: 18px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.top-banner h1 { font-size: 2rem; font-weight: 700; color: #4f8ef7; margin: 0; letter-spacing: 2px; }
.top-banner p { color: #7a8ab5; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; margin: 0; }

/* Stat cards */
.stat-card {
    background: #131720;
    border: 1px solid #2a3050;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    margin-bottom: 12px;
}
.stat-card .val { font-size: 2rem; font-weight: 700; color: #4f8ef7; font-family: 'Share Tech Mono', monospace; }
.stat-card .lbl { font-size: 0.85rem; color: #7a8ab5; text-transform: uppercase; letter-spacing: 1px; }
.stat-card.green .val { color: #3ecf8e; }
.stat-card.red .val   { color: #f75f5f; }

/* Section headers */
.sec-header {
    font-size: 1.3rem;
    font-weight: 700;
    color: #4f8ef7;
    letter-spacing: 2px;
    text-transform: uppercase;
    border-bottom: 1px solid #2a3050;
    padding-bottom: 6px;
    margin-bottom: 16px;
}

/* Role badge */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge.admin    { background: #1a3a6e; color: #4f8ef7; border: 1px solid #4f8ef7; }
.badge.operator { background: #1a3a2e; color: #3ecf8e; border: 1px solid #3ecf8e; }

/* Dataframe tweaks */
.stDataFrame { background: #131720 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def api_get(path):
    try:
        r = requests.get(f"{API}{path}", timeout=8)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError as e:
        return None, f"❌ Connection Error: {str(e)}"
    except requests.exceptions.Timeout:
        return None, "❌ Timeout — backend slow hai"
    except Exception as e:
        return None, f"❌ Error: {type(e).__name__}: {str(e)}"

def api_post(path, payload):
    try:
        r = requests.post(f"{API}{path}", json=payload, timeout=8)
        return r.json(), r.status_code
    except requests.exceptions.ConnectionError as e:
        return {"error": f"Connection Error: {str(e)}"}, 503
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)}"}, 500

def show_error(msg):
    st.error(msg)


def show_success(msg):
    st.success(msg)


# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = {}


# ═══════════════════════════════════════════
# LOGIN PAGE
# ═══════════════════════════════════════════
def login_page():
    st.markdown("""
    <div style="max-width:420px; margin: 80px auto;">
        <div style="text-align:center; margin-bottom:32px;">
            <div style="font-size:3rem;">🧵</div>
            <h1 style="color:#4f8ef7; font-family:Rajdhani; letter-spacing:3px; font-size:2rem; margin:0;">SMART WEAVING</h1>
            <p style="color:#7a8ab5; font-family:'Share Tech Mono'; font-size:0.8rem;">MANAGEMENT SYSTEM v1.0</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown('<div class="sec-header">🔐 LOGIN</div>', unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="admin@weaving.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")

            if st.button("LOGIN →", use_container_width=True, type="primary"):
                if not email or not password:
                    show_error("Email aur password dono bharo.")
                    return

                resp, code = api_post("/login", {"email": email, "password": password})

                if code == 200 and "user" in resp:
                    st.session_state.logged_in = True
                    st.session_state.user = resp["user"]
                    st.rerun()
                else:
                    show_error(resp.get("error", "Login failed"))


# ═══════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════
def dashboard():
    st.markdown('<div class="sec-header">📊 DASHBOARD</div>', unsafe_allow_html=True)

    # Financial summary
    fin, err = api_get("/financial/summary")
    if err:
        show_error(err)
        fin = {"total_income": 0, "total_expense": 0, "net_profit": 0}

    # Inventory count
    inv, _ = api_get("/inventory")
    inv_count = len(inv) if inv else 0

    # Looms count
    looms, _ = api_get("/looms")
    loom_count = len(looms) if looms else 0

    # Production count
    prod, _ = api_get("/production")
    prod_count = len(prod) if prod else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="stat-card green">
            <div class="val">PKR {fin['total_income']:,.0f}</div>
            <div class="lbl">Total Income</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="stat-card red">
            <div class="val">PKR {fin['total_expense']:,.0f}</div>
            <div class="lbl">Total Expense</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        profit_class = "green" if fin['net_profit'] >= 0 else "red"
        st.markdown(f"""<div class="stat-card {profit_class}">
            <div class="val">PKR {fin['net_profit']:,.0f}</div>
            <div class="lbl">Net Profit</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="stat-card">
            <div class="val">{loom_count}</div>
            <div class="lbl">Active Looms</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    with c5:
        st.markdown(f"""<div class="stat-card">
            <div class="val">{inv_count}</div>
            <div class="lbl">Inventory Items</div>
        </div>""", unsafe_allow_html=True)
    with c6:
        st.markdown(f"""<div class="stat-card">
            <div class="val">{prod_count}</div>
            <div class="lbl">Production Records</div>
        </div>""", unsafe_allow_html=True)

    # Recent financial records
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-header">💰 RECENT TRANSACTIONS</div>', unsafe_allow_html=True)
    records, err = api_get("/financial/records")
    if records:
        df = pd.DataFrame(records[:10])
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
    elif err:
        show_error(err)


# ═══════════════════════════════════════════
# INVENTORY
# ═══════════════════════════════════════════
def inventory_page():
    st.markdown('<div class="sec-header">📦 INVENTORY — RAW MATERIALS</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 View Stock", "➕ Add Material", "🔄 Restock"])

    with tab1:
        data, err = api_get("/inventory")
        if err:
            show_error(err)
        elif data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Koi inventory record nahi mila.")

    with tab2:
        st.markdown("#### New Raw Material Add Karo")
        with st.form("add_material"):
            name     = st.text_input("Material Name", placeholder="e.g., Cotton Thread")
            qty      = st.number_input("Initial Stock Quantity", min_value=0.0, step=0.5)
            unit     = st.selectbox("Unit", ["kg", "meters", "rolls", "pieces", "liters"])
            cost     = st.number_input("Cost Per Unit (PKR)", min_value=0.0, step=1.0)
            submitted = st.form_submit_button("Add Material ✅", type="primary")

            if submitted:
                if not name:
                    show_error("Material name required hai.")
                else:
                    res, code = api_post("/inventory/add", {
                        "resource_name":  name,
                        "stock_quantity": qty,
                        "unit":           unit,
                        "cost_per_unit":  cost
                    })
                    if code == 200:
                        show_success(res.get("message", "Added!"))
                    else:
                        show_error(res.get("error", "Failed"))

    with tab3:
        st.markdown("#### Existing Stock Restock Karo")
        inv, _ = api_get("/inventory")
        if inv:
            options = {f"{i.get('resource_name', 'Unknown')} (ID: {i['resource_id']})": i["resource_id"] for i in inv}
            selected = st.selectbox("Material Select Karo", list(options.keys()))
            qty_add  = st.number_input("Quantity to Add", min_value=0.1, step=0.5)

            if st.button("Restock ✅", type="primary"):
                res, code = api_post("/inventory/restock", {
                    "resource_id": options[selected],
                    "quantity":    qty_add
                })
                if code == 200:
                    show_success(res.get("message", "Restocked!"))
                else:
                    show_error(res.get("error", "Failed"))
        else:
            st.info("Pehle koi material add karo.")


# ═══════════════════════════════════════════
# LOOMS
# ═══════════════════════════════════════════
def looms_page():
    st.markdown('<div class="sec-header">⚙️ LOOM MANAGEMENT</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 View Looms", "➕ Add Loom", "🔧 Update Status"])

    with tab1:
        data, err = api_get("/looms")
        if err:
            show_error(err)
        elif data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Koi loom record nahi.")

    with tab2:
        st.markdown("#### New Loom Add Karo")
        with st.form("add_loom"):
            name   = st.text_input("Loom Name", placeholder="e.g., Loom-A1")
            status = st.selectbox("Initial Status", ["active", "idle", "maintenance"])
            mdate  = st.date_input("Next Maintenance Date", value=date.today())
            submitted = st.form_submit_button("Add Loom ✅", type="primary")

            if submitted:
                if not name:
                    show_error("Loom name required.")
                else:
                    res, code = api_post("/looms/add", {
                        "resource_name":    name,
                        "loom_status":      status,
                        "maintenance_date": str(mdate)
                    })
                    if code == 200:
                        show_success(res.get("message", "Added!"))
                    else:
                        show_error(res.get("error", "Failed"))

    with tab3:
        st.markdown("#### Loom Status Update Karo")
        looms, _ = api_get("/looms")
        if looms:
            options = {f"{l.get('loom_name', l.get('resource_name', 'Loom'))} (ID: {l['resource_id']})": l["resource_id"] for l in looms}
            selected = st.selectbox("Loom Select Karo", list(options.keys()))
            new_status = st.selectbox("New Status", ["active", "idle", "maintenance"])

            if st.button("Update Status ✅", type="primary"):
                res, code = api_post("/looms/update-status", {
                    "resource_id": options[selected],
                    "status":      new_status
                })
                if code == 200:
                    show_success(res.get("message", "Updated!"))
                else:
                    show_error(res.get("error", "Failed"))
        else:
            st.info("Pehle koi loom add karo.")


# ═══════════════════════════════════════════
# PRODUCTION
# ═══════════════════════════════════════════
def production_page():
    st.markdown('<div class="sec-header">🏭 PRODUCTION LOG</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋 History", "➕ Log Production"])

    with tab1:
        data, err = api_get("/production")
        if err:
            show_error(err)
        elif data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Koi production record nahi.")

    with tab2:
        st.markdown("#### New Production Entry")
        operators, _ = api_get("/operators")
        inv, _       = api_get("/inventory")

        if not operators:
            show_error("Koi operator nahi mila. Pehle operators add karo via Supabase.")
            return

        op_options = {}
        for o in operators:
            name = o.get("app_user", {}).get("full_name", f"Operator {o['user_id']}") if isinstance(o.get("app_user"), dict) else f"Operator {o['user_id']}"
            op_options[name] = o["user_id"]

        with st.form("add_production"):
            op_sel   = st.selectbox("Operator", list(op_options.keys()))
            prod_date = st.date_input("Production Date", value=date.today())
            output   = st.number_input("Total Output (meters/units)", min_value=0.0, step=0.5)
            notes    = st.text_area("Notes", placeholder="Optional...")

            st.markdown("#### Raw Materials Used")
            details = []
            if inv:
                mat_options = {f"{i.get('resource_name','Item')} (ID:{i['resource_id']})": i["resource_id"] for i in inv}
                num_materials = st.number_input("Kitne materials use hue?", min_value=1, max_value=10, step=1, value=1)

                for n in range(int(num_materials)):
                    c1, c2 = st.columns(2)
                    with c1:
                        mat = st.selectbox(f"Material {n+1}", list(mat_options.keys()), key=f"mat_{n}")
                    with c2:
                        qty = st.number_input(f"Qty Used {n+1}", min_value=0.0, step=0.1, key=f"qty_{n}")
                    details.append({"resource_id": mat_options[mat], "quantity_used": qty})

            submitted = st.form_submit_button("Log Production ✅", type="primary")

            if submitted:
                res, code = api_post("/production/add", {
                    "operator_id":     op_options[op_sel],
                    "production_date": str(prod_date),
                    "total_output":    output,
                    "notes":           notes,
                    "details":         details
                })
                if code == 200:
                    show_success(res.get("message", "Production logged!"))
                else:
                    show_error(res.get("error", "Failed"))


# ═══════════════════════════════════════════
# FINANCIAL
# ═══════════════════════════════════════════
def financial_page():
    st.markdown('<div class="sec-header">💰 FINANCIAL RECORDS</div>', unsafe_allow_html=True)

    # Summary cards
    fin, err = api_get("/financial/summary")
    if fin:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div class="stat-card green">
                <div class="val">PKR {fin['total_income']:,.0f}</div>
                <div class="lbl">Total Income</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="stat-card red">
                <div class="val">PKR {fin['total_expense']:,.0f}</div>
                <div class="lbl">Total Expense</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            pc = "green" if fin['net_profit'] >= 0 else "red"
            st.markdown(f"""<div class="stat-card {pc}">
                <div class="val">PKR {fin['net_profit']:,.0f}</div>
                <div class="lbl">Net Profit</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 All Records", "➕ Add Record"])

    with tab1:
        data, err = api_get("/financial/records")
        if err:
            show_error(err)
        elif data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Koi financial record nahi.")

    with tab2:
        st.markdown("#### New Financial Entry")
        prod, _ = api_get("/production")

        with st.form("add_financial"):
            prod_id  = st.number_input("Production ID (optional, 0 for none)", min_value=0, step=1)
            amount   = st.number_input("Amount (PKR)", min_value=0.0, step=100.0)
            tx_type  = st.selectbox("Transaction Type", ["income", "expense"])
            tx_date  = st.date_input("Transaction Date", value=date.today())
            desc     = st.text_area("Description", placeholder="e.g., Cotton purchase...")
            submitted = st.form_submit_button("Save Record ✅", type="primary")

            if submitted:
                payload = {
                    "production_id":    prod_id if prod_id > 0 else None,
                    "amount":           amount,
                    "transaction_type": tx_type,
                    "transaction_date": str(tx_date),
                    "description":      desc
                }
                res, code = api_post("/financial/add", payload)
                if code == 200:
                    show_success(res.get("message", "Saved!"))
                else:
                    show_error(res.get("error", "Failed"))


# ═══════════════════════════════════════════
# OPERATORS
# ═══════════════════════════════════════════
def operators_page():
    st.markdown('<div class="sec-header">👷 OPERATORS</div>', unsafe_allow_html=True)

    data, err = api_get("/operators")
    if err:
        show_error(err)
    elif data:
        # Flatten nested app_user
        rows = []
        for o in data:
            user_info = o.get("app_user") or {}
            if isinstance(user_info, dict):
                rows.append({
                    "user_id":   o["user_id"],
                    "full_name": user_info.get("full_name", "—"),
                    "email":     user_info.get("email", "—"),
                    "shift":     o.get("shift", "—"),
                    "expertise": o.get("expertise", "—"),
                })
            else:
                rows.append(o)
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Koi operator record nahi. Supabase mein directly add karo.")

    st.markdown("""
    > 💡 **Tip:** Operators add karne ke liye pehle Supabase mein `app_user` table mein user add karo, 
    phir `operator` table mein us user ka `user_id` dal do.
    """)


# ═══════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════
def main():
    if not st.session_state.logged_in:
        login_page()
        return

    user = st.session_state.user
    role = user.get("role", "operator")

    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 0 24px;">
            <div style="font-size:1.6rem; font-weight:700; color:#4f8ef7; letter-spacing:2px;">🧵 WEAVING</div>
            <div style="font-size:0.75rem; color:#7a8ab5; font-family:'Share Tech Mono';">SMART MANAGEMENT</div>
        </div>
        <div style="margin-bottom:20px;">
            <div style="color:#e0e4ef; font-weight:600;">{user.get('full_name', 'User')}</div>
            <span class="badge {'admin' if role == 'admin' else 'operator'}">{role.upper()}</span>
        </div>
        """, unsafe_allow_html=True)

        pages = ["📊 Dashboard", "📦 Inventory", "⚙️ Looms", "🏭 Production", "💰 Financial"]
        if role == "admin":
            pages.append("👷 Operators")

        page = st.radio("Navigation", pages, label_visibility="collapsed")

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = {}
            st.rerun()

    # Banner
    st.markdown(f"""
    <div class="top-banner">
        <div>🧵</div>
        <div>
            <h1>SMART WEAVING</h1>
            <p>MANAGEMENT SYSTEM — {role.upper()} PANEL</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Route
    if "Dashboard"   in page: dashboard()
    elif "Inventory" in page: inventory_page()
    elif "Looms"     in page: looms_page()
    elif "Production" in page: production_page()
    elif "Financial" in page: financial_page()
    elif "Operators" in page: operators_page()


if __name__ == "__main__":
    main()
