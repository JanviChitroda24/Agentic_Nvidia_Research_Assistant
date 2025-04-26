from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
import time
from typing import Dict, List
from backend.pinecone_db import AgenticResearchAssistant
from backend.agents.pinecone_agent import search_pinecone_db
from backend.agents.snowflake_agent import snowflake_agent_call
from backend.agents.websearch_agent import news_agent
from backend.agents.final_report_agent import combine_agents
from fastapi.responses import JSONResponse

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str
    vector_db: str
    quarter_filter: Optional[List[str]] = None
    top_k: int = 5
    document_id: Optional[str] = None  # For user-uploaded PDFs

class AvailableQuartersResponse(BaseModel):
    quarters: List[str]

# Add new endpoint model
class WebSearchRequest(BaseModel):
    query: str
    num_results: Optional[int] = 5

# Define the input model
class SearchRequest(BaseModel):
    query: str
    year_quarter_dict: Dict[str, List[str]]  # Accept string keys & string lists

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Nvidia Agentic Research Assistant"}

@app.get("/health")
async def health_check():
    """Check the health of connected services"""
    status = {
        "api": "healthy",
        "pinecone": "unknown",
    }

@app.get("/available_quarters", response_model=AvailableQuartersResponse)
async def get_available_quarters():
    """Get all available quarters from the vector databases"""
    quarters = {"2021-Q1", "2021-Q2", "2021-Q3", "2021-Q4",
                    "2022-Q1", "2022-Q2", "2022-Q3", "2022-Q4",
                    "2023-Q1", "2023-Q2", "2023-Q3", "2023-Q4",
                    "2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4",
                    "2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4"}
    
    return {"quarters": sorted(list(quarters))}
    
@app.post("/summarize_using_pinecone")
def search(request: SearchRequest):
    assistant = AgenticResearchAssistant()
    response = search_pinecone_db(assistant, request.query, request.year_quarter_dict)
    return {"response": response}    


@app.post("/fetch_images")
async def fetch_images(request: SearchRequest):
    try:
        # Call your snowflake_agent_call function to fetch image URLs
        image_urls = snowflake_agent_call(request.year_quarter_dict, request.query)
    
        # Return the list of image URLs as a JSON response
        return JSONResponse(content={"image_urls": image_urls})
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/fetch-news-markdown/")
async def fetch_news_markdown(request: SearchRequest):
    """
    Fetch news articles based on the given query and return results in markdown format.
    
    Args:
    - query (str): Search query to retrieve news.
    - num_results (int): Number of news articles to return (default 5).
    
    Returns:
    - dict: A dictionary containing the articles in markdown format.
    """
    # Call the news_agent function with the query
    output_dict = news_agent(request.query)

    
    # Return the markdown content in the response
    return {"markdown": output_dict["markdown"], "summary": output_dict["summary"]}

@app.post("/generate_report")
async def generate_report(request: SearchRequest):
    # Call the combine_agents function with the request data
    final_report = combine_agents(request.query, request.year_quarter_dict)
    
    # Return the final report as a response
    return final_report