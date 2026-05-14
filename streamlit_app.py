"""
Smart Weaving Management System
Streamlit Frontend
Connects to Flask backend at http://localhost:5000
"""

import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client

# ─────────────────────────────────────────────
# SUPABASE CONFIG
# ─────────────────────────────────────────────
# Using st.secrets for cloud deployment
try:
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    # Fallback for local testing if secrets aren't set
    URL = "https://qeiqpxmnkmbnqfubkpaq.supabase.co"
    KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFlaXFweG1ua21ibnFmdWJrcGFxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgyMTU5MDMsImV4cCI6MjA5Mzc5MTkwM30.qNVnjOtxJ-d-Gvwy_wQ_nA2wzCYTarusawRLVQaAYH4"

sb: Client = create_client(URL, KEY)

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
# HELPERS (Supabase Direct)
# ─────────────────────────────────────────────
def show_error(msg):
    st.error(msg)

def show_success(msg):
    st.success(msg)

def get_financial_summary():
    try:
        res = sb.table("financial_record").select("amount, transaction_type").execute()
        income  = sum(r["amount"] for r in res.data if r["transaction_type"] == "income")
        expense = sum(r["amount"] for r in res.data if r["transaction_type"] == "expense")
        return {
            "total_income":  income,
            "total_expense": expense,
            "net_profit":    income - expense
        }, None
    except Exception as e:
        return None, str(e)


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

                try:
                    res = sb.table("app_user").select("*").eq("email", email).eq("password", password).execute()
                    if res.data:
                        user = res.data[0]
                        is_admin = sb.table("admin").select("user_id").eq("user_id", user["user_id"]).execute()
                        user["role"] = "admin" if is_admin.data else "operator"
                        
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.rerun()
                    else:
                        show_error("Invalid email or password")
                except Exception as e:
                    show_error(f"Login error: {str(e)}")


