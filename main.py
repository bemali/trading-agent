from agents.news_agent import run_workflow
from dotenv import load_dotenv
import json
import os

def main():

    load_dotenv()

    stock_code = 'MSFT'

    result = run_workflow(stock_code)
    print(result['final_verdict'])
    print(result['graph_execution'])


if __name__ == "__main__":

    main()


    