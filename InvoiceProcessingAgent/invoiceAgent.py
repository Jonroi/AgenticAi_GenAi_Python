import json
from typing import List, Dict

# ---- ActionContext-luokka ----
class ActionContext:
    """
    Luokka, joka hallitsee toimintojen kontekstia, kuten välimuistia tai tilaa.
    """
    def __init__(self, context_data: dict = None):
        # Alustetaan konteksti tyhjällä sanakirjalla, jos sitä ei anneta
        self.context_data = context_data or {}

    def get(self, key, default=None):
        """
        Hae arvo kontekstista annetulla avaimella.

        Args:
            key: Avaimen nimi.
            default: Oletusarvo, jos avainta ei löydy.

        Returns:
            Arvo, joka vastaa annettua avainta, tai oletusarvo.
        """
        return self.context_data.get(key, default)

    def set(self, key, value):
        """
        Aseta arvo kontekstiin annetulla avaimella.

        Args:
            key: Avaimen nimi.
            value: Asetettava arvo.
        """
        self.context_data[key] = value

# ---- Laskutietojen käsittelyfunktio ----
def extract_invoice_data(action_context: ActionContext, document_text: str) -> dict:
    """
    Eristä laskutiedot annetusta tekstistä.

    Tämä työkalu käyttää kiinteää skeemaa ja erikoistunutta logiikkaa
    laskutietojen ymmärtämiseen. Se tunnistaa keskeiset kentät, kuten
    laskun numerot, päivämäärät, summat ja rivitiedot.

    Args:
        action_context: Toimintakonteksti, joka hallitsee tilaa tai välimuistia.
        document_text: Laskun tekstisisältö.

    Returns:
        Sanakirja, joka sisältää eristetyt laskutiedot standardoidussa muodossa.
    """
    # Laskun skeema, joka määrittää odotetut kentät ja niiden tyypit
    invoice_schema = {
        "type": "object",
        "required": ["invoice_number", "date", "total_amount"],
        "properties": {
            "invoice_number": {"type": "string"},
            "date": {"type": "string"},
            "total_amount": {"type": "number"},
            "vendor": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "address": {"type": "string"}
                }
            },
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "number"},
                        "unit_price": {"type": "number"},
                        "total": {"type": "number"}
                    }
                }
            }
        }
    }

    # Simuloitu LLM-vastaus (korvaa tämä todellisella LLM-kutsulla)
    simulated_response = {
        "invoice_number": "12345",
        "date": "2023-01-01",
        "total_amount": 100.0,
        "vendor": {"name": "Vendor Name", "address": "123 Vendor St."},
        "line_items": [
            {"description": "Item 1", "quantity": 1, "unit_price": 100.0, "total": 100.0}
        ]
    }

    # Tarkista, että kaikki vaaditut kentät löytyvät vastauksesta
    required_fields = invoice_schema.get("required", [])
    for field in required_fields:
        if field not in simulated_response:
            raise ValueError(f"Puuttuva vaadittu kenttä: {field}")

    return simulated_response

# ---- Laskutietojen tulostusfunktio ----
def print_invoice_data_as_list(invoice_data: dict):
    """
    Tulosta laskutiedot luettavassa listamuodossa.

    Args:
        invoice_data: Sanakirja, joka sisältää eristetyt laskutiedot.
    """
    print("Laskun tiedot:")
    print(f"  Laskunumero: {invoice_data['invoice_number']}")
    print(f"  Päivämäärä: {invoice_data['date']}")
    print(f"  Kokonaissumma: ${invoice_data['total_amount']:.2f}")
    print(f"  Toimittajan nimi: {invoice_data['vendor']['name']}")
    print(f"  Toimittajan osoite: {invoice_data['vendor']['address']}")
    print("\nRivitiedot:")
    for idx, item in enumerate(invoice_data["line_items"], start=1):
        print(f"  {idx}. Kuvaus: {item['description']}")
        print(f"     Määrä: {item['quantity']}")
        print(f"     Yksikköhinta: ${item['unit_price']:.2f}")
        print(f"     Yhteensä: ${item['total']:.2f}")
    print("-" * 40)

# ---- Pääohjelma ----
if __name__ == "__main__":
    # Lataa laskut JSON-tiedostosta
    input_file = "input_invoice.json"
    with open(input_file, 'r', encoding='utf-8') as f:
        invoice_texts = json.load(f)

    # Alusta toimintakonteksti
    action_context = ActionContext()

    # Käsittele ja tulosta kaikki laskut
    for idx, invoice_entry in enumerate(invoice_texts, start=1):
        print(f"Lasku {idx}")
        document_text = invoice_entry.get("raw_invoice_text", "")
        if not document_text:
            print(f"  Varoitus: Laskun {idx} tekstisisältö puuttuu. Ohitetaan.")
            continue

        # Eristä ja tulosta laskutiedot
        try:
            extracted_data = extract_invoice_data(action_context, document_text)
            print_invoice_data_as_list(extracted_data)
        except Exception as e:
            print(f"  Virhe laskussa {idx}: {e}")