"""
Streamlit app for the trading agent platform.
"""

import streamlit as st
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
from pathlib import Path
from datetime import datetime

# Import utility modules
from app.utils.storage import user_dir, read_json, write_json_with_lock
from app.utils.finance import update_portfolio_prices
from app.utils.news import get_news_for_stock
from app.utils.agent_adapter import ask_agent
from app.src.portfolio_updater import update_portfolio_in_background

# Set page configuration
st.set_page_config(
    page_title="Trading Agent Platform",
    page_icon="📈",
    layout="wide",
)

# Initialize session state variables
if "username" not in st.session_state:
    st.session_state.username = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "base_messages" not in st.session_state:
    st.session_state.base_messages = []
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False

# Helper function to check if user exists
def user_exists(username):
    """Check if a user directory exists."""
    return (user_dir(username) / "profile.json").exists()

# Helper function to create a new user
def create_user(username):
    """Create a new user profile."""
    profile_path = user_dir(username) / "profile.json"
    
    # Create basic profile
    profile = {
        "name": username,
        "created_at": datetime.now().isoformat(),
        "meta": {}
    }
    
    # Create empty portfolio
    portfolio_path = user_dir(username) / "portfolio.json"
    portfolio = []
    
    # Write files
    write_json_with_lock(profile_path, profile)
    write_json_with_lock(portfolio_path, portfolio)
    
    return True

# Helper function to load user profile
def load_user_profile(username):
    """Load a user's profile data."""
    profile_path = user_dir(username) / "profile.json"    
    return read_json(profile_path)

# Helper function to load user portfolio
def load_user_portfolio(username):
    """Load a user's portfolio data."""
    portfolio_path = user_dir(username) / "portfolio.json"
    # Trigger background update of portfolio prices
    update_portfolio_in_background(username)
    return read_json(portfolio_path) or []

# Function to handle login
def handle_login(username):
    """Process user login."""
    username = username.strip().lower()
    
    if not username:
        return False, "Username cannot be empty."
    
    # Check if user exists, create if not
    if not user_exists(username):
        created = create_user(username)
        if not created:
            return False, "Failed to create user."
    
    # Set session state
    st.session_state.username = username
    st.session_state.chat_history = []
    st.session_state.base_messages = []
    
    return True, f"Welcome, {username}!"

# Function to create portfolio bar chart
def create_portfolio_chart(portfolio):
    """Create a clustered bar chart for portfolio visualization."""
    if not portfolio:
        return None
    
    # Prepare data
    chart_data = []
    for item in portfolio:
        purchase_value = round(item.get('purchase_price', 0) * item.get('quantity', 0), 2)
        current_value = item.get('value', 0)
        chart_data.append({
            "Symbol": item.get('stock_code', 'Unknown'),
            "Type": "Purchase Value",
            "Value": purchase_value
        })
        chart_data.append({
            "Symbol": item.get('stock_code', 'Unknown'),
            "Type": "Current Value",
            "Value": current_value
        })
    
    df = pd.DataFrame(chart_data)
    
    # Create clustered bar chart with Altair
    # Using "column" to create clusters by Type
    chart = alt.Chart(df).mark_bar().encode(
        # Create columns by Type to make clustered bars
        column=alt.Column('Type:N', title=None),
        # X-axis shows the symbols
        x=alt.X('Symbol:N', title='Stock', axis=alt.Axis(labelAngle=-45)),
        # Y-axis shows the values
        y=alt.Y('Value:Q', title='Value ($)'),
        # Color distinguishes between purchase and current values
        color=alt.Color('Type:N', scale=alt.Scale(
            domain=['Purchase Value', 'Current Value'],
            range=['#5778a4', '#e49444']
        )),
        tooltip=['Symbol', 'Type', 'Value']
    ).properties(
        title='Portfolio Values: Purchase vs Current',
        height=400
    ).configure_view(
        stroke=None
    )
    
    return chart

# Login screen
def show_login_screen():
    """Display the login screen."""
    st.title("Trading Agent Platform")
    st.markdown("### Login to Your Account")
    
    with st.form("login_form"):
        username = st.text_input("Username (no password required)")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            success, message = handle_login(username)
            if success:
                st.success(message)
                st.rerun()  # Refresh the app after successful login
            else:
                st.error(message)
    
    st.markdown("---")
    st.markdown("*Don't have an account? Just enter a username to create one automatically.*")

# Main application
def show_main_app():
    """Display the main application after login."""
    username = st.session_state.username
    
    # Sidebar with profile info
    with st.sidebar:
        st.title(f"Welcome, {username}")
        
        profile = load_user_profile(username)
        created_at = profile.get("created_at", "Unknown")
        try:
            # Try to parse and format the date
            dt = datetime.fromisoformat(created_at)
            created_at = dt.strftime("%b %d, %Y")
        except:
            pass
        
        st.markdown(f"**Account created:** {created_at}")
        
        st.markdown("---")
        
        # LLM model selection
        st.markdown("### LLM Model Settings")
        llm_model = st.selectbox(
            "Select LLM Model",
            options=["gpt-4.1", "gpt-4.0"],
            index=0,
            key="llm_model"
        )
        
        # Update environment variable based on selection
        os.environ["LLM_MODEL"] = llm_model
        st.markdown(f"*Using model: {llm_model}*")
        
        st.markdown("---")
        
        # Navigation options
        st.markdown("### Navigation")
        
        if st.button("📊 Portfolio View", use_container_width=True):
            st.session_state.show_chat = False
            st.rerun()
            
        if st.button("💬 Chat with Agent", use_container_width=True):
            st.session_state.show_chat = True
            st.rerun()
        
        st.markdown("---")
        
        # Logout button
        if st.button("Logout", use_container_width=True):
            st.session_state.username = None
            st.rerun()  # Refresh the app after logout

    # Main content area
    if st.session_state.show_chat:
        show_chat_interface()
    else:
        show_portfolio_interface()

