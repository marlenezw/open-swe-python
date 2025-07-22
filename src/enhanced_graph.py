"""Simplified agent graph with async support."""

import json
import os
import asyncio
from pathlib import Path
from typing import Dict, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

# Import display functions
from visuals import display_agent_status, display_agent_result, print_welcome_message
from .llm import manager_llm, planner_llm, programmer_llm


# Simplified state - only what we really need
class SimpleState(Dict):
    """Simplified agent state."""
    request: str
    plan: Optional[str] = None
    code: Optional[str] = None
    files_created: list = []
    next: str = "manager"
    iterations: int = 0

def extract_thinking(text: str) -> tuple[str, str]:
    """Extract thinking content and clean text."""
    if "<think>" not in text:
        return "", text
    
    start = text.find("<think>")
    end = text.find("</think>")
    if start >= 0 and end > start:
        thoughts = text[start+7:end].strip()
        clean = text[:start] + text[end+9:]
        return thoughts, clean.strip()
    return "", text


async def stream_response(llm, messages, agent_name: str) -> str:
    """Generic async streaming handler for all agents."""
    
    display_agent_status(agent_name, "working")
   
    
    full_response = ""
    thinking_buffer = ""
    in_thinking = False
    displayed_lines = 0
    
    async for chunk in llm.astream(messages):
        if hasattr(chunk, 'content') and chunk.content:
            full_response += chunk.content
            
            # Real-time thinking display
            if "<think>" in chunk.content:
                in_thinking = True
                print(f"   💭 {agent_name.title()} Thinking (live)")
                # Get content after <think>
                start = chunk.content.find("<think>") + 7
                if start < len(chunk.content):
                    thinking_buffer += chunk.content[start:]
            elif "</think>" in chunk.content:
                # Get content before </think>
                end = chunk.content.find("</think>")
                if end > 0:
                    thinking_buffer += chunk.content[:end]
                in_thinking = False
            elif in_thinking:
                thinking_buffer += chunk.content
            
            # Display new complete lines as they come (max 10)
            if in_thinking and displayed_lines < 10:
                lines = thinking_buffer.split('\n')
                while displayed_lines < 10 and displayed_lines < len(lines) - 1:
                    line = lines[displayed_lines].strip()
                    if line:
                        print(f"      {line}")
                    displayed_lines += 1
                if displayed_lines == 10 and len(lines) > 11:
                    print("      ... (truncated)")
                    displayed_lines = 11  # Stop checking
    
    thoughts, clean_text = extract_thinking(full_response)
    
    # Don't show rich display thoughts - we already showed them live
    print()  # Just add spacing
    
    return clean_text


async def manager_agent(state: SimpleState) -> SimpleState:
    """Simplified manager - just routes to next agent."""
    messages = [
        SystemMessage(content=f"""You are a manager agent that coordinates the overall workflow:

        Your responsibilities:
        1. Analyze the current request and state
        2. Decide which agent should handle the next step
        3. Route to planner if no plan exists
        4. Route to programmer if a plan exists but no code changes made
        5. Mark as complete if work is finished

        Current state:
        - Request: {state['request'][:100]}...
        - Has plan: {bool(state.get('plan'))}
        - Has code: {bool(state.get('code'))}
        
        Reply with ONE word only:
        - "planner" if no plan exists
        - "programmer" if plan exists but no code
        - "complete" if code exists
        """),
        HumanMessage(content=state['request'])
    ]

    response = await stream_response(manager_llm, messages, "manager")
    next_agent = response.strip().lower()
    
    # Validate and default
    if next_agent not in ["planner", "programmer", "complete"]:
        if not state.get('plan'):
            next_agent = "planner"
        elif not state.get('code'):
            next_agent = "programmer"
        else:
            next_agent = "complete"
    
    display_agent_result("manager", f"Next: {next_agent}")
    
    state['next'] = next_agent
    state['iterations'] += 1
    return state


