import os
import asyncio
from datetime import datetime
from langchain_openai import ChatOpenAI
from browser_use import Agent
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DeepSearchAgent:
    def __init__(self, openai_api_key=None):
        # Use provided API key or get from environment
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        
        # Initialize the LLM
        self.llm = ChatOpenAI(model="gpt-4o")
    
    async def search_and_summarize(self, keywords, depth=2, output_file=None, language="english", blog_style=False):
        """
        Search for information about keywords and save a summary
        
        Args:
            keywords (str): Keywords or topic to search for
            depth (int): How deep to search (1-3, where 3 is deepest)
            output_file (str): Path to save the summary, defaults to keywords-based filename
            language (str): Output language, default is 'english'
            blog_style (bool): Format as blog article, default is False
        
        Returns:
            str: Path to the saved summary file
        """
        # Create a descriptive task for the agent
        depth_desc = "thoroughly" if depth >= 2 else "briefly"
        task = f"Search {depth_desc} for information about '{keywords}'. Find detailed facts, comparisons, and recent developments. Create a comprehensive summary with key points organized by subtopics."
        
        # Initialize the browser-use agent
        agent = Agent(
            task=task,
            llm=self.llm,
        )
        
        print(f"Starting deep search for: {keywords}")
        print(f"This may take a few minutes depending on search depth...")
        
        # Run the agent
        result = await agent.run()
        
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
        if blog_style or language.lower() != "english":
            print(f"Transforming results to {language} blog-style article...")
            
            # Create a prompt for the transformation
            language_str = language.lower()
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
        
        # Generate filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_keywords = keywords.replace(" ", "_").replace("/", "_").replace("\\", "_")
            output_file = f"{safe_keywords}_{timestamp}.md"
        
        # Save the summary to a file
        with open(output_file, "w", encoding="utf-8") as f:
            # For blog-style, the title is likely already in the content
            if not blog_style:
                f.write(f"# Summary: {keywords}\n\n")
                f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            f.write(result_text)
        
        print(f"Summary saved to: {output_file}")
        return output_file

async def main():
    # Create the agent
    agent = DeepSearchAgent()
    
    # Get user input
    print("Deep Search Agent")
    print("================")
    
    # Get keywords
    keywords = input("Enter keywords or topic to search for: ")
    
    # Get search depth
    depth = int(input("Enter search depth (1-3, where 3 is deepest): "))
    
    # Get language preference
    language_input = input("Enter output language (e.g., english, chinese, default: english): ")
    language = language_input.strip() if language_input.strip() else "english"
    
    # Get blog style preference
    blog_style_input = input("Format as blog article? (y/n, default: n): ")
    blog_style = blog_style_input.lower() in ["y", "yes", "true"]
    
    # Run the search
    await agent.search_and_summarize(keywords, depth, language=language, blog_style=blog_style)

if __name__ == "__main__":
    asyncio.run(main()) 