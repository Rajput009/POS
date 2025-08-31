#!/usr/bin/env python3
"""
Test script to verify that batch numbers are optional in the Pharmacy POS system.
"""

import sqlite3
import os

def test_batch_optional():
    """Test that medicines can be added without batch numbers"""
    # Connect to the database
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    
    # Test inserting a medicine without batch number
    try:
        cursor.execute("""
            INSERT INTO medicines (name, batch, expiry, stock_packs, units_per_pack, pack_price, unit_price, supplier)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Test Medicine", "", "2025-12-31", 10, 10, 25.0, 2.5, "Test Supplier"))
        
        conn.commit()
        print("✓ Successfully inserted medicine without batch number")
        
        # Verify the insertion
        cursor.execute("SELECT * FROM medicines WHERE name = ?", ("Test Medicine",))
        result = cursor.fetchone()
        
        if result:
            print(f"✓ Medicine retrieved: {result[1]} with batch: '{result[2]}'")
            # Clean up test data
            cursor.execute("DELETE FROM medicines WHERE name = ?", ("Test Medicine",))
            conn.commit()
            print("✓ Test data cleaned up")
        else:
            print("✗ Failed to retrieve inserted medicine")
            
    except Exception as e:
        print(f"✗ Error testing batch optional: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_batch_optional()