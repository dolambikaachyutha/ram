import streamlit as st
import pandas as pd
from db_utils import get_supplier_listings, get_supplier_orders

# Ensure user is logged in
if "user" not in st.session_state or not st.session_state.user:
    st.warning("Please log in as a Supplier to view this page.")
    st.switch_page("supplier_login.py")
    st.stop()

if st.session_state.user["role"] != "supplier":
    st.warning("Please log in as a Supplier to view this page.")
    st.switch_page("supplier_login.py")
    st.stop()

user = st.session_state.user

st.title(f"🏭 {user['name']} Control Center")
st.caption(
    "Supplier Dashboard • Manage your circular material inventory, sales metrics, and impact."
)

# Fetch data
try:
    listings = get_supplier_listings(user["id"])
    orders = get_supplier_orders(user["id"])
except Exception as e:
    st.error(f"Database Error: {e}")
    st.stop()

# Safe calculations
total_listed = len(listings)

total_sold = len(
    [l for l in listings if l.get("status", "").lower() == "sold"]
)

total_earnings = sum(
    float(o.get("total_price", 0))
    for o in orders
)

total_co2 = sum(
    float(l.get("carbon_saved", 0))
    for l in listings
)

# Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Material Listed",
        total_listed,
        help="Material lots listed"
    )

with col2:
    st.metric(
        "Lots Sold",
        total_sold,
        help="Transferred to circular chain"
    )

with col3:
    st.metric(
        "Total Earnings",
        f"₹{total_earnings:,.2f}",
        help="Revenue generated"
    )

with col4:
    st.metric(
        "CO₂ Diverted",
        f"{total_co2:,.2f} t",
        help="Offset savings achieved"
    )

st.divider()

# Analytics
st.subheader("📊 Listing Distribution")

if listings:

    try:
        df = pd.DataFrame(listings)

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("##### Material Types Listed")

            if "material" in df.columns:

                mat_counts = (
                    df["material"]
                    .value_counts()
                    .reset_index()
                )

                mat_counts.columns = [
                    "Material",
                    "Count"
                ]

                # Using dataframe instead of bar_chart
                st.dataframe(
                    mat_counts,
                    use_container_width=True
                )

            else:
                st.info("No material data available.")

        with col_chart2:
            st.markdown("##### Listing Status")

            if "status" in df.columns:

                status_counts = (
                    df["status"]
                    .value_counts()
                    .reset_index()
                )

                status_counts.columns = [
                    "Status",
                    "Count"
                ]

                st.dataframe(
                    status_counts,
                    use_container_width=True
                )

            else:
                st.info("No status data available.")

        st.markdown("### 📄 Current Listings")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Analytics Error: {e}")

else:
    st.info(
        "No materials listed yet. Use the Add Material page "
        "to create your first waste listing!"
    )

# Quick Actions
st.markdown("---")
st.markdown("### 🚀 Quick Actions")

col_act1, col_act2 = st.columns(2)

with col_act1:
    if st.button(
        "➕ Add Waste Material Lot",
        use_container_width=True
    ):
        st.switch_page("add_material.py")

with col_act2:
    if st.button(
        "✅ Verify Your Business",
        use_container_width=True
    ):
        st.switch_page("supplier_verification.py")
