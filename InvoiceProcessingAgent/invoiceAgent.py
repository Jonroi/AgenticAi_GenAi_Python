import json
from typing import List, Dict

# ---- ActionContext class ----
class ActionContext:
    def __init__(self, context_data: dict = None):
        self.context_data = context_data or {}

    def get(self, key, default=None):
        return self.context_data.get(key, default)

    def set(self, key, value):
        self.context_data[key] = value

# ---- Extract Invoice Data Function ----
def extract_invoice_data(action_context: ActionContext, document_text: str) -> dict:
    """
    Extract standardized invoice data from document text.

    This tool ensures consistent extraction of invoice information by using a fixed schema
    and specialized prompting for invoice understanding. It will identify key fields like
    invoice numbers, dates, amounts, and line items from any invoice format.

    Args:
        action_context: The action context for handling state or caching (if needed).
        document_text: The text content of the invoice to process.

    Returns:
        A dictionary containing the extracted invoice data in a standardized format.
    """
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

    # Simulate LLM response (replace this with actual LLM call logic)
    simulated_response = {
        "invoice_number": "12345",
        "date": "2023-01-01",
        "total_amount": 100.0,
        "vendor": {"name": "Vendor Name", "address": "123 Vendor St."},
        "line_items": [
            {"description": "Item 1", "quantity": 1, "unit_price": 100.0, "total": 100.0}
        ]
    }

    # Validate against the schema (basic validation)
    required_fields = invoice_schema.get("required", [])
    for field in required_fields:
        if field not in simulated_response:
            raise ValueError(f"Missing required field: {field}")

    return simulated_response

# ---- Print Data as a List ----
def print_invoice_data_as_list(invoice_data: dict):
    """
    Print the invoice data in a human-readable list format.

    Args:
        invoice_data: The dictionary containing extracted invoice data.
    """
    print("Invoice Details:")
    print(f"  Invoice Number: {invoice_data['invoice_number']}")
    print(f"  Date: {invoice_data['date']}")
    print(f"  Total Amount: ${invoice_data['total_amount']:.2f}")
    print(f"  Vendor Name: {invoice_data['vendor']['name']}")
    print(f"  Vendor Address: {invoice_data['vendor']['address']}")
    print("\nLine Items:")
    for idx, item in enumerate(invoice_data["line_items"], start=1):
        print(f"  {idx}. Description: {item['description']}")
        print(f"     Quantity: {item['quantity']}")
        print(f"     Unit Price: ${item['unit_price']:.2f}")
        print(f"     Total: ${item['total']:.2f}")
    print("-" * 40)

# ---- Main Process ----
if __name__ == "__main__":
    # Load invoices from a JSON file
    input_file = "input_invoice.json"
    with open(input_file, 'r', encoding='utf-8') as f:
        invoice_texts = json.load(f)

    action_context = ActionContext()

    # Process and print all invoices
    for idx, invoice_entry in enumerate(invoice_texts, start=1):
        print(f"Invoice {idx}")
        document_text = invoice_entry.get("raw_invoice_text", "")
        if not document_text:
            print(f"  Warning: No raw invoice text found for Invoice {idx}. Skipping.")
            continue

        # Extract and print invoice data
        try:
            extracted_data = extract_invoice_data(action_context, document_text)
            print_invoice_data_as_list(extracted_data)
        except Exception as e:
            print(f"  Error Invoice {idx}: {e}")