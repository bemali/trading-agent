from src.simple_graph import run_workflow
from dotenv import load_dotenv
import json
import os

def main():
    load_dotenv()

    # get the user name
    user_name = input("Enter your name, Enter if like to go annonymous: ")
    if user_name.strip() == "":
        user_name = "Anonymous"
    print(f"Hello, {user_name}! Welcome to the Three Agents Debate System.")    

    # Get user's history
    user_history = ""
    if os.path.exists("user_profiles.json"):
        try:
            import json
            with open("user_profiles.json", "r", encoding="utf-8") as f:
                profiles = json.load(f)
                if user_name in profiles:
                    user_history = profiles[user_name].get("history", "")
        except Exception as e:
            print(f"Error loading user profiles: {e}")

        
    # get which model to use
    print("\nAvailable models:")
    print("1. gpt-4")
    print("2. claude-3-opus")
    print("3. gemini-pro")
    print("4. mistral-large")
    
    model_choice = input("\nSelect a model (1-4, default is gpt-4): ")
    
    # Map the choice to the actual model name
    model_mapping = {
        "1": "gpt-4.1",
        "2": "gpt-4.1",
        "3": "gpt-4.1",
        "4": "gpt-4.1"
    }
    
    model = model_mapping.get(model_choice, "gpt-4")
    print(f"Using model: {model}")
    
    # Run the workflow
    question = input("\nEnter your question: ")
    question_with_history = f"{user_history}\n\nUser Question: {question}" if user_history else question
    
    # Execute the graph workflow
    result = run_workflow(model,question_with_history)
    
    
    
    
    print("\n=== Final Verdict ===")
    print(result["final_verdict"])
    
    print("\n=== Summary ===")
    print(result["summary"])

    print("\n=== Graph Execution path ===")
    for ev in result["graph_execution"]:
        print(ev)
    
    
    # Update user profile with new history
    try:
        profiles = {}
        if os.path.exists("user_profiles.json"):
            with open("user_profiles.json", "r", encoding="utf-8") as f:
                profiles = json.load(f)
        
        # Add or update user profile with new history
        if user_name not in profiles:
            profiles[user_name] = {}
        
        # Use summary as history for future interactions
        profiles[user_name]["history"] = f"Previous question: {question}\nSummary: {result['summary']}"
        
        with open("user_profiles.json", "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=4)
            
    except Exception as e:
        print(f"Error updating user profile: {e}")

if __name__ == "__main__":
    main()
