import os
from sqlalchemy import (
    create_engine, Column, Integer, UniqueConstraint, String, Float, DateTime,
    ForeignKey, Index, func, text
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.exc import OperationalError
from config.config import load_config

# ---------- Load Configuration ----------
config = load_config(env="dev")  # Always load dev.yaml
db_conf = config["database"]

DB_URL = (
    f"postgresql+psycopg2://{db_conf['user']}:{db_conf['password']}@"
    f"{db_conf['host']}:{db_conf['port']}/{db_conf['name']}"
)

# ---------- Initialize Engine and Base ----------
engine = create_engine(DB_URL, echo=False, future=True)
Base = declarative_base()
metadata = Base.metadata

# ============================================================
#                        MODELS
# ============================================================

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    products = relationship("Product", back_populates="supplier")


class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    id = Column(Integer, primary_key=True)
    method = Column(String(100), unique=True, nullable=False)
    transactions = relationship("Transaction", back_populates="payment_method")


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    registration_date = Column(DateTime, default=func.now())
    country = Column(String(100))
    transactions = relationship("Transaction", back_populates="customer")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(100), index=True)
    price = Column(Float, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    supplier = relationship("Supplier", back_populates="products")
    transaction_items = relationship("TransactionItem", back_populates="product")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    timestamp = Column(DateTime, default=func.now(), index=True)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"))
    customer = relationship("Customer", back_populates="transactions")
    payment_method = relationship("PaymentMethod", back_populates="transactions")
    items = relationship("TransactionItem", back_populates="transaction")


class TransactionItem(Base):
    __tablename__ = "transaction_items"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("transaction_id", "product_id", name="uix_transaction_product"),
    )

    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product", back_populates="transaction_items")


# ---------- Indexes ----------
Index("idx_transactions_customer", Transaction.customer_id)
Index("idx_transactions_timestamp", Transaction.timestamp)
Index("idx_transaction_items_product", TransactionItem.product_id)

# ============================================================
#                      ANALYTICS VIEWS
# ============================================================

def create_views():
    """Create common analytics views in PostgreSQL."""
    views_sql = """
    -- Product Sales Summary
    CREATE OR REPLACE VIEW vw_product_sales AS
    SELECT
        p.id AS product_id,
        p.name AS product_name,
        p.category,
        SUM(ti.quantity) AS total_quantity_sold,
        ROUND(SUM(ti.quantity * p.price)::numeric, 2) AS total_revenue
    FROM transaction_items ti
    JOIN products p ON ti.product_id = p.id
    JOIN transactions t ON ti.transaction_id = t.id
    GROUP BY p.id, p.name, p.category
    ORDER BY total_revenue DESC;

    -- Monthly Revenue
    CREATE OR REPLACE VIEW vw_monthly_revenue AS
    SELECT 
        DATE_TRUNC('month', t.timestamp)::DATE AS month,
        ROUND(SUM(ti.quantity * p.price)::numeric, 2) AS total_revenue
    FROM transactions t
    JOIN transaction_items ti ON t.id = ti.transaction_id
    JOIN products p ON ti.product_id = p.id
    GROUP BY month
    ORDER BY month;

    -- Average Order Value by Country
    CREATE OR REPLACE VIEW vw_avg_order_value_by_country AS
    SELECT 
        country,
        ROUND(AVG(order_value)::numeric, 2) AS avg_order_value
    FROM (
        SELECT 
            t.id AS transaction_id,
            c.country,
            SUM(ti.quantity * p.price) AS order_value
        FROM transactions t
        JOIN customers c ON t.customer_id = c.id
        JOIN transaction_items ti ON t.id = ti.transaction_id
        JOIN products p ON ti.product_id = p.id
        GROUP BY t.id, c.country
    ) AS country_orders
    GROUP BY country
    ORDER BY avg_order_value DESC;

    -- Customer Lifetime Value
    CREATE OR REPLACE VIEW vw_customer_lifetime_value AS
    SELECT 
        c.id AS customer_id,
        c.name AS customer_name,
        c.email,
        c.country,
        ROUND(SUM(ti.quantity * p.price)::numeric, 2) AS total_spent,
        COUNT(DISTINCT t.id) AS total_orders
    FROM customers c
    JOIN transactions t ON c.id = t.customer_id
    JOIN transaction_items ti ON t.id = ti.transaction_id
    JOIN products p ON ti.product_id = p.id
    GROUP BY c.id, c.name, c.email, c.country
    ORDER BY total_spent DESC;

    -- Category Performance
    CREATE OR REPLACE VIEW vw_category_performance AS
    SELECT
        p.category,
        ROUND(SUM(ti.quantity * p.price)::numeric, 2) AS total_revenue,
        SUM(ti.quantity) AS total_units_sold,
        COUNT(DISTINCT t.id) AS total_orders
    FROM transaction_items ti
    JOIN products p ON ti.product_id = p.id
    JOIN transactions t ON ti.transaction_id = t.id
    GROUP BY p.category
    ORDER BY total_revenue DESC;
    """

    with engine.connect() as conn:
        print("📊 Creating analytics views...")
        conn.execute(text(views_sql))
        conn.commit()
        print("✅ Analytics views created successfully!")

# ============================================================
#                      INITIALIZATION
# ============================================================

def init_db():
    """Create all tables and indexes in the AWS RDS database."""
    print("🚀 Connecting to AWS RDS...")
    print(f"🔗 {DB_URL}")
    try:
        Base.metadata.create_all(engine)
        print("✅ Database schema created successfully on AWS RDS!")

        # Create analytics views
        create_views()

    except OperationalError as e:
        print("❌ Failed to connect to AWS RDS database:")
        print(str(e))


# ============================================================
#                        MAIN
# ============================================================

if __name__ == "__main__":
    init_db()
