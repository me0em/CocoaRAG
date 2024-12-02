import os
import json
from typing import Sequence, Annotated
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.tools import tool
from langchain_core.messages import ToolMessage

from cocoarag.services.rag import QueryRAGSystemService
from cocoarag.models.queries import QueryModel
from cocoarag.models.filters import FiltersModel


# Tools

@tool
def mock(query: str) -> str:
    """ Get relevent information about raven from database
    """
    print("ХУЙ")
    service = QueryRAGSystemService()
    response = service(
        user_id="e0c659a922724cb8acedec7823a2fbd0",
        group_id="248f006d18b64993a1fba9fa7d6ef1cb",
        conversation_id="ae81f9b9002a453c8863a701a0c12769",
        query=QueryModel(
            trace_id="ae81f9b9002a453c8863a701a0c12769",
            content=query
        ),
        filters=FiltersModel(content={})
    )

    return response.content

print(f"Bind new tool: {mock}")
print("Test run: who is raven?")
answer = mock.invoke("who is raven?")
print(answer)


# LLM

os.environ["OPENAI_API_KEY"] = ...
llm = ChatOpenAI(name="gpt4o")
llm_with_tools = llm.bind_tools([mock])
print("> LLM has been inited and binded with tools")

# Graph

class State(TypedDict):
    # The add_messages function defines how an update should be processed
    # Default is to replace. add_messages says "append"
    messages: Annotated[Sequence[BaseMessage], add_messages]

graph_builder = StateGraph(State)
print("> Graph has been inited")

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
print("> Chatbot (LLM + Tools) has been added")


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}
    
tool_node = BasicToolNode(tools=[mock])
graph_builder.add_node("tools", tool_node)
print("> Tools node has been added")


print("> Add conditional_edge and compile")

from typing import Literal


def route_tools(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


# The `tools_condition` function returns "tools" if the chatbot asks to use a tool, and "END" if
# it is fine directly responding. This conditional routing defines the main agent loop.
graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
    # It defaults to the identity function, but if you
    # want to use a node named something else apart from "tools",
    # You can update the value of the dictionary to something else
    # e.g., "tools": "my_tools"
    {"tools": "tools", END: END},
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break