import frappe
from frappe import _

def execute():
    try:
        print("Patch: Erfasse Inaktivierungen")
        frappe.reload_doc("spo", "doctype", "mitgliedschaft")
        inaktivierungen = frappe.db.sql("""SELECT
                                                `log`.`mitgliedschaft` AS `mitgliedschaft`,
                                                `p`.`executed_on` AS `executed_on`
                                            FROM `tabCustomer Deactivation Log Table` AS `log`
                                            JOIN `tabCustomer Deactivation Log` AS `p` ON `log`.`parent` = `p`.`name`""", as_dict=True)
        for inaktivierung in inaktivierungen:
            frappe.db.set_value("Mitgliedschaft", inaktivierung.mitgliedschaft, 'status_bezugsdatum', str(inaktivierung.executed_on).split(" ")[0])
            frappe.db.set_value("Mitgliedschaft", inaktivierung.mitgliedschaft, 'status', 'Inaktiviert')
    except Exception as err:
        print("FAILED: Erfasse Inaktivierungen")
        print(str(err))
    return
