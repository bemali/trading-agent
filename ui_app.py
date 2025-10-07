"""
Streamlit app for the three agents framework using LangGraph.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from src.graph import run_three_agents_workflow

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Three Agents Debate System",
    page_icon="🤖",
    layout="wide",
)

# App title and description
st.title("Three Agents Debate System")
st.markdown("""
This application uses a three-agent debate system powered by LangGraph and OpenAI's GPT models:

1. **Judge Agent**: Evaluates your question and provides instructions
2. **Positive Agent**: Provides arguments in favor
3. **Negative Agent**: Provides arguments against

The Judge Agent then evaluates both arguments and provides a final verdict.
""")

# Sidebar for configuration
st.sidebar.header("Configuration")

# Model selection
model = st.sidebar.selectbox(
    "Select Model",
    ["gpt-4", "gpt-3.5-turbo"],
    index=0,
)

# API Key input
api_key = st.sidebar.text_input(
    "OpenAI API Key",
    value=os.getenv("OPENAI_API_KEY", ""),
    type="password",
)

# Save API key to session state
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

# Main input area
st.header("Ask a Question")
question = st.text_area(
    "Enter a controversial question or topic for debate:",
    height=100,
)

# Process button
if st.button("Start Debate", type="primary", disabled=not (question and api_key)):
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
    elif not question:
        st.error("Please enter a question.")
    else:
        # Show processing message
        with st.spinner("The agents are debating your question..."):
            try:
                # Run the workflow
                result = run_three_agents_workflow(question, model)
                
                # Display results in tabs
                tab1, tab2, tab3, tab4 = st.tabs(["Judge Instructions", "Positive Arguments", "Negative Arguments", "Final Verdict"])
                
                with tab1:
                    st.subheader("Judge's Instructions")
                    st.markdown(result["judge_instructions"])
                
                with tab2:
                    st.subheader("Positive Agent's Response")
                    st.markdown(result["positive_response"])
                
                with tab3:
                    st.subheader("Negative Agent's Response")
                    st.markdown(result["negative_response"])
                
                with tab4:
                    st.subheader("Judge's Final Verdict")
                    st.markdown(result["final_verdict"])
                
                # Save to session history
                if "history" not in st.session_state:
                    st.session_state.history = []
                
                st.session_state.history.append({
                    "question": question,
                    "judge_instructions": result["judge_instructions"],
                    "positive_response": result["positive_response"],
                    "negative_response": result["negative_response"],
                    "final_verdict": result["final_verdict"]
                })
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.error("Please check your API key and try again.")

# History section
if "history" in st.session_state and st.session_state.history:
    st.header("Previous Debates")
    
    for i, item in enumerate(reversed(st.session_state.history)):
        with st.expander(f"Debate {len(st.session_state.history) - i}: {item['question'][:50]}..."):
            st.subheader("Question")
            st.write(item["question"])
            
            st.subheader("Judge's Instructions")
            st.write(item["judge_instructions"])
            
            st.subheader("Positive Arguments")
            st.write(item["positive_response"])
            
            st.subheader("Negative Arguments")
            st.write(item["negative_response"])
            
            st.subheader("Final Verdict")
            st.write(item["final_verdict"])

# Footer
st.markdown("---")
st.markdown("Built with Streamlit, LangGraph, and OpenAI")
