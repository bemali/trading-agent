"""
Tools for LangGraph agents to use in the three agents framework.
"""

from typing import Dict, Any, Annotated, Union
from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from ddgs import DDGS
import json
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from agents.state import NewsAgentState, ChatAgentState
from app.utils.finance import get_recent_prices as finance_get_recent_prices




# support function to determine who called the tool, by matching the last message in state

@tool
def web_search(query: str, state: Annotated[NewsAgentState, InjectedState] ) -> dict:
    """
    Searches the web for the given query using the specified search engine and returns context for the AI response.
    
    Args:
        query: The search query
        search_engine: The search engine to use (google or ddg)
        max_results: Maximum number of results to return
        
    Returns:
        A string containing the search results with source URLs
    """
    web_search_context = ""
    final_urls = []

    # logging the event for debug
    event = {'activity': 'websearch', 'activity_type': 'tools', 'status': 'success'}

    # Use duckduckgo search
    
    try: 
        results = DDGS().text(query, max_results=5)
        url_list = [i['href'] for i in results]

        # Parse each URL and extract text content       
        
        for url in url_list:
            #print(f"Fetching URL by an agent: {url}")
            try:
                response = requests.get(url, timeout=5)
                soup = BeautifulSoup(response.text, 'html.parser')
                web_search_context += f"\n\n\nSource: {url}\n\nContent:"
                # Extract text content (example: all paragraph text)
                paragraphs = soup.find_all('p')
                context = ''
                for p in paragraphs:
                    context += f"{p.get_text()[:500]}"  # Limit to 500 characters per paragraph
                context = context.strip()
                web_search_context += context + "\n"
                final_urls.append(url)
            except Exception as e:
                print(f"Error fetching {url}: {str(e)}")
                continue    

    except Exception as e:
        event['status'] = f'Failure {e}'
    # if there exists a set of URLs for this agent already, append to it
    state_urls = state.get('urls',[])
    state_urls.extend(final_urls)
    graph_execution = state.get('graph_execution',[])
    graph_execution.append(event)

    #print(graph_execution) # debugging
    
    return {'response': {'web_search_context': web_search_context, 'urls':final_urls} , 'state_updates': {'urls': state_urls , 'graph_execution': graph_execution}}


@tool
def web_search_chat(query: str, state: Annotated[ChatAgentState, InjectedState] ) -> dict:
    """
    Searches the web for the given query using the specified search engine and returns context for the AI response.
    
    Args:
        query: The search query
        search_engine: The search engine to use (google or ddg)
        max_results: Maximum number of results to return
        
    Returns:
        A string containing the search results with source URLs
    """
    web_search_context = ""
    final_urls = []

    # logging the event for debug
    event = {'activity': 'websearch', 'activity_type': 'tools', 'status': 'success'}

    # Use duckduckgo search
    
    try: 
        results = DDGS().text(query, max_results=5)
        url_list = [i['href'] for i in results]

        # Parse each URL and extract text content       
        
        for url in url_list:
            #print(f"Fetching URL by an agent: {url}")
            try:
                response = requests.get(url, timeout=5)
                soup = BeautifulSoup(response.text, 'html.parser')
                web_search_context += f"\n\n\nSource: {url}\n\nContent:"
                # Extract text content (example: all paragraph text)
                paragraphs = soup.find_all('p')
                context = ''
                for p in paragraphs:
                    context += f"{p.get_text()[:500]}"  # Limit to 500 characters per paragraph
                context = context.strip()
                web_search_context += context + "\n"
                final_urls.append(url)
            except Exception as e:
                print(f"Error fetching {url}: {str(e)}")
                continue    

    except Exception as e:
        event['status'] = f'Failure {e}'
    # if there exists a set of URLs for this agent already, append to it
    state_urls = state.get('urls',[])
    state_urls.extend(final_urls)

    graph_execution = state.get('graph_execution',[])
    graph_execution.append(event)
    print(graph_execution)

    #print(graph_execution) # debugging
    
    return {'response': {'web_search_context': web_search_context, 'urls':final_urls} , 'state_updates': {'urls': state_urls , 'graph_execution': graph_execution}}


@tool
def reach_conclusion(state: Annotated[Union[NewsAgentState, ChatAgentState], InjectedState]) -> dict:

    """
    Concludes if a agent run is completed as the judge agent has analysed the information from the research agent, and arrived at the conclusion
    
    Args:
        None
        
    Returns:
        True
    """
    # logging the event for debug
    event = {'activity': 'reach_conclusion', 'activity_type': 'tools', 'status': 'success'}
    graph_execution = state.get('graph_execution',[])
    graph_execution.append(event)

    #print(graph_execution) # debugging

    return {'response': {'reached_conclusion': True} , 'state_updates': {'reached_conclusion': True, 'graph_execution': graph_execution}}


@tool
def get_recent_prices(symbol: str, state: Annotated[ChatAgentState, InjectedState]) -> dict:
    """
    Gets the recent stock price data for the given symbol over the last 3 months.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
        
    Returns:
        A list of strings containing price data formatted as "date":{date}, "closing_price":{closing_price}
    """
    # logging the event for debug
    event = {'activity': 'get_recent_prices', 'activity_type': 'tools', 'status': 'success'}
    
    try:
        # Call the finance utility function
        price_list = finance_get_recent_prices(symbol)
        
        # Update state
        graph_execution = state.get('graph_execution', [])
        graph_execution.append(event)
        
        return {
            'response': {
                'prices': price_list,
                'symbol': symbol,
                'count': len(price_list)
            },
            'state_updates': {
                'graph_execution': graph_execution
            }
        }
    except Exception as e:
        event['status'] = f'Failure: {str(e)}'
        graph_execution = state.get('graph_execution', [])
        graph_execution.append(event)
        
        return {
            'response': {
                'prices': [],
                'symbol': symbol,
                'error': str(e),
                'count': 0
            },
            'state_updates': {
                'graph_execution': graph_execution
            }
        }
