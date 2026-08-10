import streamlit as st
import pandas as pd
from db_utils import get_supplier_orders

# -----------------------------------------
# Authentication
# -----------------------------------------

if "user" not in st.session_state:
    st.warning("Please log in as a Supplier.")
    st.switch_page("supplier_login.py")
    st.stop()

if st.session_state.user["role"] != "supplier":
    st.warning("Please log in as a Supplier.")
    st.switch_page("supplier_login.py")
    st.stop()

user = st.session_state.user

# -----------------------------------------
# Page Header
# -----------------------------------------

st.title("📈 Supplier Analytics Dashboard")
st.caption(
    "Monitor revenue, sales performance, transactions and business growth."
)

# -----------------------------------------
# Load Orders
# -----------------------------------------

try:
    orders = get_supplier_orders(user["id"])
except Exception as e:
    st.error(f"Database Error: {e}")
    st.stop()

# -----------------------------------------
# No Orders
# -----------------------------------------

if not orders:
    st.info(
        "No transactions available yet. "
        "Analytics will appear after buyers purchase your materials."
    )
    st.stop()

# -----------------------------------------
# DataFrame
# -----------------------------------------

df = pd.DataFrame(orders)

# Debug Section
with st.expander("🔍 Database Records"):
    st.write("Available Columns:")
    st.write(df.columns.tolist())
    st.dataframe(df)

# -----------------------------------------
# Date Handling
# -----------------------------------------

if "created_at" in df.columns:
    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    df["Date"] = df["created_at"].dt.date

# -----------------------------------------
# KPI Calculations
# -----------------------------------------

total_revenue = (
    df["total_price"].sum()
    if "total_price" in df.columns
    else 0
)

average_order = (
    df["total_price"].mean()
    if "total_price" in df.columns
    else 0
)

total_quantity = (
    df["quantity"].sum()
    if "quantity" in df.columns
    else 0
)

total_transactions = len(df)

# -----------------------------------------
# KPI Cards
# -----------------------------------------

st.markdown("## 📊 Business Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "💰 Revenue",
        f"₹{total_revenue:,.2f}"
    )

with c2:
    st.metric(
        "📦 Quantity Sold",
        f"{total_quantity:,.1f}"
    )

with c3:
    st.metric(
        "🛒 Transactions",
        total_transactions
    )

with c4:
    st.metric(
        "📈 Avg Order",
        f"₹{average_order:,.2f}"
    )

st.divider()

# -----------------------------------------
# Revenue Table
# -----------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("💰 Revenue Trend")

    if (
        "Date" in df.columns
        and "total_price" in df.columns
    ):

        revenue_df = (
            df.groupby("Date")["total_price"]
            .sum()
            .reset_index()
        )

        st.dataframe(
            revenue_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Revenue information unavailable.")

# -----------------------------------------
# Material Sales Table
# -----------------------------------------

with col2:

    st.subheader("♻️ Material Sales")

    if (
        "material" in df.columns
        and "quantity" in df.columns
    ):

        material_df = (
            df.groupby("material")["quantity"]
            .sum()
            .reset_index()
        )

        st.dataframe(
            material_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Material sales information unavailable.")

st.divider()

# -----------------------------------------
# Material Performance
# -----------------------------------------

if (
    "material" in df.columns
    and "quantity" in df.columns
):

    st.subheader("🏭 Material Performance")

    material_summary = (
        df.groupby("material")
        .agg(
            Total_Quantity=("quantity", "sum")
        )
        .reset_index()
    )

    st.dataframe(
        material_summary,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# -----------------------------------------
# Transaction History
# -----------------------------------------

st.subheader("📋 Transaction History")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

# -----------------------------------------
# Summary
# -----------------------------------------

st.success(
    f"Successfully analyzed {total_transactions} transactions."
)
