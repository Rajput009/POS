import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os

class PharmacyPOS:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy POS System")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 700)
        
        # Set up modern styling
        self.setup_styles()
        
        # Initialize database
        self.init_database()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.create_status_bar()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 30))
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_medicines_tab()
        self.create_sales_tab()
        self.create_returns_tab()
        self.create_reports_tab()
        self.create_settings_tab()
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Current user
        self.current_user = None
        
        # Show login
        self.show_login()

    def setup_styles(self):
        """Set up modern styling for the application"""
        self.style = ttk.Style()
        
        # Try to use a modern theme if available
        try:
            # Try to use 'clam' theme if available (more modern)
            self.style.theme_use('clam')
        except tk.TclError:
            # Fall back to default theme
            pass
        
        # Configure custom styles with modern colors and fonts
        self.style.configure('Modern.TFrame', background='#f8f9fa')
        self.style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'), foreground='#2c3e50', background='#f8f9fa')
        self.style.configure('SubHeader.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#34495e', background='#f8f9fa')
        self.style.configure('Modern.TLabel', font=('Segoe UI', 10), background='#f8f9fa', foreground='#34495e')
        self.style.configure('Modern.TLabelFrame', background='#f8f9fa', foreground='#2c3e50')
        self.style.configure('Modern.TButton', font=('Segoe UI', 10), padding=6)
        self.style.configure('Action.TButton', font=('Segoe UI', 10, 'bold'), padding=8, 
                            background='#3498db', foreground='white')
        self.style.map('Action.TButton', background=[('active', '#2980b9')])
        self.style.configure('Success.TButton', font=('Segoe UI', 10, 'bold'), padding=8, 
                            background='#27ae60', foreground='white')
        self.style.map('Success.TButton', background=[('active', '#219653')])
        self.style.configure('Danger.TButton', font=('Segoe UI', 10, 'bold'), padding=8,
                            background='#e74c3c', foreground='white')
        self.style.map('Danger.TButton', background=[('active', '#c0392b')])
        self.style.configure('Warning.TButton', font=('Segoe UI', 10, 'bold'), padding=8,
                            background='#f39c12', foreground='white')
        self.style.map('Warning.TButton', background=[('active', '#d35400')])
        
        # Configure Treeview styles with alternating row colors
        self.style.configure('Modern.Treeview', rowheight=28, font=('Segoe UI', 9), 
                            background='white', fieldbackground='white', foreground='#2c3e50')
        self.style.configure('Modern.Treeview.Heading', font=('Segoe UI', 10, 'bold'), 
                            background='#ecf0f1', foreground='#2c3e50')
        self.style.map('Modern.Treeview', background=[('selected', '#3498db')], 
                      foreground=[('selected', 'white')])
        
        # Configure Entry styles
        self.style.configure('Modern.TEntry', font=('Segoe UI', 10), 
                            fieldbackground='white', foreground='#2c3e50')
        
        # Set background color for the root window
        self.root.configure(bg='#f8f9fa')
        
    def init_database(self):
        """Initialize SQLite database with required tables"""
        self.conn = sqlite3.connect('pharmacy.db')
        self.cursor = self.conn.cursor()
        
        # Create Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        
        # Create Medicines table (making batch optional)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                batch TEXT,
                expiry DATE NOT NULL,
                stock_packs INTEGER NOT NULL,
                units_per_pack INTEGER NOT NULL,
                pack_price REAL NOT NULL,
                unit_price REAL NOT NULL,
                supplier TEXT NOT NULL
            )
        ''')
        
        # Create Sales table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATETIME NOT NULL,
                medicine_id INTEGER NOT NULL,
                qty INTEGER NOT NULL,
                type TEXT NOT NULL,
                price REAL NOT NULL,
                total REAL NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (medicine_id) REFERENCES medicines (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create Returns table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS returns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                medicine_id INTEGER NOT NULL,
                return_date DATETIME NOT NULL,
                return_qty INTEGER NOT NULL,
                return_type TEXT NOT NULL,
                reason TEXT,
                refunded_amount REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales (id),
                FOREIGN KEY (medicine_id) REFERENCES medicines (id)
            )
        ''')
        
        # Create Settings table for receipt configuration
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                pharmacy_name TEXT NOT NULL DEFAULT 'My Pharmacy',
                pharmacy_address TEXT NOT NULL DEFAULT '123 Main Street, City',
                pharmacy_phone TEXT NOT NULL DEFAULT 'Phone: 123456',
                receipt_header TEXT NOT NULL DEFAULT 'Thank you for visiting!',
                receipt_footer TEXT NOT NULL DEFAULT 'No refunds after 7 days of purchase'
            )
        ''')
        
        # Insert default admin user if not exists
        self.cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                              ('admin', 'admin123', 'Admin'))
        
        # Insert default settings if not exists
        self.cursor.execute("SELECT * FROM settings WHERE id = 1")
        if not self.cursor.fetchone():
            self.cursor.execute("""
                INSERT INTO settings (id, pharmacy_name, pharmacy_address, pharmacy_phone, receipt_header, receipt_footer)
                VALUES (1, 'My Pharmacy', '123 Main Street, City', 'Phone: 123456', 'Thank you for visiting!', 'No refunds after 7 days of purchase')
            """)
        
        self.conn.commit()

    def create_menu_bar(self):
        """Create the menu bar"""
        self.menubar = tk.Menu(self.root, bg='#f8f9fa', fg='#2c3e50', font=('Segoe UI', 10))
        self.root.config(menu=self.menubar)
        
        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0, bg='#f8f9fa', fg='#2c3e50', font=('Segoe UI', 10))
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Backup", command=self.backup_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        
        # Users menu
        users_menu = tk.Menu(self.menubar, tearoff=0, bg='#f8f9fa', fg='#2c3e50', font=('Segoe UI', 10))
        self.menubar.add_cascade(label="Users", menu=users_menu)
        users_menu.add_command(label="Manage Users", command=self.manage_users)
        
        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0, bg='#f8f9fa', fg='#2c3e50', font=('Segoe UI', 10))
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = tk.Frame(self.root, relief=tk.FLAT, bd=1, bg='#ecf0f1')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(self.status_bar, text="Not logged in", bd=1, relief=tk.FLAT, anchor=tk.W,
                                bg='#ecf0f1', fg='#7f8c8d', font=('Segoe UI', 9))
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.datetime_label = tk.Label(self.status_bar, text="", bd=1, relief=tk.FLAT, anchor=tk.E,
                                  bg='#ecf0f1', fg='#7f8c8d', font=('Segoe UI', 9))
        self.datetime_label.pack(side=tk.RIGHT)
        self.update_datetime()

    def update_datetime(self):
        """Update the datetime in status bar"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.datetime_label.config(text=now)
        self.root.after(1000, self.update_datetime)

    def create_dashboard_tab(self):
        """Create the dashboard tab"""
        self.dashboard_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Dashboard title
        title_label = ttk.Label(self.dashboard_frame, text="Dashboard", style='Header.TLabel')
        title_label.pack(pady=(20, 30))
        
        # Stats frame with modern styling
        stats_frame = tk.Frame(self.dashboard_frame, bg='#f8f9fa')
        stats_frame.pack(fill=tk.X, padx=30, pady=20)
        
        # Total medicines card
        total_medicines_frame = tk.Frame(stats_frame, bg='#3498db', relief=tk.FLAT, bd=0)
        total_medicines_frame.pack(side=tk.LEFT, padx=15, fill=tk.BOTH, expand=True)
        tk.Label(total_medicines_frame, text="Total Medicines", font=('Segoe UI', 12, 'bold'), 
                bg='#3498db', fg='white').pack(pady=(15, 5))
        self.total_medicines_label = tk.Label(total_medicines_frame, text="0", font=('Segoe UI', 24, 'bold'), 
                                             bg='#3498db', fg='white')
        self.total_medicines_label.pack(pady=15)
        
        # Low stock card
        low_stock_frame = tk.Frame(stats_frame, bg='#e74c3c', relief=tk.FLAT, bd=0)
        low_stock_frame.pack(side=tk.LEFT, padx=15, fill=tk.BOTH, expand=True)
        tk.Label(low_stock_frame, text="Low Stock (<10 packs)", font=('Segoe UI', 12, 'bold'), 
                bg='#e74c3c', fg='white').pack(pady=(15, 5))
        self.low_stock_label = tk.Label(low_stock_frame, text="0", font=('Segoe UI', 24, 'bold'), 
                                       bg='#e74c3c', fg='white')
        self.low_stock_label.pack(pady=15)
        
        # Expiry alerts card
        expiry_frame = tk.Frame(stats_frame, bg='#f39c12', relief=tk.FLAT, bd=0)
        expiry_frame.pack(side=tk.LEFT, padx=15, fill=tk.BOTH, expand=True)
        tk.Label(expiry_frame, text="Expiry Alerts", font=('Segoe UI', 12, 'bold'), 
                bg='#f39c12', fg='white').pack(pady=(15, 5))
        self.expiry_label = tk.Label(expiry_frame, text="0", font=('Segoe UI', 24, 'bold'), 
                                    bg='#f39c12', fg='white')
        self.expiry_label.pack(pady=15)
        
        # Daily sales card
        daily_sales_frame = tk.Frame(stats_frame, bg='#27ae60', relief=tk.FLAT, bd=0)
        daily_sales_frame.pack(side=tk.LEFT, padx=15, fill=tk.BOTH, expand=True)
        tk.Label(daily_sales_frame, text="Today's Sales", font=('Segoe UI', 12, 'bold'), 
                bg='#27ae60', fg='white').pack(pady=(15, 5))
        self.daily_sales_label = tk.Label(daily_sales_frame, text="$0.00", font=('Segoe UI', 24, 'bold'), 
                                         bg='#27ae60', fg='white')
        self.daily_sales_label.pack(pady=15)
        
        # Refresh dashboard
        self.refresh_dashboard()

    def refresh_dashboard(self):
        """Refresh dashboard statistics"""
        # Total medicines
        self.cursor.execute("SELECT COUNT(*) FROM medicines")
        total_medicines = self.cursor.fetchone()[0]
        self.total_medicines_label.config(text=str(total_medicines))
        
        # Low stock medicines
        self.cursor.execute("SELECT COUNT(*) FROM medicines WHERE stock_packs < 10")
        low_stock = self.cursor.fetchone()[0]
        self.low_stock_label.config(text=str(low_stock))
        
        # Expiry alerts (within 30 days)
        today = datetime.now().date()
        self.cursor.execute("SELECT COUNT(*) FROM medicines WHERE expiry <= date(?, '+30 days')", (today.isoformat(),))
        expiry_alerts = self.cursor.fetchone()[0]
        self.expiry_label.config(text=str(expiry_alerts))
        
        # Today's sales
        today_str = today.isoformat()
        self.cursor.execute("SELECT SUM(total) FROM sales WHERE date(date) = ?", (today_str,))
        daily_sales = self.cursor.fetchone()[0] or 0
        self.daily_sales_label.config(text=f"${daily_sales:.2f}")

    def create_medicines_tab(self):
        """Create the medicines tab"""
        self.medicines_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(self.medicines_frame, text="Medicines")
        
        # Form frame with modern styling
        form_frame = tk.LabelFrame(self.medicines_frame, text="Medicine Details", 
                                  font=('Segoe UI', 12, 'bold'), bg='#f8f9fa', fg='#2c3e50',
                                  relief=tk.RAISED, bd=2)
        form_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Form fields with better layout
        fields_frame = tk.Frame(form_frame, bg='#f8f9fa')
        fields_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Name
        tk.Label(fields_frame, text="Medicine Name:", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=0, column=0, sticky=tk.W, padx=5, pady=8)
        self.name_entry = ttk.Entry(fields_frame, width=30, style='Modern.TEntry')
        self.name_entry.grid(row=0, column=1, padx=5, pady=8)
        
        # Batch
        tk.Label(fields_frame, text="Batch No (Optional):", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=0, column=2, sticky=tk.W, padx=(20, 5), pady=8)
        self.batch_entry = ttk.Entry(fields_frame, width=20, style='Modern.TEntry')
        self.batch_entry.grid(row=0, column=3, padx=5, pady=8)
        
        # Expiry
        tk.Label(fields_frame, text="Expiry Date (YYYY-MM-DD):", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=1, column=0, sticky=tk.W, padx=5, pady=8)
        self.expiry_entry = ttk.Entry(fields_frame, width=20, style='Modern.TEntry')
        self.expiry_entry.grid(row=1, column=1, padx=5, pady=8)
        
        # Stock packs
        tk.Label(fields_frame, text="Stock (packs):", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=1, column=2, sticky=tk.W, padx=(20, 5), pady=8)
        self.stock_entry = ttk.Entry(fields_frame, width=20, style='Modern.TEntry')
        self.stock_entry.grid(row=1, column=3, padx=5, pady=8)
        
        # Units per pack
        tk.Label(fields_frame, text="Units per pack:", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=2, column=0, sticky=tk.W, padx=5, pady=8)
        self.units_entry = ttk.Entry(fields_frame, width=20, style='Modern.TEntry')
        self.units_entry.grid(row=2, column=1, padx=5, pady=8)
        
        # Pack price
        tk.Label(fields_frame, text="Pack Price:", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=2, column=2, sticky=tk.W, padx=(20, 5), pady=8)
        self.pack_price_entry = ttk.Entry(fields_frame, width=20, style='Modern.TEntry')
        self.pack_price_entry.grid(row=2, column=3, padx=5, pady=8)
        
        # Supplier
        tk.Label(fields_frame, text="Supplier:", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=3, column=0, sticky=tk.W, padx=5, pady=8)
        self.supplier_entry = ttk.Entry(fields_frame, width=30, style='Modern.TEntry')
        self.supplier_entry.grid(row=3, column=1, padx=5, pady=8)
        
        # Unit price (auto-calculated)
        tk.Label(fields_frame, text="Unit Price:", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=3, column=2, sticky=tk.W, padx=(20, 5), pady=8)
        self.unit_price_entry = ttk.Entry(fields_frame, width=20, style='Modern.TEntry', state='readonly')
        self.unit_price_entry.grid(row=3, column=3, padx=5, pady=8)
        
        # Bind pack price and units to auto-calculate unit price
        self.pack_price_entry.bind('<KeyRelease>', self.calculate_unit_price)
        self.units_entry.bind('<KeyRelease>', self.calculate_unit_price)
        
        # Buttons with modern styling
        buttons_frame = tk.Frame(form_frame, bg='#f8f9fa')
        buttons_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        self.add_btn = ttk.Button(buttons_frame, text="Add Medicine", command=self.add_medicine, 
                             style='Action.TButton', width=15)
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_btn = ttk.Button(buttons_frame, text="Update Medicine", command=self.update_medicine, 
                                style='Warning.TButton', width=15, state='disabled')
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(buttons_frame, text="Delete Medicine", command=self.delete_medicine, 
                                style='Danger.TButton', width=15, state='disabled')
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(buttons_frame, text="Clear Form", command=self.clear_medicine_form, 
                               style='Modern.TButton', width=15)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Search with modern styling
        search_frame = tk.Frame(self.medicines_frame, bg='#f8f9fa')
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(search_frame, text="Search (Name or Batch):", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30, style='Modern.TEntry')
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_medicines)
        
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_medicines, 
                           style='Modern.TButton')
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Treeview for medicines with modern styling
        tree_frame = tk.LabelFrame(self.medicines_frame, text="Medicine Inventory", 
                              font=('Segoe UI', 12, 'bold'), bg='#f8f9fa', fg='#2c3e50',
                              relief=tk.RAISED, bd=2)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        # Treeview with modern styling
        self.medicines_tree = ttk.Treeview(tree_frame, 
                                      columns=("ID", "Name", "Batch", "Expiry", "Stock", "Units", "Pack Price", "Unit Price"),
                                      show='headings', 
                                      style='Modern.Treeview',
                                      yscrollcommand=v_scrollbar.set, 
                                      xscrollcommand=h_scrollbar.set)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.medicines_tree.yview)
        h_scrollbar.config(command=self.medicines_tree.xview)
        
        # Define headings with better styling
        self.medicines_tree.heading("ID", text="ID")
        self.medicines_tree.heading("Name", text="Name")
        self.medicines_tree.heading("Batch", text="Batch")
        self.medicines_tree.heading("Expiry", text="Expiry")
        self.medicines_tree.heading("Stock", text="Stock (packs)")
        self.medicines_tree.heading("Units", text="Total Units")
        self.medicines_tree.heading("Pack Price", text="Pack Price")
        self.medicines_tree.heading("Unit Price", text="Unit Price")
        
        # Define column widths
        self.medicines_tree.column("ID", width=50, anchor=tk.CENTER)
        self.medicines_tree.column("Name", width=150, anchor=tk.W)
        self.medicines_tree.column("Batch", width=100, anchor=tk.W)
        self.medicines_tree.column("Expiry", width=100, anchor=tk.CENTER)
        self.medicines_tree.column("Stock", width=100, anchor=tk.CENTER)
        self.medicines_tree.column("Units", width=100, anchor=tk.CENTER)
        self.medicines_tree.column("Pack Price", width=100, anchor=tk.E)
        self.medicines_tree.column("Unit Price", width=100, anchor=tk.E)
        
        # Pack elements
        self.medicines_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind selection event
        self.medicines_tree.bind('<<TreeviewSelect>>', self.on_medicine_select)
        
        # Load medicines
        self.load_medicines()
        
        medicines = self.cursor.fetchall()
        
        for medicine in medicines:
            total_units = medicine[4] * medicine[5]
            self.medicines_tree.insert('', tk.END, values=(
                medicine[0], medicine[1], medicine[2], medicine[3], 
                medicine[4], total_units, f"${medicine[6]:.2f}", f"${medicine[7]:.2f}"
            ))

    def on_medicine_select(self, event):
        """Handle medicine selection in treeview"""
        selection = self.medicines_tree.selection()
        if selection:
            item = self.medicines_tree.item(selection[0])
            values = item['values']
            
            # Enable update and delete buttons
            self.update_btn.config(state='normal')
            self.delete_btn.config(state='normal')
            
            # Fill form with selected medicine data
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, values[1])
            
            self.batch_entry.delete(0, tk.END)
            self.batch_entry.insert(0, values[2])
            
            self.expiry_entry.delete(0, tk.END)
            self.expiry_entry.insert(0, values[3])
            
            self.stock_entry.delete(0, tk.END)
            self.stock_entry.insert(0, values[4])
            
            # Extract units from total units column
            self.units_entry.delete(0, tk.END)
            # We need to get the actual units_per_pack from database
            medicine_id = values[0]
            self.cursor.execute("SELECT units_per_pack, pack_price FROM medicines WHERE id = ?", (medicine_id,))
            result = self.cursor.fetchone()
            if result:
                self.units_entry.insert(0, result[0])
                self.pack_price_entry.delete(0, tk.END)
                self.pack_price_entry.insert(0, result[1])
                self.calculate_unit_price()

    def clear_medicine_form(self):
        """Clear the medicine form"""
        self.name_entry.delete(0, tk.END)
        self.batch_entry.delete(0, tk.END)
        self.expiry_entry.delete(0, tk.END)
        self.stock_entry.delete(0, tk.END)
        self.units_entry.delete(0, tk.END)
        self.pack_price_entry.delete(0, tk.END)
        self.unit_price_entry.config(state='normal')
        self.unit_price_entry.delete(0, tk.END)
        self.unit_price_entry.config(state='readonly')
        self.supplier_entry.delete(0, tk.END)
        
        # Disable update and delete buttons
        self.update_btn.config(state='disabled')
        self.delete_btn.config(state='disabled')

    def add_medicine(self):
        """Add a new medicine"""
        try:
            name = self.name_entry.get().strip()
            batch = self.batch_entry.get().strip()
            expiry = self.expiry_entry.get().strip()
            stock = int(self.stock_entry.get() or 0)
            units = int(self.units_entry.get() or 1)
            pack_price = float(self.pack_price_entry.get() or 0)
            unit_price = pack_price / units if units > 0 else 0
            supplier = self.supplier_entry.get().strip()
            
            if not name or not expiry or not supplier:
                messagebox.showerror("Error", "Please fill in all required fields (Name, Expiry Date, Supplier)")
                return
            
            # Insert into database (batch is now optional)
            self.cursor.execute("""
                INSERT INTO medicines (name, batch, expiry, stock_packs, units_per_pack, pack_price, unit_price, supplier)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, batch, expiry, stock, units, pack_price, unit_price, supplier))
            
            self.conn.commit()
            
            # Refresh medicines list
            self.load_medicines()
            
            # Clear form
            self.clear_medicine_form()
            
            # Refresh dashboard
            self.refresh_dashboard()
            
            messagebox.showinfo("Success", "Medicine added successfully")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for stock, units, and price")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add medicine: {str(e)}")

    def update_medicine(self):
        """Update selected medicine"""
        selection = self.medicines_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a medicine to update")
            return
        
        try:
            item = self.medicines_tree.item(selection[0])
            medicine_id = item['values'][0]
            
            name = self.name_entry.get().strip()
            batch = self.batch_entry.get().strip()
            expiry = self.expiry_entry.get().strip()
            stock = int(self.stock_entry.get() or 0)
            units = int(self.units_entry.get() or 1)
            pack_price = float(self.pack_price_entry.get() or 0)
            unit_price = pack_price / units if units > 0 else 0
            supplier = self.supplier_entry.get().strip()
            
            if not name or not expiry or not supplier:
                messagebox.showerror("Error", "Please fill in all required fields (Name, Expiry Date, Supplier)")
                return
            
            # Update in database (batch is now optional)
            self.cursor.execute("""
                UPDATE medicines 
                SET name=?, batch=?, expiry=?, stock_packs=?, units_per_pack=?, pack_price=?, unit_price=?, supplier=?
                WHERE id=?
            """, (name, batch, expiry, stock, units, pack_price, unit_price, supplier, medicine_id))
            
            self.conn.commit()
            
            # Refresh medicines list
            self.load_medicines()
            
            # Clear form
            self.clear_medicine_form()
            
            # Refresh dashboard
            self.refresh_dashboard()
            
            messagebox.showinfo("Success", "Medicine updated successfully")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for stock, units, and price")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update medicine: {str(e)}")

    def delete_medicine(self):
        """Delete selected medicine"""
        selection = self.medicines_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a medicine to delete")
            return
        
        result = messagebox.askyesno("Confirm", "Are you sure you want to delete this medicine?")
        if result:
            try:
                item = self.medicines_tree.item(selection[0])
                medicine_id = item['values'][0]
                
                # Delete from database
                self.cursor.execute("DELETE FROM medicines WHERE id=?", (medicine_id,))
                self.conn.commit()
                
                # Refresh medicines list
                self.load_medicines()
                
                # Clear form
                self.clear_medicine_form()
                
                # Refresh dashboard
                self.refresh_dashboard()
                
                messagebox.showinfo("Success", "Medicine deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete medicine: {str(e)}")

    def create_sales_tab(self):
        """Create the sales/POS tab"""
        self.sales_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(self.sales_frame, text="Sales")
        
        # Search frame with modern styling
        search_frame = tk.LabelFrame(self.sales_frame, text="Search Medicine", 
                                   font=('Segoe UI', 12, 'bold'), bg='#f8f9fa', fg='#2c3e50',
                                   relief=tk.RAISED, bd=2)
        search_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(search_frame, text="Search by Name (Batch Optional):", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').pack(side=tk.LEFT, padx=5)
        self.sales_search_entry = ttk.Entry(search_frame, width=30, style='Modern.TEntry')
        self.sales_search_entry.pack(side=tk.LEFT, padx=5)
        self.sales_search_entry.bind('<Return>', self.search_medicine_for_sale)
        
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_medicine_for_sale, 
                               style='Modern.TButton')
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Medicine info frame with modern styling
        info_frame = tk.LabelFrame(self.sales_frame, text="Medicine Information", 
                                  font=('Segoe UI', 12, 'bold'), bg='#f8f9fa', fg='#2c3e50',
                                  relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Medicine details with modern text widget
        self.medicine_info_text = tk.Text(info_frame, height=6, font=('Segoe UI', 10), 
                                         bg='white', fg='#2c3e50', relief=tk.SUNKEN, bd=1)
        self.medicine_info_text.pack(fill=tk.X, padx=10, pady=10)
        
        # Sale type and quantity with modern styling
        sale_frame = tk.Frame(self.sales_frame, bg='#f8f9fa')
        sale_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(sale_frame, text="Sale Type:", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').pack(side=tk.LEFT, padx=5)
        self.sale_type_var = tk.StringVar(value="Pack")
        pack_radio = tk.Radiobutton(sale_frame, text="Pack", variable=self.sale_type_var, value="Pack", 
                                   font=('Segoe UI', 10), bg='#f8f9fa', fg='#2c3e50', selectcolor='white')
        pack_radio.pack(side=tk.LEFT, padx=5)
        unit_radio = tk.Radiobutton(sale_frame, text="Unit", variable=self.sale_type_var, value="Unit", 
                                   font=('Segoe UI', 10), bg='#f8f9fa', fg='#2c3e50', selectcolor='white')
        unit_radio.pack(side=tk.LEFT, padx=5)
        
        tk.Label(sale_frame, text="Quantity:", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').pack(side=tk.LEFT, padx=(20, 5))
        self.quantity_entry = ttk.Entry(sale_frame, width=10, style='Modern.TEntry')
        self.quantity_entry.pack(side=tk.LEFT, padx=5)
        self.quantity_entry.bind('<Return>', self.add_to_cart)
        
        add_btn = ttk.Button(sale_frame, text="Add to Cart", command=self.add_to_cart, 
                            style='Action.TButton')
        add_btn.pack(side=tk.LEFT, padx=10)
        
        # Cart frame with modern styling
        cart_frame = tk.LabelFrame(self.sales_frame, text="Shopping Cart", 
                                  font=('Segoe UI', 12, 'bold'), bg='#f8f9fa', fg='#2c3e50',
                                  relief=tk.RAISED, bd=2)
        cart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Cart treeview with modern styling
        self.cart_tree = ttk.Treeview(cart_frame, 
                                     columns=("ID", "Name", "Type", "Quantity", "Price", "Total"),
                                     show='headings', 
                                     style='Modern.Treeview')
        
        self.cart_tree.heading("ID", text="ID")
        self.cart_tree.heading("Name", text="Medicine Name")
        self.cart_tree.heading("Type", text="Sale Type")
        self.cart_tree.heading("Quantity", text="Quantity")
        self.cart_tree.heading("Price", text="Unit Price")
        self.cart_tree.heading("Total", text="Total")
        
        self.cart_tree.column("ID", width=50, anchor=tk.CENTER)
        self.cart_tree.column("Name", width=200, anchor=tk.W)
        self.cart_tree.column("Type", width=80, anchor=tk.CENTER)
        self.cart_tree.column("Quantity", width=80, anchor=tk.CENTER)
        self.cart_tree.column("Price", width=100, anchor=tk.E)
        self.cart_tree.column("Total", width=100, anchor=tk.E)
        
        self.cart_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for cart
        cart_scrollbar = ttk.Scrollbar(cart_frame, orient=tk.VERTICAL, command=self.cart_tree.yview)
        cart_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        
        # Cart buttons with modern styling
        cart_buttons_frame = tk.Frame(self.sales_frame, bg='#f8f9fa')
        cart_buttons_frame.pack(fill=tk.X, padx=20, pady=15)
        
        remove_btn = ttk.Button(cart_buttons_frame, text="Remove Item", command=self.remove_from_cart, 
                               style='Danger.TButton')
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(cart_buttons_frame, text="Clear Cart", command=self.clear_cart, 
                              style='Modern.TButton')
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Checkout frame with modern styling
        checkout_frame = tk.Frame(self.sales_frame, bg='#f8f9fa', relief=tk.RAISED, bd=2)
        checkout_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(checkout_frame, text="Total Amount:", font=('Segoe UI', 16, 'bold'), 
                bg='#f8f9fa', fg='#27ae60').pack(side=tk.LEFT, padx=10, pady=15)
        self.total_amount_label = tk.Label(checkout_frame, text="$0.00", font=('Segoe UI', 16, 'bold'), 
                                          bg='#f8f9fa', fg='#27ae60')
        self.total_amount_label.pack(side=tk.LEFT, padx=5, pady=15)
        
        checkout_btn = ttk.Button(checkout_frame, text="Checkout", command=self.checkout, 
                                 style='Success.TButton')
        checkout_btn.pack(side=tk.RIGHT, padx=15, pady=15)
        
        # Initialize cart
        self.cart_items = []

    def search_medicine_for_sale(self, event=None):
        """Search medicine for sale"""
        search_term = self.sales_search_entry.get().strip()
        if not search_term:
            return
        
        self.cursor.execute("""
            SELECT * FROM medicines 
            WHERE name LIKE ? OR batch LIKE ?
        """, (f"%{search_term}%", f"%{search_term}%"))
        
        medicines = self.cursor.fetchall()
        
        if medicines:
            # Display first medicine found
            medicine = medicines[0]
            info_text = f"Name: {medicine[1]}\n"
            # Only show batch if it exists
            if medicine[2]:  # batch number
                info_text += f"Batch: {medicine[2]}\n"
            info_text += f"Price: ${medicine[3]:.2f}\n"
            info_text += f"Stock: {medicine[4]}\n"
            info_text += f"Expiry: {medicine[5]}\n"
            self.medicine_info_text.delete(1.0, tk.END)
            self.medicine_info_text.insert(tk.END, info_text)
        else:
            self.medicine_info_text.delete(1.0, tk.END)
            self.medicine_info_text.insert(tk.END, "No medicine found.")

    def add_to_cart(self, event=None):
        """Add selected medicine to cart"""
        medicine_info = self.medicine_info_text.get(1.0, tk.END).strip()
        if not medicine_info:
            messagebox.showwarning("Warning", "Please search and select a medicine first.")
            return
        
        quantity = self.quantity_entry.get().strip()
        if not quantity.isdigit() or int(quantity) <= 0:
            messagebox.showwarning("Warning", "Please enter a valid quantity.")
            return
        
        quantity = int(quantity)
        medicine = medicine_info.split('\n')
        medicine_id = medicine[0].split(': ')[1]
        medicine_name = medicine[1].split(': ')[1]
        medicine_price = float(medicine[2].split(': ')[1].replace('$', ''))
        medicine_stock = int(medicine[3].split(': ')[1])
        sale_type = self.sale_type_var.get()
        
        if quantity > medicine_stock:
            messagebox.showwarning("Warning", "Quantity exceeds available stock.")
            return
        
        total_price = quantity * medicine_price
        
        # Check if medicine is already in cart
        for item in self.cart_items:
            if item['id'] == medicine_id and item['type'] == sale_type:
                item['quantity'] += quantity
                item['total'] += total_price
                self.update_cart_tree()
                return
        
        # Add new item to cart
        self.cart_items.append({
            'id': medicine_id,
            'name': medicine_name,
            'type': sale_type,
            'quantity': quantity,
            'price': medicine_price,
            'total': total_price
        })
        
        self.update_cart_tree()
        self.update_total_amount()

    def update_cart_tree(self):
        """Update the cart treeview"""
        self.cart_tree.delete(*self.cart_tree.get_children())
        for item in self.cart_items:
            self.cart_tree.insert("", tk.END, values=(
                item['id'], item['name'], item['type'], item['quantity'], 
                f"${item['price']:.2f}", f"${item['total']:.2f}"
            ))

    def update_total_amount(self):
        """Update the total amount label"""
        total = sum(item['total'] for item in self.cart_items)
        self.total_amount_label.config(text=f"${total:.2f}")

    def remove_from_cart(self):
        """Remove selected item from cart"""
        selected_item = self.cart_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to remove.")
            return
        
        item_id = self.cart_tree.item(selected_item, 'values')[0]
        item_type = self.cart_tree.item(selected_item, 'values')[2]
        
        for item in self.cart_items:
            if item['id'] == item_id and item['type'] == item_type:
                self.cart_items.remove(item)
                break
        
        self.update_cart_tree()
        self.update_total_amount()

    def clear_cart(self):
        """Clear all items from cart"""
        self.cart_items = []
        self.update_cart_tree()
        self.update_total_amount()

    def checkout(self):
        """Checkout the cart"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty.")
            return
        
        # Insert sale record into sales table
        sale_id = self.generate_sale_id()
        sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_amount = sum(item['total'] for item in self.cart_items)
        
        self.cursor.execute("""
            INSERT INTO sales (sale_id, sale_date, total_amount) 
            VALUES (?, ?, ?)
        """, (sale_id, sale_date, total_amount))
        self.conn.commit()
        
        # Insert sale details into sale_details table
        for item in self.cart_items:
            self.cursor.execute("""
                INSERT INTO sale_details (sale_id, medicine_id, sale_type, quantity, price) 
                VALUES (?, ?, ?, ?, ?)
            """, (sale_id, item['id'], item['type'], item['quantity'], item['price']))
            self.conn.commit()
        
        # Update medicine stock
        for item in self.cart_items:
            self.cursor.execute("""
                UPDATE medicines 
                SET stock = stock - ? 
                WHERE id = ?
            """, (item['quantity'], item['id']))
            self.conn.commit()
        
        messagebox.showinfo("Success", "Checkout successful!")
        self.clear_cart()

    def generate_sale_id(self):
        """Generate a unique sale ID"""
        return f"S{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def create_reports_tab(self):
        """Create the reports tab"""
        self.reports_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(self.reports_frame, text="Reports")
        
        # Report options frame with modern styling
        options_frame = tk.LabelFrame(self.reports_frame, text="Report Options", 
                                     font=('Segoe UI', 12, 'bold'), bg='#f8f9fa', fg='#2c3e50',
                                     relief=tk.RAISED, bd=2)
        options_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Date range with modern styling
        tk.Label(options_frame, text="From:", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.from_date_entry = ttk.Entry(options_frame, style='Modern.TEntry')
        self.from_date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.from_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        tk.Label(options_frame, text="To:", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.to_date_entry = ttk.Entry(options_frame, style='Modern.TEntry')
        self.to_date_entry.grid(row=0, column=3, padx=5, pady=5)
        self.to_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Report type with modern styling
        tk.Label(options_frame, text="Report Type:", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.report_type_var = tk.StringVar(value="Daily Sales")
        report_types = ["Daily Sales", "Monthly Sales", "Stock Summary", "Expired Medicines", "Returns Report"]
        self.report_type_menu = ttk.Combobox(options_frame, textvariable=self.report_type_var, 
                                           values=report_types, state="readonly", 
                                           font=('Segoe UI', 10), width=20)
        self.report_type_menu.grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons with modern styling
        buttons_frame = tk.Frame(options_frame, bg='#f8f9fa')
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=15)
        
        view_btn = ttk.Button(buttons_frame, text="View Report", command=self.view_report, 
                             style='Action.TButton')
        view_btn.pack(side=tk.LEFT, padx=5)
        
        excel_btn = ttk.Button(buttons_frame, text="Export Excel", command=self.export_excel, 
                              style='Modern.TButton')
        excel_btn.pack(side=tk.LEFT, padx=5)
        
        pdf_btn = ttk.Button(buttons_frame, text="Export PDF", command=self.export_pdf, 
                            style='Modern.TButton')
        pdf_btn.pack(side=tk.LEFT, padx=5)
        
        # Report display area with modern styling
        report_display_frame = tk.LabelFrame(self.reports_frame, text="Report", 
                                            font=('Segoe UI', 12, 'bold'), bg='#f8f9fa', fg='#2c3e50',
                                            relief=tk.RAISED, bd=2)
        report_display_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Text widget for report display with modern styling
        self.report_text = tk.Text(report_display_frame, wrap=tk.WORD, font=('Courier New', 10),
                                  bg='white', fg='#2c3e50')
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        report_scrollbar = ttk.Scrollbar(report_display_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        report_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_text.configure(yscrollcommand=report_scrollbar.set)

    def search_medicine_for_sale(self, event=None):
        """Search medicine for sale"""
        search_term = self.sales_search_entry.get().strip()
        
        self.cursor.execute("""
            SELECT * FROM medicines 
            WHERE name LIKE ? OR batch LIKE ?
        """, (f"%{search_term}%", f"%{search_term}%"))
        
        medicines = self.cursor.fetchall()
        
        if medicines:
            # Display first medicine found
            medicine = medicines[0]
            info_text = f"Name: {medicine[1]}\n"
            
            # Only show batch if it exists
            if medicine[2]:  # batch number
                info_text += f"Batch: {medicine[2]}\n"
            else:
                info_text += "Batch: N/A\n"
            
            info_text += f"Expiry: {medicine[3]}\n"
            info_text += f"Stock: {medicine[4]} packs, {medicine[4] * medicine[5]} units\n"
            info_text += f"Pack Price: ${medicine[6]:.2f}\n"
            info_text += f"Unit Price: ${medicine[7]:.2f}"
            
            self.medicine_info_text.config(state='normal')
            self.medicine_info_text.delete(1.0, tk.END)
            self.medicine_info_text.insert(1.0, info_text)
            self.medicine_info_text.config(state='disabled')
            
            # Store current medicine for adding to cart
            self.current_medicine = medicine
        else:
            self.medicine_info_text.config(state='normal')
            self.medicine_info_text.delete(1.0, tk.END)

            self.medicine_info_text.insert(1.0, "Medicine not found")
            self.medicine_info_text.config(state='disabled')
            self.current_medicine = None

    def add_to_cart(self, event=None):
        """Add medicine to cart"""
        if not hasattr(self, 'current_medicine') or not self.current_medicine:
            messagebox.showerror("Error", "Please search and select a medicine first")
            return
        
        try:
            quantity = int(self.quantity_entry.get() or 0)
            if quantity <= 0:
                messagebox.showerror("Error", "Please enter a valid quantity")
                return
            
            medicine = self.current_medicine
            sale_type = self.sale_type_var.get()
            
            # Check stock
            if sale_type == "Pack":
                if quantity > medicine[4]:  # stock_packs
                    messagebox.showerror("Error", f"Insufficient stock. Available: {medicine[4]} packs")
                    return
                price = medicine[6]  # pack_price
            else:  # Unit
                total_units = medicine[4] * medicine[5]  # stock_packs * units_per_pack
                if quantity > total_units:
                    messagebox.showerror("Error", f"Insufficient stock. Available: {total_units} units")
                    return
                price = medicine[7]  # unit_price
            
            # Calculate total
            total = quantity * price
            
            # Add to cart items
            cart_item = {
                'id': medicine[0],
                'name': medicine[1],
                'type': sale_type,
                'quantity': quantity,
                'price': price,
                'total': total
            }
            
            self.cart_items.append(cart_item)
            self.update_cart_tree()
            self.update_total_amount()
            self.quantity_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")

    def calculate_unit_price(self, event=None):
        """Calculate unit price based on pack price and units per pack"""
        try:
            pack_price = float(self.pack_price_entry.get() or 0)
            units = int(self.units_entry.get() or 1)
            unit_price = pack_price / units if units > 0 else 0
            self.unit_price_entry.config(state='normal')
            self.unit_price_entry.delete(0, tk.END)
            self.unit_price_entry.insert(0, f"{unit_price:.2f}")
            self.unit_price_entry.config(state='readonly')
        except ValueError:
            pass  # Ignore invalid input

    def search_medicines(self, event=None):
        """Search medicines by name or batch"""
        search_term = self.search_entry.get().strip()
        
        # Clear existing items
        for item in self.medicines_tree.get_children():
            self.medicines_tree.delete(item)
        
        if search_term:
            self.cursor.execute("""
                SELECT * FROM medicines 
                WHERE name LIKE ? OR batch LIKE ?
                ORDER BY name
            """, (f"%{search_term}%", f"%{search_term}%"))
        else:
            self.cursor.execute("SELECT * FROM medicines ORDER BY name")
        
        medicines = self.cursor.fetchall()
        
        for medicine in medicines:
            total_units = medicine[4] * medicine[5]  # stock_packs * units_per_pack
            self.medicines_tree.insert('', tk.END, values=(
                medicine[0], medicine[1], medicine[2] or "N/A", medicine[3], 
                medicine[4], total_units, f"${medicine[6]:.2f}", f"${medicine[7]:.2f}"
            ))

    def load_medicines(self):
        """Load all medicines into the treeview"""
        # Clear existing items
        for item in self.medicines_tree.get_children():
            self.medicines_tree.delete(item)
        
        # Load medicines from database
        self.cursor.execute("SELECT * FROM medicines ORDER BY name")

                'id': medicine[0],
                'name': medicine[1],
                'type': sale_type,
                'quantity': quantity,
                'price': price,
                'total': total
            }
            
            self.cart_items.append(cart_item)
            
            # Update cart display
            self.update_cart_display()
            
            # Clear search and quantity
            self.sales_search_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
            self.medicine_info_text.config(state='normal')
            self.medicine_info_text.delete(1.0, tk.END)
            self.medicine_info_text.config(state='disabled')
            self.current_medicine = None
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")

    def update_cart_display(self):
        """Update cart display"""
        # Clear existing items
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add cart items
        total_amount = 0
        for item in self.cart_items:
            self.cart_tree.insert('', tk.END, values=(
                item['id'], item['name'], item['type'], 
                item['quantity'], f"${item['price']:.2f}", f"${item['total']:.2f}"
            ))
            total_amount += item['total']
        
        # Update total amount
        self.total_amount_label.config(text=f"${total_amount:.2f}")

    def remove_from_cart(self):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an item to remove")
            return
        
        # Get index of selected item
        item = self.cart_tree.item(selection[0])
        item_values = item['values']
        
        # Find and remove from cart items
        for i, cart_item in enumerate(self.cart_items):
            if (cart_item['id'] == item_values[0] and 
                cart_item['name'] == item_values[1] and 
                cart_item['type'] == item_values[2]):
                del self.cart_items[i]
                break
        
        # Update cart display
        self.update_cart_display()

    def clear_cart(self):
        """Clear the shopping cart"""
        self.cart_items = []
        self.update_cart_display()

    def checkout(self):
        """Process checkout"""
        if not self.cart_items:
            messagebox.showerror("Error", "Cart is empty")
            return
        
        if not self.current_user:
            messagebox.showerror("Error", "Please login first")
            return
        
        try:
            # Process each item in cart
            total_amount = 0
            sale_ids = []
            
            for item in self.cart_items:
                # Insert sale record
                self.cursor.execute("""
                    INSERT INTO sales (date, medicine_id, qty, type, price, total, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (datetime.now(), item['id'], item['quantity'], item['type'], 
                      item['price'], item['total'], self.current_user[0]))
                
                sale_id = self.cursor.lastrowid
                sale_ids.append(sale_id)
                total_amount += item['total']
                
                # Update medicine stock
                if item['type'] == "Pack":
                    self.cursor.execute("""
                        UPDATE medicines 
                        SET stock_packs = stock_packs - ? 
                        WHERE id = ?
                    """, (item['quantity'], item['id']))
                else:  # Unit
                    # Get medicine details to calculate packs and units
                    self.cursor.execute("SELECT stock_packs, units_per_pack FROM medicines WHERE id = ?", (item['id'],))
                    result = self.cursor.fetchone()
                    if result:
                        stock_packs, units_per_pack = result
                        total_units = stock_packs * units_per_pack
                        remaining_units = total_units - item['quantity']
                        
                        # Calculate new packs and units
                        new_packs = remaining_units // units_per_pack
                        new_units = remaining_units % units_per_pack
                        
                        self.cursor.execute("""
                            UPDATE medicines 
                            SET stock_packs = ? 
                            WHERE id = ?
                        """, (new_packs, item['id']))
            
            self.conn.commit()
            
            # Generate professional receipt
            receipt_text = self.generate_receipt(sale_ids, total_amount)
            
            # Show receipt in a scrollable text widget
            self.show_receipt_dialog(receipt_text)
            
            # Clear cart
            self.clear_cart()
            
            # Refresh dashboard
            self.refresh_dashboard()
            
            # Reload medicines
            if hasattr(self, 'medicines_tree'):
                self.load_medicines()
                
        except Exception as e:
            messagebox.showerror("Error", f"Checkout failed: {str(e)}")

    def generate_receipt(self, sale_ids, total_amount):
        """Generate a professional formatted receipt"""
        try:
            # Get settings
            self.cursor.execute("SELECT * FROM settings WHERE id = 1")
            settings = self.cursor.fetchone()
            
            if settings:
                pharmacy_name = settings[1]
                pharmacy_address = settings[2]
                pharmacy_phone = settings[3]
                receipt_header = settings[4]
                receipt_footer = settings[5]
            else:
                # Default values if settings not found
                pharmacy_name = "My Pharmacy"
                pharmacy_address = "123 Main Street, City"
                pharmacy_phone = "Phone: 123456"
                receipt_header = "Thank you for visiting!"
                receipt_footer = "No refunds after 7 days of purchase"
            
            # Get the first sale ID as invoice number (assuming single transaction)
            invoice_number = sale_ids[0] if sale_ids else "N/A"
            
            # Create receipt header
            receipt_lines = []
            receipt_lines.append(f"{' ' * ((40 - len(pharmacy_name)) // 2)}{pharmacy_name}")
            receipt_lines.append(f"{' ' * ((40 - len(pharmacy_address)) // 2)}{pharmacy_address}")
            receipt_lines.append(f"{' ' * ((40 - len(pharmacy_phone)) // 2)}{pharmacy_phone}")
            receipt_lines.append("-" * 40)
            
            # Add transaction details
            receipt_lines.append(f"Invoice: {invoice_number:<15} Date: {datetime.now().strftime('%d-%m-%Y')}")
            cashier_name = self.current_user[1] if self.current_user else "Unknown"
            receipt_lines.append(f"Cashier: {cashier_name}")
            receipt_lines.append("-" * 40)
            
            # Add item header
            receipt_lines.append("Item                Qty   Price   Total")
            
            # Add items
            for item in self.cart_items:
                # Format item name (truncate if too long)
                item_name = item['name'][:18] if len(item['name']) > 18 else item['name']
                # Format quantity with type
                qty_with_type = f"{item['quantity']}{item['type'][0]}"  # P for Pack, U for Unit
                # Format prices
                price = f"{item['price']:.2f}"
                total = f"{item['total']:.2f}"
                
                # Add item line
                receipt_lines.append(f"{item_name:<18} {qty_with_type:>3}  {price:>7}  {total:>7}")
            
            # Add totals section
            receipt_lines.append("-" * 40)
            receipt_lines.append(f"{'Subtotal:':>30}  {total_amount:>7.2f}")
            receipt_lines.append(f"{'Discount:':>30}  {0.00:>7.2f}")
            receipt_lines.append(f"{'Total:':>30}  {total_amount:>7.2f}")
            receipt_lines.append("-" * 40)
            
            # Add header/footer messages
            receipt_lines.append(f"{' ' * ((40 - len(receipt_header)) // 2)}{receipt_header}")
            receipt_lines.append(f"{' ' * ((40 - len(receipt_footer)) // 2)}{receipt_footer}")
            
            return "\n".join(receipt_lines)
        except Exception as e:
            # Fallback to simple receipt if formatting fails
            receipt = "===== RECEIPT =====\n"
            receipt += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            cashier_name = self.current_user[1] if self.current_user else "Unknown"
            receipt += f"Cashier: {cashier_name}\n"
            receipt += "-" * 30 + "\n"
            
            for item in self.cart_items:
                receipt += f"{item['name']} ({item['type']})\n"
                receipt += f"  {item['quantity']} x ${item['price']:.2f} = ${item['total']:.2f}\n"
            
            receipt += "-" * 30 + "\n"
            receipt += f"TOTAL: ${total_amount:.2f}\n"
            receipt += "=" * 30 + "\n"
            receipt += "Thank you for your purchase!"
            return receipt

    def show_receipt_dialog(self, receipt_text):
        """Show receipt in a dialog with print and save options"""
        receipt_window = tk.Toplevel(self.root)
        receipt_window.title("Receipt")
        receipt_window.geometry("450x650")
        receipt_window.configure(bg='#f8f9fa')
        
        # Center the window
        receipt_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Receipt title
        title_label = ttk.Label(receipt_window, text="Receipt", style='Header.TLabel')
        title_label.pack(pady=(20, 10))
        
        # Receipt text widget with scrollbar
        text_frame = tk.Frame(receipt_window, bg='#f8f9fa')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        receipt_text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Courier New", 11),
                                     bg='white', fg='#2c3e50', relief=tk.RAISED, bd=2)
        receipt_text_widget.insert(1.0, receipt_text)
        receipt_text_widget.config(state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=receipt_text_widget.yview)
        receipt_text_widget.configure(yscrollcommand=scrollbar.set)
        
        receipt_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons frame
        buttons_frame = tk.Frame(receipt_window, bg='#f8f9fa')
        buttons_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Print button
        print_btn = ttk.Button(buttons_frame, text="Print", command=lambda: self.print_receipt(receipt_text), 
                              style='Action.TButton')
        print_btn.pack(side=tk.LEFT, padx=5)
        
        # Save as PDF button
        pdf_btn = ttk.Button(buttons_frame, text="Save as PDF", command=lambda: self.save_receipt_as_pdf(receipt_text), 
                            style='Modern.TButton')
        pdf_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = ttk.Button(buttons_frame, text="Close", command=receipt_window.destroy, 
                              style='Modern.TButton')
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Make window modal
        receipt_window.transient(self.root)
        receipt_window.grab_set()
        receipt_window.wait_window()

    def print_receipt(self, receipt_text):
        """Print the receipt"""
        try:
            # Try to use the platform's print command
            import tempfile
            import subprocess
            import os
            
            # Create a temporary file with the receipt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(receipt_text)
                temp_filename = f.name
            
            # Try to print using the system's print command
            if os.name == 'nt':  # Windows
                subprocess.run(['notepad', '/p', temp_filename], check=True)
            else:  # Unix-like systems
                subprocess.run(['lp', temp_filename], check=True)
            
            # Clean up temporary file
            os.unlink(temp_filename)
            
            messagebox.showinfo("Print", "Receipt sent to printer")
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to print receipt: {str(e)}\n\nThe receipt has been copied to clipboard instead.")
            # Copy to clipboard as fallback
            self.root.clipboard_clear()
            self.root.clipboard_append(receipt_text)
            self.root.update()

    def save_receipt_as_pdf(self, receipt_text):
        """Save the receipt as PDF"""
        try:
            from tkinter import filedialog
            import tempfile
            import subprocess
            import os
            
            # Ask user for file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            
            if filename:
                # For now, we'll save as text file since we don't have PDF libraries
                # In a real implementation, you would use a library like reportlab
                with open(filename.replace('.pdf', '.txt'), 'w') as f:
                    f.write(receipt_text)
                messagebox.showinfo("Save Receipt", f"Receipt saved as text file:\n{filename.replace('.pdf', '.txt')}\n\nTo save as PDF, please use a PDF printer or convert the text file.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save receipt: {str(e)}")

    def create_returns_tab(self):
        """Create the returns tab"""
        self.returns_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(self.returns_frame, text="Returns")
        
        # Search frame with modern styling
        search_frame = tk.LabelFrame(self.returns_frame, text="Search Sale", 
                                   font=('Segoe UI', 12, 'bold'), bg='#f8f9fa', fg='#2c3e50',
                                   relief=tk.RAISED, bd=2)
        search_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(search_frame, text="Search by Invoice No or Medicine Name (Batch Optional):", 
                font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').pack(side=tk.LEFT, padx=5)
        self.return_search_entry = ttk.Entry(search_frame, width=30, style='Modern.TEntry')
        self.return_search_entry.pack(side=tk.LEFT, padx=5)
        self.return_search_entry.bind('<Return>', self.search_sales_for_return)
        
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_sales_for_return, 
                               style='Modern.TButton')
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Sales treeview with modern styling
        sales_frame = tk.LabelFrame(self.returns_frame, text="Sales Records", 
                                   font=('Segoe UI', 12, 'bold'), bg='#f8f9fa', fg='#2c3e50',
                                   relief=tk.RAISED, bd=2)
        sales_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        self.sales_tree = ttk.Treeview(sales_frame, 
                                      columns=("ID", "Date", "Medicine", "Qty", "Type", "Price", "Total"),
                                      show='headings', 
                                      style='Modern.Treeview')
        
        self.sales_tree.heading("ID", text="Invoice No")
        self.sales_tree.heading("Date", text="Date")
        self.sales_tree.heading("Medicine", text="Medicine")
        self.sales_tree.heading("Qty", text="Quantity")
        self.sales_tree.heading("Type", text="Type")
        self.sales_tree.heading("Price", text="Price")
        self.sales_tree.heading("Total", text="Total")
        
        self.sales_tree.column("ID", width=80, anchor=tk.CENTER)
        self.sales_tree.column("Date", width=120, anchor=tk.CENTER)
        self.sales_tree.column("Medicine", width=150, anchor=tk.W)
        self.sales_tree.column("Qty", width=80, anchor=tk.CENTER)
        self.sales_tree.column("Type", width=80, anchor=tk.CENTER)
        self.sales_tree.column("Price", width=80, anchor=tk.E)
        self.sales_tree.column("Total", width=80, anchor=tk.E)
        
        self.sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        sales_scrollbar = ttk.Scrollbar(sales_frame, orient=tk.VERTICAL, command=self.sales_tree.yview)
        sales_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sales_tree.configure(yscrollcommand=sales_scrollbar.set)
        
        # Return details frame with modern styling
        return_frame = tk.LabelFrame(self.returns_frame, text="Return Details", 
                                    font=('Segoe UI', 12, 'bold'), bg='#f8f9fa', fg='#2c3e50',
                                    relief=tk.RAISED, bd=2)
        return_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(return_frame, text="Return Quantity:", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=0, column=0, sticky=tk.W, padx=5, pady=10)
        self.return_qty_entry = ttk.Entry(return_frame, width=10, style='Modern.TEntry')
        self.return_qty_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=10)
        
        tk.Label(return_frame, text="Reason (Optional):", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=0, column=2, sticky=tk.W, padx=(20, 5), pady=10)
        self.return_reason_entry = ttk.Entry(return_frame, width=30, style='Modern.TEntry')
        self.return_reason_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=10)
        
        buttons_frame = tk.Frame(return_frame, bg='#f8f9fa')
        buttons_frame.grid(row=1, column=0, columnspan=4, pady=20)
        
        process_btn = ttk.Button(buttons_frame, text="Process Return", command=self.process_return, 
                                style='Danger.TButton')
        process_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(buttons_frame, text="Cancel Return", command=self.cancel_return, 
                               style='Modern.TButton')
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def search_sales_for_return(self, event=None):
        """Search sales for return"""
        search_term = self.return_search_entry.get().strip()
        
        # Clear existing items
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        if search_term:
            # Search by sale ID or medicine name/batch
            self.cursor.execute("""
                SELECT s.id, s.date, m.name, s.qty, s.type, s.price, s.total
                FROM sales s
                JOIN medicines m ON s.medicine_id = m.id
                WHERE s.id LIKE ? OR m.name LIKE ? OR m.batch LIKE ?
                ORDER BY s.date DESC
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        else:
            # Load recent sales
            self.cursor.execute("""
                SELECT s.id, s.date, m.name, s.qty, s.type, s.price, s.total
                FROM sales s
                JOIN medicines m ON s.medicine_id = m.id
                ORDER BY s.date DESC
                LIMIT 50
            """)
        
        sales = self.cursor.fetchall()
        
        for sale in sales:
            self.sales_tree.insert('', tk.END, values=(
                sale[0], sale[1], sale[2], sale[3], sale[4], f"${sale[5]:.2f}", f"${sale[6]:.2f}"
            ))

    def process_return(self):
        """Process a return"""
        selection = self.sales_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a sale to return")
            return
        
        try:
            # Get selected sale
            item = self.sales_tree.item(selection[0])
            values = item['values']
            sale_id = values[0]
            
            # Get return quantity
            return_qty = int(self.return_qty_entry.get() or 0)
            if return_qty <= 0:
                messagebox.showerror("Error", "Please enter a valid return quantity")
                return
            
            # Check if return quantity exceeds sold quantity
            self.cursor.execute("SELECT qty, type, price, medicine_id FROM sales WHERE id = ?", (sale_id,))
            sale = self.cursor.fetchone()
            
            if not sale:
                messagebox.showerror("Error", "Sale record not found")
                return
            
            sold_qty, sale_type, price, medicine_id = sale
            
            if return_qty > sold_qty:
                messagebox.showerror("Error", f"Return quantity cannot exceed sold quantity ({sold_qty})")
                return
            
            # Calculate refunded amount
            refunded_amount = return_qty * price
            
            # Get reason
            reason = self.return_reason_entry.get().strip()
            
            # Insert return record
            self.cursor.execute("""
                INSERT INTO returns (sale_id, medicine_id, return_date, return_qty, return_type, reason, refunded_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (sale_id, medicine_id, datetime.now(), return_qty, sale_type, reason, refunded_amount))
            
            # Update medicine stock
            if sale_type == "Pack":
                self.cursor.execute("""
                    UPDATE medicines 
                    SET stock_packs = stock_packs + ? 
                    WHERE id = ?
                """, (return_qty, medicine_id))
            else:  # Unit
                # Get medicine details to calculate packs and units
                self.cursor.execute("SELECT stock_packs, units_per_pack FROM medicines WHERE id = ?", (medicine_id,))
                result = self.cursor.fetchone()
                if result:
                    stock_packs, units_per_pack = result
                    total_units = stock_packs * units_per_pack
                    new_units = total_units + return_qty
                    
                    # Calculate new packs and units
                    new_packs = new_units // units_per_pack
                    new_units_remaining = new_units % units_per_pack
                    
                    self.cursor.execute("""
                        UPDATE medicines 
                        SET stock_packs = ? 
                        WHERE id = ?
                    """, (new_packs, medicine_id))
            
            self.conn.commit()
            
            # Show receipt
            receipt = "===== RETURN RECEIPT =====\n"
            receipt += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            receipt += f"Invoice No: {sale_id}\n"
            receipt += f"Medicine: {values[2]}\n"
            receipt += f"Returned: {return_qty} {sale_type}(s)\n"
            receipt += f"Refunded Amount: ${refunded_amount:.2f}\n"
            receipt += "=" * 30 + "\n"
            receipt += "Thank you!"
            
            messagebox.showinfo("Return Processed", receipt)
            
            # Clear form
            self.return_qty_entry.delete(0, tk.END)
            self.return_reason_entry.delete(0, tk.END)
            
            # Refresh dashboard
            self.refresh_dashboard()
            
            # Reload medicines
            if hasattr(self, 'medicines_tree'):
                self.load_medicines()
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid return quantity")
        except Exception as e:
            messagebox.showerror("Error", f"Return processing failed: {str(e)}")

    def cancel_return(self):
        """Cancel return operation"""
        self.return_qty_entry.delete(0, tk.END)
        self.return_reason_entry.delete(0, tk.END)

    def create_reports_tab(self):
        """Create the reports tab"""
        self.reports_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(self.reports_frame, text="Reports")
        
        # Report options frame with modern styling
        options_frame = tk.LabelFrame(self.reports_frame, text="Report Options", 
                                     font=('Segoe UI', 12, 'bold'), bg='#f0f0f0', fg='#2c3e50',
                                     relief=tk.RAISED, bd=2)
        options_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Date range with modern styling
        tk.Label(options_frame, text="From:", font=('Segoe UI', 10), bg='#f0f0f0').grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.from_date_entry = ttk.Entry(options_frame, style='Modern.TEntry')
        self.from_date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.from_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        tk.Label(options_frame, text="To:", font=('Segoe UI', 10), bg='#f0f0f0').grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.to_date_entry = ttk.Entry(options_frame, style='Modern.TEntry')
        self.to_date_entry.grid(row=0, column=3, padx=5, pady=5)
        self.to_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Report type with modern styling
        tk.Label(options_frame, text="Report Type:", font=('Segoe UI', 10), bg='#f0f0f0').grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.report_type_var = tk.StringVar(value="Daily Sales")
        report_types = ["Daily Sales", "Monthly Sales", "Stock Summary", "Expired Medicines", "Returns Report"]
        self.report_type_menu = ttk.Combobox(options_frame, textvariable=self.report_type_var, 
                                           values=report_types, state="readonly", 
                                           font=('Segoe UI', 10), width=20)
        self.report_type_menu.grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons with modern styling
        buttons_frame = tk.Frame(options_frame, bg='#f0f0f0')
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=15)
        
        view_btn = ttk.Button(buttons_frame, text="View Report", command=self.view_report, 
                             style='Action.TButton')
        view_btn.pack(side=tk.LEFT, padx=5)
        
        excel_btn = ttk.Button(buttons_frame, text="Export Excel", command=self.export_excel, 
                              style='Modern.TButton')
        excel_btn.pack(side=tk.LEFT, padx=5)
        
        pdf_btn = ttk.Button(buttons_frame, text="Export PDF", command=self.export_pdf, 
                            style='Modern.TButton')
        pdf_btn.pack(side=tk.LEFT, padx=5)
        
        # Report display area with modern styling
        report_display_frame = tk.LabelFrame(self.reports_frame, text="Report", 
                                            font=('Segoe UI', 12, 'bold'), bg='#f0f0f0', fg='#2c3e50',
                                            relief=tk.RAISED, bd=2)
        report_display_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Text widget for report display with modern styling
        self.report_text = tk.Text(report_display_frame, wrap=tk.WORD, font=('Courier New', 10),
                                  bg='white', fg='#2c3e50')
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        report_scrollbar = ttk.Scrollbar(report_display_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        report_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_text.configure(yscrollcommand=report_scrollbar.set)

    def view_report(self):
        """View selected report"""
        report_type = self.report_type_var.get()
        from_date = self.from_date_entry.get().strip()
        to_date = self.to_date_entry.get().strip()
        
        if not from_date or not to_date:
            messagebox.showerror("Error", "Please enter both from and to dates")
            return
        
        self.report_text.delete(1.0, tk.END)
        
        try:
            if report_type == "Daily Sales":
                self.cursor.execute("""
                    SELECT date, SUM(total) as daily_total
                    FROM sales
                    WHERE date BETWEEN ? AND ?
                    GROUP BY date(date)
                    ORDER BY date
                """, (from_date, f"{to_date} 23:59:59"))
                
                results = self.cursor.fetchall()
                
                report = "===== DAILY SALES REPORT =====\n"
                report += f"Period: {from_date} to {to_date}\n\n"
                report += "Date\t\tSales Amount\n"
                report += "-" * 40 + "\n"
                
                total = 0
                for row in results:
                    report += f"{row[0][:10]}\t${row[1]:.2f}\n"
                    total += row[1]
                
                report += "-" * 40 + "\n"
                report += f"TOTAL:\t\t${total:.2f}\n"
                self.report_text.insert(1.0, report)
                
            elif report_type == "Monthly Sales":
                self.cursor.execute("""
                    SELECT strftime('%Y-%m', date) as month, SUM(total) as monthly_total
                    FROM sales
                    WHERE date BETWEEN ? AND ?
                    GROUP BY strftime('%Y-%m', date)
                    ORDER BY month
                """, (from_date, f"{to_date} 23:59:59"))
                
                results = self.cursor.fetchall()
                
                report = "===== MONTHLY SALES REPORT =====\n"
                report += f"Period: {from_date} to {to_date}\n\n"
                report += "Month\t\tSales Amount\n"
                report += "-" * 40 + "\n"
                
                total = 0
                for row in results:
                    report += f"{row[0]}\t${row[1]:.2f}\n"
                    total += row[1]
                
                report += "-" * 40 + "\n"
                report += f"TOTAL:\t\t${total:.2f}\n"
                self.report_text.insert(1.0, report)
                
            elif report_type == "Stock Summary":
                self.cursor.execute("""
                    SELECT name, batch, expiry, stock_packs, units_per_pack, pack_price
                    FROM medicines
                    ORDER BY name
                """)
                
                results = self.cursor.fetchall()
                
                report = "===== STOCK SUMMARY REPORT =====\n\n"
                report += "Medicine\t\tBatch\t\tExpiry\t\tStock\tUnits\tPrice\n"
                report += "-" * 80 + "\n"
                
                for row in results:
                    total_units = row[3] * row[4]
                    report += f"{row[0][:15]}\t{row[1]}\t{row[2]}\t{row[3]}\t{total_units}\t${row[5]:.2f}\n"
                
                self.report_text.insert(1.0, report)
                
            elif report_type == "Expired Medicines":
                self.cursor.execute("""
                    SELECT name, batch, expiry, stock_packs
                    FROM medicines
                    WHERE expiry < date('now')
                    ORDER BY expiry
                """)
                
                results = self.cursor.fetchall()
                
                report = "===== EXPIRED MEDICINES REPORT =====\n\n"
                report += "Medicine\t\tBatch\t\tExpiry\t\tStock\n"
                report += "-" * 60 + "\n"
                
                for row in results:
                    report += f"{row[0][:15]}\t{row[1]}\t{row[2]}\t{row[3]}\n"
                
                self.report_text.insert(1.0, report)
                
            elif report_type == "Returns Report":
                self.cursor.execute("""
                    SELECT r.return_date, m.name, r.return_qty, r.return_type, r.refunded_amount, r.reason
                    FROM returns r
                    JOIN medicines m ON r.medicine_id = m.id
                    WHERE r.return_date BETWEEN ? AND ?
                    ORDER BY r.return_date
                """, (from_date, f"{to_date} 23:59:59"))
                
                results = self.cursor.fetchall()
                
                report = "===== RETURNS REPORT =====\n"
                report += f"Period: {from_date} to {to_date}\n\n"
                report += "Date\t\tMedicine\t\tQty\tType\tAmount\tReason\n"
                report += "-" * 80 + "\n"
                
                total_refunded = 0
                for row in results:
                    reason = row[5] if row[5] else "N/A"
                    report += f"{row[0][:10]}\t{row[1][:15]}\t{row[2]}\t{row[3]}\t${row[4]:.2f}\t{reason[:20]}\n"
                    total_refunded += row[4]
                
                report += "-" * 80 + "\n"
                report += f"TOTAL REFUNDED:\t\t\t\t\t${total_refunded:.2f}\n"
                self.report_text.insert(1.0, report)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")

    def export_excel(self):
        """Export report to Excel"""
        messagebox.showinfo("Export", "Excel export functionality would be implemented here.\nThis requires additional libraries like openpyxl or xlsxwriter.")

    def export_pdf(self):
        """Export report to PDF"""
        messagebox.showinfo("Export", "PDF export functionality would be implemented here.\nThis requires additional libraries like reportlab or fpdf.")

    def create_settings_tab(self):
        """Create the settings tab for receipt configuration"""
        self.settings_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Settings title with modern styling
        title_label = ttk.Label(self.settings_frame, text="Receipt Settings", style='Header.TLabel')
        title_label.pack(pady=(20, 30))
        
        # Settings form frame with modern styling
        form_frame = tk.LabelFrame(self.settings_frame, text="Receipt Configuration", 
                                  font=('Segoe UI', 12, 'bold'), bg='#f8f9fa', fg='#2c3e50',
                                  relief=tk.RAISED, bd=2)
        form_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Pharmacy name
        tk.Label(form_frame, text="Pharmacy Name:", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=0, column=0, sticky=tk.W, padx=5, pady=10)
        self.pharmacy_name_entry = ttk.Entry(form_frame, width=50, style='Modern.TEntry')
        self.pharmacy_name_entry.grid(row=0, column=1, padx=5, pady=10)
        
        # Pharmacy address
        tk.Label(form_frame, text="Pharmacy Address:", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=1, column=0, sticky=tk.W, padx=5, pady=10)
        self.pharmacy_address_entry = ttk.Entry(form_frame, width=50, style='Modern.TEntry')
        self.pharmacy_address_entry.grid(row=1, column=1, padx=5, pady=10)
        
        # Pharmacy phone
        tk.Label(form_frame, text="Pharmacy Phone:", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=2, column=0, sticky=tk.W, padx=5, pady=10)
        self.pharmacy_phone_entry = ttk.Entry(form_frame, width=50, style='Modern.TEntry')
        self.pharmacy_phone_entry.grid(row=2, column=1, padx=5, pady=10)
        
        # Receipt header
        tk.Label(form_frame, text="Receipt Header:", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=3, column=0, sticky=tk.W, padx=5, pady=10)
        self.receipt_header_entry = ttk.Entry(form_frame, width=50, style='Modern.TEntry')
        self.receipt_header_entry.grid(row=3, column=1, padx=5, pady=10)
        
        # Receipt footer
        tk.Label(form_frame, text="Receipt Footer:", font=('Segoe UI', 10), bg='#f8f9fa', fg='#34495e').grid(row=4, column=0, sticky=tk.W, padx=5, pady=10)
        self.receipt_footer_entry = ttk.Entry(form_frame, width=50, style='Modern.TEntry')
        self.receipt_footer_entry.grid(row=4, column=1, padx=5, pady=10)
        
        # Buttons frame with modern styling
        buttons_frame = tk.Frame(form_frame, bg='#f8f9fa')
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=30)
        
        load_btn = ttk.Button(buttons_frame, text="Load Settings", command=self.load_settings, 
                             style='Modern.TButton')
        load_btn.pack(side=tk.LEFT, padx=10)
        
        save_btn = ttk.Button(buttons_frame, text="Save Settings", command=self.save_settings, 
                             style='Action.TButton')
        save_btn.pack(side=tk.LEFT, padx=10)
        
        # Load settings when tab is created
        self.load_settings()
        
        # Only enable settings tab for Admin users
        self.notebook.tab(self.settings_frame, state='disabled')

    def load_settings(self):
        """Load receipt settings from database"""
        try:
            self.cursor.execute("SELECT * FROM settings WHERE id = 1")
            settings = self.cursor.fetchone()
            
            if settings:
                self.pharmacy_name_entry.delete(0, tk.END)
                self.pharmacy_name_entry.insert(0, settings[1])
                
                self.pharmacy_address_entry.delete(0, tk.END)
                self.pharmacy_address_entry.insert(0, settings[2])
                
                self.pharmacy_phone_entry.delete(0, tk.END)
                self.pharmacy_phone_entry.insert(0, settings[3])
                
                self.receipt_header_entry.delete(0, tk.END)
                self.receipt_header_entry.insert(0, settings[4])
                
                self.receipt_footer_entry.delete(0, tk.END)
                self.receipt_footer_entry.insert(0, settings[5])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {str(e)}")

    def save_settings(self):
        """Save receipt settings to database"""
        try:
            pharmacy_name = self.pharmacy_name_entry.get().strip()
            pharmacy_address = self.pharmacy_address_entry.get().strip()
            pharmacy_phone = self.pharmacy_phone_entry.get().strip()
            receipt_header = self.receipt_header_entry.get().strip()
            receipt_footer = self.receipt_footer_entry.get().strip()
            
            # Update settings in database
            self.cursor.execute("""
                UPDATE settings 
                SET pharmacy_name = ?, pharmacy_address = ?, pharmacy_phone = ?, receipt_header = ?, receipt_footer = ?
                WHERE id = 1
            """, (pharmacy_name, pharmacy_address, pharmacy_phone, receipt_header, receipt_footer))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Settings saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        # Global shortcuts
        self.root.bind('<Control-l>', lambda e: self.show_login())
        self.root.bind('<Control-q>', lambda e: self.exit_app())
        self.root.bind('<Control-d>', lambda e: self.notebook.select(self.dashboard_frame))
        self.root.bind('<Control-m>', lambda e: self.notebook.select(self.medicines_frame))
        self.root.bind('<Control-s>', lambda e: self.notebook.select(self.sales_frame))
        self.root.bind('<Control-r>', lambda e: self.notebook.select(self.returns_frame))
        self.root.bind('<Control-p>', lambda e: self.notebook.select(self.reports_frame))
        
        # Dashboard shortcuts
        self.root.bind('<Control-D>', lambda e: self.notebook.select(self.dashboard_frame))
        
        # Medicines shortcuts
        self.root.bind('<Control-n>', lambda e: self.clear_medicine_form())
        self.root.bind('<Control-a>', lambda e: self.add_medicine())
        self.root.bind('<Control-e>', lambda e: self.update_medicine())
        self.root.bind('<Control-Delete>', lambda e: self.delete_medicine())
        self.root.bind('<Control-f>', lambda e: self.search_entry.focus_set())
        
        # Sales shortcuts
        self.root.bind('<Control-c>', lambda e: self.checkout())
        self.root.bind('<Control-u>', lambda e: self.sale_type_var.set("Unit"))
        self.root.bind('<Control-k>', lambda e: self.sale_type_var.set("Pack"))
        
        # Returns shortcuts
        # (Ctrl+F already bound for search)
        # (Enter and Esc already handled by default behavior)
        
        # Reports shortcuts
        self.root.bind('<Control-Shift-D>', lambda e: [self.report_type_var.set("Daily Sales"), self.view_report()])
        self.root.bind('<Control-Shift-M>', lambda e: [self.report_type_var.set("Monthly Sales"), self.view_report()])
        self.root.bind('<Control-Shift-X>', lambda e: self.export_excel())
        self.root.bind('<Control-Shift-P>', lambda e: self.export_pdf())

    def show_login(self):
        """Show login dialog"""
        # Create login window
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login")
        self.login_window.geometry("350x250")
        self.login_window.resizable(False, False)
        self.login_window.transient(self.root)
        self.login_window.grab_set()
        self.login_window.configure(bg='#f8f9fa')
        
        # Center window
        self.login_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Login title
        title_label = ttk.Label(self.login_window, text="Pharmacy POS Login", style='Header.TLabel')
        title_label.pack(pady=(20, 20))
        
        # Login form frame
        form_frame = tk.Frame(self.login_window, bg='#f8f9fa')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # Username
        tk.Label(form_frame, text="Username:", font=('Segoe UI', 11), bg='#f8f9fa', fg='#34495e').pack(pady=(10, 5))
        self.username_entry = ttk.Entry(form_frame, font=('Segoe UI', 11), width=25, style='Modern.TEntry')
        self.username_entry.pack(pady=5)
        self.username_entry.focus_set()
        
        # Password
        tk.Label(form_frame, text="Password:", font=('Segoe UI', 11), bg='#f8f9fa', fg='#34495e').pack(pady=(15, 5))
        self.password_entry = ttk.Entry(form_frame, show="*", font=('Segoe UI', 11), width=25, style='Modern.TEntry')
        self.password_entry.pack(pady=5)
        
        # Login button
        login_btn = ttk.Button(form_frame, text="Login", command=self.login, style='Action.TButton')
        login_btn.pack(pady=25)
        
        # Bind Enter key to login
        self.login_window.bind('<Return>', lambda e: self.login())
        
        # Make login window modal
        self.login_window.wait_window()

    def login(self):
        """Process login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        # Check credentials
        self.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = self.cursor.fetchone()
        
        if user:
            self.current_user = user
            self.status_label.config(text=f"Logged in as: {user[1]} ({user[3]})")
            self.login_window.destroy()
            
            # Enable all tabs for Admin
            if user[3] == "Admin":
                self.notebook.tab(self.medicines_frame, state='normal')
                self.notebook.tab(self.sales_frame, state='normal')
                self.notebook.tab(self.returns_frame, state='normal')
                self.notebook.tab(self.reports_frame, state='normal')
                self.notebook.tab(self.settings_frame, state='normal')  # Enable settings for Admin
            # Enable limited tabs for Pharmacist
            elif user[3] == "Pharmacist":
                self.notebook.tab(self.medicines_frame, state='normal')
                self.notebook.tab(self.sales_frame, state='normal')
                self.notebook.tab(self.returns_frame, state='normal')
                self.notebook.tab(self.reports_frame, state='disabled')
                self.notebook.tab(self.settings_frame, state='disabled')  # Disable settings for Pharmacist
            # Enable only sales for Cashier
            else:  # Cashier
                self.notebook.tab(self.medicines_frame, state='disabled')
                self.notebook.tab(self.sales_frame, state='normal')
                self.notebook.tab(self.returns_frame, state='disabled')
                self.notebook.tab(self.reports_frame, state='disabled')
                self.notebook.tab(self.settings_frame, state='disabled')  # Disable settings for Cashier
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def logout(self):
        """Logout current user"""
        self.current_user = None
        self.status_label.config(text="Not logged in")
        
        # Disable all tabs
        self.notebook.tab(self.medicines_frame, state='disabled')
        self.notebook.tab(self.sales_frame, state='disabled')
        self.notebook.tab(self.returns_frame, state='disabled')
        self.notebook.tab(self.reports_frame, state='disabled')
        
        # Show login
        self.show_login()

    def backup_database(self):
        """Backup database"""
        try:
            import shutil
            backup_name = f"pharmacy_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2("pharmacy.db", backup_name)
            messagebox.showinfo("Backup", f"Database backed up successfully as {backup_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")

    def manage_users(self):
        """Manage users (Admin only)"""
        if not self.current_user or self.current_user[3] != "Admin":
            messagebox.showerror("Error", "Access denied. Admin rights required.")
            return
        
        messagebox.showinfo("Manage Users", "User management functionality would be implemented here.")

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Pharmacy POS System\\nVersion 1.0\\n\\nBuilt with Python and Tkinter")

    def exit_app(self):
        """Exit the application"""
        result = messagebox.askyesno("Exit", "Are you sure you want to exit?")
        if result:
            self.conn.close()
            self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = PharmacyPOS(root)
    root.mainloop()