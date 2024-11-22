import sqlite3
import csv

# ## Connectt to SQlite
connection=sqlite3.connect("synthetic.db")
conn=connection.cursor()

synthetic_product_info="""
CREATE TABLE IF NOT EXISTS synthetic_product_data (
    ProductID INTEGER PRIMARY KEY, 
    ProductName TEXT NOT NULL, 
    MerchantID INTEGER NOT NULL, 
    ClusterID INTEGER NOT NULL, 
    ClusterLabel TEXT NOT NULL, 
    CategoryID INTEGER NOT NULL, 
    Category TEXT NOT NULL, 
    Price REAL NOT NULL, 
    StockQuantity INTEGER NOT NULL, 
    Description TEXT, 
    Rating REAL
);"""

synthetic_orders_info="""
CREATE TABLE IF NOT EXISTS synthetic_orders_data (
    OrderID INTEGER PRIMARY KEY,
    ProductID INTEGER NOT NULL,
    ProductName TEXT NOT NULL,
    Category TEXT NOT NULL,
    CategoryID INTEGER NOT NULL,
    CustomerID INTEGER NOT NULL,
    OrderStatus TEXT NOT NULL,
    ReturnEligible BOOLEAN NOT NULL,
    ShippingDate DATE NOT NULL,
    FOREIGN KEY (ProductID) REFERENCES synthetic_product_data (ProductID)
);

# """
# Database and CSV file paths
db_file = "synthetic.db"
product_csv = r"C:\Users\ShashankTudum\Downloads\kata-event-datasets-20241113T102519Z-001\kata-event-datasets\synthetic-product-data.csv"
orders_csv = r"C:\Users\ShashankTudum\Downloads\kata-event-datasets-20241113T102519Z-001\kata-event-datasets\synthetic-orders-data.csv"

# Connect to the SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Function to import data into a table
def import_csv_to_table(csv_file, table_name, cursor):
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Skip the header row
        placeholders = ', '.join(['?'] * len(headers))  # Generate placeholders for values
        insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        
        # Insert all rows into the table
        for row in reader:
            cursor.execute(insert_query, row)

# Import data into synthetic_product_data
import_csv_to_table(product_csv, "synthetic_product_data", cursor)

# Import data into synthetic_orders_data
import_csv_to_table(orders_csv, "synthetic_orders_data", cursor)

# Commit changes using the connection object, not the cursor
conn.commit()
conn.close()

print("Data imported successfully!")
