import streamlit as st
import os
import requests
import json

# Constants
FASTAPI_URL = "http://127.0.0.1:8000/"  # FastAPI base URL
LOGO_PATH = "frontend/assets/app-logo.png"  # Ensure this matches your actual filename

def configure_page():
    """Sets up the Streamlit page configuration."""
    st.set_page_config(layout="wide", page_title="Nvidia Assistant")

def get_page_title():
    """Fetch page title from FastAPI."""
    try:
        response = requests.get(FASTAPI_URL)
        if response.status_code == 200:
            return response.json().get("message", "Nvidia Assistant")
        else:
            return "Nvidia Research Assistant (Fallback)"
    except requests.exceptions.RequestException:
        return "Nvidia Research Assistant (Offline)"

def display_sidebar():
    """Displays the sidebar with logo and welcome message."""
    with st.sidebar:

        # Display Logo
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, use_container_width=True)
        else:
            st.warning(f"⚠️ Logo not found! Expected path: {LOGO_PATH}")

        # Welcome Text
        st.markdown("## Welcome to **Nvidia Research Assistant!**")

        # Options for User Selection
        st.markdown("### Please select an option:")
        options = [
            "Summarize",
            "Data-driven visuals",
            "Real-time insights",
            "Complete report"
        ]
        
        action = st.radio("Select an option", options)

        # Time Duration Selection (Year)
        st.markdown("### Select the Time Duration:")
        
        # Multi-select Year selection
        years = st.multiselect("Select Year(s)", [2020, 2021, 2022, 2023, 2024, 2025], default=[2024])
        
        # Dictionary to store quarters for each year
        quarters_dict = {}

        # For each selected year, dynamically show checkboxes for quarters
        for year in years[::-1]:
            st.markdown(f"### Select Quarters for {year}:")
            quarters = []
            if st.checkbox("Q1", key=f"{year}_Q1"):
                quarters.append("1")
            if st.checkbox("Q2", key=f"{year}_Q2"):
                quarters.append("2")
            if st.checkbox("Q3", key=f"{year}_Q3"):
                quarters.append("3")
            if st.checkbox("Q4", key=f"{year}_Q4"):
                quarters.append("4")
            
            # Save selected quarters for the specific year
            quarters_dict[year] = quarters

        # Collect the selections into a tuple
        user_selection = (action, years, quarters_dict)

        return user_selection

import streamlit as st

