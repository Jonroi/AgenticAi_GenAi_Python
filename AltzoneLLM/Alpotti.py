import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from litellm import completion

# Lataa API-avain .env-tiedostosta
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API-avain puuttuu! Lisää se .env-tiedostoon.")

# Aseta API-avain LiteLLM:lle
os.environ["OPENAI_API_KEY"] = api_key

# Aseta Seleniumin polku WebDriveriin (tämä voi vaihdella tietokoneesi mukaan)
CHROME_DRIVER_PATH = "/path/to/chromedriver"  # Aseta oikea polku chromedriverille

# Käynnistä selaimen ajuri
chrome_options = Options()
chrome_options.add_argument(
    "--headless"
)  # Käynnistää selaimen näkymättömänä (headless mode)
service = Service(CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Keskusteluhistoria
messages = [{"role": "system", "content": "Olet avulias AI-avustaja."}]


# Hae tietoa altzone.fi-sivustolta (käyttäen Seleniumia)
def fetch_altzone_info(query):
    """Hakee tietoa altzone.fi-sivustolta Seleniumin avulla."""
    # Käy hakusivulla (suomi ja englanti)
    search_url_fi = f"https://altzone.fi/fi/?s={query}"  # Suomalainen versio
    search_url_en = f"https://altzone.fi/en/?s={query}"  # Englanninkielinen versio

    driver.get(search_url_fi)  # Lataa suomenkielinen hakusivu
    time.sleep(3)  # Odotetaan, että sivu latautuu

    try:
        # Hae ensimmäinen hakutulos
        first_result_fi = driver.find_element(By.CSS_SELECTOR, "h2.entry-title")
        return f"Suomeksi löytyi: {first_result_fi.text}"
    except:
        pass  # Jos ei löydy, kokeillaan englanninkielistä sivua

    driver.get(search_url_en)  # Lataa englanninkielinen hakusivu
    time.sleep(3)

    try:
        # Hae ensimmäinen hakutulos
        first_result_en = driver.find_element(By.CSS_SELECTOR, "h2.entry-title")
        return f"In English found: {first_result_en.text}"
    except:
        return "Ei löytynyt tietoa altzone.fi-sivustolta."


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

    # Hae tietoa altzone.fi-sivustolta
    altzone_info = fetch_altzone_info(user_input)

    # Lisää käyttäjän viesti ja haettu tieto keskusteluhistoriaan
    messages.append({"role": "user", "content": user_input})
    messages.append(
        {"role": "system", "content": f"Altzone.fi:n hakutulos: {altzone_info}"}
    )

    # Hanki vastaus mallilta
    assistant_response = generate_response()

    # Lisää avustajan vastaus keskusteluhistoriaan
    messages.append({"role": "assistant", "content": assistant_response})

    print("\nAvustaja:", assistant_response)

# Sulje selain ajuri lopuksi
driver.quit()
