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
from src.llms import get_llm
from src.tools import web_search
from src.custom_tool_node import TrackingToolNode, CustomToolNode
from src.state import NewsAgentState





def create_graph(model:str)-> StateGraph:

    # Define nodes

    # Tool nodes
    tools = [web_search]

    # Tool call node
    tool_node = CustomToolNode(tools)
    
    # Define Agents

    # Judge Agent
    def judge_agent(state: NewsAgentState):
        """"Judge agent provides initial instructions"""

        # judge's decisions
        reached_verdict = False
        final_verdict =""
        recursion_count = state["recursion_count"]+1

        judge_llm = get_llm(model)
        if state["messages"] != []:
            last_message_received = state["messages"][-1]
            state["judge_messages"].append(last_message_received )

        response = judge_llm.invoke(state["judge_messages"])
        if "verdict" in response.content.lower() or state["recursion_count"]>3:
            reached_verdict = True
            final_verdict = response.content


        return Command(update={
            "messages": [response],
            "graph_execution": state.get("graph_execution", []) + ["judge"],
            "judge_messages": state.get("judge_messages",[])+[response ],
            "reached_verdict":reached_verdict,
            "final_verdict":final_verdict,
            "recursion_count":recursion_count

        })
    
    # Research Agent
    def research_agent(state: NewsAgentState):
        """Researches based on the judge's instructions"""
        research_llm = get_llm(model)
        research_llm = research_llm.bind_tools(tools)

        last_message_received = state["messages"][-1]
        state["research_messages"].append(last_message_received )

        response = research_llm.invoke(state["research_messages"])

        return Command(update={
            "messages": [response],
            "graph_execution": state.get("graph_execution", []) + ["research"],
            "research_messages": state.get("research_messages",[])+[response ]
        })
    
    
    # add conditions for conditional routing

    def check_reached_verdict(state:NewsAgentState):

        reached_verdict = state["reached_verdict"]
        if reached_verdict:
            return END
        else:
            return "research"
        
    
    def check_research_message(state:NewsAgentState):

        last_research_message = state["research_messages"][-1]

        if isinstance(last_research_message, AIMessage) and last_research_message.content and not state["reached_verdict"]:
            return "judge"
        else:
            return "tools"
    

    # Create the graph
    workflow = StateGraph(NewsAgentState)
    
    # Add nodes to the graph
    workflow.add_node("judge", judge_agent)
    workflow.add_node("research", research_agent)
    workflow.add_node("tools",tool_node )
    
    # Define the edges
    # Start with the judge
    workflow.set_entry_point("judge")
    
    # From judge to research
    workflow.add_conditional_edges(
        "judge",
        check_reached_verdict
    )
    
    # From research to tools if tools are called
    workflow.add_conditional_edges(
        "research",
        check_research_message
    )
    
    # From tools back to research
    workflow.add_edge("tools", "research")

    # Finally, judge to complete
    workflow.add_edge("judge", END)
    
    # Compile the graph
    return workflow.compile()

def run_workflow(model:str, question:str):

    judge_system_message = "Your task is to rephrase the user question in a more academic manner, and provide instructions for the research agent to be able to research better on the latest information. your research agent can search latest info till 2026. better if their results are based on post June 2024 results. Once the research agent comes back with its response, give your verdict, properly summarize what the research agent has come up with including relevant citations and end the loop. Never mention the word 'verdict', unless you have come up with the final verdict."

    research_agent_system_message = "Your task is to search the web and get the info"

    initial_state = {
        "question": question,
        "messages": [],
        "judge_messages": [SystemMessage(content=judge_system_message ), HumanMessage(content=question)],
        "research_messages": [SystemMessage(content=research_agent_system_message )],
        "urls": [],
        "reached_verdict": False,
        "final_verdict": "",
        "summary": "",
        "graph_execution":[],
        "recursion_count": 0
    }

    # Create the graph
    graph = create_graph(model)
    
    
    # Run the workflow with the model and initial state
    result = graph.invoke(initial_state)

    return result
