import os
from dotenv import load_dotenv
from litellm import completion
from typing import List, Dict

# Lataa ympäristömuuttujat .env-tiedostosta
load_dotenv()

# Hae API-avain ympäristömuuttujista
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API-avain puuttuu! Lisää se .env-tiedostoon.")

# LiteLLM käyttää OpenAI:n avainta
os.environ["OPENAI_API_KEY"] = api_key


def generate_response(messages: List[Dict]) -> str:
    """Call LLM to get response"""
    response = completion(model="openai/gpt-4o", messages=messages, max_tokens=1024)
    return response.choices[0].message.content


# Käyttäjän syöte
what_to_help_with = input("What do you need help with? ")

messages = [
    {
        "role": "system",
        "content": "You are a helpful customer service representative. No matter what the user asks, "
        "the solution is to tell them to turn their computer or modem off and then back on.",
    },
    {"role": "user", "content": what_to_help_with},
]

# Hae vastaus LLM:ltä
response = generate_response(messages)
print("\nCustomer Support Response:", response)
