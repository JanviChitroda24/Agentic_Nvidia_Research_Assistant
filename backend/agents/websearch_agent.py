import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

class NewsRetriever:
    def __init__(self):
        """Initialize the NewsRetriever with the API key."""
        self.api_key = self._get_api_key()
        self.allowed_domains = [
            "nvidia.com", "investor.nvidia.com", "techcrunch.com", "theverge.com",
            "wired.com", "engadget.com", "arstechnica.com", "venturebeat.com",
            "cnet.com", "gizmodo.com", "finance.yahoo.com", "marketwatch.com",
            "wsj.com", "bloomberg.com", "reuters.com", "forbes.com",
            "businessinsider.com", "bbc.com", "cnn.com", "nytimes.com",
            "guardian.com", "tomshardware.com", "anandtech.com", "extremetech.com",
            "pcgamer.com"
        ]
        self.SERPAPI_URL = "https://serpapi.com/search"
    
    def _get_api_key(self) -> str:
        """Load the SerpApi API key from environment variables."""
        # Load environment variables from .env file
        dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", ".env"))
        load_dotenv(dotenv_path)
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            raise ValueError("API key not found. Please set the SERPAPI_API_KEY environment variable.")
        return api_key
    
    def _filter_by_domains(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter articles to include only those from allowed domains."""
        filtered_articles = []
        for article in articles:
            article_url = article.get("link", "")
            if any(domain in article_url for domain in self.allowed_domains):
                filtered_articles.append(article)
        return filtered_articles
    
    def _filter_by_date(self, articles: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
        """Filter articles to include only those within the specified time period."""
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_articles = []
        
        for article in articles:
            article_date_str = article.get("date")
            if not article_date_str:
                continue
                
            try:
                # Try multiple date formats
                for date_format in ["%b %d, %Y", "%B %d, %Y", "%Y-%m-%d"]:
                    try:
                        article_date = datetime.strptime(article_date_str, date_format)
                        break
                    except ValueError:
                        continue
                else:
                    # If none of the formats worked, skip this article
                    print("Skipping article due to invalid date format: %s", article_date_str)
                    continue
                    
                if article_date >= cutoff_date:
                    filtered_articles.append(article)
            except Exception as e:
                print("Error parsing article date: %s, Error: %s", article_date_str, e)
                continue
        
        return filtered_articles
    
    def _sort_articles_by_date(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort articles by date in descending order."""
        def get_article_date(article):
            date_str = article.get('date')
            if not date_str:
                return datetime.min
                
            for date_format in ["%b %d, %Y", "%B %d, %Y", "%Y-%m-%d"]:
                try:
                    return datetime.strptime(date_str, date_format)
                except ValueError:
                    continue
            return datetime.min
            
        return sorted(articles, key=get_article_date, reverse=True)
    
    def display_articles(self, articles: List[Dict[str, Any]]) -> None:
        """Display the articles in a formatted way."""
        if not articles:
            print("No relevant news articles found.")
            return
            
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'N/A')
            source = article.get('source', 'N/A')
            link = article.get('link', 'N/A')
            date = article.get('date', 'N/A')
            snippet = article.get('snippet', 'No content available')
            
            # Only print the article if it has a source, link, and some content
            if source != 'N/A' and link != 'N/A' and snippet != 'No content available':
                print(f"Article {i}:")
                print(f"Title: {title}")
                print(f"Source: {source}")
                print(f"Link: {link}")
                print(f"Published: {date}")
                print(f"Content: {snippet}")
                print("-" * 80)
    
    def fetch_news(
        self, 
        query: str,
        records: int
    ) -> List[Dict[str, Any]]:
        """
        Fetch news articles based on the query and filtering options.
        
        Args:
            query: The search query string
            filter_by_domains: Whether to filter results by allowed domains
            num_results: Maximum number of results to return
            time_period_days: Number of days to look back for articles
            
        Returns:
            List of filtered news articles
        """
        # Define parameters for the search query
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "tbm": "nws",
            "num": records # Request more to account for filtering
        }
        
        try:
            # Make the request to SerpApi
            response = requests.get(self.SERPAPI_URL, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors
            data = response.json()
            
            # Check if the response contains news articles
            if "news_results" not in data:
                print("No news results found for query: %s", query)
                return []
                
            articles = data["news_results"]
            
            # Apply domain filtering if requested
            articles = self._filter_by_domains(articles)
                
            # Apply date filtering
            if query != "NVIDIA":
                articles = self._filter_by_date(articles, days=90)
                
                # Sort articles by date (newest first)
                articles = self._sort_articles_by_date(articles)

                return articles[:5]
                
            # Return the requested number of articles
            return articles[:10]
            
        except requests.exceptions.RequestException as e:
            print("Error fetching news: %s", e)
            return []
        except ValueError as e:
            print("Error parsing response: %s", e)
            return []

def news_agent(financial_query):
    """Main function to run the news retrieval."""
    news_retriever = NewsRetriever()
    
    # Get top 5 financial news for NVIDIA
    print("=== TOP 5 NVIDIA FINANCIAL NEWS BASED ON QUERY ===")
    financial_articles = news_retriever.fetch_news(financial_query, 30)
    news_retriever.display_articles(financial_articles)
    
    # Get latest NVIDIA news from trusted sources
    print("\n=== LATEST NVIDIA GENERAL NEWS ===")
    general_query = "NVIDIA"
    general_articles = news_retriever.fetch_news(general_query, 25)
    news_retriever.display_articles(general_articles)


if __name__ == "__main__":
    financial_query = "Nvidia financial highlights quarterly results"
    news_agent(financial_query)