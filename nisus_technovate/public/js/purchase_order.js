frappe.ui.form.on("Purchase Order", {
    on_submit: async function (frm) {
        await update_supplier_distribution(frm);
        await update_item_prices(frm);
    }
});

// Function to update supplier distribution details
async function update_supplier_distribution(frm) {
    let supplierData;
    const response = await frappe.call({
        method: "frappe.client.get_value",
        args: {
            doctype: "Supplier",
            filters: { name: frm.doc.supplier },
            fieldname: ["custom_distribution_percentage", "custom_distribution_based_on"]
        }
    });

    supplierData = response.message || {};
    const isSamePercentage = supplierData.custom_distribution_percentage === frm.doc.custom_distribution_percentage;
    const isSameBasedOn = supplierData.custom_distribution_based_on === frm.doc.custom_distribution_based_on;

    let confirmed = true;
    if (!(isSamePercentage && isSameBasedOn)) {
        confirmed = await new Promise((resolve) => {
            frappe.confirm(
                `Do you want to update Supplier ${frm.doc.supplier} with new distribution details?\nPercentage: ${frm.doc.custom_distribution_percentage}\nBased On: ${frm.doc.custom_distribution_based_on}`,
                () => resolve(true),
                () => resolve(false)
            );
        });
    }

    if (confirmed && !(isSamePercentage && isSameBasedOn)) {
        await frappe.call({
            method: "frappe.client.set_value",
            args: {
                doctype: "Supplier",
                name: frm.doc.supplier,
                fieldname: {
                    "custom_distribution_percentage": frm.doc.custom_distribution_percentage,
                    "custom_distribution_based_on": frm.doc.custom_distribution_based_on
                }
            }
        });
    }
}

// Function to update item prices in Item Price doctype
async function update_item_prices(frm) {
    for (const row of frm.doc.items) {
        if (row.item_code && frm.doc.supplier) {
            try {
                const r = await new Promise((resolve) => {
                    frappe.call({
                        method: "frappe.client.get_value",
                        args: {
                            doctype: "Item Price",
                            filters: {
                                item_code: row.item_code,
                                price_list: "Standard Buying",
                                supplier: frm.doc.supplier
                            },
                            fieldname: ["price_list_rate", "name"]
                        },
                        callback: function (response) {
                            resolve(response);
                        }
                    });
                });

                if (r.message && r.message.price_list_rate) {
                    if (r.message.price_list_rate !== row.rate) {
                        await new Promise(resolve => setTimeout(resolve, 1500));

                        const userConfirmed = await new Promise((resolve) => {
                            frappe.confirm(
                                `Do you want to update rate for item ${row.item_code} from ${r.message.price_list_rate} to ${row.rate}?`,
                                () => resolve(true),
                                () => resolve(false)
                            );
                        });

                        if (userConfirmed) {
                            const updateResponse = await new Promise((resolve) => {
                                frappe.call({
                                    method: "frappe.client.set_value",
                                    args: {
                                        doctype: "Item Price",
                                        name: r.message.name,
                                        fieldname: { "price_list_rate": row.rate }
                                    },
                                    callback: function (response) {
                                        resolve(response);
                                    }
                                });
                            });

                            if (updateResponse.message) {
                                frappe.msgprint(`Rate for item ${row.item_code} updated successfully`);
                            }
                        } else {
                            frappe.msgprint({
                                message: `Rate for item ${row.item_code} not updated.`,
                                indicator: 'red'
                            });
                        }
                    } else {
                        frappe.model.set_value(row.doctype, row.name, "rate", r.message.price_list_rate);
                    }
                } else {
                    const insertResponse = await new Promise((resolve) => {
                        frappe.call({
                            method: "frappe.client.insert",
                            args: {
                                doc: {
                                    doctype: "Item Price",
                                    item_code: row.item_code,
                                    price_list: "Standard Buying",
                                    supplier: frm.doc.supplier,
                                    price_list_rate: row.rate
                                }
                            },
                            callback: function (response) {
                                resolve(response);
                            }
                        });
                    });

                    if (insertResponse.message) {
                        frappe.msgprint(`New Item Price for ${row.item_code} created successfully`);
                    }
                }
            } catch (error) {
                frappe.msgprint({
                    message: `Error processing item ${row.item_code}: ${error.message}`,
                    indicator: 'red'
                });

                frappe.log_error(`Error in Purchase Order on_submit for item ${row.item_code}: ${error.message}`);
            }
        }
    }
}

// Function to update price_list_rate in Purchase Order Item
frappe.ui.form.on('Purchase Order Item', {
    rate: function (frm, cdt, cdn) {
        let row = frappe.model.get_doc(cdt, cdn);

        if (row.rate && row.price_list_rate !== row.rate) {
            if (row.price_list_rate !== row.rate && row.previous_rate !== row.rate) {
                frappe.model.set_value(cdt, cdn, "price_list_rate", row.rate);
            }
        }
    }
});