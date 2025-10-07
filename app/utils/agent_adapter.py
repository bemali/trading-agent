"""
Agent adapter module for handling communication with the trading agent.
"""

from typing import List, Dict, Any
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from agents.chat_agent import get_response

def ask_agent(username: str, message: str, history: List[BaseMessage]) -> str:
    """
    Send a message to the trading agent and get a response.
    
    Args:
        username: The user's username
        message: The user's message to the agent
        history: List of previous messages in the conversation
        
    Returns:
        The agent's response as a string
    """
    
    # Add system message from chat instructions if this is a new conversation
    if not history:
        result = get_response(
        question=message)
    else:
        result = get_response(
        question=message,
        messages=history)
    
    return result['response'], result['messages']
