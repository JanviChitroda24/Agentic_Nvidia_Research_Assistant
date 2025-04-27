# Agentic_Research_Assistant

# NVIDIA Research Assistant

A comprehensive financial analysis tool for NVIDIA Corporation, combining document analysis, data visualization, and news retrieval to provide in-depth insights into NVIDIA's financial performance.

## Overview

The NVIDIA Research Assistant is a multi-agent system designed to answer questions about NVIDIA's financial performance across different time periods. It combines data from SEC filings, stock market data, and news articles to provide comprehensive answers through various analysis methods.

## Features

- **Summary Analysis**: Semantic search across financial documents with year/quarter filtering
- **Data Visualization**: Generates financial charts and metrics based on user queries
- **News Analysis**: Retrieves and analyzes recent news about NVIDIA from trusted sources
- **Complete Reports**: Combines summaries, visualizations, and news into comprehensive reports

## System Architecture

The system consists of:
- **Frontend**: Streamlit-based user interface
- **Backend**: FastAPI server for API endpoints
- **Agents**:
  - Summary Agent (Pinecone/RAG-based)
  - Data Visualization Agent (Snowflake-based)
  - Web Search Agent (SerpAPI-based)
  - Consolidated Report Agent (LangGraph-based)
- **Storage**: AWS S3 for documents and images
- **Databases**: Snowflake and Pinecone

## Prerequisites

- Python 3.8+
- AWS Account with S3 bucket configured
- Snowflake Account
- Pinecone Account
- SerpAPI Key
- Google AI (Gemini) API Key

## Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nvidia-research-assistant.git
cd Agentic_Research_Assistant
```

2. Create a virtual environment:
```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
.env file is attached in the zip file (You can directly copy that)
```
# API Keys
SERPAPI_API_KEY=your_serpapi_key
GOOGLE_API_KEY=your_gemini_key
PINECONE_API_KEY=your_pinecone_key

# AWS Config
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET_NAME=nvidia-agentic-assistant

# Snowflake Config
SNOWFLAKE_ACCOUNT=your_snowflake_account
SNOWFLAKE_USER=your_snowflake_username
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_ROLE=your_snowflake_role
```

## Running the Application

### Starting the Backend

1. Start the FastAPI backend:
```bash
cd Agentic_Research_Assistant
source myenv/bin/activate
uvicorn backend.main:app --reload
```

The backend should start on `http://127.0.0.1:8000`

### Starting the Frontend

2. Open a new terminal window, activate the virtual environment, and start the Streamlit frontend:
```bash
cd Agentic_Research_Assistant
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
streamlit run frontend/app.py
```

The Streamlit app should open automatically in your browser at `http://localhost:8501`

## Usage

1. Select the analysis type in the sidebar:
   - **Summarize**: For text-based summaries of financial data
   - **Data-driven visuals**: For charts and graphs of financial metrics
   - **Real-time insights**: For news analysis
   - **Complete report**: For comprehensive analysis

2. Select the years and quarters you want to analyze

3. Enter your question in the text area (e.g., "What were NVIDIA's revenue trends?" or "Compare gross margins across quarters")

4. Click "Submit" to generate the analysis

## Troubleshooting

### Common Errors

1. **Connection Error to FastAPI Backend**:
   - Ensure the backend is running on the correct port
   - Check if your firewall is blocking connections
   - Verify the FASTAPI_URL in the Streamlit app (`frontend/app.py`) matches the actual URL

2. **API Key Errors**:
   - Verify all API keys in the `.env` file are correct
   - Ensure the `.env` file is in the correct location
   - Check if API keys have sufficient permissions

3. **S3 Access Errors**:
   - Confirm AWS credentials are correct
   - Verify the S3 bucket exists and is accessible
   - Check IAM permissions for the AWS user

4. **Snowflake Connection Issues**:
   - Verify Snowflake credentials are correct
   - Ensure your IP is whitelisted in Snowflake network policies
   - Check if the warehouse, database, and schema exist

5. **Module Import Errors**:
   - Make sure all dependencies are installed
   - Verify Python path is correct
   - Check for any version conflicts



## Acknowledgments

- NVIDIA Investor Relations for financial data
- Yahoo Finance for historical stock data
- Google Gemini for LLM capabilities
- All third-party libraries and services used in this project
- AI assistance from language models (including Claude, Chatgpt, Gemini) which helped with code generation, debugging, and documentation
- Concepts and techniques from the Big Data Intelligence Analytics course assignment that informed the design and implementation of this project

## Contact

For questions or support, please reach out to [chitroda.j@northeawstern.edu](mailto:chitroda.j@northeawstern.edu)