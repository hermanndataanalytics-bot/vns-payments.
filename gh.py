import streamlit as st
import requests
import time
from supabase import create_client, Client # Ataovy azo antoka fa efa nanao: pip install supabase

# --- CONFIG ---
st.set_page_config(page_title="VNS TERMINATOR | Premium Access", layout="wide", page_icon="💎")

# --- SECRETS (Avy amin'ny .streamlit/secrets.toml) ---
try:
    NOWPAYMENTS_API_KEY = st.secrets["NOWPAYMENTS_API_KEY"]
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    
    # Mamorona ny Supabase Client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("Tsy hita ny Secrets. Hamarino ny .streamlit/secrets.toml")
    st.stop()

def create_invoice(amount, plan_name, billing_type):
    url = "https://api.nowpayments.io/v1/invoice"
    headers = {"x-api-key": NOWPAYMENTS_API_KEY, "Content-Type": "application/json"}
    payload = {
        "price_amount": float(amount),
        "price_currency": "usd",
        "order_id": f"VNS-{plan_name}-{billing_type}-{int(time.time())}",
        "order_description": f"VNS {plan_name} ({billing_type}) Subscription",
    }
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code in [200, 201]:
            return res.json().get('invoice_url')
    except:
        return None
    return None

# --- CSS STYLING (Premium Look) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    .stApp { background-color: #0b0e11; font-family: 'Plus Jakarta Sans', sans-serif; }
    .premium-header { text-align: center; padding: 60px 0 40px 0; }
    .secure-tag { background: rgba(59, 130, 246, 0.1); color: #3b82f6; padding: 6px 16px; border-radius: 100px; font-size: 12px; font-weight: 600; text-transform: uppercase; border: 1px solid rgba(59, 130, 246, 0.2); }
    .main-title { color: #ffffff; font-size: 52px; font-weight: 800; margin-top: 20px; }
    .plan-card { background: #161b22; border: 1px solid #30363d; padding: 45px 35px; border-radius: 24px; text-align: center; transition: all 0.4s ease; }
    .plan-card:hover { transform: translateY(-12px); border-color: #3b82f6; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4); background: #1c2128; }
    .price-number { font-size: 56px; font-weight: 800; color: #ffffff; margin: 15px 0; display: flex; align-items: center; justify-content: center; }
    .currency { font-size: 24px; vertical-align: super; margin-right: 4px; color: #3b82f6; }
    .duration { font-size: 16px; color: #8b949e; }
    .feature-item { color: #c9d1d9; font-size: 14px; margin-bottom: 12px; display: flex; align-items: center; }
    .premium-footer { margin-top: 100px; padding: 60px 0; border-top: 1px solid #30363d; background: linear-gradient(to bottom, #0b0e11, #080a0d); }
    div.stButton > button { border-radius: 12px !important; padding: 12px 24px !important; font-weight: 600 !important; }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "step" not in st.session_state:
    st.session_state.step = "plans"

# --- MAIN INTERFACE ---
if st.session_state.step == "plans":
    st.markdown("""<div class="premium-header"><span class="secure-tag">🔒 Secured by NOWPayments Protocol</span><h1 class="main-title">VNS Terminator Access</h1></div>""", unsafe_allow_html=True)
    
    col_s, _ = st.columns([1.2, 3])
    with col_s:
        billing = st.segmented_control("Billing Cycle", ["Monthly", "Lifetime"], default="Monthly")
    
    plans = {
        "BASIC": {"m": 19, "l": 199, "f": ["3 Forex Assets", "Live Analysis", "Standard Support"]},
        "PRO": {"m": 49, "l": 499, "f": ["12 Assets Access", "AI Pattern Recognition", "Signal Sync", "PDF Reports"]},
        "ELITE": {"m": 99, "l": 999, "f": ["Everything in PRO", "Crypto Quant Algorithms", "Neural Predictions"]},
        "PREMIUM": {"m": 144, "l": 1499, "f": ["Unlimited Assets", "VIP Data Warehouse", "Priority 24/7 Concierge"]}
    }

    cols = st.columns(4)
    for i, (name, data) in enumerate(plans.items()):
        with cols[i]:
            price = data["m"] if billing == "Monthly" else data["l"]
            st.markdown(f"""<div class="plan-card"><div style="color:#3b82f6;font-weight:800;font-size:12px;">{name}</div><div class="price-number"><span class="currency">$</span>{price}</div><div class="duration">billed {billing.lower()}</div><div style="text-align:left;margin-top:30px;">{"".join(['<div class="feature-item">✅ '+f+'</div>' for f in data["f"]])}</div></div>""", unsafe_allow_html=True)
            if st.button(f"Pay with Crypto", key=f"pay_{name}", type="primary" if name=="PRO" else "secondary", use_container_width=True):
                st.session_state.selected_plan, st.session_state.selected_price, st.session_state.billing_type, st.session_state.step = name, price, billing, "checkout"
                st.rerun()

elif st.session_state.step == "checkout":
    st.markdown("<div style='padding:60px 0; text-align:center;'><h1 style='color:white;'>Secure Checkout</h1></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.container(border=True):
            st.write(f"### Plan: **{st.session_state.selected_plan}**")
            st.write(f"#### Amount: **${st.session_state.selected_price}**")
            email = st.text_input("Activation Email:")
            txid = st.text_input("Transaction ID (Optional):", placeholder="Paste TXID if you have it")
            
            if st.button("🚀 COMPLETE & REGISTER", type="primary", use_container_width=True):
                if email:
                    with st.spinner("Processing..."):
                        # 1. NOWPayments Invoice
                        link = create_invoice(st.session_state.selected_price, st.session_state.selected_plan, st.session_state.billing_type)
                        if link:
                            # 2. Supabase Insert
                            try:
                                payload = {
                                    "email": email,
                                    "txid": txid if txid else "pending_link",
                                    "plan": st.session_state.selected_plan,
                                    "status": "pending",
                                    "amount": st.session_state.selected_price
                                }
                                supabase.table("payment_proofs").insert(payload).execute()
                                st.success("Registration Saved! Redirecting to payment...")
                                st.link_button("👉 CLICK TO PAY NOW", link, use_container_width=True)
                            except Exception as e:
                                st.error(f"Supabase Error: {str(e)}")
                        else:
                            st.error("Error creating payment link.")
                else:
                    st.error("Email is required.")
            
            if st.button("← Back"):
                st.session_state.step = "plans"
                st.rerun()