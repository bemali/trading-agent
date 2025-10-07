from langgraph.prebuilt import ToolNode
import inspect
from langgraph.types import Command
from typing import List, TypedDict, Any
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, END

class TrackingToolNode(ToolNode):
    def __call__(self, state):
        # Call parent ToolNode logic (this runs the tool)
        result = super().__call__(state)  # uses the internal node logic

        # Append to execution log
        tool_msgs = [m for m in result.update.get("messages", []) if hasattr(m, "name")]
        tool_names = [m.name for m in tool_msgs]

         # Append to graph_execution
        updated_graph = state.get("graph_execution", []) + tool_names

        # Return Command with updated state
        return Command(update={**result.update, "graph_execution": updated_graph}, goto=result.goto)
    

class CustomToolNode:
    """
    ToolNode-like class that executes tools from the last message's tool_calls.
    Takes a list of tool objects (each must have a 'name' and 'invoke').
    """
    def __init__(self, tools: List[Any]):
        self.tools = tools
        # Build internal mapping for lookup
        self.tools_by_name = {t.name: t for t in tools}

    def __call__(self, state) -> Command:
        commands = []
        tool_calls = getattr(state["messages"][-1], "tool_calls", [])

        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool = self.tools_by_name.get(tool_name)
            if not tool:
                continue  # skip unknown tools

            # Build invocation args
            invocation_args = tool_call.get("args", {}).copy()
            tool_signature = inspect.signature(getattr(tool, "func", tool))
            if "state" in tool_signature.parameters:
                invocation_args["state"] = state
            if "tool_call_id" in tool_signature.parameters:
                invocation_args["tool_call_id"] = tool_call.get("id")

            # Invoke tool
            result = tool.invoke(invocation_args)

            # Wrap result in Command
            if isinstance(result, Command):
                commands.append(result)
            else:
                commands.append(
                    Command(
                        update={
                            "messages": [
                                ToolMessage(
                                    content=str(result),
                                    name=tool_name,
                                    tool_call_id=tool_call.get("id")
                                )
                            ],
                            "graph_execution": [tool_name]  # track executed tool
                        }
                    )
                )

        # Merge all updates into a single Command
        merged_update = {"messages": [], "graph_execution": state["graph_execution"]}
        for cmd in commands:
            merged_update["messages"].extend(cmd.update.get("messages", []))
            merged_update["graph_execution"].extend(cmd.update.get("graph_execution", []))

        return Command(update=merged_update)
    

# Tool call conditions

def call_tool_condition(state):

        last_message = state["messages"][-1]
        case_status = state["case_status"]

        if case_status == 'open':

            if isinstance(last_message,AIMessage) and last_message.tool_calls:
                return 'tools'
            else:
                return 'agent'
        else:
            return END
        
def tool_return_condition(state):

    last_message = state["messages"][-1]
    case_status = state["case_status"]

    if case_status == 'open' and isinstance(last_message,ToolMessage) and last_message.content:
        return 'agent'
    else:
        return END
