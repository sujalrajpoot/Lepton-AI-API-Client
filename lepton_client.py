from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
import requests
import json
import re
from datetime import datetime

class LeptonAIError(Exception):
    """Base exception class for LeptonAI client errors."""
    pass

class APIConnectionError(LeptonAIError):
    """Raised when API connection fails."""
    pass

class ResponseParsingError(LeptonAIError):
    """Raised when response parsing fails."""
    pass

class ValidationError(LeptonAIError):
    """Raised when input validation fails."""
    pass

class ResponseType(Enum):
    """Enum for different types of response chunks."""
    LLM_RESPONSE = auto()
    CONTEXT = auto()
    RELATED_QUESTIONS = auto()
    UNKNOWN = auto()

@dataclass(frozen=True)
class Context:
    """
    Immutable dataclass representing context information from Lepton AI response.
    
    Attributes:
        name (str): Name of the context
        id (str): Unique identifier
        url (str): Source URL
        thumbnail_url (Optional[str]): URL of the thumbnail image
        date_published (Optional[datetime]): Publication date
        is_family_friendly (bool): Content appropriateness flag
        display_url (str): Formatted display URL
        snippet (str): Text snippet from the source
    """
    name: str
    id: str
    url: str
    thumbnail_url: Optional[str]
    date_published: Optional[datetime]
    is_family_friendly: bool
    display_url: str
    snippet: str

    def __post_init__(self):
        """Validate context attributes after initialization."""
        assert isinstance(self.name, str), "Name must be a string"
        assert isinstance(self.id, str), "ID must be a string"
        assert isinstance(self.url, str), "URL must be a string"
        assert isinstance(self.is_family_friendly, bool), "is_family_friendly must be a boolean"

class APIClient(ABC):
    """Abstract base class for API clients."""
    
    @abstractmethod
    def make_request(self, endpoint: str, data: Dict[str, Any]) -> requests.Response:
        """
        Make an API request.
        
        Args:
            endpoint (str): API endpoint
            data (Dict[str, Any]): Request payload
            
        Returns:
            requests.Response: API response
            
        Raises:
            APIConnectionError: If the request fails
        """
        pass

class ResponseParser(ABC):
    """Abstract base class for response parsers."""
    
    @abstractmethod
    def parse(self, response: requests.Response, prints: bool = False) -> Dict[str, Any]:
        """
        Parse API response.
        
        Args:
            response (requests.Response): API response to parse
            prints (bool): Whether to print response in real-time
            
        Returns:
            Dict[str, Any]: Parsed response data
            
        Raises:
            ResponseParsingError: If parsing fails
        """
        pass

class LeptonAIClient(APIClient):
    """
    Client for interacting with the Lepton AI API.
    
    Implements the APIClient interface and handles all communication with the Lepton AI API.
    """
    
    def __init__(self):
        """Initialize the Lepton AI client with default configuration."""
        self.base_url = 'https://search.lepton.run/api'
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.5',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://search.lepton.run',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        self.parser = LeptonResponseParser()

    def make_request(self, endpoint: str, data: Dict[str, Any]) -> requests.Response:
        """Implementation of APIClient.make_request."""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(url, headers=self.headers, json=data, stream=True)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise APIConnectionError(f"Failed to connect to Lepton AI API: {str(e)}")

    def search(self, query: str, prints: bool = False) -> Dict[str, Any]:
        """
        Perform a search query on Lepton AI.
        
        Args:
            query (str): Search query text
            prints (bool): Whether to print response in real-time
            
        Returns:
            Dict[str, Any]: Search results containing response text, contexts, and related questions
            
        Raises:
            ValidationError: If query is invalid
            APIConnectionError: If API request fails
            ResponseParsingError: If response parsing fails
        """
        if not isinstance(query, str) or not query.strip():
            raise ValidationError("Query must be a non-empty string")

        response = self.make_request('query', {"query": query, "rid": ""})
        return self.parser.parse(response, prints)

