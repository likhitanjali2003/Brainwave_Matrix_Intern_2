import tkinter as tk
from tkinter import messagebox,ttk
import os
from datetime import datetime
import csv
INVENTORY_FILE = "inventory.csv"
inventory = {}
LOW_STOCK_THRESHOLD = 5
CREDENTIALS_FILE = "credentials.txt"
LOGIN_HISTORY_FILE = "login_history.txt"
LOG_FILE = "inventory_log.csv"
def save_credentials(username, password):
    with open(CREDENTIALS_FILE, "a") as file:
        file.write(f"{username},{password}\n")
def check_credentials(username, password):
    try:
        with open(CREDENTIALS_FILE, "r") as file:
            for line in file:
                stored_username, stored_password = line.strip().split(",")
                if username == stored_username and password == stored_password:
                    return True
        return False
    except FileNotFoundError:
        return False
def log_login(username):
    with open(LOGIN_HISTORY_FILE, "a") as file:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{username} logged in at {current_time}\n")
def signup():
    username = entry_username.get()
    password = entry_password.get()
    if username and password:
        if check_credentials(username, password)==True:
          messagebox.showinfo("Error!!!","Account already exists!!")
          return
        save_credentials(username, password)
        messagebox.showinfo("Success", "Sign up successful! You can now log in.")
        entry_username.delete(0, tk.END)
        entry_password.delete(0, tk.END)
        root.destroy()
    else:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
def login():
    username = entry_username.get()
    password = entry_password.get()

    if check_credentials(username, password):
        messagebox.showinfo("Success", "Login successful!")
        log_login(username) 
        entry_username.delete(0, tk.END)
        entry_password.delete(0, tk.END)
        root.destroy()
    else:
        messagebox.showerror("Login Failed", "Incorrect username or password.")
root = tk.Tk()
root.title("Login System")
label_username = tk.Label(root, text="Username")
label_username.grid(row=0, column=0, padx=10, pady=10)
entry_username = tk.Entry(root)
entry_username.grid(row=0, column=1, padx=10, pady=10)
label_password = tk.Label(root, text="Password")
label_password.grid(row=1, column=0, padx=10, pady=10)
entry_password = tk.Entry(root, show="*")
entry_password.grid(row=1, column=1, padx=10, pady=10)
button_signup = tk.Button(root, text="Sign Up", command=signup)
button_signup.grid(row=2, column=0, padx=10, pady=10)
button_login = tk.Button(root, text="Log In", command=login)
button_login.grid(row=2, column=1, padx=10, pady=10)
root.mainloop()

