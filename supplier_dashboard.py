import streamlit as st
import pandas as pd
from db_utils import get_supplier_listings, get_supplier_orders

# Ensure user is logged in
if not st.session_state.user or st.session_state.user["role"] != "supplier":
    st.warning("Please log in as a Supplier to view this page.")
    st.switch_page("supplier_login.py")
    st.stop()

user = st.session_state.user

st.title(f"🏭 {user['name']} Control Center")
st.caption("Supplier Dashboard • Manage your circular material inventory, sales metrics, and impact.")

# Fetch listings & orders
listings = get_supplier_listings(user["id"])
orders = get_supplier_orders(user["id"])

# Calculations
total_listed = len(listings)
total_sold = len([l for l in listings if l["status"] == "sold"])
total_earnings = sum(o["total_price"] for o in orders)
total_co2 = sum(l["carbon_saved"] for l in listings)

# Display Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="reloop-card" style="text-align: center;">
        <h4 style="color: #64748B; font-size: 14px; margin: 0;">Total Material Listed</h4>
        <h2 style="color: #059669 !important; -webkit-text-fill-color: #059669 !important; margin: 10px 0;">{total_listed}</h2>
        <p style="color: #475569; font-size: 11px; margin: 0;">Material lots listed</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="reloop-card" style="text-align: center;">
        <h4 style="color: #64748B; font-size: 14px; margin: 0;">Lots Sold</h4>
        <h2 style="color: #059669 !important; -webkit-text-fill-color: #059669 !important; margin: 10px 0;">{total_sold}</h2>
        <p style="color: #475569; font-size: 11px; margin: 0;">Transferred to circular chain</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="reloop-card" style="text-align: center;">
        <h4 style="color: #64748B; font-size: 14px; margin: 0;">Total Earnings</h4>
        <h2 style="color: #059669 !important; -webkit-text-fill-color: #059669 !important; margin: 10px 0;">₹{total_earnings:,.2f}</h2>
        <p style="color: #475569; font-size: 11px; margin: 0;">Revenue generated</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="reloop-card" style="text-align: center;">
        <h4 style="color: #64748B; font-size: 14px; margin: 0;">CO₂ Diverted</h4>
        <h2 style="color: #059669 !important; -webkit-text-fill-color: #059669 !important; margin: 10px 0;">{total_co2:,.2f} t</h2>
        <p style="color: #475569; font-size: 11px; margin: 0;">Offset savings achieved</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Charts
st.subheader("📊 Listing Distribution")
if listings:
    df = pd.DataFrame(listings)
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("##### Material Types Listed")
        mat_counts = df["material"].value_counts().reset_index()
        mat_counts.columns = ["Material", "Count"]
        st.bar_chart(mat_counts.set_index("Material"), y="Count", color="#059669")
        
    with col_chart2:
        st.markdown("##### Listing Status")
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        st.bar_chart(status_counts.set_index("Status"), y="Count", color="#0D9488")
else:
    st.info("No materials listed yet. Use the Add Material page to create your first waste listing!")

# Quick Actions
st.markdown("---")
st.markdown("### 🚀 Quick Actions")
col_act1, col_act2 = st.columns(2)
with col_act1:
    if st.button("➕ Add Waste Material Lot", use_container_width=True):
        st.switch_page("add_material.py")
with col_act2:
    if st.button("✅ Verify Your Business", use_container_width=True):
        st.switch_page("supplier_verification.py")
