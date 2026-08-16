import streamlit as st
from config.settings import APP_TITLE, APP_ICON
from database.database import init_db, SessionLocal
from database.repository import get_default_user

# Initialize Streamlit Page Configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database Schema
init_db()

# Custom CSS for Modern, Premium Visual Styling (Minty-Indigo theme)
st.markdown("""
<style>
    /* Premium visual styling */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #161a24 100%);
        color: #e0e6ed;
    }
    
    /* Custom Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0b0d13;
        border-right: 1px solid #232834;
    }
    
    /* Card Container */
    .metric-card {
        background: rgba(30, 37, 53, 0.4);
        border: 1px solid rgba(56, 139, 253, 0.15);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
        margin-bottom: 15px;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 139, 253, 0.4);
    }
    
    /* Success highlight card (greenish border) */
    .success-card {
        background: rgba(16, 42, 33, 0.4);
        border: 1px solid rgba(46, 160, 67, 0.25);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        margin-bottom: 15px;
    }
    
    /* Risk highlight card (reddish border) */
    .risk-card {
        background: rgba(48, 16, 21, 0.4);
        border: 1px solid rgba(248, 81, 73, 0.25);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        margin-bottom: 15px;
    }
    
    /* Custom Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Outfit', 'Inter', sans-serif;
    }
    
    /* Subtle decorative dividers */
    .subtle-divider {
        height: 1px;
        background: linear-gradient(90deg, rgba(56, 139, 253, 0) 0%, rgba(56, 139, 253, 0.3) 50%, rgba(56, 139, 253, 0) 100%);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Establish Database Session
db = SessionLocal()
try:
    user = get_default_user(db)
    
    # Sidebar Navigation Menu
    st.sidebar.title("NAVIGATE")
    
    menu_options = {
        "🏠 Dashboard": "dashboard",
        "👤 Financial Profile": "profile",
        "💰 Income & Expenses": "income_expenses",
        "💳 Debt Management": "debt_management",
        "📊 Financial Analysis": "financial_analysis",
        "🎯 Debt Strategy": "debt_strategy",
        "🤖 AI Recovery Plan": "recovery_plan",
        "💬 AI Financial Assistant": "chatbot",
        "📚 Knowledge Hub": "knowledge_hub",
        "🔮 What-If Simulator": "what_if",
        "📈 Progress Tracking": "progress",
        "📄 Financial Report": "reports"
    }
    
    selected_label = st.sidebar.radio(
        "Select Module",
        options=list(menu_options.keys())
    )
    
    selected_page = menu_options[selected_label]
    
    # Sidebar Footer (Disclaimer & Info)
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<div style='font-size: 0.8rem; color: #8b949e; text-align: justify;'>"
        "⚠️ <b>Educational Guidance Only</b><br>"
        "This platform provides informational guidance based on user inputs. "
        "It does not replace certified professional, legal, tax, or investment advice."
        "</div>",
        unsafe_allow_html=True
    )
    
    # Route navigation to correct modules
    if selected_page == "dashboard":
        from ui.dashboard import show_dashboard
        show_dashboard(db, user)
        
    elif selected_page == "profile":
        from ui.profile import show_profile
        show_profile(db, user)
        
    elif selected_page == "income_expenses":
        from ui.income_expenses import show_income_expenses
        show_income_expenses(db, user)
        
    elif selected_page == "debt_management":
        from ui.debt_management import show_debt_management
        show_debt_management(db, user)
        
    elif selected_page == "financial_analysis":
        from ui.financial_analysis import show_financial_analysis
        show_financial_analysis(db, user)
        
    elif selected_page == "debt_strategy":
        from ui.debt_strategy import show_debt_strategy
        show_debt_strategy(db, user)
        
    elif selected_page == "recovery_plan":
        from ui.recovery_plan import show_recovery_plan
        show_recovery_plan(db, user)
        
    elif selected_page == "chatbot":
        from ui.chatbot import show_chatbot
        show_chatbot(db, user)
        
    elif selected_page == "knowledge_hub":
        from ui.knowledge_hub import show_knowledge_hub
        show_knowledge_hub(db, user)
        
    elif selected_page == "what_if":
        from ui.what_if import show_what_if
        show_what_if(db, user)
        
    elif selected_page == "progress":
        from ui.progress import show_progress
        show_progress(db, user)
        
    elif selected_page == "reports":
        from ui.reports import show_reports
        show_reports(db, user)

finally:
    db.close()
