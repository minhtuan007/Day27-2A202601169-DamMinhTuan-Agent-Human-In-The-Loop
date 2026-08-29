import os
import json
from typing import TypedDict, Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# ==========================================
# 1. State and Schema
# ==========================================
class GraphState(TypedDict):
    customer_id: str
    proposed_action: str
    confidence_score: float
    reasoning: str
    human_decision: str | None

class AgentOutput(BaseModel):
    proposed_action: Literal["send_email", "increase_credit_limit"] = Field(
        description="The action to propose, either 'send_email' for low risk or 'increase_credit_limit' for high risk."
    )
    confidence_score: float = Field(
        description="Confidence score from 0.0 to 1.0"
    )
    reasoning: str = Field(
        description="Reasoning for the proposed action and confidence score"
    )

# ==========================================
# 2. LLM Initialization
# ==========================================
# We use openrouter/free model as requested
llm = ChatOpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.environ.get("OPENROUTER_API_KEY", os.environ.get("OPENAI_API_KEY")),
    model="openrouter/free"
)

# For free models, using a strict JSON output parser is safer than expecting native tool calling.
from langchain_core.output_parsers import PydanticOutputParser
parser = PydanticOutputParser(pydantic_object=AgentOutput)

prompt = PromptTemplate(
    template="""You are a churn risk evaluator agent.
Given the customer ID {customer_id}, assess their churn risk.
If they are low risk, propose the action "send_email".
If they are high risk, propose the action "increase_credit_limit".
Provide a confidence score between 0.0 and 1.0.
Provide your reasoning.

{format_instructions}

Return only valid JSON.
""",
    input_variables=["customer_id"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = prompt | llm | parser

# ==========================================
# 3. Nodes
# ==========================================
def evaluate_customer(state: GraphState):
    print(f"--- EVALUATE CUSTOMER: {state['customer_id']} ---")
    
    try:
        result = chain.invoke({"customer_id": state["customer_id"]})
        return {
            "proposed_action": result.proposed_action,
            "confidence_score": result.confidence_score,
            "reasoning": result.reasoning
        }
    except Exception as e:
        print(f"Error calling LLM: {e}")
        # Fallback in case the free model fails to output valid JSON
        import random
        is_high_risk = random.choice([True, False])
        return {
            "proposed_action": "increase_credit_limit" if is_high_risk else "send_email",
            "confidence_score": round(random.uniform(0.7, 0.99), 2),
            "reasoning": "Fallback response due to LLM error."
        }

def execute_low_risk_action(state: GraphState):
    print("--- EXECUTE LOW RISK ACTION ---")
    print(f"Action '{state['proposed_action']}' executed automatically.")
    return state

def execute_high_risk_action(state: GraphState):
    print("--- EXECUTE HIGH RISK ACTION ---")
    decision = state.get("human_decision")
    
    from models import AuditEntry
    from datetime import datetime
    
    if decision == "approve" or decision == "edit":
        print(f"Action '{state['proposed_action']}' executed after human approval/edit.")
    elif decision == "reject":
        print(f"Action '{state['proposed_action']}' aborted due to human rejection.")
    
    # Audit log entry is appended in app.py or here. 
    # For simplicity, we'll let app.py write the audit log right before resuming graph, 
    # or write it here.
    return state

# ==========================================
# 4. Conditional Edge
# ==========================================
def route_action(state: GraphState):
    action = state.get("proposed_action")
    confidence = state.get("confidence_score", 0.0)
    
    print(f"--- ROUTING --- Action: {action}, Confidence: {confidence}")
    
    # Rule 1: Policy Override
    if action == "increase_credit_limit":
        print("Routing: increase_credit_limit requires human review.")
        return "execute_high_risk_action"
        
    # Rule 2: Auto-Execute
    if confidence >= 0.85 and action == "send_email": # Assuming send_email is low-risk
        print("Routing: High confidence low-risk action. Auto executing.")
        return "execute_low_risk_action"
        
    # Rule 3: Escalate/Suggest
    if confidence < 0.85:
        print("Routing: Low confidence. Escalating to human review.")
        return "execute_high_risk_action"
        
    return "execute_high_risk_action" # Default fallback

# ==========================================
# 5. Graph Compilation
# ==========================================
builder = StateGraph(GraphState)

builder.add_node("evaluate_customer", evaluate_customer)
builder.add_node("execute_low_risk_action", execute_low_risk_action)
builder.add_node("execute_high_risk_action", execute_high_risk_action)

builder.add_edge(START, "evaluate_customer")
builder.add_conditional_edges(
    "evaluate_customer",
    route_action,
    {
        "execute_low_risk_action": "execute_low_risk_action",
        "execute_high_risk_action": "execute_high_risk_action"
    }
)
builder.add_edge("execute_low_risk_action", END)
builder.add_edge("execute_high_risk_action", END)

memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory,
    interrupt_before=["execute_high_risk_action"]
)
