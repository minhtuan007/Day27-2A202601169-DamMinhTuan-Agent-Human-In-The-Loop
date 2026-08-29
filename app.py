import streamlit as st
import json
import os
from datetime import datetime
from graph import graph
from models import AuditEntry

st.set_page_config(page_title="Churn Risk Evaluation", layout="wide")

st.title("Customer Churn Risk - Human in the Loop")

# Unique thread id for the session to persist state
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "1"

config = {"configurable": {"thread_id": st.session_state.thread_id}}

def write_audit_log(entry: AuditEntry):
    log_file = "audit_log.json"
    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            try:
                logs = json.load(f)
            except:
                pass
    
    logs.append(entry.model_dump())
    
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)

st.header("1. Evaluate Customer")
col1, col2 = st.columns([3, 1])
with col1:
    customer_id = st.text_input("Enter Customer ID", value="CUST001")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Run Evaluation", use_container_width=True):
        with st.spinner("Agent is evaluating..."):
            # Start graph execution
            graph.invoke({"customer_id": customer_id, "human_decision": None}, config)
        st.success("Evaluation completed. Check status below.")

st.divider()

st.header("2. Pending Actions (Human Review)")

state_info = graph.get_state(config)

if state_info and state_info.next and "execute_high_risk_action" in state_info.next:
    state_values = state_info.values
    st.warning("Action requires human review!")
    
    st.markdown(f"**Customer ID:** {state_values.get('customer_id')}")
    st.markdown(f"**Proposed Action:** `{state_values.get('proposed_action')}`")
    st.markdown(f"**Confidence Score:** {state_values.get('confidence_score')}")
    st.markdown(f"**Reasoning:** {state_values.get('reasoning')}")
    
    st.subheader("Action")
    
    # Edit Action
    new_action = st.text_input("Edit Action (optional)", value=state_values.get('proposed_action'))
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("✅ Approve", use_container_width=True):
            decision = "approve"
            # Update state with decision
            graph.update_state(config, {"human_decision": decision})
            
            # Log audit
            entry = AuditEntry(
                timestamp=datetime.now().isoformat(),
                agent_id="churn-risk-agent",
                action=state_values.get('proposed_action'),
                confidence=state_values.get('confidence_score'),
                reviewer_id="operator_01",
                decision=decision
            )
            write_audit_log(entry)
            
            # Resume graph
            graph.invoke(None, config)
            st.rerun()
            
    with col_b:
        if st.button("❌ Reject", use_container_width=True):
            decision = "reject"
            graph.update_state(config, {"human_decision": decision})
            
            entry = AuditEntry(
                timestamp=datetime.now().isoformat(),
                agent_id="churn-risk-agent",
                action=state_values.get('proposed_action'),
                confidence=state_values.get('confidence_score'),
                reviewer_id="operator_01",
                decision=decision
            )
            write_audit_log(entry)
            
            graph.invoke(None, config)
            st.rerun()
            
    with col_c:
        if st.button("✏️ Edit & Approve", use_container_width=True):
            decision = "edit"
            graph.update_state(config, {"human_decision": decision, "proposed_action": new_action})
            
            entry = AuditEntry(
                timestamp=datetime.now().isoformat(),
                agent_id="churn-risk-agent",
                action=new_action,
                confidence=state_values.get('confidence_score'),
                reviewer_id="operator_01",
                decision=decision
            )
            write_audit_log(entry)
            
            graph.invoke(None, config)
            st.rerun()
else:
    st.info("No pending high-risk actions.")
    
    # Show last executed action if finished
    if state_info and not state_info.next and state_info.values.get("proposed_action"):
        st.success("Workflow completed.")
        st.json(state_info.values)

st.divider()

st.header("3. Audit Logs")
if os.path.exists("audit_log.json"):
    with open("audit_log.json", "r") as f:
        try:
            logs = json.load(f)
            st.json(logs)
        except Exception:
            st.write("Audit log is empty or invalid.")
else:
    st.write("No audit logs yet.")
