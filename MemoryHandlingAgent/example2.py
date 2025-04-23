import os
from dotenv import load_dotenv
from litellm import completion
from typing import List, Dict

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key is missing! Add it to the .env file.")

# LiteLLM uses OpenAI's key
os.environ["OPENAI_API_KEY"] = api_key


def generate_response(messages: List[Dict]) -> str:
    """Call LLM to get response"""
    response = completion(model="openai/gpt-4o", messages=messages, max_tokens=1024)
    return response.choices[0].message.content


def main():
    # Initial messages
    messages = [
        {
            "role": "system",
            "content": "You are an expert software engineer that prefers functional programming.",
        },
        {
            "role": "user",
            "content": "Write hello world in Python.",
        },
    ]

    # Get initial response
    initial_response = generate_response(messages)
    print("Initial response:", initial_response)

    # Add the assistant's response to the messages
    messages.append({"role": "assistant", "content": initial_response})

    # Ask the assistant to update the function
    messages.append(
        {"role": "user", "content": "Update the function to include documentation."}
    )

    # Get updated response
    updated_response = generate_response(messages)
    print("Updated response:", updated_response)


if __name__ == "__main__":
    main()
