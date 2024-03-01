import frappe
from frappe import _

def execute():
    print("Lege Sprachen an")
    languages = [
    {"sprache": "Deutsch", "flagge": "🇩🇪"},
    {"sprache": "Italienisch", "flagge": "🇮🇹"},
    {"sprache": "Französisch", "flagge": "🇫🇷"},
    {"sprache": "Spanisch", "flagge": "🇪🇸"},
    {"sprache": "Englisch", "flagge": "🇬🇧"}
    ]
    for language in languages:
        existing_language = frappe.get_all("Sprache", filters={"language": language["sprache"]})
        if not existing_language:
            new_language = frappe.get_doc({
                "doctype": "Sprache",
                "language": language["sprache"],
                "flag": language["flagge"]
            })
            new_language.insert()
        else:
            print(f"The language '{language['sprache']}' already exists.")

    return
