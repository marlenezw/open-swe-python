"""Planner agent - analyzes requirements and creates execution plans."""

from langchain_core.messages import HumanMessage, SystemMessage
from ..state import AgentState
from ..llm import planner_llm
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


def planner_agent(state: AgentState) -> AgentState:
    """
    Planner agent that analyzes requirements and creates detailed execution plans.
    
    Creates a structured plan with:
    - Problem analysis
    - Step-by-step implementation approach
    - Expected deliverables
    """
    messages = [
        SystemMessage(content="""You are an expert software planning agent.

        Your responsibilities:
        1. Analyze the coding request thoroughly
        2. Break down the problem into clear, actionable steps
        3. Create a detailed implementation plan
        4. Consider edge cases and best practices

        Please create a comprehensive plan for the following request. Include:
        - Problem analysis
        - Step-by-step implementation approach
        - File structure (if creating new files)
        - Testing considerations
        - Expected deliverables

        Format your response as a structured plan that a programmer can follow."""),
        HumanMessage(content=f"Request: {state['current_request']}")
    ]

    print("🚀 Running Planner Agent")

    response = planner_llm.invoke(messages, model_name="DeepSeek-R1-0528")

    thoughts, text = strip_thinking_tokens(response)
    
    # Update state with the cleaned plan
    new_state = state.copy()
    new_state["plan"] = text
    new_state["status"] = "planning"
    
    # Store the cleaned content back in the response object
    if hasattr(response, 'content'):
        response.content = text
    new_state["messages"].append(response)
    new_state["next_agent"] = "programmer"
    
    return new_state
