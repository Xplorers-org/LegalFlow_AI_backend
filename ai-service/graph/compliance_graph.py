from langgraph.graph import StateGraph, END
from ai-service.state.case_state import CaseState
from ai-service.agents.financial_agent import financial_agent_node
from ai-service.agents.lease_parser_agent import lease_parser_node
from ai-service.agents.legal_research_agent import legal_research_node
from ai-service.agents.legal_analysis_agent import legal_analysis_node
from ai-service.agents.drafting_agent import drafting_agent_node
from ai-service.utils.logging import get_logger

logger = get_logger("ai_service.graph")


def decision_router(state: CaseState) -> str:
    """Decision Router determining conditional branch transitions."""
    action = state.get("recommended_action", "REMINDER")
    logger.info("Decision Router evaluating transition", action=action)
    return "drafting_agent"


def build_compliance_graph() -> StateGraph:
    """Constructs the LangGraph multi-agent state machine workflow."""
    workflow = StateGraph(CaseState)

    # Add Agent Nodes
    workflow.add_node("financial_agent", financial_agent_node)
    workflow.add_node("lease_parser_agent", lease_parser_node)
    workflow.add_node("legal_research_agent", legal_research_node)
    workflow.add_node("legal_analysis_agent", legal_analysis_node)
    workflow.add_node("drafting_agent", drafting_agent_node)

    # Set Entry Point
    workflow.set_entry_point("financial_agent")

    # Define Sequential & Conditional Edges
    workflow.add_edge("financial_agent", "lease_parser_agent")
    workflow.add_edge("lease_parser_agent", "legal_research_agent")
    workflow.add_edge("legal_research_agent", "legal_analysis_agent")

    # Add Conditional Edge via Decision Router
    workflow.add_conditional_edges(
        "legal_analysis_agent",
        decision_router,
        {
            "drafting_agent": "drafting_agent"
        }
    )

    workflow.add_edge("drafting_agent", END)

    return workflow.compile()
