from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_openai.llms.base import BaseOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_llm():
    """
    Initialize and return a LangChain AzureChatOpenAI instance.
    
    Args:
        model: Optional model name to use. If None, reads from LLM_MODEL environment variable.
        temperature: Temperature parameter for the model. Defaults to 0.7.
        
    Returns:
        An initialized AzureChatOpenAI instance.
    """
    # Get model from environment if not specified
    model = os.environ.get("LLM_MODEL", "gpt-4.1")  # Default to gpt-4.1 if not set
    
    return ChatOpenAI(
    model=model,
    temperature=0.2)


if __name__ == "__main__":
    # For testing purposes
    llm = get_llm()
    response = llm.invoke([{"role": "user", "content": "how are you"}])
    print(response.content)
