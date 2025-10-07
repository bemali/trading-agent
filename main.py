from agents.news_agent import run_workflow
from agents.chat_agent import get_response
from dotenv import load_dotenv
import json
import os

def news_agent():

    load_dotenv()

    stock_code = 'MSFT'

    result = run_workflow(stock_code)
    print(result['final_verdict'])
    print(result['graph_execution'])


def chat_agent():

    question= input("What is your question:")

    result = get_response(question)
    print(result['response'])
    print(result['graph_execution'])

if __name__ == "__main__":

    chat_agent()


    