import streamlit as st
from db_utils import create_user, login_user

st.title("🛒 Buyer Portal")
st.caption("Access the circular marketplace, track orders, and calculate carbon savings.")

tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Create Account"])

# SIGN IN
with tab1:
    st.subheader("Login to your Buyer Account")
    
    with st.expander("⚡ Demo Quick Login"):
        st.info("Demo Account: `buyer@eco.com` | Password: `password123`")
        if st.button("⚡ Fill Demo Buyer Credentials", use_container_width=True):
            user = login_user("buyer@eco.com", "password123")
            if user:
                st.session_state.user = user
                st.success("Logged in as Demo Buyer!")
                st.rerun()

    email = st.text_input("Email Address", key="buyer_login_email")
    password = st.text_input("Password", type="password", key="buyer_login_pass")
    
    if st.button("Sign In as Buyer", use_container_width=True):
        if not email or not password:
            st.error("Please fill in all fields.")
        else:
            user = login_user(email, password)
            if user:
                if user["role"] == "buyer":
                    st.session_state.user = user
                    st.success(f"Welcome back, {user['name']}!")
                    st.rerun()
                else:
                    st.error("Account exists, but it is not registered as a Buyer.")
            else:
                st.error("Invalid email or password.")

# CREATE ACCOUNT
with tab2:
    st.subheader("Register as a Buyer")
    name = st.text_input("Full Name", key="buyer_reg_name")
    reg_email = st.text_input("Email Address", key="buyer_reg_email")
    reg_pass = st.text_input("Password", type="password", key="buyer_reg_pass")
    confirm_pass = st.text_input("Confirm Password", type="password", key="buyer_reg_confirm")
    
    if st.button("Register Account", use_container_width=True):
        if not name or not reg_email or not reg_pass:
            st.error("All fields are required.")
        elif reg_pass != confirm_pass:
            st.error("Passwords do not match.")
        else:
            success = create_user(name, reg_email, reg_pass, "buyer")
            if success:
                st.success("Registration successful! You can now log in using the Sign In tab.")
            else:
                st.error("Email is already registered. Please try logging in or use a different email.")

# Navigation Help
st.markdown("---")
if st.button("🏠 Back to Home Page", use_container_width=True):
    st.switch_page("pages/home.py")
