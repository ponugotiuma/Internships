from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional
from typing import List


app = FastAPI()

 

# ── Temporary data — acting as our database for now ──────────

products = [

    {'id': 1, 'name': 'Wireless Mouse', 'price': 499,  'category': 'Electronics', 'in_stock': True },

    {'id': 2, 'name': 'Notebook',       'price':  99,  'category': 'Stationery',  'in_stock': True },

    {'id': 3, 'name': 'USB Hub',         'price': 799, 'category': 'Electronics', 'in_stock': False},

    {'id': 4, 'name': 'Smart Watch', 'price': 3499, 'category':'Electronics', 'in_stock': False},

]

# ── Pydantic Model for creating products ─────────────────

class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool

# ── Endpoint 0 — Home ────────────────────────────────────────

@app.get('/')

def home():

    return {'message': 'Welcome to our E-commerce API'}

 

# ── Endpoint 1 — Return all products ──────────────────────────

@app.get('/products')

def get_all_products():

    return {'products': products, 'total': len(products)}

# ── Endpoint — Add New Product ──────────────────────────

@app.post('/products')
def add_product(product: Product):

    new_id = len(products) + 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {
        "message": "Product added successfully",
        "product": new_product
    }

@app.get('/products/filter')
def filter_products(
    category:  str  = Query(None, description='Electronics or Stationery'),
    min_price: int  = Query(None, description='Minimum price'),
    max_price: int  = Query(None, description='Maximum price'),
    in_stock:  bool = Query(None, description='True = in stock only')
):

    result = products

    if category:
        result = [p for p in result if p['category'] == category]

    if min_price:
        result = [p for p in result if p['price'] >= min_price]

    if max_price:
        result = [p for p in result if p['price'] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]

    return {'filtered_products': result, 'count': len(result)}

# ── Endpoint — Product Summary Dashboard ─────────────

@app.get('/products/summary')
def product_summary():

    total_products = len(products)

    in_stock_count = len([p for p in products if p['in_stock']])

    out_of_stock_count = total_products - in_stock_count

    cheapest = min(products, key=lambda x: x['price'])

    expensive = max(products, key=lambda x: x['price'])

    categories = list(set([p['category'] for p in products]))

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": {
            "name": expensive['name'],
            "price": expensive['price']
        },
        "cheapest": {
            "name": cheapest['name'],
            "price": cheapest['price']
        },
        "categories": categories
    }

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)


class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem]

@app.post('/orders/bulk')
def place_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = next((p for p in products if p['id'] == item.product_id), None)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product['in_stock']:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
            continue

        subtotal = product['price'] * item.quantity

        confirmed.append({
            "product": product['name'],
            "qty": item.quantity,
            "subtotal": subtotal
        })

        grand_total += subtotal

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

orders = []

class Order(BaseModel):
    product_id: int
    quantity: int

@app.post('/orders')
def create_order(order: Order):

    order_data = order.dict()
    order_data["id"] = len(orders) + 1
    order_data["status"] = "pending"

    orders.append(order_data)

    return order_data

@app.get('/orders/{order_id}')
def get_order(order_id: int):

    for order in orders:
        if order["id"] == order_id:
            return order

    return {"error": "Order not found"}

@app.patch('/orders/{order_id}/confirm')
def confirm_order(order_id: int):

    for order in orders:
        if order["id"] == order_id:
            order["status"] = "confirmed"
            return order

    return {"error": "Order not found"}

# ── Endpoint — Get Product Price Only ─────────────────

@app.get('/products/{product_id}/price')
def get_product_price(product_id: int):

    for product in products:
        if product['id'] == product_id:
            return {
                "name": product['name'],
                "price": product['price']
            }

    return {"error": "Product not found"}


@app.get('/products/audit') 
def product_audit(): 
    in_stock_list = [p for p in products if p['in_stock']] 
    out_stock_list = [p for p in products if not p['in_stock']] 
    stock_value = sum(p['price'] * 10 for p in in_stock_list) 
    priciest = max(products, key=lambda p: p['price']) 
    return { 'total_products': len(products), 'in_stock_count': len(in_stock_list), 'out_of_stock_names': [p['name'] for p in out_stock_list], 'total_stock_value': stock_value, 'most_expensive': {'name': priciest['name'], 'price': priciest['price']}, }


@app.put('/products/discount') 
def bulk_discount( category: 
    str = Query(..., description='Category to discount'), discount_percent: int = Query(..., ge=1, le=99, description='% off'), ): updated = [] for p in products: if p['category'] == category: p['price'] = int(p['price'] * (1 - discount_percent / 100)) updated.append(p) if not updated: return {'message': f'No products found in category: {category}'} return { 'message': f'{discount_percent}% discount applied to {category}', 'updated_count': len(updated), 'updated_products': updated, }


# ── Endpoint — Delete Product ──────────────────────────

@app.delete('/products/{product_id}')
def delete_product(product_id: int):

    for product in products:

        if product["id"] == product_id:
            products.remove(product)

            return {
                "message": "Product deleted successfully"
            }

    return {"error": "Product not found"}

# ── Endpoint — Update Product (Restock / Update Price) ─────────────────

@app.put('/products/{product_id}')
def update_product(
    product_id: int,
    price: Optional[int] = Query(None),
    in_stock: Optional[bool] = Query(None)
):

    for product in products:

        if product["id"] == product_id:

            if price is not None:
                product["price"] = price

            if in_stock is not None:
                product["in_stock"] = in_stock

            return {
                "message": "Product updated successfully",
                "product": product
            }

    return {"error": "Product not found"}


# ── Endpoint 2 — Return one product by its ID ──────────────────

@app.get('/products/{product_id}')

def get_product(product_id: int):

    for product in products:

        if product['id'] == product_id:

            return {'product': product}

    return {'error': 'Product not found'}

# ── Endpoint 3 — Filter by Category ──────────────────────────

@app.get('/products/category/{category_name}')
def get_products_by_category(category_name: str):

    result = [p for p in products if p['category'].lower() == category_name.lower()]

    if not result:
        return {"error": "No products found in this category"}

    return {"products": result, "count": len(result)
    
    }

# ── Endpoint 4 — In Stock Products ──────────────────────────

@app.get('/products/in_stock')
def get_instock_products():

    in_stock = [p for p in products if p['in_stock'] == True]

    return {
        "in_stock_products": in_stock,
        "count": len(in_stock)
    }


# ── Endpoint 5 — Store Summary ──────────────────────────

@app.get('/store/summary')
def store_summary():

    total_products = len(products)

    in_stock = len([p for p in products if p['in_stock'] == True])

    out_of_stock = total_products - in_stock

    categories = list(set([p['category'] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": in_stock,
        "out_of_stock": out_of_stock,
        "categories": categories
    }

# ── Endpoint 6 — Search Products ──────────────────────────

@app.get('/products/search/{keyword}')
def search_products(keyword: str):

    result = [p for p in products if keyword.lower() in p['name'].lower()]

    if not result:
        return {"message": "No products matched your search"}

    return {
        "matched_products": result,
        "total_matches": len(result)
    }



# ── Endpoint 7 — Product Deals ──────────────────────────

@app.get('/products/deals')
def product_deals():

    cheapest = min(products, key=lambda x: x['price'])

    expensive = max(products, key=lambda x: x['price'])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }

feedback = []

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)



@app.post('/feedback')
def submit_feedback(data: CustomerFeedback):

    feedback.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
    }


