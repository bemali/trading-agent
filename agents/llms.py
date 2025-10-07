from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_llm(model: str = None, temperature: float = 0.7):
    """
    Initialize and return a LangChain AzureChatOpenAI instance.
    
    Args:
        model: Optional model name to use. If None, reads from LLM_MODEL environment variable.
        temperature: Temperature parameter for the model. Defaults to 0.7.
        
    Returns:
        An initialized AzureChatOpenAI instance.
    """
    # Get model from environment if not specified
    if model is None:
        model = os.environ.get("LLM_MODEL", "gpt-4.1")  # Default to gpt-4.1 if not set
    
    return AzureChatOpenAI(
        deployment_name=model,
        temperature=temperature
    )


if __name__ == "__main__":
    # For testing purposes
    llm = get_llm(temperature=0.5)
    response = llm.invoke([{"role": "user", "content": "is there a vfs global office that handles canada visa in Brisbane?, respond with references"}])
    print(response.content)
