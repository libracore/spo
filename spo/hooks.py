# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "spo"
app_title = "SPO"
app_publisher = "libracore"
app_description = "SPO Mandatsverwaltung"
app_icon = "octicon octicon file-submodule"
app_color = "grey"
app_email = "info@libracore.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/spo/css/spo.css"
app_include_js = "/assets/spo/js/spo.js"

# include js, css files in header of web template
# web_include_css = "/assets/spo/css/spo.css"
# web_include_js = "/assets/spo/js/spo.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Customer" : "scripts/custom_scripts/customer.js",
	"Timesheet" : "scripts/custom_scripts/timesheet.js",
	"Address" : "scripts/custom_scripts/address.js"
}
doctype_list_js = {
	"Timesheet" : "scripts/custom_scripts/timesheet_list.js"
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "spo.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "spo.install.before_install"
# after_install = "spo.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "spo.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"spo.tasks.all"
# 	],
# 	"daily": [
# 		"spo.tasks.daily"
# 	],
# 	"hourly": [
# 		"spo.tasks.hourly"
# 	],
# 	"weekly": [
# 		"spo.tasks.weekly"
# 	]
# 	"monthly": [
# 		"spo.tasks.monthly"
# 	]
# }
scheduler_events = {
	"daily": [
		"spo.spo.doctype.anfrage.anfrage.autom_submit",
		"spo.utils.timesheet_handlings.auto_ts_submit"
	]
}

# Testing
# -------

# before_tests = "spo.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "spo.event.get_events"
# }

# Fixtures
#fixtures = ["Custom Field"]