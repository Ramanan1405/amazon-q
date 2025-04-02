# Login and Registration Pages Explanation

The application already has login and registration functionality implemented. Here's how it works:

## Login Page
- The login page is shown using the `show_login_screen()` method
- It contains username and password fields
- After successful login, users are directed to either buyer or seller dashboard based on their role

## Registration Page
- The registration page is shown using the `show_register_screen()` method
- It allows users to enter username, password, and select their role (buyer/seller)
- New users are saved to users.json

## Product Pages
1. For Buyers:
   - After login, buyers see the buyer dashboard
   - Products are displayed using `show_products_for_buyer()`
   - They can view and purchase products

2. For Sellers:
   - After login, sellers see the seller dashboard
   - They can add new products using `show_add_product_form()`
   - Product form includes fields for name, description, price, and image

The functionality you're looking for is already implemented in the application. To use it:
1. Run the application
2. Click "Register" if you're a new user or "Login" if you already have an account
3. After logging in, you'll automatically see the products page
4. For sellers, there's a separate "Add Product" button in their dashboard

The code is organized in a way that separates the login/register functionality from the product management features, making it easy to maintain and modify if needed.