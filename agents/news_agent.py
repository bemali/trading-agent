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
#from src.state import AgentState
from agents.llms import get_llm
from agents.tools import web_search, reach_conclusion
from agents.custom_tool_node import CustomToolNode, call_tool_condition, tool_return_condition
from agents.state import NewsAgentState
from pathlib import Path
from datetime import datetime





def create_graph()-> StateGraph:

    # Define nodes

    # Tool nodes
    tools = [web_search, reach_conclusion]

    # Tool call node
    tool_node = CustomToolNode(tools)
    
    # Define Agents

    # news Agent
    def news_agent(state: NewsAgentState):
        """"Judge agent provides initial instructions"""

    

        # recursion count decisions
        recursion_count = state["recursion_count"]+1
         #llm
        llm = get_llm()
        llm = llm.bind_tools(tools)


        if state["messages"] != []:

            try: 
                response = llm.invoke(state["messages"])
            except:
               pass
               



        # logging the event for debug

        activity_type = 'tool_call' if response.tool_calls else 'ai'

        event = {'activity': 'agent', 'activity_type': activity_type , 'status': 'success'}

        # get the existing state variables
        messages = state.get('messages',[])
        graph_execution = state.get("graph_execution", [])

        # update the state variables
        messages.append(response)
        graph_execution.append(event)
    

        


        return Command(update={
            "graph_execution": graph_execution,
            "messages": messages,
            "recursion_count":recursion_count

        })
    
    def summarize(state: NewsAgentState):

        """summarizes the research by the agent"""

        llm = get_llm()
        messages = state.get("messages")

        current_date = datetime.now().strftime("%Y-%m-%d")

        system_message = f"Analyze the AI messages below and produce a concise summary highlighting the most recent news, trends, or events related to the specified stock. If the news is not relevant to make and immediate stock decision as of {current_date}, please mention so. Limit your response to 100 words maximum. Add relevant URLs to your response"

        messages_to_summarize = [SystemMessage(content = system_message)]

        for msg in messages:
            if isinstance(msg, AIMessage) or isinstance(msg, ToolMessage):
                if msg.content !='':

                    messages_to_summarize.append(AIMessage(content=msg.content))

        response = llm.invoke(messages_to_summarize)
        final_verdict = response.content
        event = {'activity': 'summarize', 'activity_type': 'ai' , 'status': 'success'}

        # get the existing state variables
        graph_execution = state.get("graph_execution", [])
        graph_execution.append(event)

        return Command(update={
            "graph_execution": graph_execution,
            "final_verdict":final_verdict
        })


    
    
    



        
    

    # Create the graph
    workflow = StateGraph(NewsAgentState)
    
    # Add nodes to the graph
    workflow.add_node("news_agent", news_agent)
    workflow.add_node("tools",tool_node)
    workflow.add_node("summarize",summarize)
    
    # Define the edges
    # Start with the judge
    workflow.set_entry_point("news_agent")
    
    
    # From agent to tools if tools are called
    workflow.add_conditional_edges(
        "news_agent",
        call_tool_condition,
        {'end': "summarize",
         'agent': "news_agent",
         'tools':'tools'}
    )
    
    # From tools back to agent
    workflow.add_conditional_edges("tools", tool_return_condition,
                      {'end': "summarize",
                       'agent': 'news_agent'})
    
    # summarize to end
    workflow.add_edge("summarize",END)
    
    # Compile the graph
    return workflow.compile()

def run_workflow(stock_code:str):

    # Load judge instructions
    with open("agents/instructions/news_agent_instructions.md","r") as f:
        agent_system_message= f.read()

    initial_state = {
        "stock_code": stock_code,
        "messages": [SystemMessage(content=agent_system_message ), HumanMessage(content=f"instruct how to research on this stock code: {stock_code}")],
        "urls": [],
        "reached_conclusion": False,
        "final_verdict": "",
        "graph_execution":[],
        "recursion_count": 0
    }

    # Create the graph
    graph = create_graph()
    
    
    # Run the workflow with the model and initial state
    result = graph.invoke(initial_state)

    return result
