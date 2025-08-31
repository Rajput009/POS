#!/usr/bin/env python3
"""
Test script to verify the receipt printing system in the Pharmacy POS application.
"""

import sqlite3
import os

def test_settings_table():
    """Test that the settings table exists and has the correct structure"""
    # Connect to the database
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    
    try:
        # Check if settings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
        result = cursor.fetchone()
        
        if result:
            print("✓ Settings table exists")
            
            # Check table structure
            cursor.execute("PRAGMA table_info(settings)")
            columns = cursor.fetchall()
            
            expected_columns = ['id', 'pharmacy_name', 'pharmacy_address', 'pharmacy_phone', 'receipt_header', 'receipt_footer']
            actual_columns = [col[1] for col in columns]
            
            if all(col in actual_columns for col in expected_columns):
                print("✓ Settings table has correct structure")
                
                # Check if default settings exist
                cursor.execute("SELECT * FROM settings WHERE id = 1")
                settings = cursor.fetchone()
                
                if settings:
                    print("✓ Default settings exist")
                    print(f"  Pharmacy Name: {settings[1]}")
                    print(f"  Pharmacy Address: {settings[2]}")
                    print(f"  Pharmacy Phone: {settings[3]}")
                else:
                    print("✗ Default settings not found")
            else:
                print("✗ Settings table structure is incorrect")
                print(f"  Expected: {expected_columns}")
                print(f"  Actual: {actual_columns}")
        else:
            print("✗ Settings table does not exist")
            
    except Exception as e:
        print(f"✗ Error testing settings table: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_settings_table()