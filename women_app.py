from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)

# File to store product data
PRODUCTS_FILE = 'products.json'

# Initialize products file if it doesn't exist
if not os.path.exists(PRODUCTS_FILE):
    with open(PRODUCTS_FILE, 'w') as f:
        json.dump([], f)

def load_products():
    with open(PRODUCTS_FILE, 'r') as f:
        return json.load(f)

def save_products(products):
    with open(PRODUCTS_FILE, 'w') as f:
        json.dump(products, f)

@app.route('/')
def home():
    products = load_products()
    return '''
    <h1>Women Entrepreneurs Marketplace</h1>
    <h2>Add New Product</h2>
    <form action="/add_product" method="post">
        <p>Name: <input type="text" name="name" required></p>
        <p>Price: <input type="number" step="0.01" name="price" required></p>
        <p>Description: <textarea name="description" required></textarea></p>
        <p><input type="submit" value="Add Product"></p>
    </form>
    
    <h2>Available Products</h2>
    <div>
    ''' + '\n'.join([
        f'''
        <div style="border: 1px solid #ccc; margin: 10px; padding: 10px;">
            <h3>{product['name']}</h3>
            <p>Price: ${product['price']}</p>
            <p>{product['description']}</p>
            <form action="/place_order" method="post">
                <input type="hidden" name="product_id" value="{product['id']}">
                <input type="submit" value="Place Order">
            </form>
        </div>
        '''
        for product in products
    ]) + '''
    </div>
    '''

@app.route('/add_product', methods=['POST'])
def add_product():
    products = load_products()
    new_product = {
        'id': len(products) + 1,
        'name': request.form['name'],
        'price': float(request.form['price']),
        'description': request.form['description']
    }
    products.append(new_product)
    save_products(products)
    return redirect(url_for('home'))

@app.route('/place_order', methods=['POST'])
def place_order():
    product_id = int(request.form['product_id'])
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return f'''
        <h1>Order Placed Successfully</h1>
        <p>You have ordered: {product['name']}</p>
        <p>Total amount: ${product['price']}</p>
        <p><a href="/">Back to Home</a></p>
        '''
    return 'Product not found', 404

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)