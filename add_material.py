import streamlit as st
import datetime
import re

from db_utils import add_listing
from price_engine import get_price
from carbon_engine import carbon_saved
import re


def analyze_listing(text):
    text_lower = text.lower()

    material_type = "wood"

    if "cotton" in text_lower:
        material_type = "cotton"
    elif "plastic" in text_lower:
        material_type = "plastic"
    elif "paper" in text_lower:
        material_type = "paper"
    elif "metal" in text_lower:
        material_type = "metal"
    elif "textile" in text_lower or "fabric" in text_lower:
        material_type = "fabric"
    elif "organic" in text_lower:
        material_type = "organic"

    quantity = 100.0
    unit = "kg"

    qty_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(kg|tons?|units?)",
        text_lower
    )

    if qty_match:
        quantity = float(qty_match.group(1))
        unit = qty_match.group(2)

    condition = "good"

    if "excellent" in text_lower:
        condition = "excellent"
    elif "fair" in text_lower:
        condition = "fair"
    elif "poor" in text_lower:
        condition = "poor"

    return {
        "material_type": material_type,
        "quantity": quantity,
        "unit": unit,
        "condition": condition,
        "price": get_price(material_type),
        "lifetime_days": 30,
        "summary": text
    }
# -----------------------------
# Authentication Check
# -----------------------------
if "user" not in st.session_state:
    st.warning("Please log in as a Supplier to view this page.")
    st.switch_page("supplier_login.py")
    st.stop()

if st.session_state.user["role"] != "supplier":
    st.warning("Please log in as a Supplier to view this page.")
    st.switch_page("supplier_login.py")
    st.stop()

user = st.session_state.user

# -----------------------------
# Page Header
# -----------------------------
st.title("➕ List Secondary Raw Material")
st.caption(
    "Create a marketplace listing manually or use AI autofill."
)

# -----------------------------
# Session State Initialization
# -----------------------------
if "autofill" not in st.session_state:
    st.session_state.autofill = {
        "material": "Wood Waste",
        "quantity": 100.0,
        "unit": "kg",
        "price": 10.0,
        "location": "",
        "condition": "Good",
        "expiry_days": 30,
        "description": ""
    }

# -----------------------------
# AI Autofill
# -----------------------------
st.markdown("### 🪄 AI Smart Autofill")

with st.expander(
    "Type a quick description to autofill the form below:",
    expanded=True
):

    ai_desc = st.text_area(
        "Listing Description Draft",
        placeholder=(
            "e.g. We have 350 kg of wood scraps from "
            "construction trimmings in Bengaluru."
        ),
        key="ai_autofill_input"
    )

    if st.button(
        "🪄 Parse Description with AI",
        use_container_width=True
    ):

        if not ai_desc.strip():
            st.error("Please enter a description.")
        else:

            try:
                with st.spinner(
                    "Analyzing material description..."
                ):

                    result = analyze_listing(ai_desc)

                    extracted_mat = (
                        result.get(
                            "material_type",
                            "wood"
                        ).lower()
                    )

                    material_map = {
                        "wood": "Wood Waste",
                        "cotton": "Cotton Waste",
                        "fabric": "Textile Waste",
                        "plastic": "Plastic Waste",
                        "paper": "Paper Waste",
                        "metal": "Metal Scrap",
                        "organic": "Organic Waste"
                    }

                    mapped_material = material_map.get(
                        extracted_mat,
                        "Wood Waste"
                    )

                    suggested_price = get_price(
                        extracted_mat
                    )

                    loc_match = re.search(
                        r"in\s+([A-Za-z\s]+)",
                        ai_desc,
                        re.IGNORECASE
                    )

                    extracted_location = (
                        loc_match.group(1).strip()
                        if loc_match
                        else ""
                    )

                    extracted_price = result.get(
                        "price",
                        suggested_price
                    )

                    if extracted_price is None:
                        extracted_price = suggested_price

                    st.session_state.autofill = {
                        "material": mapped_material,
                        "quantity": float(
                            result.get(
                                "quantity",
                                100
                            )
                        ),
                        "unit": result.get(
                            "unit",
                            "kg"
                        ),
                        "price": float(
                            extracted_price
                        ),
                        "location": extracted_location,
                        "condition": result.get(
                            "condition",
                            "Good"
                        ).title(),
                        "expiry_days": int(
                            result.get(
                                "lifetime_days",
                                30
                            )
                        ),
                        "description": result.get(
                            "summary",
                            ai_desc
                        )
                    }

                    st.success(
                        "Fields extracted successfully."
                    )

                    st.rerun()

            except Exception as e:
                st.error(
                    f"AI parsing failed: {e}"
                )

