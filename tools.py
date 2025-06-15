from duckduckgo_search import DDGS

def web_search(query: str, max_results: int = 3) -> str:
    """Simple web search using DuckDuckGo"""
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=max_results))
        
        if not results:
            return f"No results found for: {query}"
        
        formatted = [f"Search results for '{query}':\n"]
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            snippet = result.get('body', 'No description')
            formatted.append(f"{i}. {title}\n   {snippet}\n")
        
        return "\n".join(formatted)
    except Exception as e:
        return f"Search failed: {str(e)}"

def save_conversation(session_id: str, conversation: str):
    """Save conversation to file"""
    with open(f"conversation_{session_id}.txt", "w") as f:
        f.write(conversation)

def load_conversation(session_id: str) -> str:
    """Load conversation from file"""
    try:
        with open(f"conversation_{session_id}.txt", "r") as f:
            return f.read()
    except:
        return ""