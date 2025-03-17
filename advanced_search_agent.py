import os
import asyncio
import json
from datetime import datetime
from langchain_openai import ChatOpenAI
from browser_use import Agent
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AdvancedSearchAgent:
    def __init__(self, openai_api_key=None, model="gpt-4o"):
        # Use provided API key or get from environment
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        
        # Initialize the LLM
        self.llm = ChatOpenAI(model=model)
    
    async def search_and_summarize(self, keywords, options=None):
        """
        Search for information about keywords and save a summary
        
        Args:
            keywords (str or list): Keywords or topics to search for
            options (dict): Configuration options including:
                - depth (int): How deep to search (1-3, where 3 is deepest)
                - output_format (str): 'markdown', 'json', or 'txt'
                - output_dir (str): Directory to save results
                - max_results (int): Maximum number of results to include
                - focus_areas (list): Specific aspects to focus on
                - language (str): Output language, default is 'english'
                - blog_style (bool): Format as blog article, default is False
        
        Returns:
            dict: Results including paths to saved files and summary stats
        """
        # Default options
        default_options = {
            "depth": 2,
            "output_format": "markdown",
            "output_dir": ".",
            "max_results": 10,
            "focus_areas": [],
            "language": "english",
            "blog_style": False
        }
        
        # Merge provided options with defaults
        if options is None:
            options = {}
        options = {**default_options, **options}
        
        # Handle single keyword or list of keywords
        if isinstance(keywords, str):
            keywords = [keywords]
        
        results = {}
        
        # Process each keyword
        for keyword in keywords:
            # Create a descriptive task for the agent
            depth_desc = {1: "briefly", 2: "thoroughly", 3: "exhaustively"}
            depth_level = min(max(options["depth"], 1), 3)  # Ensure depth is between 1-3
            
            # Build focus areas string if provided
            focus_str = ""
            if options["focus_areas"]:
                focus_str = f" Focus especially on: {', '.join(options['focus_areas'])}."
            
            task = (
                f"Search {depth_desc[depth_level]} for information about '{keyword}'."
                f" Find detailed facts, comparisons, and recent developments."
                f" Create a comprehensive summary with key points organized by subtopics."
                f" Include up to {options['max_results']} most relevant findings.{focus_str}"
            )
            
            # Initialize the browser-use agent
            agent = Agent(
                task=task,
                llm=self.llm,
            )
            
            print(f"Starting deep search for: {keyword}")
            print(f"This may take a few minutes depending on search depth...")
            
            # Run the agent
            start_time = datetime.now()
            result = await agent.run()
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Convert result to string if it's not already
            if hasattr(result, 'text'):
                result_text = result.text
            elif hasattr(result, '__str__'):
                result_text = str(result)
            else:
                # If we can't convert it directly, extract the last message
                try:
                    if hasattr(result, 'messages') and result.messages:
                        result_text = result.messages[-1].content
                    else:
                        result_text = "Could not extract text from search results."
                except:
                    result_text = "Could not extract text from search results."
            
            # Transform to blog-style article in specified language if requested
            if options["blog_style"] or options["language"].lower() != "english":
                print(f"Transforming results to {options['language']} blog-style article...")
                
                # Create a prompt for the transformation
                language_str = options["language"].lower()
                blog_prompt = f"""
                Transform the following research summary into a well-written, engaging {language_str} blog article.
                
                The article should:
                1. Have an engaging title and introduction
                2. Use a conversational, yet informative tone
                3. Include section headings where appropriate
                4. Maintain all the factual information from the original
                5. Conclude with some thoughtful insights
                6. Be written entirely in {language_str}
                
                Here is the research summary to transform:
                
                {result_text}
                """
                
                # Use the LLM to transform the content
                blog_response = self.llm.invoke(blog_prompt)
                result_text = blog_response.content
            
            # Ensure output directory exists
            os.makedirs(options["output_dir"], exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_keyword = keyword.replace(" ", "_").replace("/", "_").replace("\\", "_")
            
            # Save the summary based on the requested format
            if options["output_format"] == "json":
                output_file = os.path.join(options["output_dir"], f"{safe_keyword}_{timestamp}.json")
                with open(output_file, "w", encoding="utf-8") as f:
                    json_data = {
                        "keyword": keyword,
                        "timestamp": datetime.now().isoformat(),
                        "summary": result_text,
                        "metadata": {
                            "depth": options["depth"],
                            "focus_areas": options["focus_areas"],
                            "duration_seconds": duration,
                            "language": options["language"],
                            "blog_style": options["blog_style"]
                        }
                    }
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
            else:
                # Default to markdown
                ext = "md" if options["output_format"] == "markdown" else "txt"
                output_file = os.path.join(options["output_dir"], f"{safe_keyword}_{timestamp}.{ext}")
                
                with open(output_file, "w", encoding="utf-8") as f:
                    if options["output_format"] == "markdown":
                        # For blog-style, the title is likely already in the content
                        if not options["blog_style"]:
                            f.write(f"# Summary: {keyword}\n\n")
                            f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
                            if options["focus_areas"]:
                                f.write(f"**Focus Areas:** {', '.join(options['focus_areas'])}\n\n")
                    else:
                        if not options["blog_style"]:
                            f.write(f"SUMMARY: {keyword}\n")
                            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            if options["focus_areas"]:
                                f.write(f"Focus Areas: {', '.join(options['focus_areas'])}\n\n")
                    
                    f.write(result_text)
            
            print(f"Summary for '{keyword}' saved to: {output_file}")
            
            # Store results
            results[keyword] = {
                "output_file": output_file,
                "duration_seconds": duration
            }
        
        return results

async def main():
    # Create the agent
    agent = AdvancedSearchAgent()
    
    # Get user input
    print("Advanced Search Agent")
    print("====================")
    
    # Get keywords
    keywords_input = input("Enter keywords or topics to search (comma-separated): ")
    keywords = [k.strip() for k in keywords_input.split(",")]
    
    # Get search depth
    depth = int(input("Enter search depth (1-3, where 3 is deepest): "))
    
    # Get focus areas (optional)
    focus_input = input("Enter specific focus areas (comma-separated, or press Enter to skip): ")
    focus_areas = [f.strip() for f in focus_input.split(",")] if focus_input.strip() else []
    
    # Get output format
    format_options = ["markdown", "json", "txt"]
    format_input = input(f"Enter output format ({'/'.join(format_options)}, default: markdown): ")
    output_format = format_input.lower() if format_input.lower() in format_options else "markdown"
    
    # Get language preference
    language_input = input("Enter output language (e.g., english, chinese, default: english): ")
    language = language_input.strip() if language_input.strip() else "english"
    
    # Get blog style preference
    blog_style_input = input("Format as blog article? (y/n, default: n): ")
    blog_style = blog_style_input.lower() in ["y", "yes", "true"]
    
    # Configure options
    options = {
        "depth": depth,
        "output_format": output_format,
        "focus_areas": focus_areas,
        "output_dir": "search_results",
        "language": language,
        "blog_style": blog_style
    }
    
    # Run the search
    results = await agent.search_and_summarize(keywords, options)
    
    # Print summary
    print("\nSearch completed!")
    for keyword, data in results.items():
        print(f"- '{keyword}': Saved to {data['output_file']} (took {data['duration_seconds']:.1f} seconds)")

if __name__ == "__main__":
    asyncio.run(main()) 