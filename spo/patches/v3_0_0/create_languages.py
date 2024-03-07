import frappe
from frappe import _

def execute():
    print("Lege Sprachen an")
    # this will insert codes, unicode entities will be inserted as None which crashes the later code
    # Note: flags must be replaced in the frontend
    languages = [
        {"sprache": "Deutsch", "flagge": "&#127465;"},
        {"sprache": "Italienisch", "flagge": "&#127470;"},
        {"sprache": "Französisch", "flagge": "&#127467;"},
        {"sprache": "Spanisch", "flagge": "&#127466;"},
        {"sprache": "Englisch", "flagge": "&#127468;"}
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
            print("The language '{0}' already exists.".format(language['sprache']))

    return
