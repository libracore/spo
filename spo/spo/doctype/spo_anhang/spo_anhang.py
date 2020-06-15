# -*- coding: utf-8 -*-
# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SPOAnhang(Document):
	def validate(self):
		if self.facharzt_bericht:
			mandat = frappe.get_doc("Facharzt Bericht", self.facharzt_bericht).mandat
			self.mandat = mandat
