import streamlit as st
from price_engine import get_price
from material_analyzer_engine import analyze_listing
from carbon_engine import carbon_saved
from recommendation_engine import (
    recommend_transport_method, 
    calculate_circularity_score, 
    predict_demand
)
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

    quantity = 100.0
    unit = "kg"

    qty_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(kg|tons?|units?)",
        text_lower
    )

    if qty_match:
        quantity = float(qty_match.group(1))
        unit = qty_match.group(2)

    return {
        "material_type": material_type,
        "quantity": quantity,
        "unit": unit,
        "condition": "good",
        "summary": text
    }
# Ensure user is logged in
if not st.session_state.user or st.session_state.user["role"] != "supplier":
    st.warning("Please log in as a Supplier to view this page.")
    st.switch_page("supplier_login.py")
    st.stop()

st.title("🔬 AI Material Characterization & Analyzer")
st.caption("Perform deep AI analysis on complex, unstructured byproduct descriptions to extract parameters, prices, and circular scores.")

desc_input = st.text_area(
    "Paste Unstructured Material Description",
    placeholder="e.g. In our sawmill, we accumulated 15 sacks of cotton textiles offcuts. They weigh about 12 kg each. Clean, dry, cotton, white color. We are located near Vijayawada. What can we do with it?",
    height=150
)

if st.button("🔬 Analyze Material Lot", use_container_width=True):
    if not desc_input.strip():
        st.error("Please provide some text to analyze.")
    else:
        with st.spinner("Running material analyzer engine and AI model..."):
            try:
                # 1. Extracted info
                result = analyze_listing(desc_input)
                m_type = result.get("material_type", "wood")
                qty = float(result.get("quantity", 1.0))
                unit = result.get("unit", "kg")
                cond = result.get("condition", "good")
                summary = result.get("summary", "")
                
                # 2. Price suggestion
                suggested_unit_price = get_price(m_type)
                estimated_value = suggested_unit_price * qty
                
                # 3. Environmental footprint offset
                qty_kg = qty * 1000.0 if unit.lower() == "tons" else qty
                co2_offset = carbon_saved(m_type, qty_kg) / 1000.0 # metric tons
                
                # 4. Circularity Score
                score_input = {"material": m_type, "quantity": qty_kg}
                circ_score = calculate_circularity_score(score_input)
                
                # 5. Demand & Buyers
                demand = predict_demand(m_type)
                
                # 6. Transport recommendation
                transport_mode = recommend_transport_method(m_type)
                
                # Render Results
                st.success("Analysis complete!")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("### 📋 Characterization Profile")
                    st.markdown(f"""
                    <div class="reloop-card">
                        <h4 style="color:#00E676; margin:0 0 10px 0;">🔍 Extract Summary</h4>
                        <p style="color:white; font-style:italic;">"{summary}"</p>
                        <hr style="border-color:rgba(255,255,255,0.1)">
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px; font-size:14px; color:#bbb;">
                            <div><strong>Extracted Material:</strong> {m_type.upper()}</div>
                            <div><strong>Extracted Quantity:</strong> {qty} {unit}</div>
                            <div><strong>Extracted Condition:</strong> {cond.upper()}</div>
                            <div><strong>Recommended Logistics:</strong> {transport_mode}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("### 🌎 Circularity & Market Assessment")
                    st.markdown(f"""
                    <div class="reloop-card">
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; text-align:center;">
                            <div>
                                <h4 style="color:#888; font-size:13px; margin:0;">Circularity Rating</h4>
                                <h1 style="color:#00E676; margin:10px 0;">{circ_score} <span style="font-size:16px;">/ 100</span></h1>
                            </div>
                            <div>
                                <h4 style="color:#888; font-size:13px; margin:0;">Buyer Demand Level</h4>
                                <h1 style="color:#29b6f6; margin:10px 0;">{demand['level']}</h1>
                                <p style="color:#888; font-size:11px; margin:0;">{demand['interested_buyers']} buyers in region</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col2:
                    st.markdown("### 💰 Suggested Pricing")
                    st.markdown(f"""
                    <div class="reloop-card" style="text-align: center;">
                        <h4 style="color:#888; font-size:13px;">Unit Reference Price</h4>
                        <h2 style="color:white; margin:10px 0;">₹{suggested_unit_price:.2f} / kg</h2>
                        <h4 style="color:#888; font-size:13px; margin-top:20px;">Estimated Total Value</h4>
                        <h1 style="color:#00E676; margin:10px 0;">₹{estimated_value:,.2f}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("### 🌱 Carbon Offset")
                    st.markdown(f"""
                    <div class="reloop-card" style="text-align: center; border-color:#00E676;">
                        <h4 style="color:#888; font-size:13px;">CO₂ Diversion Potential</h4>
                        <h1 style="color:#00E676; margin:10px 0;">{co2_offset:.3f} t</h1>
                        <p style="color:#aaa; font-size:11px;">Offset achieved by keeping this material lot out of landfills.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                # JSON viewer
                with st.expander("🛠️ View Raw AI JSON Extraction Schema"):
                    st.json(result)
                    
            except Exception as e:
                st.error(f"Analysis failed: {e}")
