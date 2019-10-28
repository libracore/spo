from frappe import _

def get_data():
   return {
      'fieldname': 'mandat',
      'transactions': [
         {
            'label': _('Anforderungen'),
            'items': ['Anforderung Patientendossier', 'Medizinischer Bericht', 'Triage', 'Vollmacht', 'Abschlussbericht']
         }
      ]
   }