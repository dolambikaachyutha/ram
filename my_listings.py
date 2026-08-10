import streamlit as st
from db_utils import get_supplier_listings, delete_listing

# Ensure user is logged in
if not st.session_state.user or st.session_state.user["role"] != "supplier":
    st.warning("Please log in as a Supplier to view this page.")
    st.switch_page("supplier_login.py")
    st.stop()

user = st.session_state.user

st.title("📋 My Material Listings")
st.caption("Review, monitor, or withdraw your listed byproduct inventories.")

listings = get_supplier_listings(user["id"])

if not listings:
    st.info("You haven't listed any material lots yet. Head to 'Add Material' to post factory waste!")
else:
    tab_active, tab_sold = st.tabs(["🟢 Active Listings", "🔴 Sold Listings"])
    
    active_list = [l for l in listings if l["status"] == "active"]
    sold_list = [l for l in listings if l["status"] == "sold"]
    
    with tab_active:
        if not active_list:
            st.write("No active listings currently on the marketplace.")
        else:
            for l in active_list:
                col_info, col_del = st.columns([4, 1])
                with col_info:
                    st.markdown(f"""
                    <div class="reloop-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h3 style="margin:0; color:#00E676;">♻️ {l['material'].title()}</h3>
                            <span class="badge-verified" style="background-color:#123524; color:#00E676; border-color:#00E676;">Active</span>
                        </div>
                        <p style="color:#ccc; font-style:italic; font-size:13px; margin: 10px 0;">{l['description'] or 'No description provided.'}</p>
                        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:10px; font-size:13px; color:#aaa;">
                            <div><strong>Quantity:</strong> {l['quantity']} {l['unit']}</div>
                            <div><strong>Price:</strong> ₹{l['price_per_kg']:.2f} / kg</div>
                            <div><strong>Source:</strong> 📍 {l['location']}</div>
                            <div><strong>Condition:</strong> {l['condition'].upper()}</div>
                            <div><strong>Carbon saved:</strong> 🌱 {l['carbon_saved']:.2f} t CO₂</div>
                            <div><strong>Expiry Date:</strong> ⏳ {l['expiry_date'] or 'N/A'}</div>
                            <div><strong>Created at:</strong> 📅 {l['created_at']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_del:
                    st.write("")
                    st.write("")
                    st.write("")
                    if st.button("🗑️ Delete", key=f"del_{l['id']}", use_container_width=True):
                        delete_listing(l['id'])
                        st.success("Listing removed!")
                        st.toast("Listing deleted.", icon="🗑️")
                        st.rerun()
                st.write("")
                
    with tab_sold:
        if not sold_list:
            st.write("No sold listings yet.")
        else:
            for l in sold_list:
                st.markdown(f"""
                <div class="reloop-card" style="border-color: rgba(255,82,82,0.3);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <h3 style="margin:0; color:#ff5252;">♻️ {l['material'].title()}</h3>
                        <span class="badge-sold">Sold</span>
                    </div>
                    <p style="color:#aaa; font-style:italic; font-size:13px;">{l['description'] or 'No description provided.'}</p>
                    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:10px; font-size:13px; color:#999;">
                        <div><strong>Quantity Sold:</strong> {l['quantity']} {l['unit']}</div>
                        <div><strong>Price:</strong> ₹{l['price_per_kg']:.2f} / kg</div>
                        <div><strong>Location:</strong> 📍 {l['location']}</div>
                        <div><strong>Condition:</strong> {l['condition'].upper()}</div>
                        <div><strong>Carbon savings achieved:</strong> 🌱 {l['carbon_saved']:.2f} t CO₂</div>
                        <div><strong>Sold on:</strong> 📅 {l['created_at']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.write("")