# Portfolio interface
def show_portfolio_interface():
    """Display the portfolio interface."""
    st.title("Your Portfolio")
    
    username = st.session_state.username
    portfolio = load_user_portfolio(username)
    
    # Update prices button
    col1, col2 = st.columns([6, 1])
    with col1:
        last_updated = "Never"
        if portfolio and 'last_updated' in portfolio[0]:
            try:
                dt = datetime.fromisoformat(portfolio[0]['last_updated'])
                last_updated = dt.strftime("%b %d, %Y at %I:%M %p")
            except:
                pass
        st.markdown(f"*Last updated: {last_updated}*")
    with col2:
        if st.button("Update Prices", type="primary"):
            with st.spinner("Updating prices..."):
                success = update_portfolio_prices(username)
                if success:
                    st.success("Prices updated successfully!")
                    # Reload portfolio with updated prices
                    portfolio = load_user_portfolio(username)
                else:
                    st.error("Failed to update prices.")
    
    # Portfolio Summary
    if not portfolio:
        st.info("Your portfolio is empty. Add some stocks to get started!")
    else:
        # Create portfolio DataFrame for display
        df_data = []
        for item in portfolio:
            # Ensure all numeric values have proper defaults to avoid None formatting issues
            current_price = item.get('current_price')
            if current_price is None:
                current_price = 0
                
            df_data.append({
                "Company": item.get('company_name', 'Unknown'),
                "Symbol": item.get('stock_code', 'Unknown'),
                "Quantity": item.get('quantity', 0),
                "Purchase Price": f"${item.get('purchase_price', 0):.2f}",
                "Current Price": f"${current_price:.2f}",
                "Total Value": f"${item.get('value', 0):.2f}",
                "Return %": f"{item.get('percent_return', 0):.2f}%",
                "Return $": f"${item.get('total_return', 0):.2f}"
            })
        
        df = pd.DataFrame(df_data)
        
        # Calculate total portfolio value
        total_value = sum(item.get('value', 0) for item in portfolio)
        total_purchase = sum(item.get('purchase_price', 0) * item.get('quantity', 0) for item in portfolio)
        total_return = total_value - total_purchase
        total_return_percent = (total_return / total_purchase * 100) if total_purchase > 0 else 0
        
        # Portfolio metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Portfolio Value", f"${total_value:.2f}")
        with col2:
            st.metric("Total Return", f"${total_return:.2f}", f"{total_return_percent:.2f}%")
        with col3:
            num_stocks = len(portfolio)
            st.metric("Number of Holdings", f"{num_stocks}")
        
        # Display portfolio table
        st.markdown("### Holdings")
        st.dataframe(
            df,
            hide_index=True,
            column_config={
                "Return %": st.column_config.NumberColumn(
                    "Return %",
                    format="%.2f%%",
                    help="Percentage return on investment",
                ),
            },
            use_container_width=True
        )
        
        # Portfolio visualization
        st.markdown("### Portfolio Visualization")
        chart = create_portfolio_chart(portfolio)
        if chart:
            st.altair_chart(chart, use_container_width=True)
        
        # News section
        st.markdown("### Latest News")
        for item in portfolio:
            symbol = item.get('stock_code')
            if not symbol:
                continue
                
            company_name = item.get('company_name', symbol)
            st.markdown(f"#### {company_name} ({symbol})")
            
            news_items = get_news_for_stock(symbol, count=2)
            for news in news_items:
                with st.expander(f"{news['headline']} - {news['source']}"):
                    st.markdown(f"*{news['date']}*")
                    st.markdown(news['snippet'])
            
            st.markdown("---")

# Chat interface
def show_chat_interface():
    """Display the chat interface."""
    st.title("Chat with Trading Agent")
    
    username = st.session_state.username
    
    # Add a debug expander to show base messages
    with st.expander("Debug: View Base Messages", expanded=False):
        if st.session_state.base_messages:
            st.markdown("### Current Base Messages")
            for i, msg in enumerate(st.session_state.base_messages):
                msg_type = type(msg).__name__
                st.markdown(f"**Message {i+1} ({msg_type}):**")
                st.code(msg.content[:200] + "..." if len(msg.content) > 200 else msg.content)
        else:
            st.info("No base messages in history yet.")
    
    # Display chat history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(chat["user"])
        with st.chat_message("assistant"):
            st.markdown(chat["assistant"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your portfolio or trading..."):
        # Add user message to chat history
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response from agent
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response, base_messages = ask_agent(username, prompt, st.session_state.base_messages)
                st.markdown(response)
        
        # Save to history
        st.session_state.chat_history.append({
            "user": prompt,
            "assistant": response
        })
        
        # Save base messages for future calls
        st.session_state.base_messages = base_messages

# Main app logic
def main():
    """Main application entry point."""
    if st.session_state.username is None:
        show_login_screen()
    else:
        show_main_app()

if __name__ == "__main__":
    main()
