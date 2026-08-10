import streamlit as st
import pandas as pd

from db_utils import get_listings, create_order
from price_engine import get_price, PRICE_DB


# Ensure user is logged in
if (
    "user" not in st.session_state
    or not st.session_state.user
    or st.session_state.user["role"] != "buyer"
):
    st.warning("Please log in as a Buyer to view this page.")
    st.switch_page("buyer_login.py")
    st.stop()


st.title("⚖️ Price Intelligence & Market Comparison")
st.caption(
    "Compare supplier listing prices against estimated global secondary material index rates."
)

# Material category selector
material_cat = st.selectbox(
    "Select Material Class",
    ["Wood", "Plastic", "Paper", "Fabric", "Metal"]
)

# Reference market price
reference_price = get_price(material_cat)

st.metric(
    "Current Market Index Rate",
    f"₹{reference_price:.2f}/kg"
)

# Fetch listings
listings = get_listings(material_type=material_cat)

if not listings:
    st.info(
        f"There are currently no active listings for {material_cat} "
        "to run a price comparison."
    )

else:
    compare_data = []
    fair_deals = []

    for l in listings:
        diff = l["price_per_kg"] - reference_price
        pct_diff = (diff / reference_price) * 100

        compare_data.append(
            {
                "Listing": f"{l['supplier_name']} - {l['material'][:15]}",
                "Listing Price (₹)": l["price_per_kg"],
                "Market Rate (₹)": reference_price,
                "Diff (₹)": round(diff, 2),
                "Diff (%)": round(pct_diff, 1),
            }
        )

        if l["price_per_kg"] <= reference_price:
            fair_deals.append(l)

    df_compare = pd.DataFrame(compare_data)

    col_chart, col_stats = st.columns([2, 1])

    with col_chart:
        st.markdown("##### Listing Price vs Market Index Rate")

        chart_df = df_compare.set_index("Listing")[
            ["Listing Price (₹)", "Market Rate (₹)"]
        ]

        # Using dataframe instead of st.bar_chart
        # to avoid Altair/Python 3.14 issues
        st.dataframe(
            chart_df,
            use_container_width=True
        )

    with col_stats:
        st.markdown("##### Price Health Check")

        avg_price = df_compare["Listing Price (₹)"].mean()

        price_health = (
            "Excellent Sourcing Zone"
            if avg_price <= reference_price
            else "High-Cost Sourcing Zone"
        )

        health_color = (
            "#059669"
            if avg_price <= reference_price
            else "#DC2626"
        )

        percentage = abs(
            (avg_price - reference_price)
            / reference_price
            * 100
        )

        st.markdown(
            f"""
            <div style="
                padding:15px;
                border:2px solid {health_color};
                border-radius:12px;
                text-align:center;
            ">
                <h4>Average Listing Price</h4>
                <h2>₹{avg_price:.2f}/kg</h2>
                <div style="color:{health_color};font-weight:bold;">
                    {price_health}
                </div>
                <p>
                    Average is {percentage:.1f}%
                    {'below' if avg_price <= reference_price else 'above'}
                    market index rate.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("💡 Highlighted Fair-Value Deals")

    if fair_deals:
        st.success(
            f"Located {len(fair_deals)} deal(s) priced at or below the market index rate!"
        )

        for deal in fair_deals:
            col_d1, col_d2 = st.columns([4, 1])

            with col_d1:
                savings = (
                    (reference_price - deal["price_per_kg"])
                    / reference_price
                    * 100
                )

                st.markdown(
                    f"""
                    <div style="
                        border:1px solid #E2E8F0;
                        border-radius:12px;
                        padding:12px;
                        margin-bottom:10px;
                    ">
                        <h4 style="color:#059669;">
                            {deal['material'].title()}
                            (by {deal['supplier_name']})
                        </h4>

                        <p>
                            📍 {deal['location']}<br>
                            💰 ₹{deal['price_per_kg']:.2f}/kg
                            (Market ₹{reference_price:.2f})<br>
                            📦 Quantity:
                            {deal['quantity']} {deal['unit']}<br>
                            🎯 Save {savings:.0f}%
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_d2:
                st.write("")
                st.write("")

                if st.button(
                    "🛒 Procure Deal",
                    key=f"deal_buy_{deal['id']}",
                    use_container_width=True,
                ):
                    value = (
                        deal["quantity"]
                        * deal["price_per_kg"]
                    )

                    create_order(
                        deal["id"],
                        st.session_state.user["id"],
                        deal["quantity"],
                        value,
                    )

                    st.success("Deal procured successfully!")
                    st.rerun()

    else:
        st.warning(
            "All current listings for this material are priced above the reference index."
        )

st.divider()

st.subheader("🔍 Index Reference Database")

index_df = pd.DataFrame(
    list(PRICE_DB.items()),
    columns=[
        "Material Class",
        "Index Price (₹ / kg)"
    ]
)

st.dataframe(
    index_df,
    use_container_width=True
)
