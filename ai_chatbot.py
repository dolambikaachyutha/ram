import streamlit as st
from llm_client import ask_ai
from db_utils import get_listings

st.title("💬 ReLoop AI Assistant")
st.caption("Ask questions about circular economy, carbon calculations, or find available waste materials.")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Fetch active listings for injecting into the context
listings = get_listings()
listings_summary = ""
if listings:
    listings_summary = "\nAvailable Listings on the ReLoop Marketplace:\n"
    for i, l in enumerate(listings, 1):
        listings_summary += f"{i}. Material: {l['material']}, Qty: {l['quantity']} {l['unit']}, Price: ₹{l['price_per_kg']}/kg, Location: {l['location']}, Condition: {l['condition']}, Seller: {l['supplier_name']} (Trust Score: {l['trust_score'] or 5.0}/10)\n"
else:
    listings_summary = "\nNo active listings are currently available on the marketplace."

user_info = "Not logged in"
if st.session_state.user:
    user_info = f"Logged in as {st.session_state.user['name']} (Role: {st.session_state.user['role']})"

SYSTEM_CONTEXT = f"""You are the support assistant for ReLoop, an AI-driven circular economy marketplace.
Users buy or sell industrial waste materials (wood scraps, fabric, paper, plastic, metal) to recycle them.
Suggested prices are based on base rates, and CO2 savings are calculated using standard diversion factors.

User Session: {user_info}
{listings_summary}

Rules:
- Be professional, encouraging, and sustainable-focused.
- If the user asks about available materials, read the listings list above and summarize matches nicely. Mention the quantity, price, location, and the seller's trust score.
- Keep your answers concise, clear, and direct (2-4 sentences is best, unless listing matches).
"""

# Preset Questions
st.markdown("##### Quick Suggestions:")
col1, col2, col3 = st.columns(3)
preset_clicked = None
with col1:
    if st.button("What is ReLoop?", use_container_width=True):
        preset_clicked = "What is ReLoop and how does it work?"
with col2:
    if st.button("List available wood waste", use_container_width=True):
        preset_clicked = "Show me all available wood waste listings."
with col3:
    if st.button("How is CO2 calculated?", use_container_width=True):
        preset_clicked = "How do you calculate carbon savings?"

# Render chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle Chat Input
user_input = st.chat_input("Ask ReLoop AI...")
if preset_clicked:
    user_input = preset_clicked

if user_input:
    # Append user question
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing and querying..."):
            # Construct dialogue context
            dialogue = SYSTEM_CONTEXT + "\n"
            # Add last few exchanges for short-term memory
            for msg in st.session_state.chat_history[-6:]:
                dialogue += f"{msg['role'].upper()}: {msg['content']}\n"
            dialogue += "ASSISTANT: "
            
            try:
                response = ask_ai(dialogue)
            except Exception as e:
                response = f"I'm sorry, I encountered an error connecting to the AI engine: {e}"
                
            st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
    if preset_clicked:
        st.rerun()

# Clear history button
if st.session_state.chat_history:
    st.markdown("---")
    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
