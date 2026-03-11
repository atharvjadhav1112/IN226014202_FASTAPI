#Atharv Jadhav
#Author: The Cyber Alchemist


from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# Product List 
products = [
    {'id':1,'name':'Wireless Mouse','price':499,'category':'Electronics','in_stock':True},
    {'id':2,'name':'Notebook',      'price': 99,'category':'Stationery', 'in_stock':True},
    {'id':3,'name':'USB Hub',        'price':799,'category':'Electronics','in_stock':False},
    {'id':4,'name':'Pen Set',         'price': 49,'category':'Stationery', 'in_stock':True},
]

# Q1 – Show all products
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }

# Q2 – Filter by category
@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):
    filtered = [p for p in products if p["category"].lower() == category_name.lower()]
    if not filtered:
        return {"error": "No products found in this category"}
    return {"products": filtered}

# Q3 – Show only in-stock products
@app.get("/products/instock")
def get_instock_products():
    instock = [p for p in products if p["in_stock"]]
    return {"in_stock_products": instock, "count": len(instock)}

# Q4 – Store summary
@app.get("/store/summary")
def store_summary():
    total_products = len(products)
    instock = sum(1 for p in products if p["in_stock"])
    outstock = total_products - instock
    categories = list(set(p["category"] for p in products))
    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": instock,
        "out_of_stock": outstock,
        "categories": categories
    }

# Q5 – Search products
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    matches = [p for p in products if keyword.lower() in p["name"].lower()]
    if not matches:
        return {"message": "No products matched your search"}
    return {"matched_products": matches, "count": len(matches)}

# ⭐ Bonus – Deals endpoint
@app.get("/products/deals")
def product_deals():
    cheapest = min(products, key=lambda x: x["price"])
    expensive = max(products, key=lambda x: x["price"])
    return {"best_deal": cheapest, "premium_pick": expensive}

#ASSIGNMENT 2

# Q1 – Filter products by price and category
@app.get("/products/filter")
def filter_products(min_price: int = 0, max_price: int = 10000, category: Optional[str] = None):
    filtered = []

    for product in products:
        if product["price"] >= min_price and product["price"] <= max_price:
            if category:
                if product["category"].lower() == category.lower():
                    filtered.append(product)
            else:
                filtered.append(product)

    return {"filtered_products": filtered, "count": len(filtered)}

# Q2 – Get only name and price of a product
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}

#Q3 Accept Customer Feedback
feedback = []
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data)

    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
    }

# Q4 – Product summary dashboard
@app.get("/products/summary")
def product_summary():

    total_products = len(products)
    in_stock = sum(1 for p in products if p["in_stock"])
    out_stock = total_products - in_stock

    cheapest = min(products, key=lambda x: x["price"])
    expensive = max(products, key=lambda x: x["price"])

    categories = list(set(p["category"] for p in products))

    return {
        "total_products": total_products,
        "in_stock_count": in_stock,
        "out_of_stock_count": out_stock,
        "most_expensive": {"name": expensive["name"], "price": expensive["price"]},
        "cheapest": {"name": cheapest["name"], "price": cheapest["price"]},
        "categories": categories
    }
#Q5 Validate & Place a Bulk Order
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)


class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem]
@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        # find product
        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
            continue

        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

# Bonus – Create order (status pending)
# BONUS – Order Status Tracker
orders = []

@app.post("/orders")
def create_order(order: BulkOrder):

    order_id = len(orders) + 1

    order_items = []

    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)

        if product:
            order_items.append({
                "product_id": item.product_id,
                "product_name": product["name"],
                "quantity": item.quantity
            })
        else:
            order_items.append({
                "product_id": item.product_id,
                "product_name": "Unknown product",
                "quantity": item.quantity
            })

    new_order = {
        "order_id": order_id,
        "company_name": order.company_name,
        "contact_email": order.contact_email,
        "items": order_items,
        "status": "pending"
    }

    orders.append(new_order)

    return {
        "message": "Order placed successfully",
        "order": new_order
    }

# GET /orders/{order_id} → fetch a single order
@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            return order

    return {"error": "Order not found"}


# PATCH /orders/{order_id}/confirm → change status to confirmed
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"

            return {
                "message": "Order confirmed",
                "order": order
            }

    return {"error": "Order not found"}
