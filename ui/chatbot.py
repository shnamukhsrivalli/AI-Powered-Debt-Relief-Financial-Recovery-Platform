import streamlit as st
from database.repository import get_chat_history, clear_chat_history
from ai.financial_assistant import FinancialAssistant

def show_chatbot(db, user):
    st.title("💬 AI Financial Assistant")
    st.write("Discuss your debt relief questions, budgeting strategies, and calculations with our grounded AI bot.")
    
    # 1. Clear History action
    col_hdr, col_clear = st.columns([4, 1])
    with col_hdr:
        st.caption("Grounded in your financial profile data and local educational resources.")
    with col_clear:
        if st.button("🧹 Clear Chat"):
            clear_chat_history(db, user.id)
            st.success("Chat history cleared!")
            st.rerun()
            
    st.markdown("<div class='subtle-divider'></div>", unsafe_allow_html=True)
    
    # 2. Retrieve history and render chat history
    history = get_chat_history(db, user.id)
    
    # Render messages using st.chat_message
    for msg in history:
        with st.chat_message(msg.sender):
            st.markdown(msg.message)
            
    # 3. User input prompt
    if prompt := st.chat_input("Ask a question (e.g. Which debt should I pay first? or How can I lower my DTI?)"):
        # Render user message
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Call assistant
        with st.spinner("Analyzing profile context and querying knowledge base..."):
            try:
                assistant = FinancialAssistant(db)
                response = assistant.get_assistant_response(user.id, prompt)
                
                # Render assistant message
                with st.chat_message("assistant"):
                    st.markdown(response)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error getting assistant response: {str(e)}")
