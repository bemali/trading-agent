"""
Tools for LangGraph agents to use in the three agents framework.
"""

from typing import Dict, Any, Annotated
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



# support function to determine who called the tool, by matching the last message in state

@tool
def web_search(query: str) -> dict:
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

    # Use Google search
    
    results = DDGS().text(query, max_results=5)
    url_list = [i['href'] for i in results]

    # Parse each URL and extract text content
    
    for url in url_list:
        print(f"Fetching URL by an agent: {url}")
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


    # if there exists a set of URLs for this agent already, append to it
   
    

    return {'web_search_context': web_search_context, 'urls':final_urls }



if __name__ == "__main__":

    print(web_search("melbourne cup"))