async def planner_agent(state: SimpleState) -> SimpleState:
    """Simplified planner - creates implementation plan."""
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
        
        Format your response as a structured plan that a programmer can follow.
        Keep it concise and actionable.
        """),
        HumanMessage(content=state['request'])
    ]

    plan = await stream_response(planner_llm, messages, "planner")

    display_agent_result("planner", f"Plan created ({len(plan)} chars)")
    
    state['plan'] = plan
    state['next'] = "manager"
    return state


async def programmer_agent(state: SimpleState) -> SimpleState:
    """Simplified programmer - generates code."""
    messages = [
        SystemMessage(content=f"""You are an expert programmer agent. Implement this plan:

        Plan to implement:
        {state.get('plan', 'No plan provided')}

        Your responsibilities:
        1. Follow the provided plan exactly
        2. Generate complete, working code
        3. Include proper error handling and documentation
        4. Follow best practices for the programming language
        5. Provide clear implementation details
        6. Make sure to include a requirements.txt file or equivalent!

        Generate the actual code implementation. Include:
        - Complete file contents
        - Proper imports and dependencies
        - Error handling
        - Documentation/comments
        - Example usage if applicable

        Format your response as complete code with clear file organization.
        You should return a json object in this format:
        
        Format:
        ```json
        {{
            "files": [
                {{"file_path": "main.py", "file_content": "code here"}},
                {{"file_path": "templates/index.html", "file_content": "code here"}},
            ],
            "folder_name": "project_name"
        }}
        ```
        
        Use 'file_path' to support nested directories. Write complete, working code with error handling.
        Ensure all strings are properly escaped for valid JSON parsing.
        """),
        HumanMessage(content="Generate the code with properly escaped JSON")
    ]

    response = await stream_response(programmer_llm, messages, "programmer")

    # Enhanced JSON extraction with subfolder support and better error handling
    files_created = []
    if "```json" in response:
        json_start = response.find("```json") + 7
        json_end = response.find("```", json_start)
        if json_end > json_start:
            try:
                json_content = response[json_start:json_end].strip()
                
                # Parse JSON with fallback strategies
                data = None
                
                # Try standard parsing first
                try:
                    data = json.loads(json_content)
                except json.JSONDecodeError:
                    # Fix common JSON issues (trailing commas)
                    import re
                    fixed_json = re.sub(r',(\s*[}\]])', r'\1', json_content)
                    
                    try:
                        data = json.loads(fixed_json)
                    except json.JSONDecodeError:
                        # Manual extraction as last resort
                        try:
                            folder_match = re.search(r'"folder_name"\s*:\s*"([^"]*)"', json_content)
                            folder_name = folder_match.group(1) if folder_match else "output"
                            
                            # Extract files using regex
                            files = []
                            file_pattern = r'"file_path"\s*:\s*"([^"]+)"[^}]*?"file_content"\s*:\s*"([^"]*(?:\\.[^"]*)*)"'
                            
                            for match in re.finditer(file_pattern, json_content, re.DOTALL):
                                file_path = match.group(1)
                                content = match.group(2)
                                # Unescape common sequences
                                content = content.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
                                files.append({"file_path": file_path, "file_content": content})
                            
                            data = {"folder_name": folder_name, "files": files}
                        except Exception as e:
                            print(f"Failed to parse JSON: {e}")
                
                # Create files if data was successfully parsed
                if data:
                    folder = Path("./agentic_code") / data.get("folder_name", "output")
                    folder.mkdir(parents=True, exist_ok=True)
                    
                    for file_info in data.get("files", []):
                        file_path_str = file_info.get("file_path") or file_info.get("file_name")
                        file_content = file_info.get("file_content")
                        
                        if file_path_str and file_content:
                            file_path = folder / file_path_str
                            file_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            await asyncio.to_thread(file_path.write_text, file_content, encoding='utf-8')
                            files_created.append(str(file_path))
                else:
                    print("Could not parse JSON response - no files created")
                    
            except Exception as e:
                print(f"Error creating files: {e}")
                # Try to provide more detailed error information
                import traceback
                print(f"Detailed error: {traceback.format_exc()}")
                print("Response preview:")
                print(response[:1000] + "..." if len(response) > 1000 else response)
    
    
    display_agent_result("programmer", f"Created {len(files_created)} files")
    
    state['code'] = response
    state['files_created'] = files_created
    state['next'] = "manager"
    return state


def create_simple_graph():
    """Create simplified agent graph with async support."""
    workflow = StateGraph(SimpleState)
    
    # Add nodes (async functions)
    workflow.add_node("manager", manager_agent)
    workflow.add_node("planner", planner_agent)
    workflow.add_node("programmer", programmer_agent)
    
    # Simple routing
    def route(state):
        if state.get('iterations', 0) > 10:  # Safety limit
            return END
        next_agent = state.get('next', 'manager')
        return END if next_agent == 'complete' else next_agent
    
    # Set up edges
    workflow.set_entry_point("manager")
    
    for node in ["manager", "planner", "programmer"]:
        workflow.add_conditional_edges(
            node, route,
            {"manager": "manager", "planner": "planner", 
             "programmer": "programmer", END: END}
        )
    
    return workflow.compile()

async def run_agent(request: str) -> SimpleState:
    """Run the simplified agent system asynchronously."""
    initial_state = SimpleState(
        request=request,
        plan=None,
        code=None,
        files_created=[],
        next="manager",
        iterations=0
    )
    
    app = create_simple_graph()
    
    try:
        final_state = initial_state
        async for state_update in app.astream(initial_state):
            if isinstance(state_update, dict):
                for _, node_state in state_update.items():
                    final_state = node_state
                    break
        
        return final_state
        
    except Exception as e:
        print(f"Error: {e}")
        return initial_state

# Main execution
async def main():
    import sys
    
    if len(sys.argv) > 1:
        request = " ".join(sys.argv[1:])
        result = await run_agent(request)
        print(f"\nCompleted. Files created: {result.get('files_created', [])}")
    else:
        print("Usage: python simplified_graph.py <request>")

if __name__ == "__main__":
    import atexit
    import os

    print_welcome_message()

    # Close stderr on exit to suppress cleanup warnings for the moment
    atexit.register(lambda: os.close(2))

    asyncio.run(main())
