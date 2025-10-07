from typing import Dict, Any, List, TypedDict, Literal
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage, ToolMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.state import CompiledStateGraph
import os
from dotenv import load_dotenv
import inspect
from langgraph.types import Command
from agents.llms import get_llm
from agents.tools import web_search_chat, get_recent_prices
from agents.custom_tool_node import CustomToolNode, call_tool_condition, tool_return_condition
from agents.state import ChatAgentState
from pathlib import Path
from datetime import datetime


def create_graph() -> StateGraph:
    # Define nodes

    # Tool nodes
    tools = [web_search_chat, get_recent_prices]

    # Tool call node
    tool_node = CustomToolNode(tools)
    
    # Define Agents

    # Chat Agent
    def chat_agent(state: ChatAgentState):
        """Chat agent responds to user queries about their portfolio"""

        # recursion count decisions
        recursion_count = state["recursion_count"] + 1
        
        # Initialize llm
        llm = get_llm()
        llm = llm.bind_tools(tools)

        # Process messages if they exist
        if state["messages"] != []:
            try: 
                response = llm.invoke(state["messages"])
            except Exception as e:
                print(f"Error invoking LLM: {str(e)}")
                response = AIMessage(content="I'm sorry, I encountered an error processing your request. Please try again.")

        # Logging the event for debug
        activity_type = 'tool_call' if response.tool_calls else 'ai'
        event = {'activity': 'agent', 'activity_type': activity_type, 'status': 'success'}

        # Get the existing state variables
        messages = state.get('messages', [])
        graph_execution = state.get("graph_execution", [])

        # Update the state variables
        messages.append(response)
        graph_execution.append(event)

        return Command(update={
            "graph_execution": graph_execution,
            "messages": messages,
            "recursion_count": recursion_count,
            "response": response.content
        })
    
    

    # Create the graph
    workflow = StateGraph(ChatAgentState)
    
    # Add nodes to the graph
    workflow.add_node("chat_agent", chat_agent)
    workflow.add_node("tools", tool_node)
    
    # Define the edges
    # Start with the chat agent
    workflow.set_entry_point("chat_agent")
    # From agent to tools if tools are called
    workflow.add_conditional_edges(
        "chat_agent",
        call_tool_condition,
        {'end': END,
         'agent': END,
         'tools': 'tools'}
    )
    
    # From tools back to agent
    workflow.add_conditional_edges(
        "tools", 
        tool_return_condition,
        {'end': END,
         'agent': 'chat_agent'}
    )
    
    # Compile the graph
    return workflow.compile()

def get_response(question: str, messages = None, graph_execution = None, recursion_count = None):
    """
    Run the chat agent workflow with the given question.
    
    Args:
        question: The user's question about their portfolio
        
    Returns:
        The final state after the workflow completes
    """
    # Load chat agent instructions
    with open("agents/instructions/chat_instructions.md", "r") as f:
        agent_system_message = f.read()

    

    initial_state = {
        'question': question,
        'messages': messages if messages is not None else [SystemMessage(content=agent_system_message),HumanMessage(content=question)],
        'response': '',
        'urls':[],
        'graph_execution': graph_execution if graph_execution is not None else [],
        'recursion_count': recursion_count if recursion_count is not None else 0
    }

    # Create the graph
    graph = create_graph()
    
    # Run the workflow with the model and initial state
    result = graph.invoke(initial_state)

    return result
