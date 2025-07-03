import requests
from bs4 import BeautifulSoup, Tag
from typing import Dict
import anthropic
import google.generativeai as genai
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
        
        # Initialize AI clients
        self.claude_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.gemini_client = None
        
        # Try to initialize Gemini if API key is available
        gemini_api_key = os.getenv('GOOGLE_API_KEY')
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                self.gemini_client = genai.GenerativeModel('gemini-1.5-pro')
            except Exception as e:
                print(f"Warning: Could not initialize Gemini client: {e}")
                self.gemini_client = None
        
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
            
            # Use AI to analyze and extract API specifications
            api_specifications = self._extract_api_specifications_with_ai(url, raw_content)
            
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
        
        # Try to find and extract endpoint listings
        endpoint_content = self._extract_endpoint_listings(soup)
        if endpoint_content:
            text = text + "\n\nENDPOINT LISTINGS:\n" + endpoint_content
        
        # Increase limit to 50000 characters for comprehensive extraction
        # Gemini can handle much larger context windows (1M+ tokens)
        return text[:50000]
    
    def _extract_endpoint_listings(self, soup: BeautifulSoup) -> str:
        """Extract endpoint listings from navigation menus and tables."""
        endpoint_text = []
        
        # Look for common patterns in API documentation
        # 1. Navigation menus with endpoint links
        nav_links = soup.find_all('a', href=True)
        for link in nav_links:
            href = link.get('href', '')
            text = link.get_text().strip()
            if any(keyword in href.lower() for keyword in ['/api/', '/rest/', '/v1/', '/v2/', '/v3/']):
                if text and len(text) > 2:
                    endpoint_text.append(f"Endpoint: {text} -> {href}")
        
        # 2. Tables with endpoint information
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    row_text = ' | '.join(cell.get_text().strip() for cell in cells)
                    if any(keyword in row_text.lower() for keyword in ['get', 'post', 'put', 'delete', '/api/', '/rest/']):
                        endpoint_text.append(f"Table Row: {row_text}")
        
        # 3. Code blocks with endpoint examples
        code_blocks = soup.find_all(['code', 'pre'])
        for block in code_blocks:
            code_text = block.get_text().strip()
            if any(keyword in code_text.lower() for keyword in ['/api/', '/rest/', 'curl', 'http']):
                endpoint_text.append(f"Code Example: {code_text[:200]}...")
        
        return '\n'.join(endpoint_text[:50])  # Limit to avoid overwhelming

    def _extract_api_specifications_with_ai(self, url: str, content: str) -> Dict:
        """Use the best available AI model to extract API specifications for data integration."""
        
        # Choose the best model based on content length and availability
        if len(content) > 10000 and self.gemini_client:
            # Use Gemini for large content (better context window)
            return self._extract_with_gemini(url, content)
        else:
            # Use Claude for smaller content or when Gemini unavailable
            return self._extract_with_claude(url, content)
    
    def _extract_with_gemini(self, url: str, content: str) -> Dict:
        """Use Gemini Pro to extract API specifications for data integration."""
        
        system_prompt = """You are an expert API analyst specializing in data integration. Your job is to analyze API documentation and extract specifications that will be used by other AI agents to:

1. Map API data to database ontologies
2. Create programmatic SDK calls for data ingestion
3. Understand the structure and capabilities of the API

Focus on extracting information that will help with automated data integration workflows."""

        user_prompt = f"""Analyze this API documentation and extract specifications for data integration:

URL: {url}

Documentation Content:
{content}

IMPORTANT: Respond ONLY with valid JSON. Do not include any text before or after the JSON object.

Extract ALL available endpoints and entity types. Be comprehensive and thorough. Look for:
- All API endpoints mentioned
- All data models/entities described
- All authentication methods
- Rate limits and pagination details
- Integration considerations

Respond with this exact JSON structure:

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

If any information is not available, use "Not specified" for that field. Be as comprehensive as possible in extracting ALL endpoints and entity types mentioned in the documentation."""

        try:
            response = self.gemini_client.generate_content([system_prompt, user_prompt])
            gemini_response = response.text.strip()
            
            # Try to parse as JSON, with improved error handling
            try:
                import json
                # Try direct parsing first
                return json.loads(gemini_response)
            except json.JSONDecodeError:
                # Try to extract JSON from the response if it's wrapped in text
                try:
                    # Look for JSON object in the response
                    start_idx = gemini_response.find('{')
                    end_idx = gemini_response.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = gemini_response[start_idx:end_idx]
                        return json.loads(json_str)
                    else:
                        return {
                            "raw_analysis": gemini_response,
                            "note": "Could not extract JSON from Gemini response"
                        }
                except json.JSONDecodeError:
                    return {
                        "raw_analysis": gemini_response,
                        "note": "Failed to parse Gemini JSON response"
                    }
                    
        except Exception as e:
            return {
                "error": f"Gemini analysis failed: {str(e)}",
                "fallback_content": content[:500] + "..." if len(content) > 500 else content
            }
    
    def _extract_with_claude(self, url: str, content: str) -> Dict:
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

IMPORTANT: Respond ONLY with valid JSON. Do not include any text before or after the JSON object.

Extract ALL available endpoints and entity types. Be comprehensive and thorough. Look for:
- All API endpoints mentioned
- All data models/entities described
- All authentication methods
- Rate limits and pagination details
- Integration considerations

Respond with this exact JSON structure:

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

If any information is not available, use "Not specified" for that field. Be as comprehensive as possible in extracting ALL endpoints and entity types mentioned in the documentation."""

        try:
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extract the response content
            claude_response = message.content[0].text.strip()
            
            # Try to parse as JSON, with improved error handling
            try:
                import json
                # Try direct parsing first
                return json.loads(claude_response)
            except json.JSONDecodeError:
                # Try to extract JSON from the response if it's wrapped in text
                try:
                    # Look for JSON object in the response
                    start_idx = claude_response.find('{')
                    end_idx = claude_response.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = claude_response[start_idx:end_idx]
                        return json.loads(json_str)
                    else:
                        return {
                            "raw_analysis": claude_response,
                            "note": "Could not extract JSON from response"
                        }
                except json.JSONDecodeError:
                    return {
                        "raw_analysis": claude_response,
                        "note": "Failed to parse JSON response"
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