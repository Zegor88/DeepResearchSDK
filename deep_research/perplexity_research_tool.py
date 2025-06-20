from agents import function_tool
from datetime import datetime
import requests
from dotenv import load_dotenv
import os

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

current_date = datetime.now().strftime("%B %Y")


@function_tool
def get_perplexity_response(query: str) -> str:
    """Perform a search on the web using Perplexity API and return the response content.
    Args:
        query: The query to search for.
    Returns:
        The content of the search result as a string.
    """

    perplexity_system_prompt = f"""
    You are a helpful AI assistant
    Rules:
    1. Provide only the final answer. It is important that you do not include any explanation on the steps below.
    2. Do not show the intermediate steps information.
    3. For search, use the most up-to-date information on the current date - {current_date}.
    Steps:
    1. Decide if the answer should be a brief sentence or a list of suggestions.
    2. If it is a list of suggestions, first, write a brief and natural introduction based on the original query.
    3. Followed by a list of suggestions, each suggestion should be split by two newlines.
    """
    
    url = "https://api.perplexity.ai/chat/completions"

    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": perplexity_system_prompt
            },
            {
                "role": "user",
                "content": query
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=payload).json()

    # Добавим проверку на ошибки от API
    if 'error' in response:
        return f"API Error: {response['error'].get('message', 'Unknown error')}"

    # Безопасно извлекаем контент
    try:
        content = response['choices'][0]['message']['content']
        citation = response['search_results']
        output = {
            "content": content,
            "citation": citation
        }
    except (KeyError, IndexError):
        return "Error: Could not parse the response from the API."

    return output