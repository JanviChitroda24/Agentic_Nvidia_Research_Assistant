import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables

def generate_gemini_response(agent,user_query, context):
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    load_dotenv(dotenv_path)

    GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
    if GOOGLE_API_KEY:
        print("Connection successful with Gemini API")

    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-pro-latest")

    if agent == "snowflake-agent":
        prompt = f"""

            I have a table in Snowflake that contains financial data for NVidia. This table records information for each day with different columns that represent various financial metrics.
            
            **Input Table: NVIDIA_FIN_DATA**  
            Below is a brief description of each column:
            - `DATE TIMESTAMP_NTZ`: The timestamp of the financial record, indicating the specific day.
            - `OPEN FLOAT`: The opening price of the stock on that day.
            - `DAILYCHANGE FLOAT`: The absolute change in the stock price compared to the previous day.
            - `MA10 FLOAT`: The 10-day moving average of the stock's price.
            - `HIGH FLOAT`: The highest stock price recorded on that day.
            - `CLOSE FLOAT`: The closing price of the stock on that day.
            - `RSI FLOAT`: The Relative Strength Index, a technical indicator that measures the speed and change of price movements (used for determining overbought/oversold conditions).
            - `VOLUME NUMBER`: The number of shares traded on that day.
            - `DAILYCHANGEPERCENT FLOAT`: The percentage change in the stock's price compared to the previous day.
            - `TICKER TEXT`: The stock symbol or identifier for the stock being traded.
            - `DOLLARVOLUME FLOAT`: The total dollar volume of stocks traded (calculated as the stock price multiplied by the trading volume).
            - `LOW FLOAT`: The lowest stock price recorded on that day.
            - `MA30 FLOAT`: The 30-day moving average of the stock's price.
            - `VOLATILITY20D FLOAT`: The 20-day volatility of the stock's price, indicating how much the price fluctuates over the past 20 days.
            - `Year INT`: The year of the financial record.
            - `Quarter INT`: The quarter of the financial record.

            **Important Notes for Gemini:**
            - Identify the relevant columns from the provided metadata based on the user's query.
            - Generate the appropriate SQL query that will fetch the relevant data to answer the user’s query.
            - Make sure to consider: The specific financial metric(s) being asked (e.g., revenue, net income)
            - I have already added `Year` and `Quarter` as separate columns in the table.  
            - The filtering should be done **directly** using these columns, **without** needing to extract them from the `DATE` column.  
            - The user will provide a dictionary containing `Year` and `Quarter`, which should be used for filtering.  
            - Your main task is to generate the required SQL queries based on the user’s request and correctly identify the relevant column(s).

            **User Query:**  
            {user_query}

            **Time Duration:**  
            The user will specify the time frame using a dictionary containing `Year` and `Quarter`.  
            Example: `{context}`

            **Task for Gemini:**  
            Based on the user's query, generate **two separate SQL queries**:

            ### **1. Raw Data Query (Without Aggregation)**
            - This query should retrieve individual record/records (financial metrics that is relevant to the user query, e.g., `(DOLLARVOLUME)`) along with date, year, quater without aggregation.
            - It should filter based on `Year` and `Quarter`.

            **Format of Response:**
            ```sql
            QUERY;
            ```

            ### **Important Notes for Gemini:**  
            - **A valid SQL query must always be returned.**  
            - **The response must follow the format strictly**  
            - Follow with the SQL query inside a code block. Also end the query with a semi-colon(;):  
            - **Filtering should be done using `Year` and `Quarter` columns directly** (do not extract from `DATE`).  
            - The user will provide a dictionary with `Year` and `Quarter`, which should be used for filtering.  

            **Strictly format the response as follows:**  
            ```sql  
            QUERY;  
            ```  
            
            - Ensure proper formatting and structuring of the queries.
            - Do **not** include explanations before the query.
            - The explanation should follow after the SQL code, not between the queries.

        """

    elif agent == "pinecone-agent":
        prompt = f"""
            You are an AI assistant tasked with analyzing Nvidia's financial data. 
            Below is relevant financial information retrieved from a vector database, with each entry associated with a specific year and quarter. 
            Use this context to answer the question accurately, ensuring that you provide separate answers for each quarter based on the available data.

            Question: {user_query}

            Context:
            {context}

            Instructions:
            - For each year and quarter, analyze the data and provide a **detailed response**.
            - Each answer should be well-structured with a **heading** and **content**:
            - Start with a **heading** that includes the **year and quarter** (e.g., "Year: 2023, Quarter: 1").
            - Provide a **detailed, descriptive analysis** of the financial data for that specific quarter.
            - Focus on key financial highlights, trends, and performance metrics (e.g., revenue growth, profit margins, segment performance, etc.).
            - Each response should be **approximately 500 words**, covering the most important details of the quarter.
            - Ensure that your answer is comprehensive, providing insights into both positive and negative trends as well as any significant changes.
            - Provide **clear and structured insights** for each quarter individually, and avoid combining data from multiple quarters.


            Answer Format:
            - Year: year_number, Quarter: year_number
            Answer: [response for this quarter]

            Continue with the next quarters as necessary, providing separate answers for each.

        """
        
    response = gemini_model.generate_content(prompt)
    return response.text.strip()