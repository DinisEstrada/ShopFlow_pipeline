-- ============================================================
-- Basic E-Commerce Analytics (PostgreSQL)
-- ============================================================

-- ============================================================
-- 0️⃣ CREATE TABLES
-- ============================================================
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    registration_date DATE,
    country TEXT
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    category TEXT,
    price NUMERIC(10, 2),
    supplier TEXT
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    product_id INT REFERENCES products(id),
    quantity INT,
    timestamp TIMESTAMP,
    payment_method TEXT
);

-- ============================================================
-- 1️⃣ LOAD DATA FROM CSV FILES
-- ============================================================
-- ⚠️ Adjust file paths for your environment
-- (Example assumes project root path and PostgreSQL has access)

\copy customers FROM 'data/raw/customers.csv' DELIMITER ',' CSV HEADER;
\copy products FROM 'data/raw/products.csv' DELIMITER ',' CSV HEADER;
\copy transactions FROM 'data/raw/transactions.csv' DELIMITER ',' CSV HEADER;

-- ============================================================
-- 2️⃣ Top 10 Customers by Total Spending
-- ============================================================
SELECT 
    c.id AS customer_id,
    c.name AS customer_name,
    c.country,
    ROUND(SUM(t.quantity * p.price), 2) AS total_spent
FROM transactions t
JOIN customers c ON t.customer_id = c.id
JOIN products p ON t.product_id = p.id
GROUP BY c.id, c.name, c.country
ORDER BY total_spent DESC
LIMIT 10;

-- ============================================================
-- 3️⃣ Best-Selling Products by Category
-- ============================================================
SELECT 
    p.category,
    p.id AS product_id,
    p.name AS product_name,
    SUM(t.quantity) AS total_quantity_sold,
    ROUND(SUM(t.quantity * p.price), 2) AS total_revenue
FROM transactions t
JOIN products p ON t.product_id = p.id
GROUP BY p.category, p.id, p.name
ORDER BY p.category, total_quantity_sold DESC;

-- ============================================================
-- 4️⃣ Monthly Revenue Trends
-- ============================================================
SELECT 
    DATE_TRUNC('month', t.timestamp)::DATE AS month,
    ROUND(SUM(t.quantity * p.price), 2) AS total_revenue
FROM transactions t
JOIN products p ON t.product_id = p.id
GROUP BY month
ORDER BY month;

-- ============================================================
-- 5️⃣ Average Order Value by Country
-- ============================================================
SELECT 
    c.country,
    ROUND(AVG(order_value), 2) AS avg_order_value
FROM (
    SELECT 
        t.id AS transaction_id,
        c.country,
        SUM(t.quantity * p.price) AS order_value
    FROM transactions t
    JOIN customers c ON t.customer_id = c.id
    JOIN products p ON t.product_id = p.id
    GROUP BY t.id, c.country
) AS country_orders
GROUP BY country
ORDER BY avg_order_value DESC;
