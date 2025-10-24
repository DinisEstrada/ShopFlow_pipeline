import os
import csv
import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Set random seed for reproducibility
random.seed(42)
Faker.seed(42)

# Directory setup
DATA_DIR = "data/raw"
os.makedirs(DATA_DIR, exist_ok=True)

# --- CONFIG ---
NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 500
NUM_TRANSACTIONS = 5000

# --- Generate Customers ---
def generate_customers(n=NUM_CUSTOMERS):
    customers = []
    for i in range(1, n + 1):
        customers.append({
            "id": i,
            "name": fake.name(),
            "email": fake.email(),
            "registration_date": fake.date_between(start_date="-3y", end_date="today").isoformat(),
            "country": fake.country()
        })
    return customers

# --- Generate Products ---
def generate_products(n=NUM_PRODUCTS):
    categories = ["Electronics", "Clothing", "Home & Kitchen", "Books", "Sports", "Beauty", "Toys"]
    suppliers = ["Amazon", "BestBuy", "Target", "Walmart", "IKEA", "Nike", "Adidas"]
    products = []
    for i in range(1, n + 1):
        products.append({
            "id": i,
            "name": fake.word().capitalize() + " " + random.choice(categories),
            "category": random.choice(categories),
            "price": round(random.uniform(5.0, 500.0), 2),
            "supplier": random.choice(suppliers)
        })
    return products

# --- Generate Transactions ---
def generate_transactions(customers, products, n=NUM_TRANSACTIONS):
    payment_methods = ["Credit Card", "PayPal", "Debit Card", "Gift Card", "Crypto"]
    transactions = []
    for i in range(1, n + 1):
        customer = random.choice(customers)
        product = random.choice(products)
        transactions.append({
            "id": i,
            "customer_id": customer["id"],
            "product_id": product["id"],
            "quantity": random.randint(1, 5),
            "timestamp": (datetime.now() - timedelta(days=random.randint(0, 1000))).isoformat(),
            "payment_method": random.choice(payment_methods)
        })
    return transactions

# --- Save to CSV ---
def save_csv(filename, fieldnames, data):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Saved {filename} with {len(data)} records.")

# --- Main Function ---
def main():
    print("🔄 Generating synthetic e-commerce data...")

    customers = generate_customers()
    products = generate_products()
    transactions = generate_transactions(customers, products)

    save_csv("customers.csv", customers[0].keys(), customers)
    save_csv("products.csv", products[0].keys(), products)
    save_csv("transactions.csv", transactions[0].keys(), transactions)

    print("🎉 Data generation complete! Files saved in data/raw/")

if __name__ == "__main__":
    main()
