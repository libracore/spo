import frappe
from frappe import _

def execute():
    # Initial-Erstellung Demographie Bins
    print("Patch: Initial-Erstellung Demographie Bins")
    kunden = frappe.db.sql("""SELECT `name` FROM `tabCustomer`""", as_dict=True)
    m_max = len(kunden)
    print("found {0} Kunden".format(m_max))
    loop = 1
    for kunde in kunden:
        print("Create {0} of {1}".format(loop, m_max))
        try:
            m = frappe.get_doc("Customer", kunde.name)
            m.save()
        except Exception as err:
            print("{0} failed".format(kunde.name))
        loop += 1
    return
