import streamlit as st

# MUST BE FIRST STREAMLIT CALL
st.set_page_config(
    page_title="ReLoop - AI Circular Economy",
    page_icon="♻️",
    layout="wide"
)

# Initialize Session State
if "user" not in st.session_state:
    st.session_state.user = None

# Custom CSS for executive white theme visual style, premium typography & animations
st.markdown("""
<style>
    /* Import modern typography from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Sora:wght@300;400;600;700;800&display=swap');
    
    /* Apply primary font globally to Streamlit containers */
    html, body, [class*="css"], .stApp, .stAppHeader, .stAppViewContainer {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #0F172A !important;
    }
    
    /* Executive light theme background */
    .stApp {
        background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%) !important;
    }
    
    /* --- AESTHETIC HEADINGS --- */
    h1 {
        font-family: 'Sora', sans-serif !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #0F172A 0%, #059669 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        letter-spacing: -1.5px !important;
        padding-bottom: 12px !important;
        margin-top: 15px !important;
        margin-bottom: 25px !important;
        filter: drop-shadow(0px 2px 8px rgba(5, 150, 105, 0.12)) !important;
    }
    
    h2 {
        font-family: 'Sora', sans-serif !important;
        font-weight: 700 !important;
        background: linear-gradient(90deg, #1E293B 0%, #047857 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        letter-spacing: -1px !important;
        margin-top: 30px !important;
        margin-bottom: 15px !important;
        border-bottom: 1px solid #E2E8F0 !important;
        padding-bottom: 8px !important;
    }
    
    h3 {
        font-family: 'Sora', sans-serif !important;
        font-weight: 600 !important;
        color: #059669 !important;
        letter-spacing: -0.5px !important;
        margin-top: 20px !important;
    }
    
    h4, h5, h6 {
        font-family: 'Sora', sans-serif !important;
        font-weight: 600 !important;
        color: #0F172A !important;
        letter-spacing: -0.2px !important;
    }

    /* --- SIDEBAR BEAUTIFICATION --- */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    
    [data-testid="stSidebarNav"] {
        background-color: transparent !important;
        padding-top: 15px !important;
    }
    
    /* Style sidebar links */
    [data-testid="stSidebarNav"] ul li a {
        border-radius: 12px !important;
        margin: 6px 12px !important;
        color: #334155 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        padding: 10px 14px !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    
    /* Ensure internal link labels are enlarged too */
    [data-testid="stSidebarNav"] ul li a span, 
    [data-testid="stSidebarNav"] ul li a p {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }
    
    [data-testid="stSidebarNav"] ul li a:hover {
        background-color: rgba(5, 150, 105, 0.08) !important;
        color: #059669 !important;
        transform: translateX(3px) !important;
    }
    [data-testid="stSidebarNav"] ul li a:hover span,
    [data-testid="stSidebarNav"] ul li a:hover p {
        color: #059669 !important;
    }
    
    /* Style active page link */
    [data-testid="stSidebarNav"] ul li a[aria-current="page"] {
        background-color: rgba(5, 150, 105, 0.12) !important;
        color: #047857 !important;
        font-weight: 700 !important;
        border-left: 4px solid #059669 !important;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.08) !important;
    }
    [data-testid="stSidebarNav"] ul li a[aria-current="page"] span,
    [data-testid="stSidebarNav"] ul li a[aria-current="page"] p {
        color: #047857 !important;
        font-weight: 700 !important;
    }

    /* Style sidebar section headers (e.g. RELOOP, ACCESS PORTALS) */
    [data-testid="stSidebarNav"] div {
        font-size: 13px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        color: #059669 !important;
    }

    /* --- WHITE CARDS --- */
    .reloop-card {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 18px !important;
        padding: 24px !important;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04) !important;
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    
    .reloop-card:hover {
        transform: translateY(-4px) !important;
        border-color: #059669 !important;
        box-shadow: 0 12px 30px rgba(5, 150, 105, 0.12) !important;
    }
    
    /* --- METRIC CARD OVERHAUL --- */
    div[data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 18px !important;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03) !important;
        transition: all 0.25s ease !important;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(5, 150, 105, 0.4) !important;
        box-shadow: 0 6px 20px rgba(5, 150, 105, 0.08) !important;
    }
    div[data-testid="stMetricLabel"] > div {
        color: #64748B !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }
    div[data-testid="stMetricVal"] > div {
        color: #059669 !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        margin-top: 5px !important;
    }
    
    /* --- FORM STYLING --- */
    div[data-testid="stForm"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 20px !important;
        padding: 30px !important;
        box-shadow: 0 8px 30px rgba(15, 23, 42, 0.04) !important;
    }

    /* Badges */
    .badge-verified {
        background-color: rgba(5, 150, 105, 0.1);
        color: #047857;
        padding: 6px 12px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
        border: 1px solid rgba(5, 150, 105, 0.3);
        display: inline-block;
        letter-spacing: 0.5px;
    }
    .badge-pending {
        background-color: rgba(217, 119, 6, 0.1);
        color: #B45309;
        padding: 6px 12px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
        border: 1px solid rgba(217, 119, 6, 0.3);
        display: inline-block;
        letter-spacing: 0.5px;
    }
    .badge-sold {
        background-color: rgba(225, 29, 72, 0.1);
        color: #BE123C;
        padding: 6px 12px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
        border: 1px solid rgba(225, 29, 72, 0.3);
        display: inline-block;
        letter-spacing: 0.5px;
    }

    /* --- MOTION / ANIMATIONS --- */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(14px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .reloop-card, .stButton, div[data-testid="stMetric"], .stDataFrame, .element-container, div[data-testid="stForm"] {
        animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    /* --- BUTTON CUSTOMIZATION --- */
    div.stButton > button {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 0.2px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 4px 14px rgba(5, 150, 105, 0.25) !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 8px 22px rgba(5, 150, 105, 0.38) !important;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #FFFFFF !important;
    }
    
    div.stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }

    /* Customize tabs & increase Sign In / Create Account text sizes */
    div[data-testid="stTabBar"] button {
        font-family: 'Sora', sans-serif !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stTabBar"] button p, button[data-baseweb="tab"] p, button[data-baseweb="tab"] span {
        font-size: 18px !important;
        font-weight: 700 !important;
    }
    
    /* Customize input elements */
    div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea, div[data-testid="stSelectbox"] select, div[data-testid="stNumberInput"] input {
        border-radius: 10px !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        padding: 10px 16px !important;
        transition: all 0.2s ease !important;
    }
    
    div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus, div[data-testid="stNumberInput"] input:focus {
        border-color: #059669 !important;
        box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.15) !important;
        background-color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# Page Definitions
home_page = st.Page("pages/home.py", title="Home", icon="🏠", default=True)
buyer_login = st.Page("pages/buyer_login.py", title="Buyer Portal", icon="🛒")
supplier_login = st.Page("pages/supplier_login.py", title="Supplier Portal", icon="🏭")

# Buyer Pages
buyer_dash = st.Page("pages/buyer_dashboard.py", title="Dashboard", icon="📊", default=True)
marketplace = st.Page("pages/marketplace.py", title="Marketplace", icon="🛒")
ai_matcher = st.Page("pages/ai_matcher.py", title="AI Matcher", icon="🤖")
buyer_verification = st.Page("pages/buyer_verification.py", title="Verification Registry", icon="✅")
price_comparison = st.Page("pages/price_comparison.py", title="Price Comparison", icon="⚖️")
carbon_impact = st.Page("pages/carbon_impact.py", title="Carbon Impact", icon="🌱")
buyer_orders = st.Page("pages/buyer_orders.py", title="My Orders", icon="📦")

# Supplier Pages
supplier_dash = st.Page("pages/supplier_dashboard.py", title="Dashboard", icon="📊", default=True)
supplier_verification = st.Page("pages/supplier_verification.py", title="Verify Business", icon="✅")
add_material = st.Page("pages/add_material.py", title="Add Material", icon="➕")
my_listings = st.Page("pages/my_listings.py", title="My Listings", icon="📋")
buyer_requests = st.Page("pages/buyer_requests.py", title="Buyer Requests", icon="💬")
material_analyzer = st.Page("pages/material_analyzer.py", title="Material Analyzer", icon="🔬")
supplier_analytics = st.Page("pages/supplier_analytics.py", title="Analytics", icon="📈")

# Common Shared Pages
chat_bot = st.Page("pages/ai_chatbot.py", title="AI Assistant", icon="💬")
logout = st.Page("pages/logout.py", title="Logout", icon="🔓")

# Select navigation layout based on Session State
if st.session_state.user is None:
    navigation_structure = {
        "ReLoop": [home_page],
        "Access Portals": [buyer_login, supplier_login],
        "AI Assistant": [chat_bot]
    }
elif st.session_state.user["role"] == "buyer":
    navigation_structure = {
        f"Buyer: {st.session_state.user['name']}": [
            buyer_dash, marketplace, ai_matcher, buyer_verification, price_comparison, carbon_impact, buyer_orders
        ],
        "AI Assistant": [chat_bot],
        "Session Management": [logout]
    }
else:  # supplier
    navigation_structure = {
        f"Supplier: {st.session_state.user['name']}": [
            supplier_dash, supplier_verification, add_material, my_listings, buyer_requests, material_analyzer, supplier_analytics
        ],
        "AI Assistant": [chat_bot],
        "Session Management": [logout]
    }

pg = st.navigation(navigation_structure)
pg.run()