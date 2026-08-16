import streamlit as st
import pandas as pd
from database.repository import get_debts, add_debt, update_debt, delete_debt
from config.constants import DEBT_TYPES, DEBT_STATUS_ACTIVE
from models.debt_models import DebtSchema
from pydantic import ValidationError

def show_debt_management(db, user):
    st.title("💳 Debt Management")
    st.write("Track, add, edit, and mark your various credit liabilities here.")
    
    # Fetch active debts
    debts = get_debts(db, user.id)
    
    # ------------------ TOP SUMMARY METRICS ------------------
    if debts:
        total_balance = sum(d.outstanding_balance for d in debts if d.status == "Active")
        total_min_pay = sum(d.minimum_payment for d in debts if d.status == "Active")
        active_debts_count = len([d for d in debts if d.status == "Active"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"<div class='risk-card'>"
                f"<h4>Total Outstanding Debt</h4>"
                f"<h2 style='margin: 5px 0;'>{total_balance:,.2f}</h2>"
                f"<p style='color: #8b949e; margin-bottom:0;'>Across {active_debts_count} active accounts</p>"
                f"</div>",
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"<div class='metric-card'>"
                f"<h4>Total Minimum Due</h4>"
                f"<h2 style='margin: 5px 0;'>{total_min_pay:,.2f} / mo</h2>"
                f"<p style='color: #8b949e; margin-bottom:0;'>Required monthly payment</p>"
                f"</div>",
                unsafe_allow_html=True
            )
        with col3:
            high_apr = max((d.interest_rate for d in debts if d.status == "Active"), default=0.0)
            st.markdown(
                f"<div class='metric-card'>"
                f"<h4>Highest Interest Rate</h4>"
                f"<h2 style='margin: 5px 0;'>{high_apr:.1f}% APR</h2>"
                f"<p style='color: #8b949e; margin-bottom:0;'>Target for avalanche strategy</p>"
                f"</div>",
                unsafe_allow_html=True
            )
            
    st.markdown("<div class='subtle-divider'></div>", unsafe_allow_html=True)
    
    # ------------------ ADD DEBT FORM ------------------
    with st.expander("➕ Add New Debt Liability", expanded=not debts):
        with st.form("add_debt_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                name = st.text_input("Debt Name", placeholder="e.g. Citibank Gold Credit Card")
                debt_type = st.selectbox("Debt Type", options=DEBT_TYPES)
                outstanding_balance = st.number_input("Outstanding Balance ($ / ₹)", min_value=0.0, step=500.0)
                original_principal = st.number_input("Original Principal ($ / ₹)", min_value=0.0, step=500.0)
            with col_b:
                interest_rate = st.number_input("Annual Interest Rate (APR %)", min_value=0.0, max_value=100.0, step=0.1)
                minimum_payment = st.number_input("Minimum Monthly Payment ($ / ₹)", min_value=0.0, step=50.0)
                emi = st.number_input("Equated Monthly Installment (EMI) ($ / ₹)", min_value=0.0, step=50.0)
                
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    due_date = st.text_input("Due Day of Month", value="15", placeholder="e.g. 15 or 15th")
                with col_b2:
                    remaining_tenure = st.number_input("Remaining Tenure (Months)", min_value=0, step=1)
            
            submit_btn = st.form_submit_button("Add Debt Account")
            if submit_btn:
                try:
                    # Validate
                    validated = DebtSchema(
                        name=name,
                        debt_type=debt_type,
                        outstanding_balance=outstanding_balance,
                        original_principal=original_principal,
                        interest_rate=interest_rate,
                        minimum_payment=minimum_payment,
                        emi=emi,
                        due_date=due_date,
                        remaining_tenure=int(remaining_tenure),
                        status="Active"
                    )
                    
                    add_debt(
                        db, user.id, validated.name, validated.debt_type, validated.outstanding_balance,
                        validated.original_principal, validated.interest_rate, validated.minimum_payment,
                        validated.emi, validated.due_date, validated.remaining_tenure, validated.status
                    )
                    st.success(f"Added debt liability: {validated.name}")
                    st.rerun()
                except ValidationError as e:
                    for error in e.errors():
                        st.error(f"❌ {error['msg']}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    # ------------------ VIEW AND UPDATE DEBTS ------------------
    st.subheader("Current Debt Ledger")
    
    if not debts:
        st.info("No liabilities tracked yet. Record your debts to calculate recovery scores.")
    else:
        debt_rows = []
        for d in debts:
            debt_rows.append({
                "ID": d.id,
                "Name": d.name,
                "Type": d.debt_type,
                "Balance": d.outstanding_balance,
                "Principal": d.original_principal,
                "APR (%)": d.interest_rate,
                "Min Payment": d.minimum_payment,
                "EMI": d.emi,
                "Due Date": d.due_date,
                "Tenure": d.remaining_tenure,
                "Status": d.status
            })
            
        df_debts = pd.DataFrame(debt_rows)
        st.dataframe(
            df_debts[["Name", "Type", "Balance", "Principal", "APR (%)", "Min Payment", "EMI", "Due Date", "Tenure", "Status"]],
            use_container_width=True
        )
        
        # Edit/Delete expander
        with st.expander("✏️ Edit or Remove Existing Liability"):
            selected_debt_name = st.selectbox(
                "Select Liability to Modify",
                options=[d.name for d in debts]
            )
            
            # Find selected debt object
            s_debt = next((d for d in debts if d.name == selected_debt_name), None)
            
            if s_debt:
                with st.form("edit_debt_form"):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        e_name = st.text_input("Name", value=s_debt.name)
                        e_type = st.selectbox("Type", options=DEBT_TYPES, index=DEBT_TYPES.index(s_debt.debt_type) if s_debt.debt_type in DEBT_TYPES else 0)
                        e_balance = st.number_input("Outstanding Balance", value=s_debt.outstanding_balance, min_value=0.0)
                        e_principal = st.number_input("Original Principal", value=s_debt.original_principal, min_value=0.0)
                        e_status = st.selectbox("Status", options=["Active", "Paid"], index=0 if s_debt.status == "Active" else 1)
                    with col_e2:
                        e_apr = st.number_input("Interest Rate (APR %)", value=s_debt.interest_rate, min_value=0.0, max_value=100.0)
                        e_min_pay = st.number_input("Minimum Monthly Payment", value=s_debt.minimum_payment, min_value=0.0)
                        e_emi = st.number_input("Equated Monthly Installment (EMI)", value=s_debt.emi, min_value=0.0)
                        e_due = st.text_input("Due Day", value=s_debt.due_date if s_debt.due_date else "15")
                        e_tenure = st.number_input("Remaining Months", value=s_debt.remaining_tenure, min_value=0)
                    
                    e_col1, e_col2 = st.columns([1, 1])
                    with e_col1:
                        save_changes = st.form_submit_button("💾 Save Changes")
                        if save_changes:
                            try:
                                validated = DebtSchema(
                                    name=e_name,
                                    debt_type=e_type,
                                    outstanding_balance=e_balance,
                                    original_principal=e_principal,
                                    interest_rate=e_apr,
                                    minimum_payment=e_min_pay,
                                    emi=e_emi,
                                    due_date=e_due,
                                    remaining_tenure=int(e_tenure),
                                    status=e_status
                                )
                                
                                update_debt(
                                    db, s_debt.id, validated.name, validated.debt_type, validated.outstanding_balance,
                                    validated.original_principal, validated.interest_rate, validated.minimum_payment,
                                    validated.emi, validated.due_date, validated.remaining_tenure, validated.status
                                )
                                st.success(f"Updated: {validated.name}")
                                st.rerun()
                            except ValidationError as e:
                                for error in e.errors():
                                    st.error(f"❌ {error['msg']}")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                                
                    with e_col2:
                        delete_liability = st.form_submit_button("❌ Delete Permanently")
                        if delete_liability:
                            try:
                                delete_debt(db, s_debt.id)
                                st.warning(f"Deleted liability: {s_debt.name}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                                
        # Paid status toggler shortcuts
        st.markdown("#### Account Status Quick Actions")
        for d in debts:
            col_acc, col_status_btn = st.columns([4, 1])
            with col_acc:
                status_text = "🟢 Active" if d.status == "Active" else "⚪ Paid"
                st.write(f"**{d.name}** ({d.debt_type}) — Balance: {d.outstanding_balance:,.2f} — *{status_text}*")
            with col_status_btn:
                new_status = "Paid" if d.status == "Active" else "Active"
                btn_label = "Mark as Paid" if d.status == "Active" else "Mark as Active"
                if st.button(btn_label, key=f"toggle_stat_{d.id}"):
                    update_debt(
                        db, d.id, d.name, d.debt_type, d.outstanding_balance,
                        d.original_principal, d.interest_rate, d.minimum_payment,
                        d.emi, d.due_date, d.remaining_tenure, new_status
                    )
                    st.success(f"Set {d.name} status to {new_status}")
                    st.rerun()
