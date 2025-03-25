frappe.ui.form.on('Purchase Invoice', {
    onload_post_render: function (frm) {  // Ensures child tables are fully loaded
        console.log("onload_post_render triggered", frm.doc.items);
        setTimeout(() => {
            set_taxes(frm);
        }, 500);  // Slight delay to prevent UI override issues
    },
    validate: function (frm) {
        console.log("validate triggered", frm.doc.items);
        set_taxes(frm);
    }
});

function set_taxes(frm) {
    if (!frm.doc) {
        console.log("Form doc is undefined");
        return;
    }

    if (frm.doc.items && frm.doc.items.length > 0 && frm.doc.items[0].purchase_order) {
        let purchase_order_id = frm.doc.items[0].purchase_order;
        console.log("Fetching Purchase Order:", purchase_order_id);

        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Purchase Order",
                name: purchase_order_id
            },
            callback: function (response) {
                if (response.message) {
                    let po = response.message;
                    console.log("Fetched Purchase Order Data:", po);

                    if (po.taxes_and_charges) {
                        console.log("Setting Taxes and Charges:", po.taxes_and_charges);

                        frm.set_value("taxes_and_charges", po.taxes_and_charges);
                        frm.refresh_field("taxes_and_charges");

                        // Ensure UI updates correctly after setting value
                        setTimeout(() => {
                            frm.refresh();
                        }, 300);
                    }
                    // else if (po.taxes) {
                    //     frm.set_value("taxes", po.taxes);
                    //     frm.refresh_field("taxes");
                    // }
                    else {
                        //pass
                    }
                }
            }
        });
    }
}
