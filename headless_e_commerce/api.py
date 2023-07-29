import frappe
import frappe.defaults
from frappe import _, throw
from erpnext.e_commerce.shopping_cart.cart import get_party, get_address_docs
from erpnext.utilities.product import get_web_item_qty_in_stock
from frappe.utils import cint


@frappe.whitelist()
def get_addresses():
	return get_address_docs()

@frappe.whitelist()
def get_profile():
	return get_party().as_dict()

@frappe.whitelist()
def place_order(items: list, billing_address: str = None, shipping_address: str = None, loyalty_points: int = 0):
	party = get_party()
	cart_settings = frappe.db.get_value(
		"E Commerce Settings", None, ["company", "allow_items_not_in_stock"], as_dict=1
	)

	if not (party.customer_primary_address):
		frappe.throw(_("Set Shipping Address or Billing Address"))
	
	if not cint(cart_settings.allow_items_not_in_stock):
		for item in items:
			item["warehouse"] = frappe.db.get_value(
				"Website Item", {"item_code": item.get("item_code")}, "website_warehouse"
			)
			is_stock_item = frappe.db.get_value("Item", item.get("item_code"), "is_stock_item")

			if is_stock_item:
				item_stock = get_web_item_qty_in_stock(item.get("item_code"), "website_warehouse")
				if not cint(item_stock.in_stock):
					frappe.throw(_("{0} Not in Stock").format(item.get("item_code")))
				if item.get("qty") > item_stock.stock_qty[0][0]:
					throw(_("Only {0} in Stock for item {1}").format(item_stock.stock_qty[0][0], item.get("item_code")))
	
	# make sure to pass only item_code & qty
	parsed_items = map(lambda item: {"item_code": item.get("item_code"), "qty": item.get("qty")}, items)
	sale_invoice = frappe.get_doc(
		{
			"doctype": "Sales Invoice",
			"customer": party.name,
			"items": parsed_items,
			"customer_address": billing_address,
			"shipping_address_name": shipping_address or billing_address,
			"redeem_loyalty_points": 1 if loyalty_points else 0,
			"loyalty_points": loyalty_points if loyalty_points else None,
		}
	).insert(ignore_permissions=True)

	return sale_invoice.as_dict()

@frappe.whitelist()
def add_address(address_line1: str, city: str, country: str, address_type="Billing", state=None, pincode=None,  phone=None, email_id=None, address_line2=None, is_shipping_address=0, is_primary_address=0):
	party = get_party()
	address = frappe.get_doc(
		{
			"doctype": "Address",
			"address_title": f"{address_line1} {city} {country}",
			"address_type": address_type,
			"address_line1": address_line1,
			"address_line2": address_line2,
			"city": city,
			"state": state,
			"country": country,
			"pincode": pincode,
			"phone": phone,
			"email_id": email_id,
			"is_primary_address": 1,
			"is_shipping_address": is_shipping_address,
			"disabled": 0,
			"is_your_company_address": 0,
			"links": [],
		}
	)
	address.insert(ignore_permissions=True)

	if(not party.customer_primary_address or is_primary_address):
		party.customer_primary_address = address.name
		party.primary_address = f"{address.address_line1}\n{address.city}\n{address.country}"
		party.save(ignore_permissions=True)

	return address.as_dict()

