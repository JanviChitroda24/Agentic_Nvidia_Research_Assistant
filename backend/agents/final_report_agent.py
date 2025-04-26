from backend.agents.websearch_agent import news_agent
from backend.agents.pinecone_agent import search_pinecone_db
from backend.agents.snowflake_agent import snowflake_agent_call
from backend.pinecone_db import AgenticResearchAssistant
from langgraph.graph import StateGraph
from typing import Dict, List, Any, TypedDict

# Define a typed state for the graph
class AgentState(TypedDict):
    query: str
    year_quarter_dict: Dict[str, List[str]]
    pinecone_result: str | None
    snowflake_result: str | None
    news_result: str | None

# Define agent functions with proper signatures
def pinecone_node(state: AgentState) -> AgentState:
    """Node for Pinecone search functionality"""
    assistant = AgenticResearchAssistant()
    query = state["query"]
    year_quarter_dict = state["year_quarter_dict"]
    result = search_pinecone_db(assistant, query, year_quarter_dict)
    state["pinecone_result"] = result
    return state

def snowflake_node(state: AgentState) -> AgentState:
    """Node for Snowflake query functionality"""
    query = state["query"]
    year_quarter_dict = state["year_quarter_dict"]
    result = snowflake_agent_call(year_quarter_dict, query)
    state["snowflake_result"] = result
    return state

def news_node(state: AgentState) -> AgentState:
    """Node for News search functionality"""
    query = state["query"]
    result = news_agent(query)
    state["news_result"] = result
    return state

def combine_agents(query: str, year_quarter_dict: Dict[str, List[str]]) -> str:
    """
    Orchestrates multiple agent calls using LangGraph and combines their results.
    
    Args:
        query: The search query string
        year_quarter_dict: Dictionary of years and quarters to analyze
        
    Returns:
        Combined report from all agents
    """
    # Create a LangGraph StateGraph object
    workflow = StateGraph(AgentState)
    
    # Add nodes to the graph
    workflow.add_node("pinecone", pinecone_node)
    workflow.add_node("snowflake", snowflake_node)
    workflow.add_node("news", news_node)
    
    # Define the workflow graph edges
    workflow.set_entry_point("pinecone")
    workflow.add_edge("pinecone", "snowflake")
    workflow.add_edge("snowflake", "news")
    
    # Compile the graph
    app = workflow.compile()
    
    # Initialize the state
    initial_state = {
        "query": query,
        "year_quarter_dict": year_quarter_dict,
        "pinecone_result": None,
        "snowflake_result": None,
        "news_result": None
    }
    
    # Execute the workflow
    final_state = app.invoke(initial_state)
    
    # Combine the results into a final repor

    final_report = {"pinecone_result": final_state['pinecone_result'],
                    "snowflake_result": final_state['snowflake_result'],
                    "news_result": final_state['news_result']}
    
    return final_report

# Example of how to invoke the function
if __name__ == "__main__":
    query = "Nvidia financial results"
    year_quarter_dict = {
        "2023": ["1"],  # This means Q1 of 2023
        "2022": ["4"]   # You can include more if needed
    }
    report = combine_agents(query, year_quarter_dict)
    print(report)