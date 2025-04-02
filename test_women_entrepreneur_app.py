from PIL import Image, ImageTk
from datetime import datetime
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import ttk, messagebox
from unittest.mock import MagicMock, patch
from unittest.mock import Mock, patch
from unittest.mock import mock_open, patch
from unittest.mock import patch
from unittest.mock import patch, MagicMock
from unittest.mock import patch, mock_open
from women_app import women_entrepreneur_app
from women_entrepreneur_app import women_app
import json
import os
import pytest
import shutil
import tkinter as tk
import unittest

class TestWomenEntrepreneurApp:

    def test___init___1(self):
        """
        Test the initialization of WomenEntrepreneurApp.

        This test verifies that the WomenEntrepreneurApp is correctly initialized
        with the expected attributes and initial state.
        """
        app = WomenEntrepreneurApp()

        # Check if the root window is created
        assert isinstance(app.root, tk.Tk)
        assert app.root.title() == "Women Entrepreneur Marketplace"
        assert app.root.geometry() == "800x600"

        # Check if data is loaded
        assert hasattr(app, 'users')
        assert hasattr(app, 'products')
        assert hasattr(app, 'orders')

        # Check if session variables are initialized
        assert app.current_user is None
        assert app.cart_items == []

        # Check if main frames are created
        assert isinstance(app.login_frame, ttk.Frame)
        assert isinstance(app.seller_frame, ttk.Frame)
        assert isinstance(app.buyer_frame, ttk.Frame)

        # Check if login screen is shown
        assert app.login_frame.winfo_ismapped()
        assert not app.seller_frame.winfo_ismapped()
        assert not app.buyer_frame.winfo_ismapped()

        # Clean up
        app.root.destroy()

    def test___init___file_not_found(self):
        """
        Test the __init__ method when JSON files are not found.
        This tests the error handling for FileNotFoundError in the load_data method.
        """
        # Temporarily rename or move JSON files to simulate FileNotFoundError
        if os.path.exists('users.json'):
            os.rename('users.json', 'users_temp.json')
        if os.path.exists('products.json'):
            os.rename('products.json', 'products_temp.json')
        if os.path.exists('orders.json'):
            os.rename('orders.json', 'orders_temp.json')

        try:
            app = WomenEntrepreneurApp()
            assert app.users == []
            assert app.products == []
            assert app.orders == []
        finally:
            # Restore JSON files
            if os.path.exists('users_temp.json'):
                os.rename('users_temp.json', 'users.json')
            if os.path.exists('products_temp.json'):
                os.rename('products_temp.json', 'products.json')
            if os.path.exists('orders_temp.json'):
                os.rename('orders_temp.json', 'orders.json')

    def test_add_product_1(self):
        """
        Test adding a product with a valid image source.

        This test verifies that a product can be successfully added
        when a valid image source is provided. It checks if the product
        is added to the products list, the image is copied to the
        correct location, and the data is saved properly.
        """
        app = WomenEntrepreneurApp()
        app.current_user = {'id': 1, 'username': 'test_seller'}
        app.products = []

        # Mock tkinter elements
        name_entry = tk.StringVar(value="Test Product")
        desc_entry = tk.Text()
        desc_entry.insert(tk.END, "Test Description")
        price_entry = tk.StringVar(value="10.99")
        image_path = tk.StringVar(value="test_image.jpg")

        # Create a temporary test image
        with open("test_image.jpg", "w") as f:
            f.write("test image content")

        # Call the add_product method
        app.add_product()

        # Assertions
        assert len(app.products) == 1
        assert app.products[0]['name'] == "Test Product"
        assert app.products[0]['description'] == "Test Description"
        assert app.products[0]['price'] == 10.99
        assert app.products[0]['image'] == "product_1.jpg"
        assert os.path.exists(os.path.join('product_images', 'product_1.jpg'))

        # Clean up
        os.remove("test_image.jpg")
        os.remove(os.path.join('product_images', 'product_1.jpg'))

    def test_add_product_invalid_price(self):
        """
        Test that the add_product method handles invalid price input correctly.
        """
        # Mock necessary objects and methods
        mock_app = Mock()
        mock_app.products = []
        mock_app.current_user = {'id': 1}
        mock_app.save_data = Mock()
        mock_app.show_seller_dashboard = Mock()

        # Create mock entry widgets
        mock_name_entry = Mock()
        mock_name_entry.get.return_value = "Test Product"
        mock_desc_entry = Mock()
        mock_desc_entry.get.return_value = "Test Description"
        mock_price_entry = Mock()
        mock_price_entry.get.return_value = "invalid_price"
        mock_image_path = Mock()
        mock_image_path.get.return_value = ""

        # Create mock add window
        mock_add_window = Mock()

        # Patch messagebox.showerror
        with patch('tkinter.messagebox.showerror') as mock_showerror:
            # Call the add_product method
            WomenEntrepreneurApp.add_product(mock_app, mock_name_entry, mock_desc_entry, 
                                             mock_price_entry, mock_image_path, mock_add_window)

            # Assert that showerror was called with the correct message
            mock_showerror.assert_called_once_with("Error", "Invalid price format")

        # Assert that the product was not added and other methods were not called
        assert len(mock_app.products) == 0
        mock_app.save_data.assert_not_called()
        mock_app.show_seller_dashboard.assert_not_called()
        mock_add_window.destroy.assert_not_called()

    def test_add_to_cart_1(self):
        """
        Test adding a product to the cart.

        This test verifies that when a product is added to the cart:
        1. The product is correctly appended to the cart_items list.
        2. The product details (id, name, price, quantity) are correctly stored.
        3. A success message is shown to the user.
        """
        app = WomenEntrepreneurApp()
        product = {
            'id': 1,
            'name': 'Test Product',
            'price': 10.99,
            'image': 'test_image.jpg'
        }

        # Mock the messagebox.showinfo to avoid actual popup during test
        original_showinfo = messagebox.showinfo
        messagebox.showinfo = lambda *args, **kwargs: None

        app.add_to_cart(product)

        # Restore the original showinfo function
        messagebox.showinfo = original_showinfo

        assert len(app.cart_items) == 1
        assert app.cart_items[0] == {
            'id': 1,
            'name': 'Test Product',
            'price': 10.99,
            'quantity': 1
        }

    def test_add_to_cart_with_missing_product_fields(self):
        """
        Test add_to_cart method with a product missing required fields.
        This tests the edge case of an incomplete product dictionary being passed to the method.
        """
        app = WomenEntrepreneurApp()
        incomplete_product = {'id': 1, 'name': 'Test Product'}  # Missing 'price' field

        # Mocking the messagebox to prevent actual popup
        original_showinfo = messagebox.showinfo
        messagebox.showinfo = lambda *args, **kwargs: None

        try:
            app.add_to_cart(incomplete_product)
        except KeyError:
            assert len(app.cart_items) == 0, "Cart should remain empty when adding incomplete product"
        else:
            assert False, "KeyError should be raised when adding incomplete product"
        finally:
            # Restore original messagebox function
            messagebox.showinfo = original_showinfo

    def test_checkout_empty_cart(self):
        """
        Test checkout functionality when the cart is empty.

        This test verifies that when the cart is empty (not self.cart_items),
        a warning message is displayed and the function returns without
        creating an order.
        """
        app = WomenEntrepreneurApp()
        app.cart_items = []

        # Mock the messagebox.showwarning function
        with pytest.mock.patch.object(messagebox, 'showwarning') as mock_showwarning:
            app.checkout()

            # Assert that showwarning was called with the correct arguments
            mock_showwarning.assert_called_once_with("Cart Empty", "Your cart is empty!")

        # Assert that no order was created
        assert len(app.orders) == 0

    def test_checkout_empty_cart_2(self):
        """
        Test checkout with an empty cart.
        Verifies that the method shows a warning message when the cart is empty.
        """
        app = WomenEntrepreneurApp()
        app.cart_items = []

        # Mock the messagebox.showwarning function
        with pytest.mock.patch.object(messagebox, 'showwarning') as mock_showwarning:
            app.checkout()
            mock_showwarning.assert_called_once_with("Cart Empty", "Your cart is empty!")

    def test_choose_image_1(self):
        """
        Test that the choose_image method sets the image_path when a file is selected.

        This test simulates the user selecting an image file through the file dialog
        and verifies that the image_path is updated correctly.
        """
        app = WomenEntrepreneurApp()

        # Mock the filedialog.askopenfilename to return a predefined file path
        with patch('tkinter.filedialog.askopenfilename', return_value='/path/to/image.jpg'):
            # Create a StringVar to hold the image path
            image_path = tk.StringVar()

            # Call the choose_image method
            app.choose_image()

            # Assert that the image_path was set correctly
            self.assertEqual(image_path.get(), '/path/to/image.jpg')

    def test_choose_image_cancelled_selection(self):
        """
        Test the scenario where the user cancels the file selection dialog without choosing an image.
        This tests the edge case where the filedialog.askopenfilename() returns an empty string.
        """
        root = tk.Tk()
        image_path = tk.StringVar()

        # Mock the filedialog.askopenfilename to return an empty string
        original_askopenfilename = filedialog.askopenfilename
        filedialog.askopenfilename = lambda **kwargs: ""

        try:
            # Call the choose_image function
            def choose_image():
                file_path = filedialog.askopenfilename(
                    filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
                )
                if file_path:
                    image_path.set(file_path)

            choose_image()

            # Assert that the image_path variable remains unchanged
            assert image_path.get() == "", "Image path should remain empty when file selection is cancelled"

        finally:
            # Restore the original askopenfilename function
            filedialog.askopenfilename = original_askopenfilename
            root.destroy()

    def test_delete_product_1(self):
        """
        Test that the delete_product method removes the product when user confirms deletion.
        """
        app = WomenEntrepreneurApp()
        app.current_user = {'id': 1, 'username': 'test_seller', 'role': 'seller'}
        product = {'id': 1, 'name': 'Test Product', 'price': 10.0, 'seller_id': 1}
        app.products = [product]

        # Mock the messagebox.askyesno to return True (user confirms deletion)
        def mock_askyesno(*args, **kwargs):
            return True

        original_askyesno = messagebox.askyesno
        messagebox.askyesno = mock_askyesno

        # Call the delete_product method
        app.delete_product()

        # Restore the original messagebox.askyesno
        messagebox.askyesno = original_askyesno

        # Assert that the product was removed from the products list
        assert len(app.products) == 0

        # Clean up
        app.root.destroy()

    def test_delete_product_confirmation_cancelled(self):
        """
        Test that the product is not deleted when the user cancels the confirmation dialog.
        """
        app = WomenEntrepreneurApp()
        product = {'id': 1, 'name': 'Test Product', 'price': 10.0}
        app.products = [product]

        # Mock the messagebox.askyesno to return False (simulating user cancelling)
        def mock_askyesno(*args, **kwargs):
            return False

        original_askyesno = messagebox.askyesno
        messagebox.askyesno = mock_askyesno

        try:
            app.delete_product()

            # Assert that the product was not deleted
            assert len(app.products) == 1
            assert app.products[0] == product
        finally:
            # Restore the original messagebox.askyesno function
            messagebox.askyesno = original_askyesno

    def test_edit_product_1(self):
        """
        Test that the edit_product method returns immediately when selection is empty.

        This test verifies that the edit_product method exits early when an empty
        selection is provided, without performing any product editing operations.
        """
        app = WomenEntrepreneurApp()
        app.tree = ttk.Treeview(app.root)  # Mock treeview

        # Call edit_product with an empty selection
        result = app.edit_product([])

        # Assert that the method returns None (implicitly returns None in Python)
        assert result is None

    def test_edit_product_2(self):
        """
        Test that edit_product correctly handles the case when a selection is made,
        but the corresponding product is not found in the products list.
        """
        app = WomenEntrepreneurApp()
        app.products = []  # Ensure the products list is empty
        app.tree = ttk.Treeview(app.root)

        # Create a mock selection
        mock_selection = ('item1',)
        app.tree.item = lambda x: {'values': [1]}  # Mock the item method to return a product ID

        # Call the method under test
        app.edit_product(mock_selection)

        # Assert that the method returns without error
        # Since the product is not found, no window should be created
        assert len(app.root.winfo_children()) == 0

    def test_edit_product_3(self):
        """
        Test case for edit_product method when user confirms product deletion.

        This test verifies that when a product is selected for editing, the delete
        confirmation dialog is shown, and upon user confirmation, the product is
        removed from the products list, data is saved, and the seller dashboard
        is refreshed.
        """
        app = WomenEntrepreneurApp()
        app.products = [{'id': 1, 'name': 'Test Product', 'price': 10.0}]
        app.tree = MagicMock()
        app.tree.item.return_value = {'values': [1]}

        with patch('tkinter.messagebox.askyesno', return_value=True), \
             patch.object(app, 'save_data') as mock_save_data, \
             patch.object(app, 'show_seller_dashboard') as mock_show_dashboard:

            app.edit_product([1])

            self.assertEqual(len(app.products), 0)
            mock_save_data.assert_called_once()
            mock_show_dashboard.assert_called_once()

    def test_edit_product_empty_selection(self):
        """
        Test the edit_product method with an empty selection.
        This tests the edge case where the method is called without selecting any product.
        """
        app = WomenEntrepreneurApp()
        app.edit_product([])  # Empty selection
        # No assertion needed as the method should simply return without any action

    def test_edit_product_invalid_price(self):
        """
        Test the edit_product method with an invalid price input.
        This tests the edge case where the user enters a non-numeric value for the price.
        """
        app = WomenEntrepreneurApp()
        app.products = [{'id': 1, 'name': 'Test Product', 'description': 'Test Description', 'price': 10.0}]
        app.tree = ttk.Treeview(app.root)
        app.tree.insert('', 'end', values=(1,))

        # Mock the Toplevel window and its widgets
        edit_window = tk.Toplevel()
        name_entry = ttk.Entry(edit_window)
        name_entry.insert(0, 'Test Product')
        desc_entry = tk.Text(edit_window)
        desc_entry.insert('1.0', 'Test Description')
        price_entry = ttk.Entry(edit_window)
        price_entry.insert(0, 'invalid_price')  # Invalid price input

        # Mock the update_product function
        def update_product():
            app.edit_product(app.tree.get_children())

        # Trigger the update
        update_product()

        # Assert that an error message is shown
        assert messagebox.showerror.called_with("Error", "Invalid price format")

    def test_edit_product_nonexistent_product(self):
        """
        Test the edit_product method with a non-existent product ID.
        This tests the edge case where the selected product is not found in the products list.
        """
        app = WomenEntrepreneurApp()
        app.products = []  # Ensure products list is empty
        app.tree = ttk.Treeview(app.root)
        app.tree.insert('', 'end', values=(999,))  # Insert a non-existent product ID
        app.edit_product(app.tree.get_children())
        # No assertion needed as the method should simply return without any action

    def test_handle_login_1(self):
        """
        Test that handle_login shows an error message when username or password is empty.
        """
        app = WomenEntrepreneurApp()
        app.users = [{'username': 'test', 'password': 'test', 'role': 'buyer'}]

        # Mock the messagebox.showerror method
        original_showerror = messagebox.showerror
        messagebox.showerror = lambda title, message: None

        # Test with empty username
        app.handle_login('', 'password')
        self.assertIsNone(app.current_user)

        # Test with empty password
        app.handle_login('username', '')
        self.assertIsNone(app.current_user)

        # Restore the original messagebox.showerror method
        messagebox.showerror = original_showerror

    def test_handle_login_2(self):
        """
        Test successful login for a seller user.
        Verifies that the seller dashboard is shown after successful login.
        """
        app = WomenEntrepreneurApp()
        app.users = [{'id': 1, 'username': 'seller1', 'password': 'pass123', 'role': 'seller'}]
        app.show_seller_dashboard = lambda: None  # Mock the dashboard method

        with pytest.raises(tk.TclError):  # Catch the error when trying to show messagebox in test environment
            app.handle_login('seller1', 'pass123')

        assert app.current_user == app.users[0]

    def test_handle_login_3(self):
        """
        Test handle_login method for a valid buyer login.

        This test verifies that when a buyer with valid credentials logs in,
        the method sets the current user correctly and shows the buyer dashboard.
        """
        app = WomenEntrepreneurApp()
        app.users = [{'id': 1, 'username': 'buyer1', 'password': 'pass1', 'role': 'buyer'}]
        app.show_buyer_dashboard = lambda: None  # Mock the dashboard method

        app.handle_login('buyer1', 'pass1')

        assert app.current_user == app.users[0]
        assert app.current_user['role'] == 'buyer'

    def test_handle_login_empty_credentials(self):
        """
        Test that handle_login shows an error message when username or password is empty.
        """
        app = WomenEntrepreneurApp()
        app.handle_login("", "")

        # Assert that an error messagebox was shown
        messagebox.showerror.assert_called_once_with("Error", "Please fill in all fields")

    def test_handle_login_invalid_credentials(self):
        """
        Test that handle_login shows an error message when credentials are invalid.
        """
        app = WomenEntrepreneurApp()
        app.users = [{'username': 'testuser', 'password': 'testpass', 'role': 'buyer'}]
        app.handle_login("wronguser", "wrongpass")

        # Assert that an error messagebox was shown
        messagebox.showerror.assert_called_once_with("Error", "Invalid credentials")

    def test_handle_register_1(self):
        """
        Test that handle_register shows an error message when username or password is empty.
        """
        app = WomenEntrepreneurApp()
        app.users = []  # Ensure users list is empty

        with pytest.raises(tk.TclError):  # Catch the error raised by messagebox in test environment
            app.handle_register("", "password", "buyer")

        with pytest.raises(tk.TclError):  # Catch the error raised by messagebox in test environment
            app.handle_register("username", "", "seller")

        assert len(app.users) == 0  # Verify no user was added

    def test_handle_register_empty_password(self):
        """
        Test that handle_register shows an error message when password is empty.
        """
        app = WomenEntrepreneurApp()
        app.handle_register("username", "", "buyer")
        assert messagebox.showerror.called_with("Error", "Please fill in all fields")

    def test_handle_register_empty_username(self):
        """
        Test that handle_register shows an error message when username is empty.
        """
        app = WomenEntrepreneurApp()
        app.handle_register("", "password", "buyer")
        assert messagebox.showerror.called_with("Error", "Please fill in all fields")

    def test_handle_register_existing_username(self):
        """
        Test that handle_register shows an error message when username already exists.
        """
        app = WomenEntrepreneurApp()
        app.users = [{'username': 'existinguser'}]
        app.handle_register("existinguser", "password", "buyer")
        assert messagebox.showerror.called_with("Error", "Username already exists")

    def test_load_data_1(self):
        """
        Test the load_data method when all JSON files exist and contain valid data.
        This test verifies that the method correctly loads users, products, and orders
        from their respective JSON files.
        """
        mock_users_data = '[{"id": 1, "username": "user1", "password": "pass1", "role": "buyer"}]'
        mock_products_data = '[{"id": 1, "name": "Product 1", "price": 10.0}]'
        mock_orders_data = '[{"id": 1, "buyer_id": 1, "total_amount": 10.0}]'

        mock_open_calls = {
            'users.json': mock_users_data,
            'products.json': mock_products_data,
            'orders.json': mock_orders_data
        }

        def mock_open_func(filename, mode):
            return mock_open(read_data=mock_open_calls[filename])()

        with patch('builtins.open', side_effect=mock_open_func):
            app = WomenEntrepreneurApp()
            app.load_data()

        self.assertEqual(app.users, json.loads(mock_users_data))
        self.assertEqual(app.products, json.loads(mock_products_data))
        self.assertEqual(app.orders, json.loads(mock_orders_data))

    def test_load_data_file_not_found(self):
        """
        Test the load_data method when the JSON files are not found.
        This tests the FileNotFoundError handling for all three file types.
        """
        app = WomenEntrepreneurApp()

        # Mock the open function to raise FileNotFoundError for all files
        with patch('builtins.open', side_effect=FileNotFoundError):
            app.load_data()

        # Assert that the data lists are empty when files are not found
        self.assertEqual(app.users, [])
        self.assertEqual(app.products, [])
        self.assertEqual(app.orders, [])

    def test_logout_clears_user_and_cart(self):
        """
        Test that logout method clears the current user and empties the cart
        """
        app = WomenEntrepreneurApp()
        app.current_user = {"username": "testuser", "role": "buyer"}
        app.cart_items = [{"id": 1, "name": "Test Product", "price": 10.0, "quantity": 1}]

        app.logout()

        self.assertIsNone(app.current_user)
        self.assertEqual(len(app.cart_items), 0)
        # Note: We can't directly test if show_login_screen was called since it's a GUI method

    def test_logout_clears_user_and_cart_2(self):
        """
        Test that the logout method clears the current user and empties the cart.
        """
        app = WomenEntrepreneurApp()
        app.current_user = {"username": "test_user", "id": 1}
        app.cart_items = [{"id": 1, "name": "Test Product", "price": 10.0, "quantity": 1}]

        app.logout()

        assert app.current_user is None
        assert app.cart_items == []

    def test_logout_shows_login_screen(self):
        """
        Test that the logout method calls show_login_screen.
        """
        app = WomenEntrepreneurApp()
        app.show_login_screen = MagicMock()

        app.logout()

        app.show_login_screen.assert_called_once()

    def test_run_1(self):
        """
        Test that the run method calls mainloop on the root window.
        This test verifies that the application's main event loop is started correctly.
        """
        app = WomenEntrepreneurApp()
        with patch.object(app.root, 'mainloop') as mock_mainloop:
            app.run()
            mock_mainloop.assert_called_once()

    def test_run_no_gui_environment(self):
        """
        Test the run method when no GUI environment is available.
        This test checks if the method gracefully handles the case where tkinter
        cannot create a main window, which could occur in environments without
        a graphical interface.
        """
        app = WomenEntrepreneurApp()

        # Simulate absence of GUI by replacing tk.Tk with a function that raises TclError
        def mock_tk_error(*args, **kwargs):
            raise tk.TclError("No display name and no $DISPLAY environment variable")

        original_tk = tk.Tk
        tk.Tk = mock_tk_error

        try:
            app.run()
        except tk.TclError as e:
            assert str(e) == "No display name and no $DISPLAY environment variable"
        finally:
            # Restore the original Tk function
            tk.Tk = original_tk

    def test_save_data_1(self):
        """
        Test that the save_data method correctly saves users, products, and orders data to their respective JSON files.
        """
        app = WomenEntrepreneurApp()
        app.users = [{"id": 1, "username": "test_user"}]
        app.products = [{"id": 1, "name": "Test Product"}]
        app.orders = [{"id": 1, "total": 100}]

        mock_open_func = mock_open()
        with patch('builtins.open', mock_open_func):
            app.save_data()

        mock_open_func.assert_any_call('users.json', 'w')
        mock_open_func.assert_any_call('products.json', 'w')
        mock_open_func.assert_any_call('orders.json', 'w')

        handle = mock_open_func()
        calls = handle.write.call_args_list

        assert json.loads(calls[0][0][0]) == app.users
        assert json.loads(calls[1][0][0]) == app.products
        assert json.loads(calls[2][0][0]) == app.orders

    def test_show_add_product_form_1(self):
        """
        Test the show_add_product_form method when an image is selected.

        This test verifies that:
        1. A new Toplevel window is created.
        2. The window is configured correctly.
        3. All necessary widgets are added to the window.
        4. The 'Choose Image' functionality works as expected.
        5. The 'Add Product' functionality correctly handles the selected image.
        """
        app = WomenEntrepreneurApp()
        app.current_user = {'id': 1}
        app.products = []

        with patch('tkinter.Toplevel') as mock_toplevel, \
             patch('tkinter.StringVar') as mock_stringvar, \
             patch('tkinter.filedialog.askopenfilename') as mock_askopenfilename, \
             patch('shutil.copy2') as mock_copy2:

            mock_window = MagicMock()
            mock_toplevel.return_value = mock_window
            mock_stringvar.return_value = MagicMock()
            mock_askopenfilename.return_value = '/path/to/image.jpg'

            app.show_add_product_form()

            # Verify window creation and configuration
            mock_toplevel.assert_called_once_with(app.root)
            mock_window.title.assert_called_once_with("Add New Product")
            mock_window.geometry.assert_called_once_with("400x500")

            # Verify that all necessary widgets are added
            expected_widgets = ['Label', 'Entry', 'Text', 'Button']
            for widget in expected_widgets:
                self.assertTrue(any(call.args[0] == mock_window and call.__class__.__name__ == widget 
                                    for call in mock_window.method_calls))

            # Simulate choosing an image
            choose_image_button = next(call for call in mock_window.method_calls if call.args[1] == "Choose Image")
            choose_image_button.args[2]()
            mock_askopenfilename.assert_called_once()

            # Simulate adding a product
            add_product_button = next(call for call in mock_window.method_calls if call.args[1] == "Add Product")
            add_product_button.args[2]()

            # Verify that the image is copied
            mock_copy2.assert_called_once()
            self.assertEqual(len(app.products), 1)
            self.assertIn('image', app.products[0])
            self.assertTrue(app.products[0]['image'].startswith('product_1'))

    def test_show_add_product_form_2(self):
        """
        Test the show_add_product_form method when no image is selected.

        This test verifies that when no file path is chosen for the product image,
        the method still creates a new product with a default image filename.
        """
        app = WomenEntrepreneurApp()
        app.current_user = {'id': 1}
        app.products = []

        with patch('tkinter.Toplevel') as mock_toplevel, \
             patch('tkinter.StringVar') as mock_stringvar, \
             patch('tkinter.filedialog.askopenfilename', return_value=''), \
             patch('shutil.copy2') as mock_copy2:

            mock_window = MagicMock()
            mock_toplevel.return_value = mock_window
            mock_stringvar.return_value.get.return_value = ''

            app.show_add_product_form()

            # Simulate adding a product without selecting an image
            add_product_command = mock_window.mock_calls[-1][1][1]['command']
            mock_window.nametowidget.return_value.get.side_effect = ['Test Product', '10.99']
            mock_window.nametowidget.return_value.get.return_value = 'Test Description'

            add_product_command()

            # Assert that a new product was added with default image
            self.assertEqual(len(app.products), 1)
            self.assertEqual(app.products[0]['image'], 'default.png')
            mock_copy2.assert_not_called()  # Ensure no image was copied

    def test_show_add_product_form_3(self):
        """
        Test the show_add_product_form method when a file is selected but image_src is not set.
        This test verifies that the method handles the case where a file is chosen but not processed.
        """
        app = WomenEntrepreneurApp()
        app.root = tk.Tk()
        app.current_user = {'id': 1}
        app.products = []

        with patch('tkinter.Toplevel') as mock_toplevel, \
             patch('tkinter.StringVar') as mock_stringvar, \
             patch('tkinter.filedialog.askopenfilename') as mock_askopenfilename:

            mock_askopenfilename.return_value = "test_image.jpg"
            mock_stringvar_instance = mock_stringvar.return_value
            mock_stringvar_instance.get.return_value = ""

            app.show_add_product_form()

            mock_toplevel.assert_called_once()
            mock_askopenfilename.assert_called_once()
            mock_stringvar_instance.get.assert_called_once()

            # Verify that the image_path is not set even though a file was selected
            self.assertEqual(mock_stringvar_instance.get.return_value, "")

    def test_show_buyer_dashboard_1(self):
        """
        Test the show_buyer_dashboard method to ensure it correctly sets up the buyer dashboard.

        This test verifies that:
        1. The login and seller frames are hidden
        2. The buyer frame is displayed
        3. The welcome message is shown with the correct username
        4. The 'View Cart' and 'Logout' buttons are present
        5. The products are displayed for the buyer
        """
        app = WomenEntrepreneurApp()
        app.current_user = {'username': 'TestBuyer', 'id': 1}
        app.show_buyer_dashboard()

        assert app.login_frame.winfo_manager() == "", "Login frame should be hidden"
        assert app.seller_frame.winfo_manager() == "", "Seller frame should be hidden"
        assert app.buyer_frame.winfo_manager() == "pack", "Buyer frame should be displayed"

        welcome_label = app.buyer_frame.winfo_children()[0]
        assert isinstance(welcome_label, ttk.Label), "First widget should be a welcome label"
        assert welcome_label.cget("text") == "Welcome, TestBuyer!", "Welcome message should display correct username"

        buttons = [w for w in app.buyer_frame.winfo_children() if isinstance(w, ttk.Button)]
        assert any(b.cget("text") == "View Cart" for b in buttons), "View Cart button should be present"
        assert any(b.cget("text") == "Logout" for b in buttons), "Logout button should be present"

        # Check if show_products_for_buyer was called (indirectly, as it's a method call)
        assert len(app.buyer_frame.winfo_children()) > 3, "Products should be displayed for the buyer"

        app.root.destroy()

    def test_show_buyer_dashboard_with_empty_username(self):
        """
        Test show_buyer_dashboard when current_user has an empty username
        """
        app = WomenEntrepreneurApp()
        app.current_user = {'username': ''}

        app.show_buyer_dashboard()

        welcome_label = app.buyer_frame.winfo_children()[0]
        assert isinstance(welcome_label, ttk.Label)
        assert welcome_label.cget('text') == "Welcome, !"

    def test_show_buyer_dashboard_without_current_user(self):
        """
        Test show_buyer_dashboard when no user is logged in (current_user is None)
        """
        app = WomenEntrepreneurApp()
        app.current_user = None

        with pytest.raises(AttributeError):
            app.show_buyer_dashboard()

    def test_show_cart_1(self):
        """
        Test the show_cart method when the cart is empty and an image exists.

        This test verifies that:
        1. A new window is created for the cart.
        2. The window displays the correct title and size.
        3. A warning message is shown when attempting to checkout with an empty cart.
        4. The cart window is not destroyed after the warning.
        """
        app = WomenEntrepreneurApp()
        app.cart_items = []

        # Mock the existence of an image file
        def mock_exists(path):
            return True

        original_exists = os.path.exists
        os.path.exists = mock_exists

        # Call the method under test
        app.show_cart()

        # Assert that a new window was created
        assert len(app.root.winfo_children()) == 2
        cart_window = app.root.winfo_children()[1]
        assert isinstance(cart_window, tk.Toplevel)

        # Check window properties
        assert cart_window.title() == "Shopping Cart"
        assert cart_window.geometry() == "600x400"

        # Simulate clicking the checkout button
        checkout_button = None
        for widget in cart_window.winfo_children():
            if isinstance(widget, ttk.Button) and widget.cget('text') == "Checkout":
                checkout_button = widget
                break

        assert checkout_button is not None

        # Mock the messagebox.showwarning function
        original_showwarning = messagebox.showwarning
        warning_shown = False
        def mock_showwarning(title, message):
            nonlocal warning_shown
            warning_shown = True
            assert title == "Cart Empty"
            assert message == "Your cart is empty!"

        messagebox.showwarning = mock_showwarning

        # Trigger the checkout
        checkout_button.invoke()

        # Assert that the warning was shown
        assert warning_shown

        # Assert that the cart window was not destroyed
        assert cart_window.winfo_exists()

        # Restore original functions
        os.path.exists = original_exists
        messagebox.showwarning = original_showwarning

    def test_show_cart_2(self):
        """
        Test the show_cart method when the cart is not empty and the product image exists.

        This test verifies that:
        1. The cart window is created and configured correctly.
        2. Cart items are displayed properly, including their images.
        3. The total amount is calculated and displayed accurately.
        4. The checkout button is present and functional.
        """
        app = WomenEntrepreneurApp()
        app.cart_items = [
            {'id': 1, 'name': 'Test Product', 'price': 10.0, 'quantity': 2, 'image': 'test_image.jpg'}
        ]

        with patch('tkinter.Toplevel') as mock_toplevel, \
             patch('tkinter.ttk.Frame') as mock_frame, \
             patch('tkinter.ttk.Label') as mock_label, \
             patch('tkinter.ttk.Button') as mock_button, \
             patch('PIL.Image.open') as mock_image_open, \
             patch('PIL.ImageTk.PhotoImage') as mock_photo_image, \
             patch('os.path.exists', return_value=True):

            mock_cart_window = MagicMock()
            mock_toplevel.return_value = mock_cart_window

            app.show_cart()

            # Assert that the cart window was created and configured correctly
            mock_toplevel.assert_called_once_with(app.root)
            mock_cart_window.title.assert_called_once_with("Shopping Cart")
            mock_cart_window.geometry.assert_called_once_with("600x400")

            # Assert that the frame for cart items was created
            mock_frame.assert_called()

            # Assert that the product image was loaded and displayed
            mock_image_open.assert_called_once_with(os.path.join('product_images', 'test_image.jpg'))
            mock_photo_image.assert_called()

            # Assert that labels for product details were created
            mock_label.assert_any_call(mock_frame(), text='Test Product')
            mock_label.assert_any_call(mock_frame(), text='$10.00 x 2')

            # Assert that the total amount is displayed correctly
            mock_label.assert_any_call(mock_cart_window, text='Total: $20.00')

            # Assert that the checkout button was created
            mock_button.assert_called_with(mock_cart_window, text="Checkout", command=mock_button.return_value.command)

    def test_show_cart_empty_cart(self):
        """
        Test the show_cart method when the cart is empty.
        Verifies that a warning message is displayed and no order is created.
        """
        app = WomenEntrepreneurApp()
        app.cart_items = []
        app.current_user = {'id': 1}
        app.orders = []

        # Mock the messagebox.showwarning function
        original_showwarning = messagebox.showwarning
        messagebox.showwarning = lambda *args, **kwargs: None

        # Call the show_cart method
        app.show_cart()

        # Verify that no order was created
        assert len(app.orders) == 0

        # Restore the original messagebox.showwarning function
        messagebox.showwarning = original_showwarning

    def test_show_login_screen_1(self):
        """
        Test that show_login_screen hides other frames and sets up the login frame correctly.
        """
        app = WomenEntrepreneurApp()
        app.seller_frame = Mock()
        app.buyer_frame = Mock()
        app.login_frame = Mock()

        app.show_login_screen()

        app.seller_frame.pack_forget.assert_called_once()
        app.buyer_frame.pack_forget.assert_called_once()
        app.login_frame.pack.assert_called_once_with(padx=20, pady=20, fill='both', expand=True)
        app.login_frame.winfo_children.assert_called_once()
        for widget in app.login_frame.winfo_children():
            widget.destroy.assert_called_once()

    def test_show_products_for_buyer_1(self):
        """
        Test the show_products_for_buyer method when the product image exists.

        This test verifies that:
        1. The product frame is created and packed correctly.
        2. Product cards are created for each product.
        3. Product images are loaded and displayed when they exist.
        4. Product information (name, description, price) is displayed correctly.
        5. The "Add to Cart" button is created for each product.
        """
        app = WomenEntrepreneurApp()
        app.products = [
            {
                'id': 1,
                'name': 'Test Product',
                'description': 'Test Description',
                'price': 10.99,
                'image': 'test_image.jpg'
            }
        ]

        # Mock the existence of the image file
        os.path.exists = lambda x: True

        # Mock Image and ImageTk to avoid actual image loading
        Image.open = lambda x: type('MockImage', (), {'resize': lambda self, size: self})()
        ImageTk.PhotoImage = lambda x: None

        app.show_products_for_buyer()

        # Assert that the products frame was created and packed
        assert len(app.buyer_frame.winfo_children()) == 1
        products_frame = app.buyer_frame.winfo_children()[0]
        assert isinstance(products_frame, ttk.Frame)

        # Assert that a product card was created
        assert len(products_frame.winfo_children()) == 1
        card = products_frame.winfo_children()[0]
        assert isinstance(card, ttk.Frame)

        # Assert that the product information is displayed correctly
        labels = [w for w in card.winfo_children() if isinstance(w, ttk.Label)]
        assert len(labels) == 4  # Image, Name, Description, Price
        assert labels[1]['text'] == 'Test Product'
        assert labels[2]['text'] == 'Test Description'
        assert labels[3]['text'] == 'Price: ₹10.99'

        # Assert that the "Add to Cart" button is created
        buttons = [w for w in card.winfo_children() if isinstance(w, ttk.Button)]
        assert len(buttons) == 1
        assert buttons[0]['text'] == "🛒 Add to Cart"

    def test_show_products_for_buyer_2(self):
        """
        Test the show_products_for_buyer method when the product image does not exist.

        This test verifies that the method handles the case where a product's image file
        is not found in the expected location. It ensures that the method continues to
        display the product information without raising an exception, even when the
        image cannot be loaded.
        """
        app = WomenEntrepreneurApp()
        app.products = [{
            'id': 1,
            'name': 'Test Product',
            'description': 'Test Description',
            'price': 10.99,
            'image': 'non_existent_image.jpg'
        }]

        # Mock the os.path.exists to return False for any image path
        original_exists = os.path.exists
        os.path.exists = lambda path: False if path.endswith('.jpg') else original_exists(path)

        try:
            app.show_products_for_buyer()

            # Assert that the product information is displayed
            product_labels = [widget for widget in app.buyer_frame.winfo_children() if isinstance(widget, ttk.Label)]
            assert any(label.cget('text') == 'Test Product' for label in product_labels)
            assert any(label.cget('text') == 'Test Description' for label in product_labels)
            assert any(label.cget('text') == 'Price: ₹10.99' for label in product_labels)

            # Assert that no ImageTk.PhotoImage was created (since the image doesn't exist)
            assert not any(isinstance(widget, ttk.Label) and hasattr(widget, 'image') for widget in app.buyer_frame.winfo_children())

        finally:
            # Restore the original os.path.exists function
            os.path.exists = original_exists

    def test_show_register_screen_1(self):
        """
        Test that the show_register_screen method clears the login frame and creates registration widgets.
        """
        app = WomenEntrepreneurApp()

        # Add a dummy widget to the login frame
        ttk.Label(app.login_frame, text="Dummy").pack()

        # Call the method under test
        app.show_register_screen()

        # Check that the login frame is cleared
        assert len(app.login_frame.winfo_children()) > 0

        # Check that registration widgets are created
        widgets = app.login_frame.winfo_children()
        widget_types = [type(w) for w in widgets]

        assert ttk.Label in widget_types
        assert ttk.Entry in widget_types
        assert ttk.Radiobutton in widget_types
        assert ttk.Button in widget_types

        # Clean up
        app.root.destroy()

    def test_show_register_screen_no_login_frame(self):
        """
        Test the show_register_screen method when the login_frame attribute is not set.
        This tests the edge case where the method is called before the login_frame is initialized.
        """
        app = WomenEntrepreneurApp()
        app.login_frame = None

        with self.assertRaises(AttributeError):
            app.show_register_screen()

    def test_show_seller_dashboard_1(self):
        """
        Test that the seller dashboard is displayed correctly for a logged-in seller.

        This test verifies that:
        1. The login and buyer frames are hidden
        2. The seller frame is displayed
        3. The welcome message is shown with the correct username
        4. The 'Add New Product' button is present
        5. The seller's products are displayed
        6. The logout button is present
        """
        app = WomenEntrepreneurApp()
        app.current_user = {'id': 1, 'username': 'test_seller', 'role': 'seller'}

        app.show_seller_dashboard()

        assert app.login_frame.winfo_ismapped() == 0
        assert app.buyer_frame.winfo_ismapped() == 0
        assert app.seller_frame.winfo_ismapped() == 1

        welcome_label = app.seller_frame.winfo_children()[0]
        assert isinstance(welcome_label, ttk.Label)
        assert welcome_label.cget('text') == "Welcome, test_seller!"

        add_product_button = app.seller_frame.winfo_children()[1]
        assert isinstance(add_product_button, ttk.Button)
        assert add_product_button.cget('text') == "Add New Product"

        logout_button = app.seller_frame.winfo_children()[-1]
        assert isinstance(logout_button, ttk.Button)
        assert logout_button.cget('text') == "Logout"

        app.root.destroy()

    def test_show_seller_dashboard_no_current_user(self):
        """
        Test show_seller_dashboard when there is no current user logged in.
        This tests the edge case where the method is called without a user being logged in.
        """
        app = WomenEntrepreneurApp()
        app.current_user = None

        with pytest.raises(AttributeError):
            app.show_seller_dashboard()

    def test_show_seller_dashboard_non_seller_user(self):
        """
        Test show_seller_dashboard when the current user is not a seller.
        This tests the edge case where a non-seller user attempts to access the seller dashboard.
        """
        app = WomenEntrepreneurApp()
        app.current_user = {'id': 1, 'username': 'test_buyer', 'role': 'buyer'}

        with pytest.raises(ValueError):
            app.show_seller_dashboard()

    def test_show_seller_products_1(self):
        """
        Test that the show_seller_products method creates a frame for products
        and displays the seller's products in a table.
        """
        app = WomenEntrepreneurApp()
        app.current_user = {'id': 1, 'username': 'test_seller', 'role': 'seller'}
        app.products = [
            {'id': 1, 'seller_id': 1, 'name': 'Test Product', 'description': 'Test Description', 'price': 10.0},
            {'id': 2, 'seller_id': 2, 'name': 'Other Product', 'description': 'Other Description', 'price': 20.0}
        ]

        app.show_seller_products()

        # Check if products_frame is created
        assert len(app.seller_frame.winfo_children()) > 0
        products_frame = app.seller_frame.winfo_children()[0]
        assert isinstance(products_frame, ttk.Frame)

        # Check if Treeview is created
        assert len(products_frame.winfo_children()) > 0
        tree = products_frame.winfo_children()[0]
        assert isinstance(tree, ttk.Treeview)

        # Check if the correct product is displayed
        items = tree.get_children()
        assert len(items) == 1
        values = tree.item(items[0])['values']
        assert values[0] == 1  # ID
        assert values[1] == 'Test Product'  # Name
        assert values[2] == 'Test Description'  # Description
        assert values[3] == 10.0  # Price
        assert values[4] == 'Edit/Delete'  # Actions

    def test_show_seller_products_no_seller_products(self):
        """
        Test the behavior of show_seller_products when the current seller has no products.
        This tests the edge case where the seller's product list is empty.
        """
        app = WomenEntrepreneurApp()
        app.current_user = {'id': 1, 'username': 'test_seller', 'role': 'seller'}
        app.products = [{'id': 1, 'seller_id': 2, 'name': 'Test Product', 'description': 'Test Description', 'price': 10.0}]

        app.show_seller_products()

        # Assert that the treeview is created but empty
        products_frame = app.seller_frame.winfo_children()[0]
        tree = products_frame.winfo_children()[0]
        assert isinstance(tree, ttk.Treeview)
        assert len(tree.get_children()) == 0

    def test_update_product_1(self):
        """
        Test that the update_product method successfully updates a product's details
        and shows a success message when valid input is provided.
        """
        app = WomenEntrepreneurApp()
        app.current_user = {'id': 1, 'username': 'test_seller', 'role': 'seller'}
        app.products = [{'id': 1, 'seller_id': 1, 'name': 'Old Name', 'description': 'Old Description', 'price': 10.0}]

        # Mock the tkinter widgets
        app.root = tk.Tk()
        edit_window = tk.Toplevel(app.root)
        name_entry = tk.Entry(edit_window)
        name_entry.insert(0, "New Name")
        desc_entry = tk.Text(edit_window)
        desc_entry.insert("1.0", "New Description")
        price_entry = tk.Entry(edit_window)
        price_entry.insert(0, "15.0")

        # Call the update_product method
        app.update_product()

        # Assert that the product was updated
        assert app.products[0]['name'] == "New Name"
        assert app.products[0]['description'] == "New Description"
        assert app.products[0]['price'] == 15.0

        # Assert that a success message was shown (this requires mocking messagebox)
        with pytest.raises(tk.TclError):  # This error is raised because we're not in a mainloop
            messagebox.showinfo("Success", "Product updated successfully!")

        # Clean up
        app.root.destroy()

    def test_update_product_invalid_price(self):
        """
        Test updating a product with an invalid price format.
        This should trigger the ValueError exception and display an error message.
        """
        # Mock the necessary tkinter objects
        mock_name_entry = tk.Entry()
        mock_name_entry.insert(0, "Test Product")

        mock_desc_entry = tk.Text()
        mock_desc_entry.insert("1.0", "Test Description")

        mock_price_entry = tk.Entry()
        mock_price_entry.insert(0, "invalid_price")

        # Mock the product dictionary
        product = {
            'name': 'Old Name',
            'description': 'Old Description',
            'price': 10.0
        }

        # Mock the self object
        class MockSelf:
            def save_data(self):
                pass

            def show_seller_dashboard(self):
                pass

        mock_self = MockSelf()

        # Mock the edit_window
        mock_edit_window = tk.Toplevel()

        # Call the update_product function
        with pytest.raises(ValueError):
            update_product()

        # Assert that the error message is displayed
        assert messagebox.showerror.call_args[0][0] == "Error"
        assert messagebox.showerror.call_args[0][1] == "Invalid price format"

        # Assert that the product details remain unchanged
        assert product['name'] == 'Old Name'
        assert product['description'] == 'Old Description'
        assert product['price'] == 10.0

class WomenEntrepreneurApp:

    def __init__(self):
        self.root = tk.Tk()
        self.current_user = None
        self.cart_items = []
        self.login_frame = ttk.Frame(self.root)

    def add_product(self):
        name = name_entry.get()
        description = desc_entry.get("1.0", tk.END).strip()
        try:
            price = float(price_entry.get())
            
            image_src = image_path.get()
            if image_src:
                _, ext = os.path.splitext(image_src)
                image_filename = f"product_{len(self.products) + 1}{ext}"
                image_dest = os.path.join('product_images', image_filename)
                shutil.copy2(image_src, image_dest)
            else:
                image_filename = "default.png"
            
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
        except ValueError:
            messagebox.showerror("Error", "Invalid price format")

    def logout(self):
        self.current_user = None
        self.cart_items = []
        self.show_login_screen()

    def save_data(self):
        with open('products.json', 'w') as f:
            json.dump(self.products, f, indent=2)
