
from typing import Dict, Any, List, TypedDict, Literal, Annotated
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage

# Define the state schema
class NewsAgentState(TypedDict):
    """State for agent workflow which analyses the news items and gives insights."""
    # The stock code to be analysed
    stock_code: str 
    # Messages for the tools used
    messages: List[BaseMessage]
    # Reference URLs
    urls: List[str]
    # If the judge has reached the final verdict
    reached_conclusion: bool
    # The final verdict from the judge
    final_verdict: str
    # Graph execution
    graph_execution: List[dict]
    # Recursion count
    recursion_count:int


class ChatAgentState(TypedDict):
    """State for the three agents workflow."""
    # The original user question
    question: str 
    # Messages for the tools used
    messages: List[BaseMessage]
    # Reference URLs
    urls: List[str]
    # Response
    response: str
    # Graph execution
    graph_execution: List[dict]
    # Recursion count
    recursion_count:int