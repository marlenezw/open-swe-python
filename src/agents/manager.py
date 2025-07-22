"""Manager agent - routes requests and coordinates workflow."""

from langchain_core.messages import HumanMessage, SystemMessage
from ..state import AgentState
from ..llm import manager_llm
from ..utils import clean_llm_response

# Helper function to strip thinking tokens
def strip_thinking_tokens(text: str):
    """
    Extract the content between <think> and </think> tags and remove them from the text.
    """
    thoughts = ""
    while "<think>" in text and "</think>" in text:
        start = text.find("<think>")
        end = text.find("</think>")
        # Extract the content between tags (excluding the tags themselves)
        thoughts += text[start + len("<think>"):end].strip() + "\n\n"
        # Remove the tags and their content from the original text
        text = text[:start] + text[end + len("</think>"):]
    return thoughts.strip(), text.strip()


def manager_agent(state: AgentState) -> AgentState:
    """
    Manager agent that routes requests and coordinates the overall workflow.
    
    Decides whether to:
    - Route to planner for new requests
    - Route to programmer if plan exists
    - Mark as complete if all work is done
    """
    messages = [
        SystemMessage(content="""You are a manager agent that coordinates a coding workflow.

        Your responsibilities:
        1. Analyze the current request and state
        2. Decide which agent should handle the next step
        3. Route to planner if no plan exists
        4. Route to programmer if a plan exists but no code changes made
        5. Mark as complete if work is finished

        Current state:
        - Request: {request}
        - Plan exists: {has_plan}
        - Code changes made: {has_changes}
        - Status: {status}

        Respond with exactly one of: "planner", "programmer", or "complete"
        """.format(
                    request=state["current_request"],
                    has_plan=state["plan"] is not None,
                    has_changes=len(state["code_changes"]) > 0,
                    status=state["status"]
                )),
                HumanMessage(content=f"Current request: {state['current_request']}")
            ]

    print("🚀 Running Manager Agent")
    
    response = manager_llm.invoke(messages, model_name="DeepSeek-R1-0528")
    
    # Clean response by removing thinking tokens
    thoughts, text = strip_thinking_tokens(response)

    # Determine next agent based on cleaned response
    next_agent = text.strip().lower()

    if next_agent not in ["planner", "programmer", "complete"]:
        # Default routing logic
        if not state["plan"]:
            next_agent = "planner"
        elif not state["code_changes"]:
            next_agent = "programmer"
        else:
            next_agent = "complete"
    
    # Update state
    new_state = state.copy()
    new_state["next_agent"] = next_agent
    
    # Create a cleaned response object for storing in messages
    # Store the cleaned content back in the response object
    if hasattr(response, 'content'):
        response.content = text
    new_state["messages"].append(response)
    
    if next_agent == "complete":
        new_state["status"] = "complete"
    
    return new_state