st.divider()

# -----------------------------
# Listing Form
# -----------------------------
st.markdown("### 📝 Listing Parameters")

with st.form("add_material_form"):

    material_options = [
        "Wood Waste",
        "Cotton Waste",
        "Textile Waste",
        "Plastic Waste",
        "Paper Waste",
        "Metal Scrap",
        "Organic Waste"
    ]

    selected_material = (
        st.session_state.autofill["material"]
    )

    material_index = (
        material_options.index(
            selected_material
        )
        if selected_material
        in material_options
        else 0
    )

    material = st.selectbox(
        "Material Category",
        material_options,
        index=material_index
    )

    col1, col2 = st.columns(2)

    with col1:
        quantity = st.number_input(
            "Quantity",
            min_value=1.0,
            value=float(
                st.session_state.autofill[
                    "quantity"
                ]
            )
        )

    with col2:
        unit_options = [
            "kg",
            "tons",
            "units"
        ]

        unit_value = (
            st.session_state.autofill["unit"]
        )

        unit_index = (
            unit_options.index(unit_value)
            if unit_value in unit_options
            else 0
        )

        unit = st.selectbox(
            "Measurement Unit",
            unit_options,
            index=unit_index
        )

    col3, col4 = st.columns(2)

    with col3:
        price_per_kg = st.number_input(
            "Price (₹/kg)",
            min_value=0.1,
            value=float(
                st.session_state.autofill[
                    "price"
                ]
            )
        )

    with col4:
        location = st.text_input(
            "Location",
            value=st.session_state.autofill[
                "location"
            ]
        )

    condition_options = [
        "Excellent",
        "Good",
        "Fair",
        "Poor"
    ]

    condition = st.selectbox(
        "Condition",
        condition_options,
        index=condition_options.index(
            st.session_state.autofill[
                "condition"
            ]
        )
        if st.session_state.autofill[
            "condition"
        ] in condition_options
        else 1
    )

    expiry_date = st.date_input(
        "Expiry Date",
        value=(
            datetime.date.today()
            + datetime.timedelta(
                days=int(
                    st.session_state.autofill[
                        "expiry_days"
                    ]
                )
            )
        )
    )

    description = st.text_area(
        "Description",
        value=st.session_state.autofill[
            "description"
        ]
    )

    submit_btn = st.form_submit_button(
        "📢 Publish Material Listing",
        use_container_width=True
    )

# -----------------------------
# Save Listing
# -----------------------------
if submit_btn:

    if not location.strip():
        st.error(
            "Please provide a location."
        )

    elif expiry_date < datetime.date.today():
        st.error(
            "Expiry date cannot be in the past."
        )

    else:

        try:

            category_key = (
                material.split()[0]
                .lower()
            )

            qty_kg = (
                quantity * 1000
                if unit == "tons"
                else quantity
            )

            saved_carbon = (
                carbon_saved(
                    category_key,
                    qty_kg
                ) / 1000
            )

            add_listing(
                supplier_id=user["id"],
                material=material,
                quantity=quantity,
                unit=unit,
                price_per_kg=price_per_kg,
                location=location,
                condition=condition.lower(),
                description=description,
                carbon_saved=saved_carbon,
                expiry_date=expiry_date.strftime(
                    "%Y-%m-%d"
                )
            )

            st.success(
                "Listing published successfully!"
            )

            st.toast(
                "Listing Published!",
                icon="📢"
            )

            st.switch_page(
                "my_listings.py"
            )

        except Exception as e:
            st.error(
                f"Failed to publish listing: {e}"
            )
