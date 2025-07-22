"""Example usage of the Python Open SWE agent."""

from mcp.server.fastmcp import FastMCP, Context  

mcp = FastMCP('langchain-coder-mcp')

@mcp.tool()
def run_code_agent(request: str) -> dict:
    """Given a coding request, this tool runs the Python Open SWE agent.
    To create the code required for the task."""
    
    request = f"{request}"
    
    try:
        # Run the agent

        command = f'python -m src.enhanced_graph "{request}"'
        return f"This is the command to run: {command}. Use this exact command and include quotation marks around the request as shown.!"

    except Exception as e:
        print(f"❌ Error running example: {e}")

@mcp.prompt()
def create_repo(location: str = "folder") -> str:
    """Generate a prompt for creating a Github repository from new projects"""

    prompt = f"""Create a new GitHub repository using the Github mcp server 
    using the files located here {location}. The repository should be named 
     appropriately and should include a README.md file with a brief description 
     of the project. It should also include a requirements.txt file with the
     necessary dependencies for the project and a License file."""

    prompt = f"{prompt}"

    # Return a more direct prompt that's easier for the LLM to follow
    return prompt



if __name__ == "__main__":
    # run_code_agent("Create a Python function to calculate the factorial of a number.")
    mcp.run()