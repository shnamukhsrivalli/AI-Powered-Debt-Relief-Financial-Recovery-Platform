import streamlit as st
import os
from rag.pipeline import RAGPipeline
from config.settings import KNOWLEDGE_DIR

def show_knowledge_hub(db, user):
    st.title("📚 Knowledge Hub")
    st.write("Query or browse verified financial recovery and debt relief materials grounded in local education data.")
    
    # 1. Initialize Pipeline
    pipeline = RAGPipeline()
    
    try:
        # Build index on first access if not done
        pipeline.initialize_rag()
    except Exception as e:
        st.error(f"❌ Failed to initialize RAG index: {str(e)}")
        return
        
    # RAG Search bar
    st.subheader("Search Financial Topics")
    query = st.text_input("Enter your question", placeholder="e.g. What is debt avalanche or emergency funds?")
    search_btn = st.button("🔍 Query Hub")
    
    if search_btn and query.strip():
        with st.spinner("Searching knowledge database and generating grounded answer..."):
            try:
                results = pipeline.get_grounded_answer(query)
                answer = results["answer"]
                sources = results["sources"]
                
                # Show Grounded Answer
                st.markdown("### 💬 AI Grounded Explanation")
                st.markdown(
                    f"<div class='metric-card' style='padding: 20px;'>\n"
                    f"{answer}\n"
                    f"</div>",
                    unsafe_allow_html=True
                )
                
                # Show Sources Used
                if sources:
                    st.markdown("#### Grounding Sources / Citations")
                    for s in sources:
                        badge_color = "#2ea043" if s["score"] > 0.5 else "#388bfd"
                        st.markdown(
                            f"<div style='background: rgba(30,37,53,0.3); border: 1px solid rgba(255,255,255,0.05); border-radius: 6px; padding: 10px; margin-bottom: 8px;'>"
                            f"📁 <b>{s['title']}</b> (File: <i>{s['source']}</i>) "
                            f"<span style='float: right; font-size: 0.8rem; background-color: {badge_color}; color: white; padding: 1px 6px; border-radius: 4px;'>Score: {s['score']:.2f}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
            except Exception as e:
                st.error(f"❌ Error performing query: {str(e)}")
                
    st.markdown("<div class='subtle-divider'></div>", unsafe_allow_html=True)
    
    # 2. Browse Library
    st.subheader("Browse Educational Articles")
    
    # List files in data/knowledge/
    if os.path.exists(KNOWLEDGE_DIR):
        files = [f for f in os.listdir(KNOWLEDGE_DIR) if f.endswith(".md")]
        if not files:
            st.info("No educational articles found in knowledge base directory.")
        else:
            selected_file = st.selectbox(
                "Select an article to read",
                options=files,
                format_func=lambda name: name.replace(".md", "").replace("_", " ").title()
            )
            
            if selected_file:
                file_path = KNOWLEDGE_DIR / selected_file
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        article_content = f.read()
                        
                    st.markdown(
                        f"<div class='metric-card' style='padding: 25px;'>\n"
                        f"{article_content}\n"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.error(f"❌ Error reading article: {str(e)}")
    else:
        st.error("Knowledge base folder does not exist.")
