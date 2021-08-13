# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from spo.spo.doctype.meldestelle.meldestelle import _create_reporting

@frappe.whitelist(allow_guest=True)
def create_reporting(**kwargs):
    return _create_reporting(**kwargs)
