import os
from dotenv import load_dotenv
from litellm import completion

# Lataa API-avain .env-tiedostosta
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API-avain puuttuu! Lisää se .env-tiedostoon.")

# Aseta API-avain LiteLLM:lle
os.environ["OPENAI_API_KEY"] = api_key

# Keskusteluhistoria
messages = [{"role": "system", "content": "Olet avulias AI-avustaja."}]


def generate_response():
    """Kutsu LLM-mallia ja hanki vastaus keskusteluhistorian perusteella."""
    response = completion(model="gpt-4o", messages=messages, max_tokens=512)

    # Varmista, että vastaus on kelvollinen
    if "choices" not in response or not response["choices"]:
        return "Virhe: Mallilta ei saatu vastausta."

    return response["choices"][0]["message"]["content"]


# Tulosta aloitusviesti
print("Hei! Kuinka voin auttaa sinua?")

while True:
    user_input = input("\nKäyttäjä: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Näkemiin!")
        break

    # Lisää käyttäjän viesti keskusteluhistoriaan
    messages.append({"role": "user", "content": user_input})

    # Hanki vastaus mallilta
    assistant_response = generate_response()

    # Lisää avustajan vastaus keskusteluhistoriaan
    messages.append({"role": "assistant", "content": assistant_response})

    print("\nAvustaja:", assistant_response)
