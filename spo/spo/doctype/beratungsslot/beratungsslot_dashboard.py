from frappe import _

def get_data():
    return {
        'fieldname': 'beratungsslot',
        'transactions': [
            {
                'label': _('Buchhaltung'),
                'items': ['Sales Invoice']
            }
        ]
    }
