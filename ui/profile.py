import streamlit as st
from database.repository import get_profile, save_profile
from models.financial_models import UserProfileSchema
from pydantic import ValidationError

def show_profile(db, user):
    st.title("👤 Financial Profile")
    st.write("Establish your personal information and recovery goals to tailor the AI models and strategies.")
    
    # Retrieve current profile from database
    profile = get_profile(db, user.id)
    
    # Set default values if profile does not exist
    default_name = profile.name if profile else ""
    default_age = profile.age_range if profile else "26-35"
    default_employment = profile.employment_status if profile else "Employed Full-Time"
    default_goal = profile.financial_goal if profile else "Become Debt Free"
    default_period = profile.planning_period if profile else 12
    
    age_options = ["Under 25", "26-35", "36-45", "46-55", "56-65", "Over 65"]
    employment_options = ["Employed Full-Time", "Employed Part-Time", "Self-Employed", "Freelancer", "Unemployed", "Retired", "Student"]
    goal_options = ["Become Debt Free", "Consolidate Debts", "Reduce Monthly Outflow", "Improve Savings Rate", "Build Emergency Fund", "Other"]
    
    with st.form("profile_form"):
        st.markdown("### Personal Details")
        
        name = st.text_input("Name", value=default_name, placeholder="Enter your full name")
        
        col1, col2 = st.columns(2)
        with col1:
            age_range = st.selectbox("Age Range", options=age_options, index=age_options.index(default_age) if default_age in age_options else 1)
        with col2:
            employment_status = st.selectbox("Employment Status", options=employment_options, index=employment_options.index(default_employment) if default_employment in employment_options else 0)
            
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("### Recovery Target & Planning")
        
        financial_goal = st.selectbox("Primary Financial Goal", options=goal_options, index=goal_options.index(default_goal) if default_goal in goal_options else 0)
        planning_period = st.slider("Planning Horizon (Months)", min_value=3, max_value=60, value=default_period, step=3, help="The number of months for your debt payoff target.")
        
        submit_btn = st.form_submit_button("Save Profile")
        
        if submit_btn:
            try:
                # Validate inputs using Pydantic schema
                validated_data = UserProfileSchema(
                    name=name,
                    age_range=age_range,
                    employment_status=employment_status,
                    financial_goal=financial_goal,
                    planning_period=planning_period
                )
                
                # Save validated inputs in the database
                save_profile(
                    db,
                    user_id=user.id,
                    name=validated_data.name,
                    age_range=validated_data.age_range,
                    employment_status=validated_data.employment_status,
                    financial_goal=validated_data.financial_goal,
                    planning_period=validated_data.planning_period
                )
                st.success("🎉 Financial Profile saved successfully!")
                st.rerun()
                
            except ValidationError as e:
                for error in e.errors():
                    st.error(f"❌ {error['msg']}")
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")

    # Show summary of current profile
    if profile:
        st.markdown("---")
        st.markdown("### Current Saved Profile Summary")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Profile Name", profile.name)
            st.metric("Age Range", profile.age_range)
        with col2:
            st.metric("Employment Status", profile.employment_status)
            st.metric("Financial Goal", profile.financial_goal)
        with col3:
            st.metric("Planning Period", f"{profile.planning_period} Months")
            st.metric("Last Updated", profile.updated_at.strftime("%Y-%m-%d %H:%M"))
