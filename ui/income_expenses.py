import streamlit as st
import pandas as pd
import plotly.express as px
from database.repository import (
    get_incomes, add_income, delete_income,
    get_expenses, add_expense, delete_expense
)
from config.constants import INCOME_CATEGORIES, EXPENSE_CATEGORIES
from models.financial_models import IncomeSchema, ExpenseSchema
from pydantic import ValidationError

def show_income_expenses(db, user):
    st.title("💰 Income & Expenses")
    st.write("Record your monthly inflows and outflows to build a complete cash flow model.")
    
    # Retrieve income and expenses from database
    incomes = get_incomes(db, user.id)
    expenses = get_expenses(db, user.id)
    
    # ------------------ INCOME SECTION ------------------
    st.subheader("Monthly Income Streams")
    
    inc_col1, inc_col2 = st.columns([1, 2])
    
    with inc_col1:
        st.markdown("#### Add Income Source")
        with st.form("add_income_form", clear_on_submit=True):
            source = st.selectbox("Income Source Category", options=INCOME_CATEGORIES)
            custom_source = st.text_input("Custom Label (Optional)", placeholder="e.g. Acme Corp Contract")
            amount = st.number_input("Monthly Net Amount ($ / ₹)", min_value=0.0, step=100.0)
            
            submit_inc = st.form_submit_button("Add Income")
            if submit_inc:
                try:
                    label = custom_source.strip() if custom_source.strip() else source
                    # Validate
                    validated = IncomeSchema(source=label, amount=amount, frequency="Monthly")
                    
                    add_income(db, user.id, validated.source, validated.amount, validated.frequency)
                    st.success(f"Added income: {validated.source}")
                    st.rerun()
                except ValidationError as e:
                    for error in e.errors():
                        st.error(f"❌ {error['msg']}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    
    with inc_col2:
        st.markdown("#### Active Income Sources")
        if not incomes:
            st.info("No income sources added yet. Enter one using the form on the left.")
        else:
            inc_data = []
            for inc in incomes:
                inc_data.append({
                    "ID": inc.id,
                    "Source": inc.source,
                    "Amount": inc.amount,
                    "Frequency": inc.frequency
                })
            df_inc = pd.DataFrame(inc_data)
            
            # Display items with individual delete buttons
            for idx, row in df_inc.iterrows():
                col_item, col_del = st.columns([4, 1])
                with col_item:
                    st.markdown(
                        f"<div class='metric-card' style='padding: 10px 15px; margin-bottom: 8px;'>"
                        f"<b>{row['Source']}</b>: {row['Amount']:.2f} ({row['Frequency']})"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                with col_del:
                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                    if st.button("🗑️ Delete", key=f"del_inc_{row['ID']}"):
                        delete_income(db, row["ID"])
                        st.success(f"Removed {row['Source']}")
                        st.rerun()
                        
    st.markdown("<div class='subtle-divider'></div>", unsafe_allow_html=True)
    
    # ------------------ EXPENSES SECTION ------------------
    st.subheader("Monthly Expenditures")
    
    exp_col1, exp_col2 = st.columns([1, 2])
    
    with exp_col1:
        st.markdown("#### Add Expense Category")
        with st.form("add_expense_form", clear_on_submit=True):
            category = st.selectbox("Expense Category", options=list(EXPENSE_CATEGORIES.keys()))
            custom_category = st.text_input("Custom Label (Optional)", placeholder="e.g. Gym membership")
            amount = st.number_input("Monthly Amount ($ / ₹)", min_value=0.0, step=50.0)
            
            submit_exp = st.form_submit_button("Add Expense")
            if submit_exp:
                try:
                    label = custom_category.strip() if custom_category.strip() else category
                    classification = EXPENSE_CATEGORIES.get(category, "Discretionary")
                    
                    # Validate
                    validated = ExpenseSchema(category=label, amount=amount, classification=classification)
                    
                    add_expense(db, user.id, validated.category, validated.amount, validated.classification)
                    st.success(f"Added expense: {validated.category}")
                    st.rerun()
                except ValidationError as e:
                    for error in e.errors():
                        st.error(f"❌ {error['msg']}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    
    with exp_col2:
        st.markdown("#### Active Expenditures")
        if not expenses:
            st.info("No expenses added yet. Enter one using the form on the left.")
        else:
            exp_data = []
            for exp in expenses:
                exp_data.append({
                    "ID": exp.id,
                    "Category": exp.category,
                    "Amount": exp.amount,
                    "Classification": exp.classification
                })
            df_exp = pd.DataFrame(exp_data)
            
            for idx, row in df_exp.iterrows():
                col_item, col_del = st.columns([4, 1])
                with col_item:
                    badge_color = "#388bfd" if row["Classification"] == "Essential" else "#f78166"
                    st.markdown(
                        f"<div class='metric-card' style='padding: 10px 15px; margin-bottom: 8px;'>"
                        f"<span style='background-color: {badge_color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; margin-right: 8px;'>{row['Classification']}</span>"
                        f"<b>{row['Category']}</b>: {row['Amount']:.2f}"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                with col_del:
                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                    if st.button("🗑️ Delete", key=f"del_exp_{row['ID']}"):
                        delete_expense(db, row["ID"])
                        st.success(f"Removed {row['Category']}")
                        st.rerun()
                        
    st.markdown("<div class='subtle-divider'></div>", unsafe_allow_html=True)
    
    # ------------------ CALCULATIONS & METRICS ------------------
    st.subheader("Cash Flow Summary & Metrics")
    
    # Calculations
    total_income = sum(inc.amount for inc in incomes)
    annual_income = total_income * 12
    total_expenses = sum(exp.amount for exp in expenses)
    essential_expenses = sum(exp.amount for exp in expenses if exp.classification == "Essential")
    discretionary_expenses = sum(exp.amount for exp in expenses if exp.classification == "Discretionary")
    
    expense_ratio = (total_expenses / total_income * 100) if total_income > 0 else 0.0
    disposable_income = total_income - total_expenses
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"<div class='success-card'>"
            f"<h4>Monthly Net Income</h4>"
            f"<h2 style='margin: 5px 0;'>{total_income:,.2f}</h2>"
            f"<p style='color: #8b949e; margin-bottom:0;'>Estimated Annual: {annual_income:,.2f}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
    with col2:
        card_class = "risk-card" if expense_ratio > 75 else "metric-card"
        st.markdown(
            f"<div class='{card_class}'>"
            f"<h4>Monthly Expenses</h4>"
            f"<h2 style='margin: 5px 0;'>{total_expenses:,.2f}</h2>"
            f"<p style='color: #8b949e; margin-bottom:0;'>Expense Ratio: {expense_ratio:.1f}%</p>"
            f"</div>",
            unsafe_allow_html=True
        )
    with col3:
        disp_class = "success-card" if disposable_income > 0 else "risk-card"
        st.markdown(
            f"<div class='{disp_class}'>"
            f"<h4>Disposable Cash Flow</h4>"
            f"<h2 style='margin: 5px 0;'>{disposable_income:,.2f}</h2>"
            f"<p style='color: #8b949e; margin-bottom:0;'>Before Debt Obligations</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
    # Graphical Visualizations
    if incomes or expenses:
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            if expenses:
                df_exp = pd.DataFrame(df_exp)
                fig_exp = px.pie(
                    df_exp, 
                    values="Amount", 
                    names="Category", 
                    title="Expense Breakdown by Category",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_exp.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e0e6ed")
                st.plotly_chart(fig_exp, use_container_width=True)
            else:
                st.info("Add expenses to view the expenditure chart.")
                
        with chart_col2:
            if expenses:
                df_class = df_exp.groupby("Classification").sum().reset_index()
                fig_class = px.pie(
                    df_class, 
                    values="Amount", 
                    names="Classification", 
                    title="Essential vs Discretionary Expenses",
                    color_discrete_map={"Essential": "#388bfd", "Discretionary": "#f78166"}
                )
                fig_class.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e0e6ed")
                st.plotly_chart(fig_class, use_container_width=True)
            else:
                st.info("Add expenses to view essential/discretionary ratio.")
