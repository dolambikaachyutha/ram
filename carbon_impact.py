import streamlit as st
import pandas as pd
import sqlite3
from db.db_utils import get_buyer_orders, get_connection

# Ensure user is logged in
if not st.session_state.user or st.session_state.user["role"] != "buyer":
    st.warning("Please log in as a Buyer to view this page.")
    st.switch_page("pages/buyer_login.py")
    st.stop()

user = st.session_state.user

st.title("🌱 Carbon Impact Tracker")
st.caption("Measure and share the environmental footprint offset achieved by procuring circular resources.")

# Fetch Buyer Orders
orders = get_buyer_orders(user["id"])
total_co2 = sum(o["carbon_saved"] for o in orders)

st.subheader("Your Cumulative Environmental Impact")

# Render metrics in columns
col1, col2, col3, col4 = st.columns(4)

# 1 Ton of CO2 equivalents:
# ~16.5 tree seedlings grown for 10 years
# ~0.22 typical passenger vehicles driven for a year
# ~121,643 smartphones charged
# ~0.12 home electricity use for a year

trees_equivalent = total_co2 * 16.5
cars_equivalent = total_co2 * 0.22
phones_equivalent = total_co2 * 121643
homes_equivalent = total_co2 * 0.12

with col1:
    st.markdown(f"""
    <div class="reloop-card" style="text-align: center; border-color: #059669; height: 180px;">
        <div style="font-size: 30px; margin-bottom: 5px;">🌲</div>
        <h4 style="color:#64748B; font-size:13px; margin: 0;">Tree Seedlings</h4>
        <h2 style="color:#059669 !important; -webkit-text-fill-color:#059669 !important; margin: 10px 0;">{trees_equivalent:,.1f}</h2>
        <p style="color:#475569; font-size:11px; margin: 0;">Seedlings grown for 10 yrs</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="reloop-card" style="text-align: center; border-color: #059669; height: 180px;">
        <div style="font-size: 30px; margin-bottom: 5px;">🚗</div>
        <h4 style="color:#64748B; font-size:13px; margin: 0;">Cars Off Road</h4>
        <h2 style="color:#059669 !important; -webkit-text-fill-color:#059669 !important; margin: 10px 0;">{cars_equivalent:,.2f}</h2>
        <p style="color:#475569; font-size:11px; margin: 0;">Passenger vehicles off road/yr</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="reloop-card" style="text-align: center; border-color: #059669; height: 180px;">
        <div style="font-size: 30px; margin-bottom: 5px;">📱</div>
        <h4 style="color:#64748B; font-size:13px; margin: 0;">Phone Charges</h4>
        <h2 style="color:#059669 !important; -webkit-text-fill-color:#059669 !important; margin: 10px 0;">{phones_equivalent:,.0f}</h2>
        <p style="color:#475569; font-size:11px; margin: 0;">Smartphones charged avoided</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="reloop-card" style="text-align: center; border-color: #059669; height: 180px;">
        <div style="font-size: 30px; margin-bottom: 5px;">🏠</div>
        <h4 style="color:#64748B; font-size:13px; margin: 0;">Home Power</h4>
        <h2 style="color:#059669 !important; -webkit-text-fill-color:#059669 !important; margin: 10px 0;">{homes_equivalent:,.2f}</h2>
        <p style="color:#475569; font-size:11px; margin: 0;">Homes electricity offset/yr</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Leaderboard Query
st.subheader("🏆 Global Carbon Leaderboard")
st.write("See who's driving the circular economy forward. Join forces to scale carbon offsets!")

conn = get_connection()
cur = conn.cursor()

# Get all buyers and sum carbon saved from their purchases
cur.execute("""
SELECT u.name as buyer_name, COUNT(o.id) as total_purchases, COALESCE(SUM(l.carbon_saved), 0.0) as carbon_saved
FROM users u
LEFT JOIN orders o ON u.id = o.buyer_id
LEFT JOIN listings l ON o.listing_id = l.id
WHERE u.role = 'buyer'
GROUP BY u.id
ORDER BY carbon_saved DESC, total_purchases DESC
""")

rows = cur.fetchall()
conn.close()

if not rows:
    st.info("No buyers logged on the leaderboard.")
else:
    leaderboard_data = []
    for rank, row in enumerate(rows, 1):
        leaderboard_data.append({
            "Rank": f"🏆 #{rank}" if rank == 1 else f"🥈 #{rank}" if rank == 2 else f"🥉 #{rank}" if rank == 3 else f"#{rank}",
            "Organization Name": row["buyer_name"],
            "Procured Listings": row["total_purchases"],
            "CO₂ Saved (Metric Tons)": round(row["carbon_saved"], 3)
        })
        
    df_leaderboard = pd.DataFrame(leaderboard_data)
    st.dataframe(df_leaderboard, use_container_width=True, hide_index=True)
    
    st.info("💡 Tip: Want to move up the leaderboard? Procure high-mass materials like plastics or metals, which divert larger quantities of landfill waste and yield higher carbon coefficients!")
