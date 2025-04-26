import snowflake.connector
from dotenv import load_dotenv
import os
import re
import io
import pandas as pd
import matplotlib.pyplot as plt
from backend.llm_response import generate_gemini_response
from datetime import datetime
from backend.s3_utils import upload_image_to_s3, fetch_images_from_s3_folder

# Load environment variables
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", ".env"))
load_dotenv(dotenv_path)

def fetch_snowflake_df(query):
    # Snowflake connection details
    SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")  # e.g. 'vwcoqxf-qtb83828'
    SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")  # Your Snowflake username
    SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")  # Your Snowflake password
    SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE")  # Your role, e.g., 'SYSADMIN'

    # Connecting to Snowflake
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,        # This should be your username
        password=SNOWFLAKE_PASSWORD,       # This should be your password
        account=SNOWFLAKE_ACCOUNT,     # This should be your Snowflake account URL
        role=SNOWFLAKE_ROLE          # Optional, if you need to specify the role
    )

    cur = conn.cursor()
    cur.execute("USE DATABASE NVIDIA_DB;")  # Specify the database
    cur.execute("USE SCHEMA NVIDIA_DB.NVIDIA_SCHEMA;")  # Specify the schema

    #print(agg_query)
    columns = re.search(r"SELECT\s+(.*?)\s+FROM", query, re.IGNORECASE)

    # Split the extracted column names by commas and strip whitespace
    if columns:
        column_names = [col.strip() for col in columns.group(1).split(",")]
        print(column_names)
    else:
        print("No columns found.")

    cur.execute(query)
    results = cur.fetchall()  # Fetch all rows
    #print(results)
    print(type(results))
    df = pd.DataFrame(results, columns=column_names)
    print(df)
    return df


def plot_graph(df, column_name, folder_name):
    print(f"Plotting graphs for column: {column_name}")
    if column_name not in df.columns:
        print(f"Column '{column_name}' not found in the DataFrame.")
        return
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(df['DATE'], df[column_name], label=column_name, color='blue')

    # Set title and labels
    plt.title(f'Plot of {column_name} over Time')
    plt.xlabel('Date')
    plt.ylabel(column_name)
    plt.legend(title=column_name)

    # Rotate x-axis labels for readability
    plt.xticks(rotation=45)

    # Save the plot as a PNG file
    plt.tight_layout()  # Adjust layout to avoid clipping
    #plt.savefig(f'{column_name}_plot.png', format='png')

    # Save the plot to a BytesIO object
    image_buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(image_buffer, format='png')  # Save as PNG
    image_buffer.seek(0)  # Reset buffer position

    # Generate image
    image_name = f"{column_name}_plot.png"

    # Upload the image to S3
    uploaded_url = upload_image_to_s3(
        image_content=image_buffer.getvalue(),  # Get binary content
        filename=image_name,
        folder=f"plots/{folder_name}",  # Optional folder name
        content_type="image/png"
    )

    print(f"Uploaded Image URL: {uploaded_url}")

def snowflake_agent_call(year_quarter_dict, query):
    llm_query_response = generate_gemini_response("snowflake-agent",query,year_quarter_dict)
    print(llm_query_response)

    match = re.findall(r"(SELECT[\s\S]*?);", llm_query_response)

    # Store the queries in variables
    raw_query = match[0] if len(match) >= 1 else None

    print("\nRaw Data Query:")
    print(raw_query)

    #fetch_snowflake_df(agg_query)
    df = fetch_snowflake_df(raw_query)

    # Dynamically get columns other than 'DATE'
    columns_to_plot = [col for col in df.columns if col.upper() not in ['DATE', "YEAR", "QUARTER"]]
    print(columns_to_plot)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{timestamp}_visuals"

    for col in columns_to_plot:
        plot_graph(df, col, folder_name)

    image_urls = fetch_images_from_s3_folder(f"plots/{folder_name}")
    print(image_urls)
    return image_urls


# year_quarter_dict = {
#     "2024": ["1", "2"],
#     "2023": ["2"]
# }

# query = "What is the 10-day moving average and 30-day moving average?"
# queries = """
# What is the opening price and closing price?
# What is the 10-day moving average and 30-day moving average?
# What is the daily change and daily change percentage?
# What is the highest and lowest stock price recorded?

# """

# snowflake_agent_call(year_quarter_dict, query)