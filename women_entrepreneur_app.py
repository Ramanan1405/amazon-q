import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import shutil
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class WomenEntrepreneurApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Women Entrepreneur Marketplace")
        self.root.geometry("800x600")
        
        # Load data from JSON files
        self.load_data()
        
        # Initialize session variables
        self.current_user = None
        self.cart_items = []
        
        # Create main frames
        self.login_frame = ttk.Frame(self.root)
        self.seller_frame = ttk.Frame(self.root)
        self.buyer_frame = ttk.Frame(self.root)
        
        # Initialize login screen
        self.show_login_screen()
        
    def load_data(self):
        # Load users data
        try:
            with open('users.json', 'r') as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = []

        # Load products data
        try:
            with open('products.json', 'r') as f:
                self.products = json.load(f)
        except FileNotFoundError:
            self.products = []

        # Load orders data
        try:
            with open('orders.json', 'r') as f:
                self.orders = json.load(f)
        except FileNotFoundError:
            self.orders = []

    def save_data(self):
        # Save users data
        with open('users.json', 'w') as f:
            json.dump(self.users, f, indent=2)

        # Save products data
        with open('products.json', 'w') as f:
            json.dump(self.products, f, indent=2)

        # Save orders data
        with open('orders.json', 'w') as f:
            json.dump(self.orders, f, indent=2)
    
    def show_login_screen(self):
        # Create new window for login
        login_window = tk.Toplevel(self.root)
        login_window.title("Login")
        login_window.geometry("300x400")
        
        # Create frame inside the window
        login_frame = ttk.Frame(login_window)
        login_frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Create login widgets
        ttk.Label(login_frame, text="Welcome to Women Entrepreneur App", font=('Helvetica', 12, 'bold')).pack(pady=10)
        
        ttk.Label(login_frame, text="Username:").pack(pady=5)
        username_entry = ttk.Entry(login_frame)
        username_entry.pack(pady=5)
        
        ttk.Label(login_frame, text="Password:").pack(pady=5)
        password_entry = ttk.Entry(login_frame, show="*")
        password_entry.pack(pady=5)
        
        def handle_login_and_close():
            if self.handle_login(username_entry.get(), password_entry.get()):
                login_window.destroy()
        
        ttk.Button(login_frame, text="Login", 
                   command=handle_login_and_close).pack(pady=10)
        ttk.Button(login_frame, text="Register", 
                   command=lambda: [login_window.destroy(), self.show_register_screen()]).pack(pady=5)
        
        # Make this window modal
        login_window.transient(self.root)
        login_window.grab_set()
        self.root.wait_window(login_window)
    
    def show_register_screen(self):
        # Clear login frame
        for widget in self.login_frame.winfo_children():
            widget.destroy()
        
        # Create registration widgets
        ttk.Label(self.login_frame, text="Register New Account").pack(pady=10)
        
        ttk.Label(self.login_frame, text="Username:").pack(pady=5)
        username_entry = ttk.Entry(self.login_frame)
        username_entry.pack(pady=5)
        
        ttk.Label(self.login_frame, text="Password:").pack(pady=5)
        password_entry = ttk.Entry(self.login_frame, show="*")
        password_entry.pack(pady=5)
        
        role_var = tk.StringVar(value="buyer")
        ttk.Radiobutton(self.login_frame, text="Buyer", variable=role_var, 
                        value="buyer").pack(pady=5)
        ttk.Radiobutton(self.login_frame, text="Seller", variable=role_var, 
                        value="seller").pack(pady=5)
        
        ttk.Button(self.login_frame, text="Register", 
                   command=lambda: self.handle_register(
                       username_entry.get(), 
                       password_entry.get(), 
                       role_var.get()
                   )).pack(pady=10)
        ttk.Button(self.login_frame, text="Back to Login", 
                   command=self.show_login_screen).pack(pady=5)
    
    def handle_login(self, username, password):
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        user = next((u for u in self.users if u['username'] == username and u['password'] == password), None)
        
        if user:
            self.current_user = user
            if user['role'] == 'seller':
                self.show_seller_dashboard()
            else:
                self.show_buyer_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")
    
    def handle_register(self, username, password, role):
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        try:
            if any(u['username'] == username for u in self.users):
                messagebox.showerror("Error", "Username already exists")
                return
                
            user = {
                'id': len(self.users) + 1,
                'username': username,
                'password': password,
                'role': role
            }
            self.users.append(user)
            self.save_data()
            messagebox.showinfo("Success", "Registration successful!")
            self.show_login_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {str(e)}")
    
    def show_seller_dashboard(self):
        self.login_frame.pack_forget()
        self.buyer_frame.pack_forget()
        self.seller_frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Clear previous widgets
        for widget in self.seller_frame.winfo_children():
            widget.destroy()
        
        # Create seller dashboard widgets
        ttk.Label(self.seller_frame, 
                 text=f"Welcome, {self.current_user['username']}!").pack(pady=10)
        
        # Add product button
        ttk.Button(self.seller_frame, text="Add New Product", 
                  command=self.show_add_product_form).pack(pady=5)
        
        # Show seller's products
        self.show_seller_products()
        
        # Logout button
        ttk.Button(self.seller_frame, text="Logout", 
                  command=self.logout).pack(pady=5)
    
    def show_add_product_form(self):
        # Create new window for adding product
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Product")
        add_window.geometry("400x500")
        
        ttk.Label(add_window, text="Product Name:").pack(pady=5)
        name_entry = ttk.Entry(add_window)
        name_entry.pack(pady=5)
        
        ttk.Label(add_window, text="Description:").pack(pady=5)
        desc_entry = ttk.Text(add_window, height=4)
        desc_entry.pack(pady=5)
        
        ttk.Label(add_window, text="Price:").pack(pady=5)
        price_entry = ttk.Entry(add_window)
        price_entry.pack(pady=5)
        
        ttk.Label(add_window, text="Product Image:").pack(pady=5)
        image_path = tk.StringVar()
        
        def choose_image():
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if file_path:
                image_path.set(file_path)
        
        ttk.Button(add_window, text="Choose Image", command=choose_image).pack(pady=5)
        
        def add_product():
            name = name_entry.get()
            description = desc_entry.get("1.0", tk.END).strip()
            try:
                price = float(price_entry.get())
                
                # Copy image to product_images directory
                image_src = image_path.get()
                if image_src:
                    # Generate unique filename
                    _, ext = os.path.splitext(image_src)
                    image_filename = f"product_{len(self.products) + 1}{ext}"
                    image_dest = os.path.join('product_images', image_filename)
                    shutil.copy2(image_src, image_dest)
                else:
                    image_filename = "default.png"  # You should provide a default image
                
                product = {
                    'id': len(self.products) + 1,
                    'seller_id': self.current_user['id'],
                    'name': name,
                    'description': description,
                    'price': price,
                    'image': image_filename
                }
                
                self.products.append(product)
                self.save_data()
                
                messagebox.showinfo("Success", "Product added successfully!")
                add_window.destroy()
                self.show_seller_dashboard()
            except ValueError:
                messagebox.showerror("Error", "Invalid price format")
        
        ttk.Button(add_window, text="Add Product", 
                  command=add_product).pack(pady=10)
    
    

    def show_seller_products(self):
        # Create frame for products 
        products_frame = ttk.Frame(self.seller_frame)
        products_frame.pack(fill='both', expand=True, pady=10)
        
        # Get seller's products
        products = [p for p in self.products if p['seller_id'] == self.current_user['id']]
        
        # Display products in a table
        columns = ('id', 'name', 'description', 'price', 'actions')
        tree = ttk.Treeview(products_frame, columns=columns, show='headings')
        
        # Define column headings
        tree.heading('id', text='ID')
        tree.heading('name', text='Name') 
        tree.heading('description', text='Description')
        tree.heading('price', text='Price')
        tree.heading('actions', text='Actions')
        
        # Add data to the table
        for product in products:
            tree.insert('', tk.END, values=(*product[:-1], 'Edit/Delete'))
        
        tree.pack(fill='both', expand=True)
        
        # Bind double-click event for editing
        tree.bind('<Double-1>', lambda e: self.edit_product(tree.selection()))
    
    def edit_product(self, selection):
        if not selection:
            return
        
        item = selection[0]
        product_id = int(self.tree.item(item)['values'][0])
        
        # Get product details
        product = next((p for p in self.products if p['id'] == product_id), None)
        if not product:
            return
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Product")
        edit_window.geometry("400x500")
        
        ttk.Label(edit_window, text="Product Name:").pack(pady=5)
        name_entry = ttk.Entry(edit_window)
        name_entry.insert(0, product['name'])
        name_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Description:").pack(pady=5)
        desc_entry = ttk.Text(edit_window, height=4)
        desc_entry.insert("1.0", product['description'])
        desc_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Price:").pack(pady=5)
        price_entry = ttk.Entry(edit_window)
        price_entry.insert(0, str(product['price']))
        price_entry.pack(pady=5)
        
        def update_product():
            try:
                product['name'] = name_entry.get()
                product['description'] = desc_entry.get("1.0", tk.END).strip()
                product['price'] = float(price_entry.get())
                
                self.save_data()
                messagebox.showinfo("Success", "Product updated successfully!")
                edit_window.destroy()
                self.show_seller_dashboard()
            except ValueError:
                messagebox.showerror("Error", "Invalid price format")
        
        def delete_product():
            if messagebox.askyesno("Confirm Delete", 
                                 "Are you sure you want to delete this product?"):
                self.products.remove(product)
                self.save_data()
                messagebox.showinfo("Success", "Product deleted successfully!")
                edit_window.destroy()
                self.show_seller_dashboard()
        
        ttk.Button(edit_window, text="Update Product", 
                  command=update_product).pack(pady=10)
        ttk.Button(edit_window, text="Delete Product", 
                  command=delete_product).pack(pady=5)
    
    def show_buyer_dashboard(self):
        self.login_frame.pack_forget()
        self.seller_frame.pack_forget()
        self.buyer_frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Clear previous widgets
        for widget in self.buyer_frame.winfo_children():
            widget.destroy()
        
        # Create buyer dashboard widgets
        ttk.Label(self.buyer_frame, 
                 text=f"Welcome, {self.current_user['username']}!").pack(pady=10)
        
        # Show all products
        self.show_products_for_buyer()
        
        # Shopping cart button
        ttk.Button(self.buyer_frame, text="View Cart", 
                  command=self.show_cart).pack(pady=5)
        
        # Logout button
        ttk.Button(self.buyer_frame, text="Logout", 
                  command=self.logout).pack(pady=5)
    
    def show_products_for_buyer(self):
        # Create frame for products
        products_frame = ttk.Frame(self.buyer_frame)
        products_frame.pack(fill='both', expand=True, pady=10)
        
        # Create product cards
        for product in self.products:
            # Create an attractive product card with border and padding
            card = ttk.Frame(products_frame, relief='solid', borderwidth=2)
            card.pack(fill='x', pady=10, padx=20)
            
            # Load and display product image
            image_path = os.path.join('product_images', product['image'])
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize((150, 150))  # Resize image to fit card
                photo = ImageTk.PhotoImage(image)
                image_label = ttk.Label(card, image=photo)
                image_label.image = photo  # Keep a reference
                image_label.pack(pady=5)
            
            # Improved product information display with better styling
            ttk.Label(card, text=product['name'], font=('Arial', 14, 'bold')).pack(pady=(5,2))
            ttk.Label(card, text=product['description'], font=('Arial', 10, 'italic')).pack(pady=2)
            ttk.Label(card, text=f"Price: ₹{product['price']:.2f}", font=('Arial', 12, 'bold'), foreground='#2E8B57').pack(pady=2)
            
            # Styled Add to Cart button
            add_cart_btn = ttk.Button(card, text="🛒 Add to Cart", 
                      command=lambda p=product: self.add_to_cart(p))
            add_cart_btn.pack(pady=10, ipadx=10, ipady=5)
    
    def add_to_cart(self, product):
        self.cart_items.append({
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'quantity': 1
        })
        messagebox.showinfo("Success", "Item added to cart!")
    
    def show_cart(self):
        # Create new window for cart
        cart_window = tk.Toplevel(self.root)
        cart_window.title("Shopping Cart")
        cart_window.geometry("600x400")
        
        # Create scrollable frame for cart items
        cart_frame = ttk.Frame(cart_window)
        cart_frame.pack(fill='both', expand=True, pady=10)
        
        # Show cart items
        total = 0
        for item in self.cart_items:
            item_frame = ttk.Frame(cart_frame)
            item_frame.pack(fill='x', pady=5, padx=10)
            
            # Load and display product image
            image_path = os.path.join('product_images', item['image'])
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize((50, 50))  # Smaller size for cart
                photo = ImageTk.PhotoImage(image)
                image_label = ttk.Label(item_frame, image=photo)
                image_label.image = photo  # Keep a reference
                image_label.pack(side='left', padx=5)
            
            ttk.Label(item_frame, text=item['name']).pack(side='left')
            ttk.Label(item_frame, 
                     text=f"${item['price']:.2f} x {item['quantity']}").pack(side='right')
            
            total += item['price'] * item['quantity']
        
        ttk.Label(cart_window, 
                 text=f"Total: ${total:.2f}").pack(pady=10)
        
        def checkout():
            if not self.cart_items:
                messagebox.showwarning("Cart Empty", "Your cart is empty!")
                return
            
            # Create order
            order = {
                'id': len(self.orders) + 1,
                'buyer_id': self.current_user['id'],
                'total_amount': total,
                'items': self.cart_items.copy(),
                'date': datetime.now().isoformat()
            }
            
            self.orders.append(order)
            self.save_data()
            self.cart_items = []
            messagebox.showinfo("Success", "Order placed successfully!")
            cart_window.destroy()
        
        ttk.Button(cart_window, text="Checkout", 
                  command=checkout).pack(pady=10)
    
    def logout(self):
        self.current_user = None
        self.cart_items = []
        self.show_login_screen()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = WomenEntrepreneurApp()
    app.run()