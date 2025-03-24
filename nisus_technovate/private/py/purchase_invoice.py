import frappe
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice
import erpnext.stock.doctype.purchase_receipt.purchase_receipt as purchase_receipt
import erpnext.buying.doctype.purchase_order.purchase_order as purchase_order

def on_submit(doc, method):
    create_nepl_purchase_invoice(doc, method)

# def create_nepl_purchase_invoice(doc, method):

#     if doc.company != "Cash":
#         return  # Only process if PR belongs to 'Cash'

#     # Get the Purchase Order and Purchase Receipt linked to this Purchase Invoice
#     purchase_order_cash = doc.items[0].purchase_order if doc.items else None
#     purchase_receipt_cash = doc.items[0].purchase_receipt if doc.items else None

#     if not (purchase_order_cash or purchase_receipt_cash):
#         frappe.throw("No linked Purchase Order/Receipt found for this Purchase Invoice.")

#     # Fetch the linked Purchase Receipt for 'Nisus' from Company A's PR
#     if purchase_receipt_cash:
#         purchase_receipt_nepl = frappe.db.get_value("Purchase Receipt", purchase_receipt_cash, "custom_purchase_receipt_nepl")
#         if not purchase_receipt_nepl:
#             frappe.throw("No linked Nisus Purchase Receipt found for this Purchase Invoice.")

#         # Generate the Purchase Invoice for Nisus from Purchase Receipt
#         purchase_invoice_nepl = purchase_receipt.make_purchase_invoice(purchase_receipt_nepl)
#         purchase_invoice_nepl.save()
#         doc.custom_purchase_invoice_nepl = purchase_invoice_nepl.name
#         doc.save()
#         purchase_invoice_nepl.submit()
#         frappe.msgprint(f"Purchase Invoice created for 'Nisus Energy Pvt Ltd' from Purchase Receipt {purchase_receipt_nepl}")

#     # If no Purchase Receipt is present, use the Purchase Order
#     elif purchase_order_cash:
#         purchase_order_nepl = frappe.db.get_value("Purchase Order", purchase_order_cash, "custom_purchase_order_nepl")
#         if not purchase_order_nepl:
#             frappe.throw("No linked Nisus Purchase Order found for this Purchase Invoice.")

#         # Generate the Purchase Invoice for Nisus from Purchase Order
#         purchase_invoice_nepl = purchase_order.make_purchase_invoice(purchase_order_nepl)
#         purchase_invoice_nepl.save()
#         doc.custom_purchase_invoice_nepl = purchase_invoice_nepl.name
#         doc.save()
#         purchase_invoice_nepl.submit()
#         frappe.msgprint(f"Purchase Invoice created for 'Nisus Energy Pvt Ltd' from Purchase Order {purchase_order_nepl}")

def create_nepl_purchase_invoice(doc, method):
    if doc.company != "Cash":
        return  # Only process if PR belongs to 'Cash'

    # Get the Purchase Order and Purchase Receipt linked to this Purchase Invoice
    purchase_order_cash = doc.items[0].purchase_order if doc.items else None
    purchase_receipt_cash = doc.items[0].purchase_receipt if doc.items else None

    if not (purchase_order_cash or purchase_receipt_cash):
        frappe.throw("No linked Purchase Order/Receipt found for this Purchase Invoice.")

    # Determine the source (Purchase Receipt or Purchase Order) and process accordingly
    source_type, source_name, make_invoice_method = None, None, None

    if purchase_receipt_cash:
        source_type = "Purchase Receipt"
        source_name = frappe.db.get_value("Purchase Receipt", purchase_receipt_cash, "custom_purchase_receipt_nepl")
        make_invoice_method = purchase_receipt.make_purchase_invoice
    elif purchase_order_cash:
        source_type = "Purchase Order"
        source_name = frappe.db.get_value("Purchase Order", purchase_order_cash, "custom_purchase_order_nepl")
        make_invoice_method = purchase_order.make_purchase_invoice

    if not source_name:
        frappe.throw(f"No linked Nisus {source_type} found for this Purchase Invoice.")

    # Generate the Purchase Invoice for Nisus
    purchase_invoice_nepl = make_invoice_method(source_name)
    purchase_invoice_nepl.save()
    # doc.custom_purchase_invoice_nepl = purchase_invoice_nepl.name
    frappe.db.set_value("Purchase Invoice", doc.name, "custom_purchase_invoice_nepl", purchase_invoice_nepl.name)
    # doc.save()
    purchase_invoice_nepl.submit()

    frappe.msgprint(f"Purchase Invoice created for 'Nisus Energy Pvt Ltd' from {source_type} {source_name}")