def log_change(action, product_id, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([action, product_id, details, timestamp])

def save_inventory():
    with open(INVENTORY_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Product ID", "Name", "Quantity", "Price"])
        for product_id, data in inventory.items():
            writer.writerow([product_id, data['name'], data['quantity'], data['price']])

def load_inventory():
    if os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                product_id = row["Product ID"]
                inventory[product_id] = {
                    "name": row["Name"],
                    "quantity": int(row["Quantity"]),
                    "price": float(row["Price"])
                }
        update_inventory_list()

def add_product():
    product_id = entry_id_add.get()
    name = entry_name_add.get()
    quantity = entry_quantity_add.get()
    price = entry_price_add.get()

    if product_id in inventory:
        messagebox.showerror("Error", "Product ID already exists!")
        return
    
    try:
        quantity = int(quantity)
        price = float(price)
        if quantity < 0 or price < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Please enter valid quantity and price.")
        return

    inventory[product_id] = {'name': name, 'quantity': quantity, 'price': price}
    save_inventory()
    log_change("ADD", product_id, f"Added product '{name}' with quantity {quantity} and price {price}")
    messagebox.showinfo("Success", "Product added successfully!")
    update_inventory_list()
    clear_add_fields()

def edit_product():
    product_id = entry_id_edit.get()

    if product_id not in inventory:
        messagebox.showerror("Error", "Product ID not found!")
        return

    try:
        quantity = int(entry_quantity_edit.get())
        price = float(entry_price_edit.get())
        if quantity < 0 or price < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Please enter valid quantity and price.")
        return

    old_data = inventory[product_id]
    inventory[product_id] = {
        'name': entry_name_edit.get(),
        'quantity': quantity,
        'price': price
    }
    save_inventory()
    log_change("EDIT", product_id, f"Updated product '{entry_name_edit.get()}' from quantity {old_data['quantity']} to {quantity} and price {old_data['price']} to {price}")
    messagebox.showinfo("Success", "Product updated successfully!")
    update_inventory_list()
    clear_edit_fields()

def delete_product():
    product_id = entry_id_delete.get()

    if product_id not in inventory:
        messagebox.showerror("Error", "Product ID not found!")
        return

    deleted_product = inventory[product_id]
    del inventory[product_id]
    save_inventory()
    log_change("DELETE", product_id, f"Deleted product '{deleted_product['name']}' with quantity {deleted_product['quantity']} and price {deleted_product['price']}")
    messagebox.showinfo("Success", "Product deleted successfully!")
    update_inventory_list()
    clear_delete_fields()

def show_low_stock():
    low_stock_items = [f"{id}: {data['name']} (Qty: {data['quantity']})"
                       for id, data in inventory.items() if data['quantity'] < LOW_STOCK_THRESHOLD]
    if low_stock_items:
        messagebox.showwarning("Low Stock Alert", "\n".join(low_stock_items))
    else:
        messagebox.showinfo("Low Stock Alert", "No items with low stock.")

def update_inventory_list():
    for row in tree.get_children():
        tree.delete(row)

    for product_id, data in inventory.items():
        tree.insert("", tk.END, values=(product_id, data['name'], data['quantity'], f"Rs.{data['price']:.2f}"))

def clear_add_fields():
    entry_id_add.delete(0, tk.END)
    entry_name_add.delete(0, tk.END)
    entry_quantity_add.delete(0, tk.END)
    entry_price_add.delete(0, tk.END)

def clear_edit_fields():
    entry_id_edit.delete(0, tk.END)
    entry_name_edit.delete(0, tk.END)
    entry_quantity_edit.delete(0, tk.END)
    entry_price_edit.delete(0, tk.END)

def clear_delete_fields():
    entry_id_delete.delete(0, tk.END)

def logout():
    response = messagebox.askyesno("Logout", "Are you sure you want to log out?")
    if response:
        root.destroy()

def generate_report():
    report_window = tk.Toplevel(root)
    report_window.title("Sales Report")
    tk.Label(report_window, text="Sales Report:").pack(pady=10)

    report_text = tk.Text(report_window, width=50, height=20)
    report_text.pack(padx=10, pady=10)

    for product_id, data in inventory.items():
        report_text.insert(tk.END, f"ID: {product_id}, Name: {data['name']}, Quantity: {data['quantity']}, Price: Rs.{data['price']:.2f}\n")

    report_text.config(state=tk.DISABLED)

root = tk.Tk()
root.title("Inventory Management System with Tabs")

notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, padx=10, pady=10)

tab_add = ttk.Frame(notebook)
notebook.add(tab_add, text="Add Product")
tk.Label(tab_add, text="Product ID:").grid(row=0, column=0, padx=10, pady=5)
entry_id_add = tk.Entry(tab_add)
entry_id_add.grid(row=0, column=1, padx=10, pady=5)
tk.Label(tab_add, text="Name:").grid(row=1, column=0, padx=10, pady=5)
entry_name_add = tk.Entry(tab_add)
entry_name_add.grid(row=1, column=1, padx=10, pady=5)
tk.Label(tab_add, text="Quantity:").grid(row=2, column=0, padx=10, pady=5)
entry_quantity_add = tk.Entry(tab_add)
entry_quantity_add.grid(row=2, column=1, padx=10, pady=5)
tk.Label(tab_add, text="Price:").grid(row=3, column=0, padx=10, pady=5)
entry_price_add = tk.Entry(tab_add)
entry_price_add.grid(row=3, column=1, padx=10, pady=5)
button_add = tk.Button(tab_add, text="Add Product", command=add_product)
button_add.grid(row=4, column=0, columnspan=2, pady=10)

tab_edit = ttk.Frame(notebook)
notebook.add(tab_edit, text="Edit Product")
tk.Label(tab_edit, text="Product ID:").grid(row=0, column=0, padx=10, pady=5)
entry_id_edit = tk.Entry(tab_edit)
entry_id_edit.grid(row=0, column=1, padx=10, pady=5)
tk.Label(tab_edit, text="Name:").grid(row=1, column=0, padx=10, pady=5)
entry_name_edit = tk.Entry(tab_edit)
entry_name_edit.grid(row=1, column=1, padx=10, pady=5)
tk.Label(tab_edit, text="Quantity:").grid(row=2, column=0, padx=10, pady=5)
entry_quantity_edit = tk.Entry(tab_edit)
entry_quantity_edit.grid(row=2, column=1, padx=10, pady=5)
tk.Label(tab_edit, text="Price:").grid(row=3, column=0, padx=10, pady=5)
entry_price_edit = tk.Entry(tab_edit)
entry_price_edit.grid(row=3, column=1, padx=10, pady=5)
button_edit = tk.Button(tab_edit, text="Edit Product", command=edit_product)
button_edit.grid(row=4, column=0, columnspan=2, pady=10)

tab_delete = ttk.Frame(notebook)
notebook.add(tab_delete, text="Delete Product")
tk.Label(tab_delete, text="Product ID:").grid(row=0, column=0, padx=10, pady=5)
entry_id_delete = tk.Entry(tab_delete)
entry_id_delete.grid(row=0, column=1, padx=10, pady=5)
button_delete = tk.Button(tab_delete, text="Delete Product", command=delete_product)
button_delete.grid(row=1, column=0, columnspan=2, pady=10)

tab_inventory = ttk.Frame(notebook)
notebook.add(tab_inventory, text="Inventory Tracking")
tree = ttk.Treeview(tab_inventory, columns=("ID", "Name", "Quantity", "Price"), show="headings")
tree.heading("ID", text="Product ID")
tree.heading("Name", text="Name")
tree.heading("Quantity", text="Quantity")
tree.heading("Price", text="Price")
tree.pack(fill=tk.BOTH, expand=True)
button_low_stock = tk.Button(tab_inventory, text="Show Low Stock Alert", command=show_low_stock)
button_low_stock.pack(pady=10)

tab_reports = ttk.Frame(notebook)
notebook.add(tab_reports, text="Reports")
button_generate_report = tk.Button(tab_reports, text="Generate Sales Report", command=generate_report)
button_generate_report.pack(pady=10)

tab_logout = ttk.Frame(notebook)
notebook.add(tab_logout, text="Logout")
button_logout = tk.Button(tab_logout, text="Logout", command=logout)
button_logout.pack(pady=10)

load_inventory()

root.mainloop()
