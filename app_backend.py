"""
Smart Weaving Management System
Flask Backend
Connects to Supabase PostgreSQL
"""

from flask import Flask, request, jsonify
from supabase import create_client, Client
from flask_cors import CORS

# ─────────────────────────────────────────────
# SUPABASE CONFIG
# ─────────────────────────────────────────────
SUPABASE_URL = "https://qeiqpxmnkmbnqfubkpaq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFlaXFweG1ua21ibnFmdWJrcGFxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgyMTU5MDMsImV4cCI6MjA5Mzc5MTkwM30.qNVnjOtxJ-d-Gvwy_wQ_nA2wzCYTarusawRLVQaAYH4"   # ← Supabase dashboard se naya key paste karo (rotate kar le pehle)

app: Flask = Flask(__name__)
CORS(app)

sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/")
def index():
    return jsonify({"status": "Smart Weaving API running ✅"})


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    pw    = data.get("password")

    res = sb.table("app_user").select("*").eq("email", email).eq("password", pw).execute()
    if not res.data:
        return jsonify({"error": "Invalid email or password"}), 401

    user = res.data[0]
    is_admin = sb.table("admin").select("user_id").eq("user_id", user["user_id"]).execute()
    user["role"] = "admin" if is_admin.data else "operator"
    return jsonify({"user": user})


@app.route("/operators", methods=["GET"])
def get_operators():
    res = sb.table("operator").select("user_id, shift, expertise, app_user(full_name, email)").execute()
    return jsonify(res.data)


@app.route("/inventory", methods=["GET"])
def get_inventory():
    res = sb.table("v_inventory").select("*").execute()
    return jsonify(res.data)


@app.route("/inventory/add", methods=["POST"])
def add_raw_material():
    d = request.json
    try:
        r = sb.table("resource").insert({
            "resource_name": d["resource_name"],
            "resource_type": "raw_material"
        }).execute()
        rid = r.data[0]["resource_id"]
        sb.table("raw_material").insert({
            "resource_id":    rid,
            "stock_quantity": float(d["stock_quantity"]),
            "unit":           d["unit"],
            "cost_per_unit":  float(d["cost_per_unit"])
        }).execute()
        return jsonify({"message": f"Raw material '{d['resource_name']}' added ✅", "resource_id": rid})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/inventory/restock", methods=["POST"])
def restock():
    d   = request.json
    rid = d["resource_id"]
    qty = float(d["quantity"])
    cur = sb.table("raw_material").select("stock_quantity").eq("resource_id", rid).execute()
    if not cur.data:
        return jsonify({"error": "Resource not found"}), 404
    new_qty = cur.data[0]["stock_quantity"] + qty
    sb.table("raw_material").update({"stock_quantity": new_qty}).eq("resource_id", rid).execute()
    return jsonify({"message": f"Restocked {qty} units ✅", "new_stock": new_qty})


@app.route("/looms", methods=["GET"])
def get_looms():
    res = sb.table("v_loom_status").select("*").execute()
    return jsonify(res.data)


@app.route("/looms/add", methods=["POST"])
def add_loom():
    d = request.json
    try:
        r = sb.table("resource").insert({
            "resource_name": d["resource_name"],
            "resource_type": "loom"
        }).execute()
        rid = r.data[0]["resource_id"]
        sb.table("loom").insert({
            "resource_id":      rid,
            "loom_status":      d.get("loom_status", "active"),
            "maintenance_date": d.get("maintenance_date")
        }).execute()
        return jsonify({"message": f"Loom '{d['resource_name']}' added ✅", "resource_id": rid})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/looms/update-status", methods=["POST"])
def update_loom_status():
    d = request.json
    sb.table("loom").update({"loom_status": d["status"]}).eq("resource_id", d["resource_id"]).execute()
    return jsonify({"message": "Loom status updated ✅"})


@app.route("/production", methods=["GET"])
def get_production():
    res = sb.table("v_production_history").select("*").execute()
    return jsonify(res.data)


@app.route("/production/add", methods=["POST"])
def add_production():
    d = request.json
    try:
        p = sb.table("production").insert({
            "operator_id":     d["operator_id"],
            "production_date": d["production_date"],
            "total_output":    float(d["total_output"]),
            "notes":           d.get("notes", "")
        }).execute()
        pid = p.data[0]["production_id"]
        for item in d.get("details", []):
            sb.table("production_detail").insert({
                "production_id": pid,
                "resource_id":   item["resource_id"],
                "quantity_used": float(item["quantity_used"])
            }).execute()
        return jsonify({"message": "Production logged ✅", "production_id": pid})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/financial", methods=["GET"])
def get_financial():
    res = sb.table("v_financial_summary").select("*").execute()
    return jsonify(res.data)


@app.route("/financial/records", methods=["GET"])
def get_all_records():
    res = sb.table("financial_record").select("*").order("transaction_date", desc=True).execute()
    return jsonify(res.data)


@app.route("/financial/add", methods=["POST"])
def add_financial():
    d = request.json
    try:
        sb.table("financial_record").insert({
            "production_id":    d.get("production_id"),
            "amount":           float(d["amount"]),
            "transaction_type": d["transaction_type"],
            "transaction_date": d["transaction_date"],
            "description":      d.get("description", "")
        }).execute()
        return jsonify({"message": "Financial record saved ✅"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/financial/summary", methods=["GET"])
def financial_totals():
    res = sb.table("financial_record").select("amount, transaction_type").execute()
    income  = sum(r["amount"] for r in res.data if r["transaction_type"] == "income")
    expense = sum(r["amount"] for r in res.data if r["transaction_type"] == "expense")
    return jsonify({
        "total_income":  income,
        "total_expense": expense,
        "net_profit":    income - expense
    })


@app.route("/inventory/delete", methods=["POST"])
def delete_inventory():
    d = request.json
    rid = d.get("resource_id")
    try:
        sb.table("raw_material").delete().eq("resource_id", rid).execute()
        sb.table("resource").delete().eq("resource_id", rid).execute()
        return jsonify({"message": "Raw material deleted ✅"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/looms/delete", methods=["POST"])
def delete_loom():
    d = request.json
    rid = d.get("resource_id")
    try:
        sb.table("loom").delete().eq("resource_id", rid).execute()
        sb.table("resource").delete().eq("resource_id", rid).execute()
        return jsonify({"message": "Loom deleted ✅"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/production/delete", methods=["POST"])
def delete_production():
    d = request.json
    pid = d.get("production_id")
    try:
        sb.table("production_detail").delete().eq("production_id", pid).execute()
        sb.table("financial_record").delete().eq("production_id", pid).execute()
        sb.table("production").delete().eq("production_id", pid).execute()
        return jsonify({"message": "Production record deleted ✅"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/financial/delete", methods=["POST"])
def delete_financial():
    d = request.json
    rid = d.get("record_id")
    try:
        sb.table("financial_record").delete().eq("record_id", rid).execute()
        return jsonify({"message": "Financial record deleted ✅"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/operators/delete", methods=["POST"])
def delete_operator():
    d = request.json
    uid = d.get("user_id")
    try:
        sb.table("operator").delete().eq("user_id", uid).execute()
        sb.table("app_user").delete().eq("user_id", uid).execute()
        return jsonify({"message": "Operator deleted ✅"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
