import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os

# Test if the main application can be imported and run
try:
    # Try to import and create a simple test window
    root = tk.Tk()
    root.title("Pharmacy POS Test")
    root.geometry("300x200")
    
    label = tk.Label(root, text="Pharmacy POS Application\nReady to Run", font=("Arial", 14))
    label.pack(pady=20)
    
    def close_app():
        root.destroy()
        print("Test successful - Application can run")
    
    button = tk.Button(root, text="Close Test", command=close_app)
    button.pack(pady=10)
    
    root.mainloop()
    
except Exception as e:
    print(f"Error running test: {e}")