def display_main_content(user_selection):
    """Displays the main content on the page."""
    page_title = get_page_title()  # Replace with your actual page title logic
    st.title(page_title)

    # Unpack user_selection into separate variables for readability
    action, years, quarters_dict = user_selection

    # Create a container to hold the elements
    with st.container():
        # Create two columns for left-hand side (LHS) and right-hand side (RHS)
        col1, col2 = st.columns(2)

        # Left column (LHS) for Action
        with col1:
            st.markdown(f"##### Reaseach Approach")
            st.success(f"###### {action}")

        # Right column (RHS) for Year and Quarter
        with col2:
            st.write("##### Year and Quarter:")
            for year in years:
                quarters = ', '.join(quarters_dict.get(year, []))
                st.success(f"###### Year: {year} | Quarter: {quarters}")

    # Create a text box (text area) for user input
    prompt = st.text_area("#####", height=150, placeholder="Example: Analyze sales trend for given duaration")  # height sets initial size

    # Button to submit the input
    submit_button = st.button("Submit")

    # When the submit button is pressed
    if submit_button:
        # Check if a year and at least one quarter is selected
        if not years:
            st.write("##### ⚠️ Please select at least one year and one quarter before submitting.")
        elif all(len(quarters_dict.get(year, [])) == 0 for year in years):
            st.write("##### ⚠️ Please select at least one quarter before submitting.")
        elif not prompt:
            st.write("##### ⚠️ Please enter a prompt before submitting.")
        else:
            print("Years ",years)
            print(action)

            # Prepare request payload
            request_data = {
                    "query": prompt,
                    "year_quarter_dict": {str(year): quarters_dict[year] for year in years}
                }
            print(request_data)

            if action == "Summarize":
                # Send request to FastAPI
                try:
                    response = requests.post(f"{FASTAPI_URL}summarize_using_pinecone", json=request_data)
                    if response.status_code == 200:
                        result = response.json().get("response", "No response received.")
                        st.success("✅ Response received:")
                        st.write(result)
                    else:
                        st.error(f"❌ Error: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Failed to connect to API: {e}")

            elif action == "Data-driven visuals":
                try:
                    # Send request to FastAPI's /fetch_images endpoint
                    response = requests.post(f"{FASTAPI_URL}fetch_images", json=request_data)
                    print(response)
                    # Extract the image URLs from the response
                    image_urls = response.json().get("image_urls", [])
                    
                    # If image URLs are received, display them in Streamlit
                    if image_urls:
                        for url in image_urls:
                            st.image(url, caption="Generated Plot", use_container_width=True)
                    else:
                        st.warning("No images found.")
                
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Failed to connect to API: {e}")

            elif action == "Real-time insights":
                # Construct the full URL to call the FastAPI endpoint
                url = f"{FASTAPI_URL}/fetch-news-markdown/"
                
                # Send GET request to the FastAPI endpoint
                try:
                    response = requests.post(url, json=request_data)
                    response.raise_for_status()  # Raise an exception for bad responses

                    # If the request is successful, extract the summary and markdown content
                    data = response.json()
                    summary = data.get("summary", "")
                    markdown_content = data.get("markdown", "")
                    
                    if summary:
                        st.subheader("Summary")
                        st.write(summary)  # Display the summary

                    if markdown_content:
                        # Split the markdown content into two columns
                        column1, column2 = st.columns(2)

                        # Column 1 (Financial News)
                        with column1:
                            st.markdown("### NVIDIA NEWS BASED ON YOUR QUERY")
                            top_financial_news = markdown_content.split("LATEST NVIDIA GENERAL NEWS")[0]
                            #st.markdown(top_financial_news)
                            # Split the content based on the delimiter "--------------------------------------------------------------------------------\n#"
                            news_items = top_financial_news.split("\n--------------------------------------------------------------------------------\n")

                            # Display each split as a separate st.info()
                            for news in news_items:
                                if len(news.strip()) > 50:  # Only display non-empty content
                                    st.info(news.strip())  # Display the content in an info box

                        # Add a line between columns using st.markdown and custom CSS
                        st.markdown("""
                            <style>
                                div[data-testid="stHorizontalBlock"] > div {
                                    border-right: 2px solid #ccc;
                                    border-left: 2px solid #ccc;
                                }
                            </style>
                        """, unsafe_allow_html=True)

                        # Column 2 (General News)
                        with column2:
                            st.markdown("### NVIDIA GENERAL NEWS")
                            latest_general_news = markdown_content.split("LATEST NVIDIA GENERAL NEWS")[1]
                            #st.markdown(latest_general_news)
                            news_items = latest_general_news.split("\n--------------------------------------------------------------------------------\n")

                            # Display each split as a separate st.info()
                            for news in news_items:
                                if len(news.strip()) > 0:  # Only display non-empty content
                                    st.info(news.strip())  # Display the content in an info box

                    else:
                        st.write("No articles found for the given query.")
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"An error occurred while fetching news: {e}")
            elif action == "Complete report":
                url = f"{FASTAPI_URL}/generate_report/"
                
                # Send GET request to the FastAPI endpoint
                try:
                    response = requests.post(url, json=request_data)
                    response.raise_for_status()  # Raise an exception for bad responses

                    # If the request is successful, extract the summary and markdown content
                    data = response.json()
                    pinecone_result = data.get("pinecone_result", "")
                    snowflake_result = data.get("snowflake_result", "")
                    news_result = data.get("news_result", {})

                    # Extract summary and markdown from news_result if it exists
                    news_summary = news_result.get("summary", "")
                    news_markdown = news_result.get("markdown", "")
                    top_financial_news = news_markdown.split("LATEST NVIDIA GENERAL NEWS")[0]
                    st.markdown("## NVIDIA REPORT")
                    st.markdown("### NVIDIA Report Summary")
                    st.write(pinecone_result)
                    st.markdown("### NVIDIA Visual Summary")
                    if snowflake_result:
                        for url in snowflake_result:
                            st.image(url, caption="Generated Plot", use_container_width=True)
                    else:
                        st.warning("No images found.")
                    st.markdown("### NVIDIA News Summary and Top Financial News")
                    if news_summary:
                        st.markdown("### News Summary")
                        st.write(news_summary)  # Display the summary
                    if top_financial_news:
                        st.markdown("### Top 5 Financial News")
                        st.write(top_financial_news)

                except requests.exceptions.RequestException as e:
                    st.error(f"An error occurred while fetching news: {e}")


                
        
    
def main():
    """Main function to run the Streamlit app."""
    configure_page()
    user_selection = display_sidebar()
    display_main_content(user_selection)

if __name__ == "__main__":
    main()
