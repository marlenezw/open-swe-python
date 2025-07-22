"""Programmer agent - implements plans by making code changes."""

from langchain_core.messages import HumanMessage, SystemMessage
from ..state import AgentState
from ..llm import programmer_llm
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

# # Step 1: Generate a query to search the web for the latest info
# async def generate_query(state: SummaryState):
#     # Format the prompt
#     current_date = get_current_date()
#     formatted_prompt = query_writer_instructions.format(
#         current_date=current_date,
#         research_topic=state.research_topic
#     )

#     messages = [
#         SystemMessage(content=formatted_prompt),
#         HumanMessage(content="Generate a query for web search:"),
#     ]

#     # Use the model to analyze the summary and decide whether to continue research or finalize it
#     result = await deep_seek_model.ainvoke(messages)
    
#     thoughts, text = strip_thinking_tokens(result.content)

#     # Send thinking update to client
#     if state.websocket_id in active_connections:
#         await active_connections[state.websocket_id].send({
#             "type": "thinking", 
#             "data": {"thoughts": thoughts}
#         })

#     query = json.loads(text)
#     search_query = query['query']
#     rationale = query['rationale']
#     # Send update to client
#     if state.websocket_id in active_connections:
#         await active_connections[state.websocket_id].send({
#             "type": "generate_query", 
#             "data": {"query": search_query, "rationale": rationale, "thoughts": thoughts}
#         })
    
#     return {"search_query": search_query, "rationale": rationale}


def programmer_agent(state: AgentState) -> AgentState:
    """
    Programmer agent that implements the plans by generating actual code.
    
    Takes the plan and creates:
    - Complete code implementations
    - File contents with proper structure
    - Documentation and comments
    """
    messages = [
        SystemMessage(content="""You are an expert programmer agent.

    Your responsibilities:
    1. Follow the provided plan exactly
    2. Generate complete, working code
    3. Include proper error handling and documentation
    4. Follow best practices for the programming language
    5. Provide clear implementation details

    Plan to implement:
    {plan}

    Generate the actual code implementation. Include:
    - Complete file contents
    - Proper imports and dependencies
    - Error handling
    - Documentation/comments
    - Example usage if applicable

    Format your response as complete code with clear file organization.""".format(
                plan=state["plan"] or "No plan provided"
            )),
            HumanMessage(content=f"Original request: {state['current_request']}")
        ]

    print("🚀 Running Programmer Agent")

    response = programmer_llm.invoke(messages, model_name="DeepSeek-R1-0528")

    thoughts, text = strip_thinking_tokens(response)


    # Update state with the cleaned code implementation
    new_state = state.copy()
    new_state["code_changes"].append(text)
    new_state["status"] = "programming"
    
    # Store the cleaned content back in the response object
    if hasattr(response, 'content'):
        response.content = text
    new_state["messages"].append(response)
    new_state["next_agent"] = "complete"
    
    return new_state
