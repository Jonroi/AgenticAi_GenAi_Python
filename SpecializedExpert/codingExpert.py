import os
from dotenv import load_dotenv
from typing import Dict

# Lataa ympäristömuuttujat .env-tiedostosta
load_dotenv()

# Hae API-avain ympäristömuuttujista
api_key = os.getenv("OPENAI_API_KEY")

# Tarkista, että API-avain on asetettu
if not api_key:
    raise ValueError("API-avain puuttuu! Lisää se .env-tiedostoon.")

# ---- Työkalujen rekisteröinti ----
def register_tool(tags=None):
    """
    Koristetyökalu, joka rekisteröi toiminnon tiettyjen tunnisteiden avulla.

    Args:
        tags (list): Lista tunnisteista, jotka kuvaavat työkalun tarkoitusta.

    Returns:
        decorator: Koristefunktio, joka lisää tunnisteet funktioon.
    """
    def decorator(func):
        func.tags = tags
        return func
    return decorator


# ---- LLM-kyselytoiminto ----
def prompt_expert(action_context: Dict, description_of_expert: str, prompt: str) -> str:
    """
    Kysyy asiantuntijalta (LLM) vastauksen annettuun kysymykseen.

    Args:
        action_context (Dict): Toimintakonteksti, joka voi sisältää tilatietoja.
        description_of_expert (str): Kuvaus asiantuntijan roolista ja osaamisesta.
        prompt (str): Käyttäjän kysymys tai pyyntö.

    Returns:
        str: LLM:n tuottama vastaus.
    """
    from litellm import completion

    try:
        # Rakenna viestit OpenAI:n API:lle
        messages = [
            {"role": "system", "content": description_of_expert},
            {"role": "user", "content": prompt}
        ]

        # Kutsu LLM:ää ja palauta vastaus
        response = completion(
            model="gpt-4",  # Käytettävä malli
            messages=messages,
            api_key=api_key,
            max_tokens=1000  # Maksimimäärä vastauksen tokeneita
        )
        return response.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    except Exception as e:
        return f"Virhe LLM-kyselyssä: {e}"


# ---- Vastausten tallennus tiedostoon ----
def save_response_to_file(filename: str, content: str):
    """
    Tallentaa annetun sisällön tekstitiedostoon.

    Args:
        filename (str): Tiedoston nimi, johon sisältö tallennetaan.
        content (str): Tallennettava sisältö.
    """
    # Selvitä nykyisen skriptin sijainti
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)

    # Kirjoita sisältö tiedostoon
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"Vastaus tallennettu tiedostoon: {file_path}")


# ---- Työkalut ----
@register_tool(tags=["documentation"])
def generate_technical_documentation(action_context: Dict, code_or_feature: str) -> str:
    """
    Luo tekninen dokumentaatio konsultoimalla asiantuntijaa.

    Args:
        action_context (Dict): Toimintakonteksti.
        code_or_feature (str): Koodi tai ominaisuus, josta dokumentaatio luodaan.

    Returns:
        str: LLM:n tuottama tekninen dokumentaatio.
    """
    response = prompt_expert(
        action_context=action_context,
        description_of_expert="""
        Olet kokenut tekninen kirjoittaja, jolla on 15 vuoden kokemus ohjelmistodokumentaatiosta.
        """,
        prompt=f"""
        Luo kattava tekninen dokumentaatio seuraavasta koodista tai ominaisuudesta:

        {code_or_feature}
        """
    )
    save_response_to_file("technical_documentation.txt", response)
    return response


@register_tool(tags=["testing"])
def design_test_suite(action_context: Dict, feature_description: str) -> str:
    """
    Suunnittele testisarja konsultoimalla asiantuntijaa.

    Args:
        action_context (Dict): Toimintakonteksti.
        feature_description (str): Ominaisuuden kuvaus, jota testataan.

    Returns:
        str: LLM:n tuottama testisuunnitelma.
    """
    response = prompt_expert(
        action_context=action_context,
        description_of_expert="""
        Olet kokenut QA-insinööri, jolla on 12 vuoden kokemus testisuunnittelusta.
        """,
        prompt=f"""
        Suunnittele kattava testisarja seuraavalle ominaisuudelle:

        {feature_description}
        """
    )
    save_response_to_file("test_suite.txt", response)
    return response


@register_tool(tags=["code_quality"])
def perform_code_review(action_context: Dict, code: str) -> str:
    """
    Arvioi koodi ja ehdota parannuksia konsultoimalla asiantuntijaa.

    Args:
        action_context (Dict): Toimintakonteksti.
        code (str): Arvioitava koodi.

    Returns:
        str: LLM:n tuottama koodiarvio.
    """
    response = prompt_expert(
        action_context=action_context,
        description_of_expert="""
        Olet kokenut ohjelmistoarkkitehti, jolla on 20 vuoden kokemus koodiarvioista.
        """,
        prompt=f"""
        Arvioi seuraava koodi ja ehdota yksityiskohtaisia parannuksia:

        {code}
        """
    )
    save_response_to_file("code_review.txt", response)
    return response


@register_tool(tags=["communication"])
def write_feature_announcement(action_context: Dict, feature_details: str, audience: str) -> str:
    """
    Kirjoita ominaisuuden julkistus konsultoimalla asiantuntijaa.

    Args:
        action_context (Dict): Toimintakonteksti.
        feature_details (str): Ominaisuuden yksityiskohdat.
        audience (str): Kohdeyleisö.

    Returns:
        str: LLM:n tuottama julkistusteksti.
    """
    response = prompt_expert(
        action_context=action_context,
        description_of_expert="""
        Olet kokenut tuotemarkkinointipäällikkö, jolla on 12 vuoden kokemus teknisestä viestinnästä.
        """,
        prompt=f"""
        Kirjoita ominaisuuden julkistus seuraaville yksityiskohdille:

        {feature_details}

        Kohdeyleisö: {audience}
        """
    )
    save_response_to_file("feature_announcement.txt", response)
    return response


# ---- Pääohjelma ----
if __name__ == "__main__":
    # Alusta toimintakonteksti
    action_context = {}

    print("Luodaan tekninen dokumentaatio:")
    documentation = generate_technical_documentation(action_context,  """
    def add_numbers(a, b):
        \"\"\"Palauttaa kahden luvun summan.\"\"\"
        return a + b
    """)
    print(documentation)

    print("\nSuunnitellaan testisarja:")
    test_suite = design_test_suite(action_context, "Esimerkkiominaisuuden kuvaus")
    print(test_suite)

    print("\nSuoritetaan koodiarvio:")
    code_review = perform_code_review(action_context, "def example_function(): pass")
    print(code_review)

    print("\nKirjoitetaan ominaisuuden julkistus:")
    announcement = write_feature_announcement(action_context, "Esimerkkiominaisuuden yksityiskohdat", "tekninen yleisö")
    print(announcement)