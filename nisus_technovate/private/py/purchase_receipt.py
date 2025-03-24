import frappe
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import PurchaseReceipt
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt

def on_submit(doc, method):
    # super(PurchaseReceipt, doc).on_submit()
    create_nepl_purchase_receipt(doc, method)

def create_nepl_purchase_receipt(doc, method):
    if doc.company != "Cash":
        return  # Only process if PR belongs to 'Cash'

    # Get the Purchase Order linked to this Purchase Receipt
    purchase_order_cash = doc.items[0].purchase_order if doc.items else None
    if not purchase_order_cash:
        frappe.throw("No linked Purchase Order found for this Purchase Receipt.")

    # Fetch the linked Purchase Order for 'Nisus' from Company A's PO
    nepl_po = frappe.db.get_value("Purchase Order", purchase_order_cash, "custom_purchase_order_nepl")  # Assuming 'nisus_po' is the custom field
    if not nepl_po:
        frappe.throw("No linked Nisus Purchase Order found for this Purchase Receipt.")

    # Generate the Purchase Receipt for Nisus using the default method
    nepl_pr = make_purchase_receipt(nepl_po)
    nepl_pr.save()

    # doc.custom_purchase_receipt_nepl = nepl_pr.name
    frappe.db.set_value("Purchase Order", nepl_po, "custom_purchase_receipt_nepl", nepl_pr.name)
    # doc.save()
    nepl_pr.submit()
    frappe.msgprint(f"Purchase Receipt created for 'Nisus Energy Pvt Ltd' from {nepl_po}")
