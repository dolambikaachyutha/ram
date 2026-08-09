import streamlit as st

# Clear the logged-in user. webapp.py rebuilds navigation on the next run,
# and since home_page is the default page for logged-out users, the app
# automatically returns to the Home page.
st.session_state.user = None
st.success("You have been successfully logged out.")
st.rerun()
