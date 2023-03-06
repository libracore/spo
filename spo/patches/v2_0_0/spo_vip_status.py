import frappe
from frappe import _

def execute():
    # Initial-Erstellung SPO VIP Status
    try:
        print("Patch: Initial-Erstellung SPO VIP Status")
        status_normal = frappe.get_doc({
            'doctype': 'SPO VIP Status',
            'title': 'Normal'
        }).insert()
        status_vip = frappe.get_doc({
            'doctype': 'SPO VIP Status',
            'title': 'VIP'
        }).insert()
    except Exception as err:
        print("FAILED: Initial-Erstellung SPO VIP Status")
        print(str(err))
    try:
        # create user restrictions
        print("Patch: create user restrictions")
        users = frappe.db.sql("""SELECT `name` FROM `tabUser` WHERE `name` != 'Administrator' AND `enabled` = 1""", as_dict=True)
        for user in users:
            try:
                user_permission = frappe.get_doc({
                    'doctype': 'User Permission',
                    'user': user.name,
                    'for_value': 'Normal',
                    'allow': 'SPO VIP Status',
                    'is_default': 1,
                    'apply_to_all_doctypes': 1
                }).insert()
            except Exception as e:
                print("{0} failed: {1}".format(user.name, e))
    except Exception as err:
        print("FAILED: create user restrictions")
        print(str(err))
    return
