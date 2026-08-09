import streamlit as st
import pandas as pd
from db.db_utils import get_supplier_orders

# Ensure user is logged in
if not st.session_state.user or st.session_state.user["role"] != "supplier":
    st.warning("Please log in as a Supplier to view this page.")
    st.switch_page("pages/supplier_login.py")
    st.stop()

user = st.session_state.user

st.title("📈 Commercial Analytics & Financial Metrics")
st.caption("Review sales statistics, revenue timelines, and circular economy transaction metrics.")

# Fetch supplier orders
orders = get_supplier_orders(user["id"])

if not orders:
    st.info("You haven't completed any transactions yet. When buyers procure your materials, sales metrics will display here!")
else:
    df = pd.DataFrame(orders)
    # Parse dates
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["Date"] = df["created_at"].dt.date
    
    # Financial KPI summary cards
    total_rev = df["total_price"].sum()
    avg_order = df["total_price"].mean()
    total_qty = df["quantity"].sum()
    total_txs = len(df)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"₹{total_rev:,.2f}")
    with col2:
        st.metric("Average Deal Value", f"₹{avg_order:,.2f}")
    with col3:
        st.metric("Volume Transferred", f"{total_qty:,.1f} kg")
    with col4:
        st.metric("Total Transactions", total_txs)
        
    st.divider()
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("##### Revenue Timeline")
        daily_rev = df.groupby("Date")["total_price"].sum().reset_index()
        daily_rev = daily_rev.sort_values("Date")
        st.line_chart(daily_rev.set_index("Date"), y="total_price", color="#00E676")
        
    with col_chart2:
        st.markdown("##### Sales Volume by Material Category")
        mat_sales = df.groupby("material")["quantity"].sum().reset_index()
        st.bar_chart(mat_sales.set_index("material"), y="quantity", color="#123524")
        
    # Transaction detail sheet
    st.subheader("📋 Completed Transaction Details")
    tx_display = df.rename(columns={
        "id": "Transaction ID",
        "material": "Material Category",
        "quantity": "Quantity Sold (kg)",
        "price_per_kg": "Price per kg",
        "total_price": "Total Earnings (₹)",
        "buyer_name": "Procured By Organization",
        "created_at": "Transaction Timestamp"
    })
    st.dataframe(tx_display[[
        "Transaction ID", "Material Category", "Quantity Sold (kg)", 
        "Price per kg", "Total Earnings (₹)", "Procured By Organization", "Transaction Timestamp"
    ]], use_container_width=True, hide_index=True)
