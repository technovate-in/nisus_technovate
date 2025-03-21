import frappe
from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder

def on_submit(doc, method):
    # Call the default on_submit logic
    # super(PurchaseOrder, doc).on_submit()

    # Add your custom logic here
    create_po_for_nepl(doc, method)

def create_po_for_nepl(doc, method):
    if doc.company == 'Cash':
        supplier_percent = doc.custom_distribution_percentage

        # Create a copy of the original document
        new_po_doc = frappe.copy_doc(doc)
        new_po_doc.company = 'Nisus Energy Pvt Ltd'

        # Determine warehouse
        warehouse = 'Stores - NEPL'
        if doc.set_warehouse:
            warehouse = f'{doc.set_warehouse.split("-")[0]}' + '- NEPL'
        new_po_doc.set_warehouse = warehouse

        # Clear the items list
        new_po_doc.items = []

        for item in doc.items:
            new_item = item.as_dict().copy()

            # Clear existing ID and parent fields
            new_item["name"] = None
            new_item["parent"] = None
            new_item["parentfield"] = "items"
            new_item["parenttype"] = "Purchase Order"

            new_item["warehouse"] = warehouse
            new_item["expense_account"] = 'Cost of Goods Sold - NEPL'
            new_item["cost_center"] = 'Main - NEPL'
            new_item["material_request"] = ''
            new_item["supplier_quotation"] = ''
            new_item["supplier_quotation_item"] = ''

            if doc.custom_distribution_based_on == 'Quantity':
                new_item["qty"] = int(item.qty * (supplier_percent / 100))

            elif doc.custom_distribution_based_on == 'Amount':
                new_item["rate"] = float(round(item.rate * (supplier_percent / 100), 2))
                print(new_item['rate'])
            
            new_po_doc.append("items", new_item)

        # Update tax account heads
        if new_po_doc.taxes:
            new_po_doc.taxes = []
            for row in doc.taxes:
                new_tax = row.as_dict().copy()
                new_tax["name"] = None
                new_tax["parent"] = None
                new_tax["account_head"] = f'{row.account_head.split("-")[0]}' + '- NEPL'
                new_po_doc.append("taxes", new_tax)

        # Save and submit the new PO
        new_po_doc.save()
        doc.custom_purchase_order_nepl = new_po_doc.name
        doc.save()
        new_po_doc.submit()

        frappe.msgprint(
            f"New PO created for 'Nisus Energy Pvt Ltd' as per Supplier ({supplier_percent}%)"
        )