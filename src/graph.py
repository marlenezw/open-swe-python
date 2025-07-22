"""Main agent graph using LangGraph supervisor pattern."""

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from .state import AgentState
from .agents import manager_agent, planner_agent, programmer_agent
from .config import config


def create_agent_graph():
    """Create the main agent graph using supervisor pattern."""
    
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Add agent nodes
    workflow.add_node("manager", manager_agent)
    workflow.add_node("planner", planner_agent) 
    workflow.add_node("programmer", programmer_agent)
    
    # Define routing logic
    def route_to_agent(state: AgentState):
        """Route to the next agent based on manager decision."""
        next_agent = state.get("next_agent")
        
        if next_agent == "complete":
            return END
        elif next_agent in ["planner", "programmer"]:
            return next_agent
        else:
            return "manager"
    
    # Add edges
    workflow.set_entry_point("manager")
    workflow.add_conditional_edges(
        "manager",
        route_to_agent,
        {
            "planner": "planner",
            "programmer": "programmer", 
            END: END
        }
    )
    workflow.add_edge("planner", "manager")
    workflow.add_edge("programmer", "manager")
    
    # Compile the graph
    app = workflow.compile()
    
    return app


def run_agent(request: str) -> AgentState:
    """Run the agent system with a given request."""
    # Initialize state
    initial_state: AgentState = {
        "messages": [],
        "current_request": request,
        "plan": None,
        "code_changes": [],
        "status": "planning",
        "next_agent": None,
        "iteration_count": 0,
        "error_message": None
    }
    
    # Create and run the graph
    app = create_agent_graph()
    
    try:
        # Run the graph with iteration limit
        final_state = None
        for state in app.stream(initial_state, {"recursion_limit": config.max_iterations}):
            final_state = state
            # Get the last node's state
            if isinstance(state, dict):
                for node_name, node_state in state.items():
                    final_state = node_state
                    break
        
        return final_state or initial_state
        
    except Exception as e:
        # Handle errors gracefully
        error_state = initial_state.copy()
        error_state["status"] = "error"
        error_state["error_message"] = str(e)
        return error_state
