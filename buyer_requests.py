import streamlit as st
from db_utils import get_supplier_orders, update_order_status, get_all_buyer_requests

# Ensure user is logged in
if not st.session_state.user or st.session_state.user["role"] != "supplier":
    st.warning("Please log in as a Supplier to view this page.")
    st.switch_page("supplier_login.py")
    st.stop()

user = st.session_state.user

st.title("💬 Buyer Requests & Order Management")
st.caption("Track purchases of your listed material lots and review open sourcing requirements posted by buyers.")

tab_orders, tab_sourcing = st.tabs(["🛒 Orders Received", " Sourcing Requests Posted by Buyers"])

# 1. ORDERS RECEIVED
with tab_orders:
    orders = get_supplier_orders(user["id"])
    if not orders:
        st.info("No orders received yet. Once a buyer procures your listings, transaction records will display here.")
    else:
        st.subheader("Manage Active Purchases")
        for o in orders:
            col_info, col_status = st.columns([3, 1])
            with col_info:
                st.markdown(f"""
                <div class="reloop-card">
                    <h4 style="margin:0; color:#00E676;">♻ {o['material'].title()} Lot</h4>
                    <div style="margin-top:10px; font-size:13px; color:#bbb; display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                        <div><strong>Buyer Org:</strong> {o['buyer_name']}</div>
                        <div><strong>Quantity Ordered:</strong> {o['quantity']:.1f} kg</div>
                        <div><strong>Total Value:</strong> ₹{o['total_price']:.2f}</div>
                        <div><strong>Order Date:</strong> {o['created_at']}</div>
                        <div><strong>Ship To Location:</strong> {o['location']}</div>
                        <div><strong>Order ID:</strong> #RL-{o['id']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_status:
                st.write("")
                st.write("")
                current_status = o["status"].title()
                status_list = ["Processing", "Shipped", "Delivered"]
                if current_status not in status_list:
                    status_list.append(current_status)
                    
                selected_status = st.selectbox(
                    "Update Status",
                    status_list,
                    index=status_list.index(current_status),
                    key=f"status_select_{o['id']}"
                )
                if selected_status.lower() != o["status"].lower():
                    update_order_status(o["id"], selected_status)
                    st.success(f"Order #{o['id']} status updated to {selected_status}!")
                    st.toast("Status updated!", icon="🚚")
                    st.rerun()
            st.write("")

# 2. OPEN SOURCING REQUESTS
with tab_sourcing:
    sourcing_reqs = get_all_buyer_requests()
    if not sourcing_reqs:
        st.info("No active sourcing requests posted by buyers at this time.")
    else:
        st.subheader("Market Demand Feed")
        st.write("Browse what buyers are actively searching for and fulfill their request by listing the material category.")
        for r in sourcing_reqs:
            st.markdown(f"""
            <div class="reloop-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; color:#29b6f6;"> Sourcing: {r['material_type'].title()}</h4>
                    <span class="badge-verified" style="background-color:rgba(41,182,246,0.1); color:#29b6f6; border-color:#29b6f6;">Open Request</span>
                </div>
                <div style="margin-top:10px; font-size:13px; color:#bbb; display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:10px;">
                    <div><strong>Buyer:</strong> {r['buyer_name']}</div>
                    <div><strong>Target Volume:</strong> {r['quantity']:.1f} kg</div>
                    <div><strong>Max Budget:</strong> ₹{r['max_price']:.2f} / kg</div>
                    <div><strong>Posted on:</strong> {r['created_at']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
