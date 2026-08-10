import streamlit as st
import pandas as pd
from db_utils import get_buyer_orders

# Ensure user is logged in
if "user" not in st.session_state or not st.session_state.user:
    st.warning("Please log in as a Buyer to view this page.")
    st.switch_page("buyer_login.py")
    st.stop()

if st.session_state.user["role"] != "buyer":
    st.warning("Please log in as a Buyer to view this page.")
    st.switch_page("buyer_login.py")
    st.stop()

user = st.session_state.user

st.title(f"📊 Welcome, {user['name']}")
st.caption("Buyer Dashboard • View your circular procurement and environmental metrics.")

# Fetch orders
try:
    orders = get_buyer_orders(user["id"])
except Exception as e:
    st.error(f"Failed to load orders: {e}")
    st.stop()

# Metrics
total_procured = sum(float(o.get("quantity", 0)) for o in orders)
total_spent = sum(float(o.get("total_price", 0)) for o in orders)
total_co2 = sum(float(o.get("carbon_saved", 0)) for o in orders)
order_count = len(orders)

# Metric Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Materials Purchased",
        value=f"{total_procured:,.1f} kg"
    )

with col2:
    st.metric(
        label="Total Spent",
        value=f"₹{total_spent:,.2f}"
    )

with col3:
    st.metric(
        label="CO₂ Saved",
        value=f"{total_co2:,.2f} t"
    )

with col4:
    st.metric(
        label="Transactions",
        value=order_count
    )

st.divider()

st.subheader("📦 Procurement & Impact Analytics")

if orders:

    try:
        df = pd.DataFrame(orders)

        st.write("Loaded Orders:", len(df))

        # Date processing
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(
                df["created_at"],
                errors="coerce"
            )

            df = df.dropna(subset=["created_at"])

            if not df.empty:
                df["Date"] = df["created_at"].dt.date

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("##### Spending Timeline")

            if (
                "Date" in df.columns and
                "total_price" in df.columns
            ):
                daily_spend = (
                    df.groupby("Date")["total_price"]
                    .sum()
                    .reset_index()
                    .sort_values("Date")
                )

                # Use dataframe instead of line_chart
                # if Altair causes deployment issues
                st.dataframe(
                    daily_spend,
                    use_container_width=True
                )
            else:
                st.info("No spending data available.")

        with chart_col2:
            st.markdown("##### Material Procurement Breakdown")

            if (
                "material" in df.columns and
                "quantity" in df.columns
            ):
                mat_breakdown = (
                    df.groupby("material")["quantity"]
                    .sum()
                    .reset_index()
                )

                st.dataframe(
                    mat_breakdown,
                    use_container_width=True
                )
            else:
                st.info("No material data available.")

        st.markdown("### 📄 Purchase History")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Analytics error: {e}")

else:
    st.info(
        "You haven't made any purchases yet. "
        "Head over to the Marketplace or AI Matcher "
        "to find waste materials!"
    )

# Quick Actions
st.markdown("---")
st.markdown("### 🚀 Quick Actions")

act_col1, act_col2 = st.columns(2)

with act_col1:
    if st.button(
        "🛒 Open Marketplace",
        use_container_width=True
    ):
        st.switch_page("marketplace.py")

with act_col2:
    if st.button(
        "🤖 Find Supplier with AI Matcher",
        use_container_width=True
    ):
        st.switch_page("ai_matcher.py")
