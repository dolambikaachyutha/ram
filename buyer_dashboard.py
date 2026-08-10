import streamlit as st
import pandas as pd
from db_utils import get_buyer_orders

# Ensure user is logged in
if not st.session_state.user or st.session_state.user["role"] != "buyer":
    st.warning("Please log in as a Buyer to view this page.")
    st.switch_page("buyer_login.py")
    st.stop()

user = st.session_state.user

st.title(f"📊 Welcome, {user['name']}")
st.caption("Buyer Dashboard • View your circular procurement and environmental metrics.")

# Fetch Buyer Orders
orders = get_buyer_orders(user["id"])

# Compute Metrics
total_procured = sum(o["quantity"] for o in orders)
total_spent = sum(o["total_price"] for o in orders)
total_co2 = sum(o["carbon_saved"] for o in orders)
order_count = len(orders)

# Layout: Metric columns
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="reloop-card" style="text-align: center;">
        <h4 style="color: #64748B; font-size: 14px; margin: 0;">Materials Purchased</h4>
        <h2 style="color: #059669 !important; -webkit-text-fill-color: #059669 !important; margin: 10px 0;">{total_procured:,.1f} kg</h2>
        <p style="color: #475569; font-size: 11px; margin: 0;">Procured waste byproducts</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="reloop-card" style="text-align: center;">
        <h4 style="color: #64748B; font-size: 14px; margin: 0;">Total Spent</h4>
        <h2 style="color: #059669 !important; -webkit-text-fill-color: #059669 !important; margin: 10px 0;">₹{total_spent:,.2f}</h2>
        <p style="color: #475569; font-size: 11px; margin: 0;">Circularity investments</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="reloop-card" style="text-align: center;">
        <h4 style="color: #64748B; font-size: 14px; margin: 0;">Total CO₂ Saved</h4>
        <h2 style="color: #059669 !important; -webkit-text-fill-color: #059669 !important; margin: 10px 0;">{total_co2:,.2f} t</h2>
        <p style="color: #475569; font-size: 11px; margin: 0;">Carbon footprint reduction</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="reloop-card" style="text-align: center;">
        <h4 style="color: #64748B; font-size: 14px; margin: 0;">Total Transactions</h4>
        <h2 style="color: #059669 !important; -webkit-text-fill-color: #059669 !important; margin: 10px 0;">{order_count}</h2>
        <p style="color: #475569; font-size: 11px; margin: 0;">Completed orders</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Charts & Analytics
st.subheader("📦 Procurement & Impact Analytics")
if orders:
    df = pd.DataFrame(orders)
    # Ensure dates are parsed
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["Date"] = df["created_at"].dt.date
    
    c_col1, c_col2 = st.columns(2)
    
    with c_col1:
        st.markdown("##### Spending Timeline")
        daily_spend = df.groupby("Date")["total_price"].sum().reset_index()
        # Sort by date
        daily_spend = daily_spend.sort_values("Date")
        st.line_chart(daily_spend.set_index("Date"), y="total_price", color="#059669")
        
    with c_col2:
        st.markdown("##### Material Procurement Breakdown")
        mat_breakdown = df.groupby("material")["quantity"].sum().reset_index()
        st.bar_chart(mat_breakdown.set_index("material"), y="quantity", color="#0D9488")
else:
    st.info("You haven't made any purchases yet. Head over to the Marketplace or AI Matcher to find waste materials!")

# Quick Navigation Section
st.markdown("---")
st.markdown("### 🚀 Quick Actions")
act_col1, act_col2 = st.columns(2)
with act_col1:
    if st.button("🛒 Open Marketplace", use_container_width=True):
        st.switch_page("marketplace.py")
with act_col2:
    if st.button("🤖 Find Supplier with AI Matcher", use_container_width=True):
        st.switch_page("ai_matcher.py")
