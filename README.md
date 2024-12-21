# Lepton AI API Client

A professional Python client for interacting with the Lepton AI search API. This client provides a robust, type-safe, and efficient way to access Lepton AI's search capabilities while following modern Python best practices.

## ⚠️ Disclaimer

This code is provided strictly for **educational purposes only**. It is intended to demonstrate professional Python coding practices, API interaction patterns, and modern software design principles. The implementation:

- Should not be used to harm or disrespect Lepton AI or its services
- Must not be used to circumvent API rate limits or terms of service
- Is not officially associated with or endorsed by Lepton AI
- Should be used responsibly and in accordance with Lepton AI's terms of service

Please visit [Lepton AI's official website](https://www.lepton.ai/) for official API access and documentation.

## 🌟 Features

- **Robust Error Handling**: Custom exception hierarchy for precise error management
- **Type Safety**: Comprehensive type hints and runtime type checking
- **Clean Architecture**: Following SOLID principles and clean code practices
- **Streaming Support**: Efficient handling of streaming responses
- **Data Validation**: Strict validation of inputs and outputs
- **Professional Logging**: Structured warning and error logging
- **Immutable Data Structures**: Thread-safe data handling with immutable objects

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/sujalrajpoot/Lepton-AI-API-Client.git

# Navigate to the project directory
cd Lepton-AI-API-Clien

# Install dependencies
pip install requests
```

## 📋 Requirements

- Python 3.8 or higher
- requests
- dataclasses (included in Python 3.7+)
- typing-extensions (for Python < 3.8)

## 🚀 Quick Start

```python
from lepton_client import LeptonAIClient, LeptonAIError, format_search_results

# Initialize the client
client = LeptonAIClient()

try:
    # Perform a search
    results = client.search("what is quantum computing?", prints=True)
    
    # Format and print results
    print(format_search_results(results))
except LeptonAIError as e:
    print(f"Error: {str(e)}")
```

## 🔍 Response Structure

The client returns a dictionary containing:
- `response`: The main response text
- `contexts`: List of Context objects with source information
- `related_questions`: List of related search queries

Example response structure:
```python
{
    "response": "Detailed answer about quantum computing...",
    "contexts": [
        Context(
            name="Introduction to Quantum Computing",
            url="https://example.com/quantum",
            # ... other context fields
        ),
        # ... more contexts
    ],
    "related_questions": [
        "How does quantum entanglement work?",
        "What are qubits?",
        # ... more questions
    ]
}
```

## 🔧 Advanced Usage

### Custom Error Handling

```python
try:
    results = client.search("your query")
except APIConnectionError as e:
    print("Connection failed:", e)
except ResponseParsingError as e:
    print("Parsing failed:", e)
except ValidationError as e:
    print("Invalid input:", e)
```

### Context Processing

```python
results = client.search("your query")
for context in results["contexts"]:
    if context.is_family_friendly:
        print(f"Source: {context.name}")
        print(f"Published: {context.date_published}")
        print(f"Summary: {context.snippet}")
```

## 📝 Development Guidelines

1. **Type Safety**
   - Use type hints consistently
   - Add runtime type checking for critical functions
   - Validate all external inputs

2. **Error Handling**
   - Use custom exceptions for specific error cases
   - Provide meaningful error messages
   - Log errors appropriately

3. **Testing**
   - Write unit tests for all new features
   - Maintain test coverage above 80%
   - Include integration tests for API interactions

## 🔒 Security Best Practices

- Never store API credentials in code
- Validate and sanitize all inputs
- Use secure HTTPS connections
- Implement rate limiting
- Log security-relevant events

## 📚 API Documentation

### LeptonAIClient

Main client class for interacting with the Lepton AI API.

```python
class LeptonAIClient:
    def search(self, query: str, prints: bool = False) -> Dict[str, Any]:
        """
        Perform a search query.
        
        Args:
            query (str): Search query text
            prints (bool): Whether to print response in real-time
            
        Returns:
            Dict[str, Any]: Search results
            
        Raises:
            ValidationError: If query is invalid
            APIConnectionError: If API request fails
            ResponseParsingError: If response parsing fails
        """
```

### Context

Immutable dataclass for storing context information.

```python
@dataclass(frozen=True)
class Context:
    name: str
    id: str
    url: str
    thumbnail_url: Optional[str]
    date_published: Optional[datetime]
    is_family_friendly: bool
    display_url: str
    snippet: str
```

---

## 💡 How It Can Help Users
This project is perfect for developers looking to:

- Build conversational agents or chatbots with advanced AI.
- Integrate real-time responses into applications.
- Experiment with AI models using an easy-to-use API interface.
---

# Created with ❤️ by **Sujal Rajpoot**

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contact
For questions or support, please open an issue or reach out to the maintainer.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
