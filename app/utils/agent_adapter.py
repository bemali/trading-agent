"""
Agent adapter module for handling communication with the trading agent.
"""

from typing import List, Dict, Any

def ask_agent(username: str, message: str, history: List[Dict[str, str]]) -> str:
    """
    Send a message to the trading agent and get a response.
    
    Args:
        username: The user's username
        message: The user's message to the agent
        history: List of previous messages in the conversation
        
    Returns:
        The agent's response as a string
    """
    # This is a placeholder implementation
    # In a real implementation, this would connect to an actual agent/LLM
    
    # Simple response based on keywords in the message
    response = "I'm your trading assistant. How can I help you today?"
    
    if "stock" in message.lower() or "invest" in message.lower():
        response = "I can help you analyze stocks and make investment decisions."
    elif "portfolio" in message.lower():
        response = "Your portfolio is looking good! Would you like me to analyze any specific holdings?"
    elif "market" in message.lower():
        response = "The market has been volatile lately. It's important to maintain a diversified portfolio."
    elif "buy" in message.lower() or "sell" in message.lower():
        response = "I can help you evaluate whether to buy or sell a particular stock. Which one are you interested in?"
        
    return response
