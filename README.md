# Browser-Use Search Agent

This project implements an agent that can automatically search the web for information about keywords you're interested in and save summaries locally.

## Prerequisites

- Python 3.11 or higher
- OpenAI API key

## Installation

1. Clone this repository
2. Install the required packages:

```bash
pip install langchain-openai browser-use python-dotenv
```

3. Create a `.env` file in the project root with your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Basic Search Agent

The basic search agent (`search_agent.py`) allows you to search for a single keyword or topic:

```bash
python search_agent.py
```

You'll be prompted to enter:
- Keywords or topic to search for
- Search depth (1-3, where 3 is deepest)

The agent will then:
1. Search the web for information about your keywords
2. Create a comprehensive summary
3. Save the summary to a Markdown file in the current directory

### Advanced Search Agent

The advanced search agent (`advanced_search_agent.py`) provides more features:

```bash
python advanced_search_agent.py
```

You'll be prompted to enter:
- Keywords or topics to search for (comma-separated)
- Search depth (1-3, where 3 is deepest)
- Specific focus areas (optional)
- Output format (markdown, json, or txt)

The agent will:
1. Search the web for each keyword
2. Create comprehensive summaries
3. Save the summaries to files in the `search_results` directory
4. Print a summary of the search results

### Programmatic Usage

You can also use the agents programmatically in your own Python code:

```python
import asyncio
from advanced_search_agent import AdvancedSearchAgent

async def example():
    agent = AdvancedSearchAgent()
    
    # Configure search options
    options = {
        "depth": 2,
        "output_format": "markdown",
        "focus_areas": ["recent developments", "comparisons"],
        "output_dir": "my_search_results"
    }
    
    # Run the search
    results = await agent.search_and_summarize(
        ["artificial intelligence", "quantum computing"], 
        options
    )
    
    print(results)

# Run the example
asyncio.run(example())
```

## How It Works

This project uses:
- [browser-use](https://docs.browser-use.com/quickstart) - A tool that enables LLMs to browse the web
- [LangChain](https://python.langchain.com/docs/get_started/introduction) - A framework for building LLM applications
- OpenAI's GPT models - For understanding search queries and generating summaries

The agent:
1. Takes your keywords and creates a search task
2. Uses browser-use to navigate the web and find relevant information
3. Summarizes the findings in a structured format
4. Saves the results to a file in your preferred format

## Customization

You can modify the search behavior by editing the task description in the code or by providing different options when calling the `search_and_summarize` method.