import requests
from bs4 import BeautifulSoup, Tag
from typing import Dict
import anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class IntelligentAPIParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Initialize Anthropic client
        self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        if not os.getenv('ANTHROPIC_API_KEY'):
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

    def parse_api_documentation(self, url: str) -> Dict:
        """
        Intelligently parse API documentation using Claude to extract specifications for data integration.
        This agent reads API documentation and summarizes the specifications for future use by other agents.
        """
        try:
            # Fetch the page
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract raw content for AI analysis
            raw_content = self._extract_content_for_analysis(soup)
            
            # Use Claude to analyze and extract API specifications
            api_specifications = self._extract_api_specifications_with_claude(url, raw_content)
            
            result = {
                'url': url,
                'title': self._extract_title(soup),
                'api_specifications': api_specifications,
                'status': 'success'
            }
            
            return result
            
        except Exception as e:
            return {
                'url': url,
                'status': 'error',
                'error': str(e)
            }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the page title."""
        title_tag = soup.find('title')
        if title_tag and isinstance(title_tag, Tag):
            return title_tag.get_text().strip()
        return "Unknown API"

    def _extract_content_for_analysis(self, soup: BeautifulSoup) -> str:
        """Extract relevant content for AI analysis."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit to first 6000 characters to stay within Claude's context window
        return text[:6000]

    def _extract_api_specifications_with_claude(self, url: str, content: str) -> Dict:
        """Use Claude Sonnet 4 to extract API specifications for data integration."""
        
        system_prompt = """You are an expert API analyst specializing in data integration. Your job is to analyze API documentation and extract specifications that will be used by other AI agents to:

1. Map API data to database ontologies
2. Create programmatic SDK calls for data ingestion
3. Understand the structure and capabilities of the API

Focus on extracting information that will help with automated data integration workflows."""

        user_prompt = f"""Analyze this API documentation and extract specifications for data integration:

URL: {url}

Documentation Content:
{content}

Please provide a structured analysis in JSON format with these fields:

{{
    "api_overview": "Brief description of what this API does and its main purpose",
    "authentication_method": "How authentication works (API keys, OAuth, etc.)",
    "base_url": "The base URL for API calls",
    "endpoints": [
        {{
            "method": "GET/POST/PUT/DELETE",
            "path": "/api/endpoint",
            "description": "What this endpoint does",
            "data_type": "What type of data this returns (users, orders, etc.)"
        }}
    ],
    "data_models": [
        {{
            "name": "Model name",
            "fields": ["field1", "field2", "field3"],
            "description": "What this model represents"
        }}
    ],
    "rate_limits": "Rate limiting information if available",
    "pagination": "How pagination works (if mentioned)",
    "integration_notes": "Important details for data integration"
}}

If any information is not available, use "Not specified" for that field. Focus on extracting information that will be useful for automated data ingestion."""

        try:
            message = self.client.messages.create(
                model="claude-4-sonnet-20250219",
                max_tokens=2000,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extract the response content
            claude_response = message.content[0].text.strip()
            
            # Try to parse as JSON, fallback to text if it fails
            try:
                import json
                return json.loads(claude_response)
            except json.JSONDecodeError:
                return {
                    "raw_analysis": claude_response,
                    "note": "Claude provided unstructured response - manual review needed"
                }
                
        except Exception as e:
            return {
                "error": f"Claude analysis failed: {str(e)}",
                "fallback_content": content[:500] + "..." if len(content) > 500 else content
            }

# Create a global instance
api_parser = None

def get_api_parser():
    """Get or create the API parser instance."""
    global api_parser
    if api_parser is None:
        api_parser = IntelligentAPIParser()
    return api_parser 