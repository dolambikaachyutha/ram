import streamlit as st
import pandas as pd
from db.db_utils import get_listings
from engine.price_engine import get_price, PRICE_DB

# Ensure user is logged in
if not st.session_state.user or st.session_state.user["role"] != "buyer":
    st.warning("Please log in as a Buyer to view this page.")
    st.switch_page("pages/buyer_login.py")
    st.stop()

st.title("⚖️ Price Intelligence & Market Comparison")
st.caption("Compare supplier listing prices against estimated global secondary material index rates.")

# Material category selector
material_cat = st.selectbox(
    "Select Material Class",
    ["Wood", "Plastic", "Paper", "Fabric", "Metal"]
)

# Reference market price
reference_price = get_price(material_cat)

st.markdown(f"""
<div class="reloop-card" style="border-color: #A7F3D0; background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h4 style="color: #047857; margin: 0;">Market Index Rate ({material_cat})</h4>
            <h1 style="color: #065F46 !important; -webkit-text-fill-color: #065F46 !important; margin: 5px 0; filter: none !important;">₹{reference_price:.2f} <span style="font-size: 16px; color:#047857;">/ kg</span></h1>
        </div>
        <div style="font-size: 40px;">📈</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Fetch listings of this category
listings = get_listings(material_type=material_cat)

if not listings:
    st.info(f"There are currently no active listings for {material_cat} to run a price comparison.")
else:
    # Prepare comparison data
    compare_data = []
    fair_deals = []
    
    for l in listings:
        diff = l["price_per_kg"] - reference_price
        pct_diff = (diff / reference_price) * 100
        l_info = {
            "Listing": f"{l['supplier_name']} - {l['material'][:15]}",
            "Listing Price (₹)": l["price_per_kg"],
            "Market Rate (₹)": reference_price,
            "Diff (₹)": round(diff, 2),
            "Diff (%)": round(pct_diff, 1)
        }
        compare_data.append(l_info)
        
        if l["price_per_kg"] <= reference_price:
            fair_deals.append(l)

    df_compare = pd.DataFrame(compare_data)
    
    col_chart, col_stats = st.columns([2, 1])
    
    with col_chart:
        st.markdown("##### Listing Price vs Market Index Rate")
        # Bar chart comparison
        chart_df = df_compare.set_index("Listing")[["Listing Price (₹)", "Market Rate (₹)"]]
        st.bar_chart(chart_df, color=["#059669", "#0284C7"])
        
    with col_stats:
        st.markdown("##### Price Health Check")
        avg_price = df_compare["Listing Price (₹)"].mean()
        price_health = "Excellent Sourcing Zone" if avg_price <= reference_price else "High-Cost Sourcing Zone"
        health_color = "#059669" if avg_price <= reference_price else "#DC2626"
        
        st.markdown(f"""
        <div class="reloop-card" style="text-align: center; border-color: {health_color};">
            <h4 style="color:#64748B; margin: 0;">Average Listing Price</h4>
            <h2 style="color: #0F172A !important; -webkit-text-fill-color: #0F172A !important; margin: 10px 0;">₹{avg_price:.2f} / kg</h2>
            <div style="font-size: 14px; font-weight: bold; color: {health_color}; margin-top: 10px;">
                {price_health}
            </div>
            <p style="color:#64748B; font-size:11px; margin-top: 5px;">
                Average is {abs((avg_price - reference_price)/reference_price*100):.1f}% 
                {'below' if avg_price <= reference_price else 'above'} market index rate.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    # Fair Value Deals list
    st.subheader("💡 Highlighted Fair-Value Deals")
    if fair_deals:
        st.success(f"Located {len(fair_deals)} deal(s) priced at or below the market index rate!")
        for deal in fair_deals:
            col_d1, col_d2 = st.columns([4, 1])
            with col_d1:
                st.markdown(f"""
                <div class="reloop-card">
                    <div style="display:flex; justify-content:space-between; align-items: center;">
                        <h4 style="margin:0; color:#059669;">{deal['material'].title()} (by {deal['supplier_name']})</h4>
                        <span class="badge-verified">Save {((reference_price - deal['price_per_kg'])/reference_price*100):.0f}%</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-top:10px; font-size:13px; color:#334155;">
                        <div>📍 {deal['location']}</div>
                        <div>Price: ₹{deal['price_per_kg']:.2f}/kg (Market: ₹{reference_price:.2f})</div>
                        <div>Quantity: {deal['quantity']} {deal['unit']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_d2:
                st.write("")
                st.write("")
                if st.button("🛒 Procure Deal", key=f"deal_buy_{deal['id']}", use_container_width=True):
                    val = deal['quantity'] * deal['price_per_kg']
                    create_order(deal['id'], user['id'], deal['quantity'], val)
                    st.success("Deal procured!")
                    st.rerun()
    else:
        st.warning("All current listings for this material are priced above the reference index. Keep an eye out or explore similar materials!")

st.divider()
st.subheader("🔍 Index Reference Database")
st.dataframe(pd.DataFrame(list(PRICE_DB.items()), columns=["Material Class", "Index Price (₹ / kg)"]), use_container_width=True)
