import streamlit as st
from db.db_utils import get_listings, create_order

# Ensure user is logged in
if not st.session_state.user or st.session_state.user["role"] != "buyer":
    st.warning("Please log in as a Buyer to view this page.")
    st.switch_page("pages/buyer_login.py")
    st.stop()

user = st.session_state.user

st.title("🤖 AI Matchmaker & Smart Recommendation")
st.caption("Enter your specific material requirements to locate the optimal circular resource matches.")

# Input Form
with st.form("matcher_form"):
    st.subheader("Your Requirements")
    col1, col2, col3 = st.columns(3)
    with col1:
        req_material = st.text_input("Required Material Keyword", placeholder="e.g. wood, plastic, fabric")
    with col2:
        req_qty = st.number_input("Required Quantity (kg)", min_value=1, value=100)
    with col3:
        req_loc = st.text_input("Your Location (City)", placeholder="e.g. Bengaluru")
        
    submit_btn = st.form_submit_button("🔍 Run AI Matchmaker", use_container_width=True)

# Run Matching logic
if submit_btn:
    if not req_material:
        st.error("Please enter a material keyword to search.")
    else:
        # Get active listings matching keyword (we can search all active)
        all_listings = get_listings()
        matches = []
        
        for l in all_listings:
            # Check if keyword is in material or description
            mat_name = l["material"].lower()
            desc = (l["description"] or "").lower()
            keyword = req_material.lower()
            
            if keyword in mat_name or keyword in desc:
                # Simulate distance
                l_city = l["location"].strip().lower()
                b_city = req_loc.strip().lower() if req_loc else ""
                
                if not b_city:
                    distance = 50.0  # default
                elif l_city == b_city:
                    distance = 12.0  # same city close distance
                else:
                    # Deterministic distance based on string hash difference for stability
                    distance = float(abs(hash(l_city) - hash(b_city)) % 400 + 30)
                
                l["distance_km"] = distance
                
                # Compute Recommendation Match Score
                # Perfect score is 100.
                score = 100.0
                
                # 1. Price factor (cheaper is better)
                # Deduct 1.5 points per Rupee
                score -= min(l["price_per_kg"] * 1.5, 40)
                
                # 2. Distance factor (closer is better)
                # Deduct 0.1 points per km
                score -= min(distance * 0.1, 30)
                
                # 3. Trust factor (higher score is better)
                trust = l["trust_score"] if l["trust_score"] is not None else 5.0
                score += (trust - 5.0) * 3.0  # add/subtract up to 15 points
                
                # 4. Verification bonus
                if l["verification_status"] == "approved":
                    score += 10.0
                    
                # Bind score to [0, 100]
                l["match_score"] = max(0.0, min(100.0, score))
                matches.append(l)
                
        if not matches:
            st.warning("No listings found matching that material keyword. Ask the AI assistant or browse the Marketplace.")
        else:
            st.success(f"Located {len(matches)} matches! Calculating smart recommendations...")
            
            # Identify specific award-winners
            best_match = max(matches, key=lambda x: x["match_score"])
            cheapest = min(matches, key=lambda x: x["price_per_kg"])
            nearest = min(matches, key=lambda x: x["distance_km"])
            highest_trust = max(matches, key=lambda x: x["trust_score"] if x["trust_score"] is not None else 5.0)
            
            # Display Award Cards
            col_award1, col_award2, col_award3, col_award4 = st.columns(4)
            
            with col_award1:
                st.markdown(f"""
                <div class="reloop-card" style="border-color: #059669; height: 260px;">
                    <h3 style="color: #059669; font-size: 16px; margin-top: 0;">🥇 Best Match</h3>
                    <h4 style="margin: 10px 0; color: #0F172A;">{best_match['material'].title()}</h4>
                    <p style="font-size: 13px; color: #475569; min-height: 45px;">Seller: {best_match['supplier_name']}<br>Location: {best_match['location']}</p>
                    <h2 style="color: #059669; margin: 10px 0; font-size: 24px;">{best_match['match_score']:.1f}%</h2>
                    <p style="font-size: 11px; color: #64748B; margin: 0;">Optimized match score</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Procure Best Match", key="btn_procure_best", use_container_width=True):
                    val = best_match['quantity'] * best_match['price_per_kg']
                    create_order(best_match['id'], user['id'], best_match['quantity'], val)
                    st.success("Best Match procured!")
                    st.rerun()
                    
            with col_award2:
                st.markdown(f"""
                <div class="reloop-card" style="border-color: #0284C7; height: 260px;">
                    <h3 style="color: #0284C7; font-size: 16px; margin-top: 0;">📍 Nearest</h3>
                    <h4 style="margin: 10px 0; color: #0F172A;">{nearest['material'].title()}</h4>
                    <p style="font-size: 13px; color: #475569; min-height: 45px;">Seller: {nearest['supplier_name']}<br>Location: {nearest['location']}</p>
                    <h2 style="color: #0284C7; margin: 10px 0; font-size: 24px;">{nearest['distance_km']:.1f} km</h2>
                    <p style="font-size: 11px; color: #64748B; margin: 0;">Shortest transport route</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Procure Nearest", key="btn_procure_near", use_container_width=True):
                    val = nearest['quantity'] * nearest['price_per_kg']
                    create_order(nearest['id'], user['id'], nearest['quantity'], val)
                    st.success("Nearest procured!")
                    st.rerun()
                    
            with col_award3:
                st.markdown(f"""
                <div class="reloop-card" style="border-color: #D97706; height: 260px;">
                    <h3 style="color: #D97706; font-size: 16px; margin-top: 0;">💰 Cheapest</h3>
                    <h4 style="margin: 10px 0; color: #0F172A;">{cheapest['material'].title()}</h4>
                    <p style="font-size: 13px; color: #475569; min-height: 45px;">Seller: {cheapest['supplier_name']}<br>Location: {cheapest['location']}</p>
                    <h2 style="color: #D97706; margin: 10px 0; font-size: 24px;">₹{cheapest['price_per_kg']:.1f}/kg</h2>
                    <p style="font-size: 11px; color: #64748B; margin: 0;">Lowest cost per unit</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Procure Cheapest", key="btn_procure_cheap", use_container_width=True):
                    val = cheapest['quantity'] * cheapest['price_per_kg']
                    create_order(cheapest['id'], user['id'], cheapest['quantity'], val)
                    st.success("Cheapest procured!")
                    st.rerun()
                    
            with col_award4:
                st.markdown(f"""
                <div class="reloop-card" style="border-color: #DB2777; height: 260px;">
                    <h3 style="color: #DB2777; font-size: 16px; margin-top: 0;">⭐ Highest Trust</h3>
                    <h4 style="margin: 10px 0; color: #0F172A;">{highest_trust['material'].title()}</h4>
                    <p style="font-size: 13px; color: #475569; min-height: 45px;">Seller: {highest_trust['supplier_name']}<br>Trust Score: {highest_trust['trust_score'] or 5.0:.1f}</p>
                    <h2 style="color: #DB2777; margin: 10px 0; font-size: 24px;">{highest_trust['trust_score'] or 5.0:.1f}/10</h2>
                    <p style="font-size: 11px; color: #64748B; margin: 0;">Vetted credentials index</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Procure Trustworthy", key="btn_procure_trust", use_container_width=True):
                    val = highest_trust['quantity'] * highest_trust['price_per_kg']
                    create_order(highest_trust['id'], user['id'], highest_trust['quantity'], val)
                    st.success("Most trusted procured!")
                    st.rerun()
            
            st.divider()
            
            # Full Matches List
            st.subheader("All Matches Ordered by Match Score")
            sorted_matches = sorted(matches, key=lambda x: x["match_score"], reverse=True)
            
            for m in sorted_matches:
                score_color = "#DC2626"
                if m["match_score"] >= 80.0:
                    score_color = "#059669"
                elif m["match_score"] >= 50.0:
                    score_color = "#D97706"
                    
                st.markdown(f"""
                <div class="reloop-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h4 style="margin: 0; color: #0F172A;">♻️ {m['material'].title()}</h4>
                        <div style="font-size: 18px; font-weight: bold; color: {score_color};">Match Score: {m['match_score']:.1f}%</div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; font-size: 13px; color: #334155; margin-bottom: 15px;">
                        <div><strong>Supplier:</strong> {m['supplier_name']}</div>
                        <div><strong>Distance:</strong> 📍 {m['distance_km']:.1f} km</div>
                        <div><strong>Price:</strong> ₹{m['price_per_kg']:.2f} / kg</div>
                        <div><strong>Available Quantity:</strong> {m['quantity']:.1f} {m['unit']}</div>
                        <div><strong>Carbon Offset:</strong> 🌱 {m['carbon_saved']:.2f} t CO₂</div>
                        <div><strong>Condition Quality:</strong> {m['condition'].upper()}</div>
                        <div><strong>Expiry / Lifetime:</strong> ⏳ {m['expiry_date'] or 'N/A'}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🛒 Procure {m['material']} ({m['quantity']} {m['unit']})", key=f"buy_match_{m['id']}", use_container_width=True):
                    total_value = m['quantity'] * m['price_per_kg']
                    create_order(m['id'], user['id'], m['quantity'], total_value)
                    st.success("Successfully purchased!")
                    st.rerun()

# Post Sourcing Request
st.divider()
st.subheader("📢 Post a Sourcing Request")
st.write("Can't find a supplier lot matching your specifications? Post a request so suppliers can see your sourcing needs in their feed!")

from db.db_utils import add_buyer_request

with st.form("buyer_sourcing_form"):
    req_mat_type = st.selectbox("Material Category Needed", ["Wood Waste", "Cotton Waste", "Textile Waste", "Plastic Waste", "Paper Waste", "Metal Scrap", "Organic Waste"])
    req_vol = st.number_input("Volume Needed (kg)", min_value=1.0, value=500.0)
    req_max_price = st.number_input("Maximum Budget Price (₹ / kg)", min_value=0.1, value=15.0)
    
    post_btn = st.form_submit_button("📢 Publish Sourcing Request")
    
if post_btn:
    add_buyer_request(user["id"], req_mat_type, req_vol, req_max_price)
    st.success(f"Successfully posted sourcing request for {req_vol} kg of {req_mat_type}!")
    st.toast("Request posted!", icon="📢")

