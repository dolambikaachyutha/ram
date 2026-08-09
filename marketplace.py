import streamlit as st
from db.db_utils import get_listings, create_order

# Ensure user is logged in
if not st.session_state.user or st.session_state.user["role"] != "buyer":
    st.warning("Please log in as a Buyer to view this page.")
    st.switch_page("pages/buyer_login.py")
    st.stop()

user = st.session_state.user

st.title("🛒 Waste Material Marketplace")
st.caption("Browse, search, and procure secondary raw materials directly from verified industrial suppliers.")

# Filters Sidebar
st.sidebar.header("🔍 Marketplace Filters")

search_q = st.sidebar.text_input("Keyword Search", placeholder="e.g. wood, sawdust, textile")

material_type = st.sidebar.selectbox(
    "Material Category",
    ["All", "Wood", "Plastic", "Paper", "Fabric", "Metal", "Organic"]
)

location_f = st.sidebar.text_input("Filter Location (City)", placeholder="e.g. Bengaluru")

price_range = st.sidebar.slider(
    "Price Limit (₹ / kg)",
    min_value=0, max_value=100, value=(0, 100)
)

condition_f = st.sidebar.selectbox(
    "Material Condition",
    ["All", "Excellent", "Good", "Fair", "Poor"]
)

verified_only = st.sidebar.checkbox("Verified Suppliers Only")

# Fetch listings based on filters
listings = get_listings(
    search_query=search_q if search_q else None,
    material_type=material_type if material_type != "All" else None,
    min_price=price_range[0],
    max_price=price_range[1],
    location=location_f if location_f else None,
    condition=condition_f if condition_f != "All" else None,
    verified_only=verified_only
)

# Display listings
if not listings:
    st.info("No active material listings matched your search criteria. Try relaxing your filters!")
else:
    st.markdown(f"##### Showing {len(listings)} active listing(s)")
    
    # Grid of listings
    for l in listings:
        # Verified Badge
        badge = ""
        is_verified = (l["verification_status"] == "approved")
        if is_verified:
            badge = '<span class="badge-verified">✅ Verified Supplier</span>'
        else:
            badge = '<span class="badge-pending">Unverified Supplier</span>'
            
        trust_score = l["trust_score"] if l["trust_score"] is not None else 5.0
        trust_color = "#059669" if trust_score >= 8.0 else "#D97706" if trust_score >= 5.0 else "#DC2626"
        
        col_card, col_action = st.columns([4, 1])
        
        with col_card:
            st.markdown(f"""
            <div class="reloop-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h3 style="margin: 0; color: #059669;">{l['material'].title()}</h3>
                    <div>{badge}</div>
                </div>
                <p style="color: #475569; font-style: italic; font-size: 13px; margin-bottom: 12px;">{l['description'] or 'No description provided.'}</p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; font-size: 13px; color: #334155;">
                    <div><strong>Quantity:</strong> {l['quantity']} {l['unit']}</div>
                    <div><strong>Price per kg:</strong> ₹{l['price_per_kg']:.2f}</div>
                    <div><strong>Estimated Value:</strong> ₹{(l['quantity'] * l['price_per_kg']):,.2f}</div>
                    <div><strong>Source Location:</strong> 📍 {l['location'].title()}</div>
                    <div><strong>Condition Quality:</strong> {l['condition'].upper()}</div>
                    <div><strong>Supplier:</strong> {l['supplier_name']}</div>
                    <div><strong>Carbon Saved:</strong> 🌱 {l['carbon_saved']:.2f} t CO₂</div>
                    <div><strong>Expiry / Lifetime:</strong> ⏳ {l['expiry_date'] or 'N/A'}</div>
                    <div>
                        <strong>AI Trust Score:</strong> 
                        <span style="color: {trust_color}; font-weight: bold;">{trust_score:.1f} / 10.0</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_action:
            st.write("")
            st.write("")
            st.write("")
            total_value = l['quantity'] * l['price_per_kg']
            st.metric("Total Cost", f"₹{total_value:,.1f}")
            if st.button("🛒 Procure", key=f"buy_{l['id']}", use_container_width=True):
                # Execute purchase
                create_order(
                    listing_id=l['id'],
                    buyer_id=user["id"],
                    quantity=l['quantity'],
                    total_price=total_value
                )
                st.success(f"Successfully purchased {l['material']}!")
                st.toast(f"Order created for {l['material']}!", icon="♻️")
                st.rerun()
        st.write("") # spacing
