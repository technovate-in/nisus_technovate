import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

def on_submit(doc, method):
    # super(PurchaseReceipt, doc).on_submit()
    create_nepl_sales_invoice(doc, method)

def create_nepl_sales_invoice(doc, method):
    if doc.company != "Cash":
        return  # Only process if PR belongs to 'Cash'

    # Get the Purchase Order linked to this Purchase Receipt
    sales_order_cash = doc.items[0].sales_order if doc.items else None
    if not sales_order_cash:
        frappe.throw("No linked Purchase Order found for this Sales Invoice.")

    # Fetch the linked Purchase Order for 'Nisus' from Company A's PO
    sales_order_nepl = frappe.db.get_value("Sales Order", sales_order_cash, "custom_sales_order_nepl")
    if not sales_order_nepl:
        frappe.throw("No linked Nisus Sales Order found for this Sales Invoice.")

    # Generate the Purchase Receipt for Nisus using the default method
    sales_invoice_nepl = make_sales_invoice(sales_order_nepl)
    sales_invoice_nepl.save()

    # doc.custom_sales_invoice_nepl = sales_invoice_nepl.name
    frappe.db.set_value("Sales Invoice", doc.name, "custom_sales_invoice_nepl", sales_invoice_nepl.name)
    # doc.save()
    
    sales_invoice_nepl.submit()
    frappe.msgprint(f"Purchase Receipt created for 'Nisus Energy Pvt Ltd' from {sales_order_nepl}")
