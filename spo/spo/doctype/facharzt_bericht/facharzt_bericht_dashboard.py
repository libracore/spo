from frappe import _

def get_data():
	return {
		'fieldname': 'facharzt_bericht',
		'transactions': [
			{
				'label': _('Referenzen'),
				'items': ['SPO Anhang']
			}
		]
	}
