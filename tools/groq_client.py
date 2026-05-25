import os
from dotenv import load_dotenv
from openai import OpenAI
from openai import OpenAIError

# Load environment variables from .env file
load_dotenv()

def get_groq_client() -> OpenAI:
    """
    Initializes and returns the OpenAI client configured for the Groq API.
    Ensures that the GROQ_API_KEY is securely accessed.
    """
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables. Please check your .env file.")
    
    # Connect to Groq API using the OpenAI SDK
    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

def ask_groq(prompt: str) -> str:
    """
    Sends a prompt to the Groq API and returns the AI's response.
    
    Args:
        prompt (str): The input text to send to the AI model.
        
    Returns:
        str: The clean response content from the AI.
    """
    try:
        # Initialize the client
        client = get_groq_client()
        
        # Send the request to Groq using the specified model
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Return the clean AI response text
        return response.choices[0].message.content
        
    except OpenAIError as e:
        # Handle API-related errors gracefully
        print(f"Error communicating with Groq API: {e}")
        return f"API Error: {e}"
    except Exception as e:
        # Catch any other unexpected exceptions
        print(f"An unexpected error occurred: {e}")
        return f"Unexpected Error: {e}"
