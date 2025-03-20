frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        // Your code here
    },

    onload: function (frm) {
        set_taxes_and_charges(frm);
    },

    company: function (frm) {
        set_taxes_and_charges(frm);
    }
});

function set_taxes_and_charges(frm) {
    if (frm.is_new()) {
        let taxes_and_charges = 'Output GST In-state';
        let company_suffix = '';

        if (frm.doc.company === 'Cash') {
            company_suffix = '- C';
        } else if (frm.doc.company === 'Nisus Energy Pvt Ltd') {
            company_suffix = '- NEPL';
        }

        if (company_suffix) {
            frm.set_value('taxes_and_charges', taxes_and_charges + ' ' + company_suffix);
        }
    }
}