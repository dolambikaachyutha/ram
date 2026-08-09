import streamlit as st
from db_utils import get_all_verifications

# Ensure user is logged in
if not st.session_state.user or st.session_state.user["role"] != "buyer":
    st.warning("Please log in as a Buyer to view this page.")
    st.switch_page("pages/buyer_login.py")
    st.stop()

st.title("✅ Supplier Verification Registry")
st.caption("Review supplier credentials, official GST registration status, and trust scores before procurement.")

verifications = get_all_verifications()

if not verifications:
    st.info("No suppliers have submitted verification details yet.")
else:
    st.markdown("### Vetted Supplier Registry")
    
    # We can display them as beautiful cards
    for v in verifications:
        # Determine status badge
        if v["document_status"] == "approved":
            status_badge = '<span class="badge-verified">✅ Vetted & Approved</span>'
        elif v["document_status"] == "rejected":
            status_badge = '<span class="badge-sold">❌ Rejected</span>'
        else:
            status_badge = '<span class="badge-pending">⏳ Under Review</span>'
            
        trust_color = "#ffc107"
        if v["trust_score"] >= 8.0:
            trust_color = "#00E676"
        elif v["trust_score"] < 5.0:
            trust_color = "#ff5252"
            
        st.markdown(f"""
        <div class="reloop-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h4 style="margin: 0; font-size: 18px; color: white;">🏭 {v['company_name']}</h4>
                <div>{status_badge}</div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; font-size: 14px; color: #bbb; margin-top: 10px;">
                <div><strong>GST registration:</strong> <code>{v['gst_number']}</code></div>
                <div><strong>Registered Address:</strong> {v['address']}</div>
                <div><strong>Supplier Email:</strong> {v['supplier_email']}</div>
                <div>
                    <strong>AI Trust Index:</strong> 
                    <span style="color: {trust_color}; font-weight: bold; font-size: 16px;">{v['trust_score']:.1f} / 10.0</span>
                </div>
            </div>
            <div style="background: rgba(0, 230, 118, 0.05); padding: 10px; border-radius: 8px; margin-top: 15px; font-size: 13px; color: #ccc; border: 1px solid rgba(0, 230, 118, 0.1);">
                💡 <strong>Trust Score Breakdown:</strong> Score calculated by evaluating GST format correctness, geographic proximity to logistics networks, business email verification, and listing accuracy logs.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("") # spacing