class LeptonResponseParser(ResponseParser):
    """Parser for Lepton AI API responses."""
    
    def parse(self, response: requests.Response, prints: bool = False) -> Dict[str, Any]:
        """
        Implementation of ResponseParser.parse.
        
        Args:
            response (requests.Response): API response to parse
            prints (bool): Whether to print response in real-time
            
        Returns:
            Dict[str, Any]: Parsed response data containing response text, contexts, and related questions
            
        Raises:
            ResponseParsingError: If response parsing fails
        """
        result = {
            "response": "",
            "contexts": [],
            "related_questions": []
        }

        try:
            for line in response.iter_lines(decode_unicode=True):
                if not line or line in ['__LLM_RESPONSE__', '__RELATED_QUESTIONS__']:
                    continue
                    
                try:
                    json_value = json.loads(line)
                    if 'contexts' in str(line):
                        result["contexts"] = self._parse_contexts(line)
                    elif '"question"' in line:
                        result["related_questions"] = self._parse_questions(line)
                except json.JSONDecodeError:
                    # Handle non-JSON lines (LLM response text)
                    cleaned_text = self._clean_response_text(line)
                    result["response"] += cleaned_text
                    if prints:
                        print(cleaned_text, end='', flush=True)

            return result
        except Exception as e:
            raise ResponseParsingError(f"Failed to parse response: {str(e)}")

    def _parse_contexts(self, line: str) -> List[Context]:
        """
        Parse context information from response line.
        
        Args:
            line (str): Response line containing context data
            
        Returns:
            List[Context]: List of parsed Context objects
        """
        data = json.loads(line)
        contexts = []
        
        for ctx in data.get("contexts", []):
            try:
                date_published = datetime.fromisoformat(ctx.get('datePublished', '').replace('Z', '+00:00')) if ctx.get('datePublished') else None
                context = Context(
                    name=ctx.get('name', ''),
                    id=ctx.get('id', ''),
                    url=ctx.get('url', ''),
                    thumbnail_url=ctx.get('thumbnailUrl'),
                    date_published=date_published,
                    is_family_friendly=bool(ctx.get('isFamilyFriendly', True)),
                    display_url=ctx.get('displayUrl', ''),
                    snippet=ctx.get('snippet', '')
                )
                contexts.append(context)
            except (ValueError, AssertionError) as e:
                print(f"Warning: Skipping invalid context: {str(e)}")
                
        return contexts

    def _parse_questions(self, value: str) -> List[str]:
        """
        Parse related questions from response line.
        
        Args:
            value (str): Response line containing questions
            
        Returns:
            List[str]: List of related questions
        """
        data = json.loads(value)
        return [q["question"] for q in data if isinstance(q, dict) and "question" in q]

    def _clean_response_text(self, text: str) -> str:
        """
        Clean and format response text.
        
        Args:
            text (str): Raw response text
            
        Returns:
            str: Cleaned and formatted text
        """
        text = re.sub(r'\[citation:\d+\]', '', text)
        text = text.replace(' .', '.')
        return f"{text}\n"
    
def format_search_results(results: Dict[str, Any]) -> str:
    """
    Format search results for display.
    
    Args:
        results (Dict[str, Any]): Search results to format
        
    Returns:
        str: Formatted results string
    """
    output = []
    
    if "response" in results:
        output.append(f"Response:\n{results['response']}\n")
    
    if "contexts" in results:
        output.append("Contexts:")
        for ctx in results["contexts"]:
            output.extend([
                f"Context Name: {ctx.name}",
                f"    ID: {ctx.id}",
                f"    URL: {ctx.url}",
                f"    Published: {ctx.date_published}",
                f"    Family Friendly: {ctx.is_family_friendly}",
                f"    Snippet: {ctx.snippet}\n"
            ])
    
    if "related_questions" in results:
        output.append("Related Questions:")
        for i, question in enumerate(results["related_questions"], 1):
            output.append(f"Question {i}: {question}")
    
    return "\n".join(output)

# Example usage
if __name__ == "__main__":
    try:
        client = LeptonAIClient()
        results = client.search("what is thermodynamics?", prints=True)
        print("\n" + format_search_results(results))
    except LeptonAIError as e:
        print(f"Error: {str(e)}")