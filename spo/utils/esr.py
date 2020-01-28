from __future__ import unicode_literals
import frappe, os, json, math
from frappe.utils.background_jobs import enqueue
from PyPDF2 import PdfFileWriter
import frappe, os, json
"""
Function for generating ESR-numbers for orange swiss payment slips ("Oranger Einzahlungsschein").
@param
    chf: amount in chf without rappen
    rappen: amount in rappen
    help1, help2, help3: fix, "+" or ">", no editing required
    referenceNumber: contains matag number, zeros, client number and job number
    participantNumber: bankaccount number
@usage generateCodeline("4378", "85", "94476300000000128001105152", "01200027")
 
"""
def moduloTenRecursive(number):
	lut = [0, 9, 4, 6, 8, 2, 7, 1, 3, 5];
	carryover = 0;
	for i in str(number):
		t = carryover + int(i)
		carryover = lut[t % 10];
	return str((10 - carryover) % 10)

@frappe.whitelist()
def generateCodeline(betrag, referenceNumber, participantNumber):
	bc = "01"
	help1 = ">"
	help2 = "+"
	help3 = ">"
	_rappen, franken = math.modf(betrag)
	if len(str(_rappen)) == 3:
		_rappen = str(_rappen) + "0"
		
	if len(referenceNumber) < 26:  # check if referenceNumber has less than 27 chars
		referenceNumber = (26-len(referenceNumber))*"0" + referenceNumber
			
	chf = str(int(franken))
	rappen = str(_rappen).split(".")[1]
	if len(chf) < 8:  # check if amount has less than eight chars
		chf = (8-len(chf))*"0" + chf
	if len(rappen) < 2:  # check if amount has less than 2 chars
		rappen = (2-len(rappen))*"0" + rappen

	# dynamic, check digit for bc and value (calculated with modulo 10 recursive)
	p1 = moduloTenRecursive(bc + chf + rappen)  
	# dynamic, check digit for referenceNumber (calculated with modulo 10 recursive)
	p2 = moduloTenRecursive(referenceNumber)
	
	return bc + chf + rappen + p1 + help1 + referenceNumber + p2 + help2 + " " + participantNumber + help3

def get_reference_number(referenceNumber):
	if len(referenceNumber) < 26:  # check if referenceNumber has less than 27 chars
		referenceNumber = (26-len(referenceNumber))*"0" + referenceNumber
	
	p2 = moduloTenRecursive(referenceNumber)
	
	return referenceNumber + p2
	
# START bereinigungscode
# bereinigungscode, kann nur von hand ausgefuehrt werden
def esr_reference_correction():
	all_sinvs = frappe.db.sql("""SELECT COUNT(`name`), `customer` FROM `tabSales Invoice` WHERE `docstatus` != 2""", as_list=True)[0][0]
	loop = 1
	sinvs = frappe.db.sql("""SELECT `name`, `customer`, `grand_total` FROM `tabSales Invoice` WHERE `docstatus` != 2""", as_dict=True)
	for sinv in sinvs:
		print("Correct {sinv} ({loop} of {all_sinvs})...".format(sinv=sinv.name, loop=loop, all_sinvs=all_sinvs))
		referencenumber = "974554" + sinv.customer.split("-")[2] + "0000" + sinv.name.split("-")[1] + sinv.name.split("-")[2] 
		new_ref = get_reference_number(referencenumber)
		new_code = generateCodeline(sinv.grand_total, referencenumber, "012000272")
		update_sinv = frappe.db.sql("""UPDATE `tabSales Invoice` SET `esr_reference` = '{new_ref}', `esr_code` = '{new_code}' WHERE `name` = '{name}'""".format(new_ref=new_ref, new_code=new_code, name=sinv.name), as_list=True)
		print("correction done...")
		loop += 1
	print("Finished all Sales Invoices (total: {all_sinvs})".format(all_sinvs=all_sinvs))
	
# bereinigungscode, kann nur von hand ausgefuehrt werden
def rechnungsnachdruck():
	all_sinvs = frappe.db.sql("""SELECT COUNT(`name`), `customer` FROM `tabSales Invoice` WHERE `docstatus` != 2""", as_list=True)[0][0]
	sinvs = frappe.db.sql("""SELECT `name` FROM `tabSales Invoice` WHERE `docstatus` != 2""", as_dict=True)
	qty = 0
	batch = 1
	to_print = []
	
	print("found {all_sinvs} Invoices to print".format(all_sinvs=all_sinvs))
	print("start printing...")
	
	for sinv in sinvs:
		if qty < 501:
			qty += 1
			to_print.append(sinv.name)
		else:
			# start background....(500er batch)
			bind_source = "/assets/spo/sinvs_for_print/NACHDRUCK/batch_{batch}.pdf".format(batch=batch)
			physical_path = "/home/frappe/frappe-bench/sites" + bind_source
			pdf_batch(to_print, format="Mitgliederrechnung", dest=str(physical_path), batch=batch)
			print("start background job {batch}".format(batch=batch))
			
			to_print = []
			qty = 1
			batch += 1
			to_print.append(sinv.name)
			
	# start background....(rest batch)
	bind_source = "/assets/spo/sinvs_for_print/NACHDRUCK/batch_{batch}.pdf".format(batch=batch)
	physical_path = "/home/frappe/frappe-bench/sites" + bind_source
	pdf_batch(to_print, format="Mitgliederrechnung", dest=str(physical_path), batch=batch)
	print("start LAST background job {batch}".format(batch=batch))
	
def pdf_batch(to_print, format=None, dest=None, batch=None):
	max_time = 4800
	args = {
		'sales_invoices': to_print,
		'format': "Mitgliederrechnung",
		'dest': dest
	}
	enqueue("spo.utils.esr.print_bind", queue='long', job_name='Erstelle PDF Batch {batch}'.format(batch=batch), timeout=max_time, **args)
	
def print_bind(sales_invoices, format=None, dest=None):
	# Concatenating pdf files
	output = PdfFileWriter()
	for sales_invoice in sales_invoices:
		output = frappe.get_print("Sales Invoice", sales_invoice, format, as_pdf = True, output = output)
	if dest != None:
		if isinstance(dest, str): # when dest is a file path
			destdir = os.path.dirname(dest)
			if destdir != '' and not os.path.isdir(destdir):
				os.makedirs(destdir)
			with open(dest, "wb") as w:
				output.write(w)
		else: # when dest is io.IOBase
			output.write(dest)
			print("first return")
		return
	else:
		print("second return")
		return output
# ENDE bereinigungscode