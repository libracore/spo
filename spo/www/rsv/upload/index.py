from __future__ import unicode_literals
import frappe
from frappe import _
import six
import json

no_cache = 1

def get_context(context):
    # lade URL Parameter
    # und prüfe ob 'id' und 'login' vorhanden
    try:
        query_params = frappe.request.args
        context.query_login = query_params['id']
        context.query_login = query_params['login']
    except:
        kickout()
    
    # Keinen Zugriff per Default
    context.access = False
    
    # Prüfe ID und Login
    context = check_credentials(context, query_params)
    
    if context.access:
        # Lade RSV & User spezifische Daten
        context = get_rsv_information(context, query_params)
        return context
    else:
        kickout()

def kickout():
    frappe.throw(_("You need to be logged in to access this page"), frappe.PermissionError)

def check_credentials(context, query_params):
    # Prüfung ob die RSV Identifikation gültig ist
    # und ob ein Contact mit dem spezifischen Login existiert
    if frappe.db.exists("Customer", {"rsv_upload_id": query_params['id']}) and frappe.db.exists("Contact", {"rsv_upload_login": query_params['login']}):
        context.access = True
        return context
    else:
        kickout()

def get_rsv_information(context, query_params):
    try:
        # erlaube Zugriff
        context.access = True
        
        # Kundendaten (RSV)
        customer = frappe.db.exists("Customer", {"rsv_upload_id": query_params['id']})
        context.customer = frappe.db.sql("""
                                            SELECT
                                                `customer_name`,
                                                `name`
                                            FROM `tabCustomer`
                                            WHERE `name` = '{0}'""".format(customer), as_dict=True)[0]
        
        # Kontaktdaten (Login Spezifisch)
        contact = frappe.db.exists("Contact", {"rsv_upload_login": query_params['login']})
        context.contact = frappe.db.sql("""
                                            SELECT
                                                `first_name`,
                                                `last_name`,
                                                `salutation`,
                                                `salutation_title`
                                            FROM `tabContact`
                                            WHERE `name` = '{0}'""".format(contact), as_dict=True)[0]
        
        verknuepfte_mitarbeiter = frappe.db.sql("""
                                            SELECT
                                                `first_name`,
                                                `last_name`,
                                                `name`
                                            FROM `tabContact`
                                            WHERE `name` IN (
                                                SELECT `parent` FROM `tabDynamic Link`
                                                WHERE `parenttype` = 'Contact'
                                                AND `link_name` = '{0}'
                                            )""".format(customer), as_dict=True)
        
        context.mitarbeiter = verknuepfte_mitarbeiter
        
        context.anlage_key = frappe.db.get_single_value('RSV Upload Tool Settings', 'anlage_key')
        
        return context
    except:
        kickout()

@frappe.whitelist(allow_guest=True)
def erstelle_anfrage(form_data):
    if isinstance(form_data, six.string_types):
        form_data = json.loads(form_data)
    
    if form_data['anlage_key'] == frappe.db.get_single_value('RSV Upload Tool Settings', 'anlage_key'):
        with_files = False
        form_data['doctype'] = 'Anfrage'
        form_data['spo_ombudstelle'] = 'Nein'
        form_data['kontakt_via'] = 'Upload Tool'
        form_data['eingeschraenkter_zugriff'] = 1
        
        if form_data['anhang']:
            with_files = True
        
        del form_data['anlage_key']
        del form_data['anhang']
        
        new_anfrage = frappe.get_doc(form_data)
        new_anfrage.insert(ignore_permissions=True)
        
        if not with_files:
            return {
                'files': 0,
                'anfrage': new_anfrage.name
            }
        else:
            return {
                'files': 1,
                'anfrage': new_anfrage.name,
                'key': frappe.db.get_value("RSV Upload Tool Settings", "RSV Upload Tool Settings", "upload_key"),
                'secret': frappe.db.get_value("RSV Upload Tool Settings", "RSV Upload Tool Settings", "upload_secret")
            }
    else:
        kickout()
