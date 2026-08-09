import streamlit as st
from db.db_utils import get_buyer_orders

# Ensure user is logged in
if not st.session_state.user or st.session_state.user["role"] != "buyer":
    st.warning("Please log in as a Buyer to view this page.")
    st.switch_page("pages/buyer_login.py")
    st.stop()

user = st.session_state.user

st.title("📦 My Procurement Orders")
st.caption("Track your purchased materials and circular economy transactions.")

orders = get_buyer_orders(user["id"])

if not orders:
    st.info("No orders found. Explore listings in the Marketplace to place your first order.")
else:
    for o in orders:
        status_badge = ""
        # Let's map order status to HTML badges
        if o["status"] == "completed" or o["status"] == "Delivered":
            status_badge = '<span class="badge-verified">✅ Delivered</span>'
        elif o["status"] == "Shipped":
            status_badge = '<span class="badge-verified" style="border-color:#29b6f6; color:#29b6f6; background-color:rgba(41,182,246,0.1)">🚚 Shipped</span>'
        else:
            status_badge = '<span class="badge-pending">⏳ Processing</span>'
            
        st.markdown(f"""
        <div class="reloop-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="margin: 0; color: #00E676;">♻️ {o['material'].title()}</h3>
                <div>{status_badge}</div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; font-size: 14px; color: #ccc;">
                <div><strong>Supplier:</strong> {o['supplier_name']}</div>
                <div><strong>Quantity Purchased:</strong> {o['quantity']:.1f} {o['unit']}</div>
                <div><strong>Price per Unit:</strong> ₹{o['price_per_kg']:.2f} / kg</div>
                <div><strong>Total Transaction Value:</strong> <span style="color:#00E676; font-weight:bold;">₹{o['total_price']:.2f}</span></div>
                <div><strong>Location Source:</strong> 📍 {o['location']}</div>
                <div><strong>Carbon Prevented:</strong> 🌱 {o['carbon_saved']:.2f} t CO₂</div>
                <div><strong>Transaction Date:</strong> 📅 {o['created_at']}</div>
                <div><strong>Order ID:</strong> #RL-{o['id']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("") # spacing
