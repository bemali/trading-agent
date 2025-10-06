from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv


def get_llm(model:str, temperature: float = 0.7):
    
    return AzureChatOpenAI(
    deployment_name=model,)


if __name__ == "__main__":

    load_dotenv()
    
    llm = get_llm(model = "gpt-4.1", temperature=0.5)
    response = llm.invoke([{"role": "user", "content": "is there a vfs global office that handles canada visa in Bribane?, respond with references"}])
    print(response.content)