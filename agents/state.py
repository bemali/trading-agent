
from typing import Dict, Any, List, TypedDict, Literal, Annotated
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage

# Define the state schema
class NewsAgentState(TypedDict):
    """State for the three agents workflow."""
    # The original user question
    question: str 
    # Messages for the tools used
    messages: List[BaseMessage]
    # Messages to the judge
    judge_messages: List[BaseMessage]
    # Messages to the research agent
    research_messages: List[BaseMessage]
    # Reference URLs
    urls: List[str]
    # If the judge has reached the final verdict
    reached_verdict: bool
    # The final verdict from the judge
    final_verdict: str
    # Final summary of the debate
    summary: str
    # Graph execution
    graph_execution: List[str]
    # Recursion count
    recursion_count:int


class ChatAgentState(TypedDict):
    """State for the three agents workflow."""
    # The original user question
    question: str 
    # Messages for the tools used
    messages: List[BaseMessage]
    # Messages to the judge
    judge_messages: List[BaseMessage]
    # Messages to the research agent
    research_messages: List[BaseMessage]
    # Reference URLs
    urls: List[str]
    # If the judge has reached the final verdict
    reached_verdict: bool
    # The final verdict from the judge
    final_verdict: str
    # Final summary of the debate
    summary: str
    # Graph execution
    graph_execution: List[str]
    # Recursion count
    recursion_count:int