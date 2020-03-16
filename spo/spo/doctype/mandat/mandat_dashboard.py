from frappe import _

def get_data():
	return {
		'fieldname': 'mandat',
		'transactions': [
			{
				'label': _('Anforderungen'),
				'items': ['Vollmacht', 'Anforderung Patientendossier', 'Medizinischer Bericht', 'Triage', 'Abschlussbericht']
			},
			{
				'label': _('Buchhaltung'),
				'items': ['Sales Invoice', 'Purchase Invoice']
			},
			{
				'label': _('Diverses'),
				'items': ['Freies Schreiben', 'SPO Anhang']
			}
		]
	}
