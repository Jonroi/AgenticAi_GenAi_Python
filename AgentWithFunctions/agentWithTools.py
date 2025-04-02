import os
import json
from dotenv import load_dotenv
from litellm import completion
from typing import List, Dict

# Lataa ympäristömuuttujat .env-tiedostosta
load_dotenv()

# Hae API-avain ympäristömuuttujista
api_key = os.getenv("OPENAI_API_KEY")

# Tarkista, että API-avain on asetettu
if not api_key:
    raise ValueError("API-avain puuttuu! Lisää se .env-tiedostoon.")

# Aseta API-avain ympäristömuuttujaksi LiteLLM:ää varten
os.environ["OPENAI_API_KEY"] = api_key


def list_files() -> List[str]:
    """List files in the current directory."""
    return os.listdir(".")


def read_file(file_name: str) -> str:
    """Read a file's contents."""
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: {file_name} not found."
    except Exception as e:
        return f"Error: {str(e)}"



def write_file(file_name: str, content: str) -> str:
    """Write content to a file."""
    try:
        with open(file_name, "w") as file:
            file.write(content)
        return f"File '{file_name}' updated successfully."
    except Exception as e:
        return f"Error: {str(e)}"

def update_json_file(file_name: str, key: str, value: str) -> str:
    """Updates a JSON file that contains a list by modifying an existing dictionary in the list."""
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        if not isinstance(data, list):
            return f"Error: {file_name} sisältää objektin, mutta odotettiin listaa."

        # Tarkistetaan, löytyykö jo avain "color": "redhair"
        for item in data:
            if item.get("color") == key:
                item["description"] = value
                break
        else:
            # Jos ei löytynyt, lisätään uusi objekti listaan
            data.append({"color": key, "description": value})

        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        
        return f"Updated {file_name} with {key}: {value}"

    except FileNotFoundError:
        return f"Error: {file_name} not found."
    except json.JSONDecodeError:
        return f"Error: {file_name} contains invalid JSON."
    except Exception as e:
        return f"Error: {str(e)}"





tool_functions = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "update_json_file": update_json_file,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Returns a list of files in the directory.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the content of a specified file in the directory.",
            "parameters": {
                "type": "object",
                "properties": {"file_name": {"type": "string"}},
                "required": ["file_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_json_file",
            "description": "Updates or modifies a JSON file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {"type": "string"},
                    "key": {"type": "string"},
                    "value": {"type": "string"}
                },
                "required": ["file_name", "key", "value"]
            }
        }
    }
]

# Kehote
agent_rules = [{
    "role": "system",
    "content": """
You are an AI assistant that interacts with the file system using tools.

- If the user asks to write or modify json file then use `update_json_file` and generate preferred content.
- Use `list_files` **only** if the user explicitly asks for a file list or doesn't specify a file name.
- If the user asks to read a file, always use `read_file`.
Always respond with the most relevant tool call.
"""
}]


# Käyttäjän tehtävä
user_task = input("What would you like me to do? ")

memory = [{"role": "user", "content": user_task}]
messages = agent_rules + memory


# LLM-kutsu
response = completion(
    model="openai/gpt-4o",
    messages=messages,
    tools=tools,
    max_tokens=1024
)

# Debug-tulosteet
print("Messages sent to LLM:", messages)
print("LLM Response:", response)

# Tarkista, palauttaako LLM työkalukutsun
if not response.choices[0].message.tool_calls:
    # Jos työkalukutsua ei ole, tulosta LLM:n tekstivastaus
    print(f"LLM Response: {response.choices[0].message.content}")
    exit()

# Työkalukutsun käsittely
tool = response.choices[0].message.tool_calls[0]
tool_name = tool.function.name
tool_args = json.loads(tool.function.arguments)

# Suorita työkalu
result = tool_functions[tool_name](**tool_args)

print(f"Tool Name: {tool_name}")
print(f"Tool Arguments: {tool_args}")
print(f"Result: {result}")

# Päivitä muisti tuloksella
memory.append({"role": "assistant", "content": result})