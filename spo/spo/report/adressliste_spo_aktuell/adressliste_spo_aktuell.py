# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from six.moves import range
from six import iteritems
import frappe


field_map = {
	"Contact": [ "salutation", "first_name", "last_name", "spo_aktuell" ],
	"Address": [ "address_line1", "address_line2", "plz", "city" ]
}

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_columns(filters):
	party_type = 'Customer'
	party_type_value = "customer_group"
	return [
		"Kunde:Link/{party_type}".format(party_type=party_type),
		"Kundengruppe::100".format(party_value_type = frappe.unscrub(str(party_type_value))),
		"Anrede",
		"Vorname",
		"Nachname",
		"SPO Aktuell",
		"Strasse und Hausnummer",
		"Zusatz",
		"PLZ",
		"Ort",
		"Sprache"
	]

def get_data(filters):
	party_type = 'Customer'
	party = ''
	party_group = "customer_group"

	return get_party_addresses_and_contact(party_type, party, party_group)

def get_party_addresses_and_contact(party_type, party, party_group):
	data = []
	filters = None
	party_details = frappe._dict()

	if not party_type:
		return []

	if party:
		filters = { "name": party }

	fetch_party_list = frappe.get_list(party_type, filters=filters, fields=["name", party_group], as_list=True)
	party_list = [d[0] for d in fetch_party_list]
	party_groups = {}
	for d in fetch_party_list:
		party_groups[d[0]] = d[1]

	for d in party_list:
		party_details.setdefault(d, frappe._dict())

	party_details = get_party_details(party_type, party_list, "Contact", party_details)
	party_details = get_party_details(party_type, party_list, "Address", party_details)

	for party, details in iteritems(party_details):
		contacts  = details.get("contact", [])
		addresses = details.get("address", [])
		
		if not any([contacts, addresses]):
			result = [party]
			result.append(party_groups[party])
			result.extend(add_blank_columns_for("Contact"))
			result.extend(add_blank_columns_for("Address"))
			data.append(result)
		else:
			contacts = list(map(list, contacts))
			addresses = list(map(list, addresses))
			

			max_length = max(len(contacts), len(addresses))
			for idx in range(0, max_length):
				result = [party]
				result.append(party_groups[party])
				
				contact = contacts[idx] if idx < len(contacts) else add_blank_columns_for("Contact")
				address = addresses[idx] if idx < len(addresses) else add_blank_columns_for("Address")
				result.extend(contact)
				result.extend(address)
				result.append(frappe.get_doc("Customer", party).language)
				

				data.append(result)
	return data

def get_party_details(party_type, party_list, doctype, party_details):
	filters =  [
		["Dynamic Link", "link_doctype", "=", party_type],
		["Dynamic Link", "link_name", "in", party_list]
	]
	fields = ["`tabDynamic Link`.link_name"] + field_map.get(doctype, [])

	records = frappe.get_list(doctype, filters=filters, fields=fields, as_list=True)
	for d in records:
		details = party_details.get(d[0])
		details.setdefault(frappe.scrub(doctype), []).append(d[1:])

	return party_details

def add_blank_columns_for(doctype):
	return ["" for field in field_map.get(doctype, [])]

def get_party_group(party_type):
	if not party_type: return
	group = {
		"Customer": "customer_group",
		"Supplier": "supplier_group",
		"Sales Partner": "partner_type"
	}

	return group[party_type]