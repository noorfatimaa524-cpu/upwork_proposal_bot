from langchain.tools import tool

@tool
def save_to_file(text: str) -> str:
    """Save text to a file."""
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(text)
    return "Saved successfully"


@tool
def format_proposal(text: str) -> str:
    """Format freelancer proposal."""
    return f"""
Professional Proposal:

{text}
"""