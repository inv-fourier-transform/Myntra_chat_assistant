import pandas as pd
import sqlite3

# Database and CSV file paths
db_path = 'myntra_db.sqlite'
csv_path = "C:/Users/Inspire/Code/Gen AI/Myntra_chat_assistant/app/resources/myntra_sports_shoes_20251011.csv"

# Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop existing table to avoid schema mismatch
cursor.execute('DROP TABLE IF EXISTS product;')

# Recreate the table with the correct schema
cursor.execute('''
CREATE TABLE product (    
    title TEXT,
    brand TEXT,
    gender TEXT,
    mrp INTEGER,
    discount_percent FLOAT,
    price_after_discount INTEGER,
    star_rating FLOAT,
    num_ratings INTEGER,
    product_link TEXT,
    scraped_on DATETIME
);
''')

conn.commit()

# Read CSV file
df = pd.read_csv(csv_path)

# Insert data
df.to_sql('product', conn, if_exists='replace', index=False)

conn.close()

print("✅ Data inserted successfully!")
