import frappe
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder

def on_submit(doc, method):
    # Call the default on_submit logic
    # super(PurchaseOrder, doc).on_submit()

    # Add your custom logic here
    create_so_for_nepl(doc, method)
    pass

def create_so_for_nepl(doc, method):
    if doc.company == "Cash":
        customer_percent = doc.custom_distribution_percentage

        new_so_doc = frappe.copy_doc(doc)
        new_so_doc.company = 'Nisus Energy Pvt Ltd'

        warehouse = 'Stores - NEPL'
        if doc.set_warehouse:
            warehouse = f'{doc.set_warehouse.split("-")[0]}' + '- NEPL'

        new_so_doc.set_warehouse = warehouse
        new_so_doc.items = []

        for item in doc.items:
            new_item = item.as_dict().copy()
            new_item["name"] = None
            new_item["parent"] = None
            new_item["parentfield"] = "items"
            new_item["parenttype"] = "Sales Order"
            
            new_item["warehouse"] = warehouse
            new_item['cost_center'] = f'{item.cost_center.split("-")[0]}' + '- NEPL'

            if doc.custom_distribution_based_on == 'Quantity':
                new_item["qty"] = int(item.qty * (customer_percent / 100))
            elif doc.custom_distribution_based_on == 'Amount':
                new_item["rate"] = float(round(item.rate * (customer_percent / 100), 2))

            new_so_doc.append("items", new_item)

        if doc.taxes:
            new_so_doc.taxes = []
            for row in doc.taxes:
                new_tax = row.as_dict().copy()
                new_tax["name"] = None
                new_tax["parent"] = None
                if "-" in row.account_head:
                    new_tax["account_head"] = f'{row.account_head.split("-")[0]}' + '- NEPL'
                else:
                    frappe.throw(f"Invalid account head format: {row.account_head}")
                if "-" in row.cost_center:
                    print('change cost center')
                    new_tax["cost_center"] = f'{row.cost_center.split("-")[0]}' + '- NEPL'
                else:
                    frappe.throw(f"Invalid cost center format: {row.cost_center}")
                new_so_doc.append("taxes", new_tax)

        new_so_doc.save()
        doc.custom_sales_order_nepl = new_so_doc.name
        doc.save()
        new_so_doc.submit()
        frappe.msgprint(f"New SO created for 'Nisus Energy Pvt Ltd' as per Customer ({customer_percent}%)")