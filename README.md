# Pharmacy POS System

A desktop Pharmacy Point of Sale application built with Python, Tkinter, and SQLite.

## Features

- Role-based login (Admin, Pharmacist, Cashier)
- Dashboard with key metrics
- Medicine management (add, edit, delete)
- Sales processing with cart functionality
- Return processing
- Reporting system
- Database backup
- Keyboard shortcuts for all operations
- **Batch numbers are now optional for medicines**
- **Professional receipt printing system with customizable header/footer**

## Requirements

- Python 3.6 or higher
- Tkinter (usually included with Python)
- SQLite (usually included with Python)

## Installation

1. Make sure you have Python installed on your system
2. No additional packages are required for basic functionality
3. For Excel/PDF export functionality, you would need to install additional libraries:
   ```
   pip install openpyxl xlsxwriter reportlab
   ```

## Running the Application

1. Save the `main.py` file in a directory
2. Run the application:
   ```
   python main.py
   ```

## Default Login

- Username: `admin`
- Password: `admin123`
- Role: Admin

## Keyboard Shortcuts

### Global Shortcuts
- `Ctrl+L` - Login/Logout
- `Ctrl+Q` - Quit App
- `Ctrl+D` - Dashboard
- `Ctrl+M` - Medicines
- `Ctrl+S` - Sales
- `Ctrl+R` - Returns
- `Ctrl+P` - Reports

### Dashboard
- `Ctrl+D` - Go to Dashboard

### Medicines
- `Ctrl+N` - New Medicine
- `Ctrl+A` - Add
- `Ctrl+E` - Edit/Update
- `Ctrl+Del` - Delete
- `Ctrl+F` - Focus Search

### Sales
- `Enter` - Add to Cart
- `Ctrl+C` - Checkout
- `Del` - Remove item
- `Ctrl+F` - Focus Search
- `Ctrl+U` - Sale by Unit
- `Ctrl+K` - Sale by Pack

### Returns
- `Ctrl+F` - Search
- `Enter` - Process Return
- `Esc` - Cancel Return

### Reports
- `Ctrl+Shift+D` - Daily Sales
- `Ctrl+Shift+M` - Monthly Sales
- `Ctrl+Shift+X` - Export Excel
- `Ctrl+Shift+P` - Export PDF

## Recent Changes

### Batch Numbers Now Optional
- Batch numbers are no longer required when adding or updating medicines
- The database schema has been updated to allow NULL values for batch numbers
- All forms and search functionality have been updated to handle optional batch numbers
- Display shows "N/A" when no batch number is available

### Professional Receipt Printing System
- Added a new Settings tab (Admin only) for customizing receipt header and footer
- Professional receipt formatting with aligned columns
- Receipt includes:
  - Custom pharmacy name, address, and phone
  - Invoice number and date/time
  - Cashier name
  - Itemized list with medicine name, quantity, price, and total
  - Subtotal, discounts, and final total
  - Custom header and footer messages
- Receipt dialog with options to:
  - Print directly
  - Save as PDF (currently saves as text file)
  - Close dialog

## Packaging with PyInstaller

To create a standalone executable:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Create the executable:
   ```
   pyinstaller --onefile --windowed main.py
   ```

3. The executable will be in the `dist` folder

## Database

The application uses SQLite and creates a `pharmacy.db` file in the same directory as the script.

Tables:
- `users` - User accounts and roles
- `medicines` - Medicine inventory
- `sales` - Sales transactions
- `returns` - Return transactions
- `settings` - Receipt configuration (pharmacy name, address, phone, header, footer)

## License

This project is open source and available under the MIT License.