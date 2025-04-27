from diagrams import Diagram, Cluster
from diagrams.programming.language import Python
from diagrams.onprem.client import Users
from diagrams.gcp.compute import Run
from diagrams.aws.storage import S3
from diagrams.custom import Custom

# Set diagram formatting
graph_attr = {
    "fontsize": "24",
    "bgcolor": "white",
    "splines": "ortho",
}

# Base path for images (Updated to your absolute path)
base_path = r"input_icons"

# Create the diagram
with Diagram("nvidia-research-assistant", show=False, graph_attr=graph_attr, direction="TB"):
   
    # User/Client
    user = Users("End User")

     # Select a PDF
    with Cluster("PDF Cloud Storage"):
        image_pdf_upload = Custom("Store NVidia PDFs and Dynamic Visuals", f"{base_path}/s3_image.png")
   
    # Frontend Cluster
    with Cluster("Frontend (User Interface)"):
        streamlit = Custom("Streamlit UI", f"{base_path}/streamlit.png")
   
    # Cloud Infrastructure Cluster
    with Cluster("GCP VM Instance"):
        # GCP Cloud Run hosting the FastAPI backend
        cloud_run = Custom("GCP VM Instance", f"{base_path}/gcp.png")

        with Cluster("Backend"):
            fastapi = Custom("FastAPI", f"{base_path}/FastAPI.png")

        with Cluster("Processing Agents"):
            pinecone = Custom("Summary Agent", f"{base_path}/pinecone.png")
            snowflake = Custom("Visual Agent", f"{base_path}/snowflake.png")
            websearch = Custom("Web Search Agent", f"{base_path}/serpapi.png")

            with Cluster("langraph"):
                with Cluster("Consolidated Report Agent"):
                    langgraph = Custom("Langraph Agent", f"{base_path}/langgraph.png")
                

            with Cluster("LLM Integration"):
                llm = Custom("LLM Integration", f"{base_path}/llm.png")
                gemini = Custom("Gemini \n (Google)", f"{base_path}/gemini.png")

    user >> streamlit
    streamlit >> user
    streamlit >> image_pdf_upload 
    streamlit >> cloud_run >> fastapi >> pinecone
    streamlit >> cloud_run >> fastapi >> snowflake
    streamlit >> cloud_run >> fastapi >> websearch
    streamlit >> cloud_run >> fastapi >> langgraph

    pinecone >> fastapi
    snowflake >> fastapi
    websearch >> fastapi
    langgraph >> fastapi

    pinecone >> langgraph
    snowflake >> langgraph
    websearch >> langgraph

    pinecone >> llm
    snowflake >> llm
    websearch >> llm
    langgraph >> llm

    llm >> gemini

    image_pdf_upload >> streamlit
    cloud_run >> streamlit

    fastapi >> cloud_run

