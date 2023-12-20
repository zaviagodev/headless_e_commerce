import frappe

def after_install():
    frappe.get_single("Webshop Settings").update({
        "products_per_page": 100,
        "show_price": 1,
        "show_stock_availability": 1,
        "allow_items_not_in_stock": 1,
        "enabled": 1,

    }).save()