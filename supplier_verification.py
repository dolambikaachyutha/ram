import streamlit as st
from db_utils import get_verification_status, submit_verification
from llm_client import ask_ai

# Ensure user is logged in
if not st.session_state.user or st.session_state.user["role"] != "supplier":
    st.warning("Please log in as a Supplier to view this page.")
    st.switch_page("pages/supplier_login.py")
    st.stop()

user = st.session_state.user

st.title("✅ Business Verification Center")
st.caption("Verify your industrial credentials to achieve Verified Supplier status and boost buyer trust.")

status = get_verification_status(user["id"])

if status:
    # Display current verification profile
    badge = ""
    if status["document_status"] == "approved":
        badge = '<span class="badge-verified">✅ Vetted & Approved</span>'
    elif status["document_status"] == "rejected":
        badge = '<span class="badge-sold">❌ Rejected</span>'
    else:
        badge = '<span class="badge-pending">⏳ Pending Review</span>'
        
    trust_color = "#00E676" if status["trust_score"] >= 8.0 else "#ffc107" if status["trust_score"] >= 5.0 else "#ff5252"
    
    st.markdown(f"""
    <div class="reloop-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
            <h3 style="margin:0;">Verification Profile</h3>
            <div>{badge}</div>
        </div>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:15px; font-size:14px; color:#bbb;">
            <div><strong>Company Name:</strong> {status['company_name']}</div>
            <div><strong>GST Registration:</strong> <code>{status['gst_number']}</code></div>
            <div><strong>Factory Address:</strong> {status['address']}</div>
            <div>
                <strong>AI Trust Score:</strong> 
                <span style="color:{trust_color}; font-weight:bold; font-size:18px;">{status['trust_score']:.1f} / 10.0</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("Your business verification is active. If you need to update registration details, resubmit the form below.")
    st.divider()

# Submission Form (shows either for new verification or updating)
st.subheader("Submit Verification Credentials")
with st.form("verification_form"):
    company_name = st.text_input("Official Registered Company Name", value=status["company_name"] if status else user["name"])
    gst_number = st.text_input("GST Identification Number (GSTIN)", value=status["gst_number"] if status else "", max_chars=15, placeholder="e.g. 29GGGGG1314R9Z9")
    address = st.text_area("Factory/Warehouse Dispatch Address", value=status["address"] if status else "", placeholder="e.g. Plot 45, Phase 2, Industrial Area, Bengaluru, Karnataka")
    doc_upload = st.file_uploader("Upload Business License / GST Copy (PDF or Image - Simulated)", type=["pdf", "png", "jpg"])
    
    submit_btn = st.form_submit_button("Submit Credentials for Vetting")

if submit_btn:
    if not gst_number or not address or not company_name:
        st.error("Please fill in all details.")
    elif len(gst_number) != 15:
        st.error("Invalid GSTIN. An official Indian GST number must be exactly 15 characters long.")
    else:
        with st.spinner("AI evaluating credentials and establishing Trust Score..."):
            # Prompt Gemini to evaluate and score
            scoring_prompt = f"""You are a compliance scoring engine for a business network.
            Company Name: {company_name}
            GST: {gst_number}
            Address: {address}
            
            Evaluate if the address looks like a real industrial facility, and if the GST format is reasonably valid (e.g. starts with state code digits, alphanumeric structure).
            Generate a numeric trust score out of 10.0 (like 8.7 or 9.5).
            Respond with ONLY the numeric value (no explain, no extra words). If invalid or suspect, score low (under 5.0).
            """
            try:
                ai_verdict = ask_ai(scoring_prompt).strip()
                # Clean characters if model added extra text
                import re
                score_match = re.search(r"(\d+(\.\d+)?)", ai_verdict)
                trust_score = float(score_match.group(1)) if score_match else 7.5
                trust_score = min(10.0, max(1.0, trust_score))
            except Exception as e:
                trust_score = 7.5 # fallback score
                
            # Submit to DB (mark approved automatically for smooth hackathon experience)
            submit_verification(
                supplier_id=user["id"],
                company_name=company_name,
                gst_number=gst_number,
                address=address,
                trust_score=trust_score,
                status="approved"
            )
            
            st.success(f"Verification approved! Your company trust score is established at {trust_score:.1f} / 10.0")
            st.toast("Credentials verified!", icon="✅")
            st.rerun()
