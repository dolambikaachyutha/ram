import streamlit as st
from db.db_utils import create_user, login_user

st.title("🏭 Supplier Portal")
st.caption("Verify your business, list factory waste materials, and manage buyer inquiries.")

tab1, tab2 = st.tabs(["🔐 Supplier Sign In", "📝 Register Company"])

# SIGN IN
with tab1:
    st.subheader("Login to your Supplier Account")
    
    with st.expander("⚡ Demo Quick Login"):
        st.info("Demo Account: `supplier@eco.com` | Password: `password123`")
        if st.button("⚡ Fill Demo Supplier Credentials", use_container_width=True):
            user = login_user("supplier@eco.com", "password123")
            if user:
                st.session_state.user = user
                st.success("Logged in as Demo Supplier!")
                st.rerun()

    email = st.text_input("Company Email", key="supplier_login_email")
    password = st.text_input("Password", type="password", key="supplier_login_pass")
    
    if st.button("Sign In as Supplier", use_container_width=True):
        if not email or not password:
            st.error("Please fill in all fields.")
        else:
            user = login_user(email, password)
            if user:
                if user["role"] == "supplier":
                    st.session_state.user = user
                    st.success(f"Welcome back, {user['name']}!")
                    st.rerun()
                else:
                    st.error("Account exists, but it is not registered as a Supplier.")
            else:
                st.error("Invalid email or password.")

# CREATE ACCOUNT
with tab2:
    st.subheader("Register your Business")
    company_name = st.text_input("Company / Business Name", key="supplier_reg_name")
    reg_email = st.text_input("Company Email", key="supplier_reg_email")
    reg_pass = st.text_input("Password", type="password", key="supplier_reg_pass")
    confirm_pass = st.text_input("Confirm Password", type="password", key="supplier_reg_confirm")
    
    if st.button("Register Company Account", use_container_width=True):
        if not company_name or not reg_email or not reg_pass:
            st.error("All fields are required.")
        elif reg_pass != confirm_pass:
            st.error("Passwords do not match.")
        else:
            success = create_user(company_name, reg_email, reg_pass, "supplier")
            if success:
                st.success("Supplier account registered successfully! You can now log in using the Supplier Sign In tab.")
            else:
                st.error("Email is already registered. Please try logging in or use a different email.")

# Navigation Help
st.markdown("---")
if st.button("🏠 Back to Home Page", use_container_width=True):
    st.switch_page("pages/home.py")
