frappe.ui.form.on("Item", {
    refresh: function (frm) {
        // Wait for the dashboard to load, then hide the Stock Levels section
        setTimeout(() => {
            $(".form-dashboard-section:contains('Stock Levels')").hide();
        }, 500);
    }
});