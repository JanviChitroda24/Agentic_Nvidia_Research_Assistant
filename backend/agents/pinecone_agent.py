from backend.pinecone_db import AgenticResearchAssistant  # adjust import as needed
import logging

def search_pinecone_db(self, query, year_quarter_dict):
    query_embedding = self.model.encode([query]).tolist()[0]  # single vector
    try:
        # Flatten all (year, quarter) combinations
        all_quarters = [(str(year), str(q)) for year, quarters in year_quarter_dict.items() for q in quarters]
        n_quarters = len(all_quarters)

        if n_quarters == 0:
            logging.warning("No quarters provided for search.")
            return "Please specify at least one quarter."

        # Dynamically decide how many top results per quarter
        if n_quarters == 1:
            top_k_per_quarter = 20
        elif n_quarters == 2:
            top_k_per_quarter = 10
        elif n_quarters == 3:
            top_k_per_quarter = 7
        else:  # 4 or 5
            top_k_per_quarter = 5

        combined_matches = []

        for year, quarter in all_quarters:
            filter_criteria = {
                "year": {"$eq": year},
                "quarter": {"$eq": quarter}
            }
            results = self.index.query(
                vector=[query_embedding],
                top_k=top_k_per_quarter,
                include_metadata=True,
                filter=filter_criteria
            )
            combined_matches.extend(results.get("matches", []))
            #print(combined_matches)

        if not combined_matches:
            logging.warning("No relevant matches found for the given quarters.")
            return "No relevant information found for the specified year and quarters."

        # Extract matched texts along with metadata
        retrieved_data = [
            (match["metadata"]["text"], match["metadata"]["year"], match["metadata"]["quarter"])
            for match in combined_matches
        ]

        # Create context
        context = "\n".join([f"Year: {year}, Quarter: {quarter} - {text}" for text, year, quarter in retrieved_data])
        print(context)
        prompt = f"""You are an AI assistant tasked with analyzing Nvidia's financial data. 
            Below is relevant financial information retrieved from a vector database, with each entry associated with a specific year and quarter. 
            Use this context to answer the question accurately.
            Question: {query}
            Context: {context}
        """

        # # Generate Gemini response
        # response = self.gemini_model.generate_content(prompt)
        # return response.text

    except Exception as e:
        logging.error(f"Error during search: {e}")
        return "Error occurred during search."



# Step 1: Instantiate the class
assistant = AgenticResearchAssistant()

# Step 2: Define your query
query = "What were Nvidia's major financial highlights"

# Step 3: Define year_quarter_dict
# This is a dictionary where the key is the year and the value is a list of quarters you want to filter on.
year_quarter_dict = {
    "2023": ["1"],  # This means Q1 of 2023
    "2022": ["4"]   # You can include more if needed
}

# Step 4: Call the search function
response = search_pinecone_db(assistant, query, year_quarter_dict)

# Step 5: Print the AI's response
print("Gemini's Response:")
print(response)
