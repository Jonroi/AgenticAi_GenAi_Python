import os
from dotenv import load_dotenv
from litellm import completion
import re

# Lataa API-avain .env-tiedostosta
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key is missing! Add it to the .env file.")

# Aseta API-avain LiteLLM:lle
os.environ["OPENAI_API_KEY"] = api_key

# Keskusteluhistoria
messages = [
    {
        "role": "system",
        "content": "You are an assistant that generates Python functions, adds documentation, and creates test cases.",
    }
]


def generate_response():
    """Call the LLM and get a response based on the conversation history."""
    response = completion(model="gpt-4o", messages=messages, max_tokens=512)

    # Varmista, että vastaus on kelvollinen
    if "choices" not in response or not response["choices"]:
        return "Error: No response from the model."

    return response["choices"][0]["message"]["content"]


def parse_code_and_comment(response):
    """Parse the code and commentary from the response."""
    # Etsi ensimmäinen Python-koodi (tunnistaa, että koodi alkaa `def`)
    code_match = re.search(r"(def .+?:[\s\S]+?)(?=\n\s*\n|\Z)", response)

    if code_match:
        code = code_match.group(0).strip()
        commentary = response.replace(code, "").strip()
        return code, commentary
    return response, ""


# Ensimmäinen kysymys
print("What function would you like me to create?")
user_input = input("\nUser: ")

# Lisää käyttäjän syöte keskusteluhistoriaan
messages.append(
    {"role": "user", "content": f"Write a Python function for: {user_input}"}
)

# Hanki vastaus LLM:ltä
response = generate_response()

# Parsitaan koodi ja kommentit
code, commentary = parse_code_and_comment(response)

# Näytetään luotu koodi (ilman kommentteja)
print("\nGenerated function:\n")
print(code)

# Toinen kysymys: Lisää dokumentaatio
messages.append(
    {
        "role": "user",
        "content": f"Add comprehensive documentation to the following Python function:\n\n{code}",
    }
)

response_with_docs = generate_response()

# Parsitaan dokumentoidut koodi ja kommentit
documented_code, docs_commentary = parse_code_and_comment(response_with_docs)

# Näytetään dokumentoitu koodi
print("\nDocumented function:\n")
print(documented_code)

# Kolmas kysymys: Lisää testit
messages.append(
    {
        "role": "user",
        "content": f"Add test cases using Python's unittest framework for the following Python function:\n\n{documented_code}",
    }
)

response_with_tests = generate_response()

# Parsitaan testikoodi ja kommentit
test_code, test_commentary = parse_code_and_comment(response_with_tests)

# Näytetään testit
print("\nGenerated test cases:\n")
print(test_code)