# ═══════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════
def dashboard():
    st.markdown('<div class="sec-header">📊 DASHBOARD</div>', unsafe_allow_html=True)

    # Financial summary
    fin, err = get_financial_summary()
    if err:
        show_error(f"Financial summary error: {err}")
        fin = {"total_income": 0, "total_expense": 0, "net_profit": 0}

    # Inventory count
    try:
        inv_res = sb.table("v_inventory").select("*").execute()
        inv_count = len(inv_res.data) if inv_res.data else 0
    except: inv_count = 0

    # Looms count
    try:
        looms_res = sb.table("v_loom_status").select("*").execute()
        loom_count = len(looms_res.data) if looms_res.data else 0
    except: loom_count = 0

    # Production count
    try:
        prod_res = sb.table("v_production_history").select("*").execute()
        prod_count = len(prod_res.data) if prod_res.data else 0
    except: prod_count = 0

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
    try:
        records_res = sb.table("financial_record").select("*").order("transaction_date", desc=True).limit(10).execute()
        if records_res.data:
            df = pd.DataFrame(records_res.data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No records found.")
    except Exception as e:
        show_error(f"Transactions error: {str(e)}")


# ═══════════════════════════════════════════
# INVENTORY
# ═══════════════════════════════════════════
def inventory_page():
    st.markdown('<div class="sec-header">📦 INVENTORY — RAW MATERIALS</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 View Stock", "➕ Add Material", "🔄 Restock", "🗑️ Delete"])

    with tab1:
        try:
            data_res = sb.table("v_inventory").select("*").execute()
            if data_res.data:
                df = pd.DataFrame(data_res.data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Koi inventory record nahi mila.")
        except Exception as e:
            show_error(f"Inventory fetch error: {str(e)}")

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
                    try:
                        r = sb.table("resource").insert({
                            "resource_name": name,
                            "resource_type": "raw_material"
                        }).execute()
                        rid = r.data[0]["resource_id"]
                        sb.table("raw_material").insert({
                            "resource_id":    rid,
                            "stock_quantity": float(qty),
                            "unit":           unit,
                            "cost_per_unit":  float(cost)
                        }).execute()
                        show_success(f"Raw material '{name}' added ✅")
                    except Exception as e:
                        show_error(f"Add error: {str(e)}")

    with tab3:
        st.markdown("#### Existing Stock Restock Karo")
        try:
            inv_res = sb.table("v_inventory").select("resource_id, resource_name").execute()
            inv = inv_res.data
        except: inv = []
        
        if inv:
            options = {f"{i.get('resource_name', 'Unknown')} (ID: {i['resource_id']})": i["resource_id"] for i in inv}
            selected = st.selectbox("Material Select Karo", list(options.keys()))
            qty_add  = st.number_input("Quantity to Add", min_value=0.1, step=0.5)

            if st.button("Restock ✅", type="primary"):
                try:
                    rid = options[selected]
                    cur = sb.table("raw_material").select("stock_quantity").eq("resource_id", rid).execute()
                    if cur.data:
                        new_qty = cur.data[0]["stock_quantity"] + qty_add
                        sb.table("raw_material").update({"stock_quantity": new_qty}).eq("resource_id", rid).execute()
                        show_success(f"Restocked {qty_add} units ✅")
                    else:
                        show_error("Resource not found")
                except Exception as e:
                    show_error(f"Restock error: {str(e)}")
        else:
            st.info("Pehle koi material add karo.")

    with tab4:
        st.markdown("#### Raw Material Delete Karo")
        st.warning("⚠️ Deleting a material will permanently remove it and cannot be undone.")
        try:
            inv_res2 = sb.table("v_inventory").select("resource_id, resource_name").execute()
            inv_del = inv_res2.data
        except:
            inv_del = []

        if inv_del:
            del_options = {f"{i.get('resource_name', 'Unknown')} (ID: {i['resource_id']})": i["resource_id"] for i in inv_del}
            del_selected = st.selectbox("Material Select Karo (Delete)", list(del_options.keys()), key="inv_del_select")

            confirm_del = st.checkbox("Haan, main confirm karta/karti hoon ke yeh delete karna chahta/chahti hoon", key="inv_del_confirm")
            if st.button("🗑️ Delete Material", type="primary", disabled=not confirm_del):
                try:
                    rid = del_options[del_selected]
                    sb.table("raw_material").delete().eq("resource_id", rid).execute()
                    sb.table("resource").delete().eq("resource_id", rid).execute()
                    show_success("Raw material deleted ✅")
                    st.rerun()
                except Exception as e:
                    show_error(f"Delete error: {str(e)}")
        else:
            st.info("Koi material nahi mila.")


# ═══════════════════════════════════════════
# LOOMS
# ═══════════════════════════════════════════
def looms_page():
    st.markdown('<div class="sec-header">⚙️ LOOM MANAGEMENT</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 View Looms", "➕ Add Loom", "🔧 Update Status", "🗑️ Delete"])

    with tab1:
        try:
            data_res = sb.table("v_loom_status").select("*").execute()
            if data_res.data:
                df = pd.DataFrame(data_res.data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Koi loom record nahi.")
        except Exception as e:
            show_error(f"Looms fetch error: {str(e)}")

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
                    try:
                        r = sb.table("resource").insert({
                            "resource_name": name,
                            "resource_type": "loom"
                        }).execute()
                        rid = r.data[0]["resource_id"]
                        sb.table("loom").insert({
                            "resource_id":      rid,
                            "loom_status":      status,
                            "maintenance_date": str(mdate)
                        }).execute()
                        show_success(f"Loom '{name}' added ✅")
                    except Exception as e:
                        show_error(f"Add error: {str(e)}")

    with tab3:
        st.markdown("#### Loom Status Update Karo")
        try:
            looms_res = sb.table("v_loom_status").select("resource_id, resource_name").execute()
            looms = looms_res.data
        except: looms = []

        if looms:
            options = {f"{l.get('resource_name', 'Loom')} (ID: {l['resource_id']})": l["resource_id"] for l in looms}
            selected = st.selectbox("Loom Select Karo", list(options.keys()))
            new_status = st.selectbox("New Status", ["active", "idle", "maintenance"])

            if st.button("Update Status ✅", type="primary"):
                try:
                    sb.table("loom").update({"loom_status": new_status}).eq("resource_id", options[selected]).execute()
                    show_success("Loom status updated ✅")
                except Exception as e:
                    show_error(f"Update error: {str(e)}")
        else:
            st.info("Pehle koi loom add karo.")

    with tab4:
        st.markdown("#### Loom Delete Karo")
        st.warning("⚠️ Deleting a loom will permanently remove it and cannot be undone.")
        try:
            looms_del_res = sb.table("v_loom_status").select("resource_id, resource_name").execute()
            looms_del = looms_del_res.data
        except:
            looms_del = []

        if looms_del:
            del_options = {f"{l.get('resource_name', 'Loom')} (ID: {l['resource_id']})": l["resource_id"] for l in looms_del}
            del_selected = st.selectbox("Loom Select Karo (Delete)", list(del_options.keys()), key="loom_del_select")

            confirm_del = st.checkbox("Haan, main confirm karta/karti hoon ke yeh delete karna chahta/chahti hoon", key="loom_del_confirm")
            if st.button("🗑️ Delete Loom", type="primary", disabled=not confirm_del):
                try:
                    rid = del_options[del_selected]
                    sb.table("loom").delete().eq("resource_id", rid).execute()
                    sb.table("resource").delete().eq("resource_id", rid).execute()
                    show_success("Loom deleted ✅")
                    st.rerun()
                except Exception as e:
                    show_error(f"Delete error: {str(e)}")
        else:
            st.info("Koi loom nahi mila.")


# ═══════════════════════════════════════════
# PRODUCTION
# ═══════════════════════════════════════════
def production_page():
    st.markdown('<div class="sec-header">🏭 PRODUCTION LOG</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 History", "➕ Log Production", "🗑️ Delete"])

    with tab1:
        try:
            data_res = sb.table("v_production_history").select("*").execute()
            if data_res.data:
                df = pd.DataFrame(data_res.data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Koi production record nahi.")
        except Exception as e:
            show_error(f"Production fetch error: {str(e)}")

    with tab2:
        st.markdown("#### New Production Entry")
        try:
            op_res = sb.table("operator").select("user_id, app_user(full_name, email)").execute()
            operators = op_res.data
            inv_res = sb.table("v_inventory").select("resource_id, resource_name").execute()
            inv = inv_res.data
        except:
            operators, inv = [], []

        if not operators:
            show_error("Koi operator nahi mila. Pehle operators add karo via Supabase.")
            return

        op_options = {}
        for o in operators:
            name = o.get("app_user", {}).get("full_name", f"Operator {o['user_id']}")
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
                try:
                    p = sb.table("production").insert({
                        "operator_id":     op_options[op_sel],
                        "production_date": str(prod_date),
                        "total_output":    float(output),
                        "notes":           notes
                    }).execute()
                    pid = p.data[0]["production_id"]
                    
                    for item in details:
                        sb.table("production_detail").insert({
                            "production_id": pid,
                            "resource_id":   item["resource_id"],
                            "quantity_used": float(item["quantity_used"])
                        }).execute()
                    
                    show_success("Production logged ✅")
                except Exception as e:
                    show_error(f"Log error: {str(e)}")

    with tab3:
        st.markdown("#### Production Record Delete Karo")
        st.warning("⚠️ Deleting a production record will also delete its details and linked financial records.")
        try:
            prod_del_res = sb.table("v_production_history").select("production_id, operator_name, production_date, total_output").execute()
            prod_del = prod_del_res.data
        except:
            prod_del = []

        if prod_del:
            del_options = {
                f"{p.get('operator_name','?')} — {p.get('production_date','?')} — {p.get('total_output','?')} units (ID: {p['production_id']})": p["production_id"]
                for p in prod_del
            }
            del_selected = st.selectbox("Production Record Select Karo", list(del_options.keys()), key="prod_del_select")

            confirm_del = st.checkbox("Haan, main confirm karta/karti hoon ke yeh delete karna chahta/chahti hoon", key="prod_del_confirm")
            if st.button("🗑️ Delete Production Record", type="primary", disabled=not confirm_del):
                try:
                    pid = del_options[del_selected]
                    sb.table("production_detail").delete().eq("production_id", pid).execute()
                    sb.table("financial_record").delete().eq("production_id", pid).execute()
                    sb.table("production").delete().eq("production_id", pid).execute()
                    show_success("Production record deleted ✅")
                    st.rerun()
                except Exception as e:
                    show_error(f"Delete error: {str(e)}")
        else:
            st.info("Koi production record nahi mila.")


# ═══════════════════════════════════════════
# FINANCIAL
# ═══════════════════════════════════════════
def financial_page():
    st.markdown('<div class="sec-header">💰 FINANCIAL RECORDS</div>', unsafe_allow_html=True)

    # Summary cards
    fin, err = get_financial_summary()
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
    elif err:
        show_error(f"Financial summary error: {err}")

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📋 All Records", "➕ Add Record", "🗑️ Delete"])

    with tab1:
        try:
            records_res = sb.table("financial_record").select("*").order("transaction_date", desc=True).execute()
            if records_res.data:
                df = pd.DataFrame(records_res.data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Koi financial record nahi.")
        except Exception as e:
            show_error(f"Financial fetch error: {str(e)}")

    with tab2:
        st.markdown("#### New Financial Entry")

        with st.form("add_financial"):
            prod_id  = st.number_input("Production ID (optional, 0 for none)", min_value=0, step=1)
            amount   = st.number_input("Amount (PKR)", min_value=0.0, step=100.0)
            tx_type  = st.selectbox("Transaction Type", ["income", "expense"])
            tx_date  = st.date_input("Transaction Date", value=date.today())
            desc     = st.text_area("Description", placeholder="e.g., Cotton purchase...")
            submitted = st.form_submit_button("Save Record ✅", type="primary")

            if submitted:
                try:
                    payload = {
                        "production_id":    prod_id if prod_id > 0 else None,
                        "amount":           float(amount),
                        "transaction_type": tx_type,
                        "transaction_date": str(tx_date),
                        "description":      desc
                    }
                    sb.table("financial_record").insert(payload).execute()
                    show_success("Financial record saved ✅")
                except Exception as e:
                    show_error(f"Save error: {str(e)}")

    with tab3:
        st.markdown("#### Financial Record Delete Karo")
        st.warning("⚠️ Yeh action permanent hai aur undo nahi ho sakta.")
        try:
            fin_del_res = sb.table("financial_record").select("*").order("transaction_date", desc=True).execute()
            fin_del = fin_del_res.data
        except:
            fin_del = []

        if fin_del:
            del_options = {
                f"{r.get('transaction_type','?').upper()} — PKR {r.get('amount','?')} — {r.get('transaction_date','?')} — {r.get('description','') or 'No desc'} (ID: {r['record_id']})": r["record_id"]
                for r in fin_del
            }
            del_selected = st.selectbox("Record Select Karo", list(del_options.keys()), key="fin_del_select")

            confirm_del = st.checkbox("Haan, main confirm karta/karti hoon ke yeh delete karna chahta/chahti hoon", key="fin_del_confirm")
            if st.button("🗑️ Delete Financial Record", type="primary", disabled=not confirm_del):
                try:
                    rid = del_options[del_selected]
                    sb.table("financial_record").delete().eq("record_id", rid).execute()
                    show_success("Financial record deleted ✅")
                    st.rerun()
                except Exception as e:
                    show_error(f"Delete error: {str(e)}")
        else:
            st.info("Koi financial record nahi mila.")


# ═══════════════════════════════════════════
# OPERATORS
# ═══════════════════════════════════════════
def operators_page():
    st.markdown('<div class="sec-header">👷 OPERATORS</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋 View Operators", "🗑️ Delete Operator"])

    with tab1:
        try:
            op_res = sb.table("operator").select("user_id, shift, expertise, app_user(full_name, email)").execute()
            data = op_res.data
            if data:
                rows = []
                for o in data:
                    user_info = o.get("app_user") or {}
                    rows.append({
                        "user_id":   o["user_id"],
                        "full_name": user_info.get("full_name", "—"),
                        "email":     user_info.get("email", "—"),
                        "shift":     o.get("shift", "—"),
                        "expertise": o.get("expertise", "—"),
                    })
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Koi operator record nahi. Supabase mein directly add karo.")
        except Exception as e:
            show_error(f"Operators fetch error: {str(e)}")

        st.markdown("""
        > 💡 **Tip:** Operators add karne ke liye pehle Supabase mein `app_user` table mein user add karo, 
        phir `operator` table mein us user ka `user_id` dal do.
        """)

    with tab2:
        st.markdown("#### Operator Delete Karo")
        st.warning("⚠️ Operator delete karne se uska `app_user` record bhi permanently delete ho jayega.")
        try:
            op_del_res = sb.table("operator").select("user_id, shift, app_user(full_name, email)").execute()
            ops_del = op_del_res.data
        except:
            ops_del = []

        if ops_del:
            del_options = {}
            for o in ops_del:
                u = o.get("app_user") or {}
                label = f"{u.get('full_name', 'Unknown')} — {u.get('email', '?')} (Shift: {o.get('shift','?')}) [ID: {o['user_id']}]"
                del_options[label] = o["user_id"]

            del_selected = st.selectbox("Operator Select Karo", list(del_options.keys()), key="op_del_select")

            confirm_del = st.checkbox("Haan, main confirm karta/karti hoon ke yeh delete karna chahta/chahti hoon", key="op_del_confirm")
            if st.button("🗑️ Delete Operator", type="primary", disabled=not confirm_del):
                try:
                    uid = del_options[del_selected]
                    sb.table("operator").delete().eq("user_id", uid).execute()
                    sb.table("app_user").delete().eq("user_id", uid).execute()
                    show_success("Operator deleted ✅")
                    st.rerun()
                except Exception as e:
                    show_error(f"Delete error: {str(e)}")
        else:
            st.info("Koi operator nahi mila.")


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
