"""
reset_db.py — safely resets your ShopFlow database.

Drops all dependent views first, then all tables defined by SQLAlchemy models.
Use this in development environments (⚠️ destructive operation).
"""

import os
from sqlalchemy import text, create_engine
from config.config import load_config
from src.scripts.db_setup import Base

# ============================================================
# Load configuration and connect to database
# ============================================================

config = load_config(env=os.environ.get("ENV", "dev"))
db_conf = config["database"]

DB_URL = (
    f"postgresql+psycopg2://{db_conf['user']}:{db_conf['password']}@"
    f"{db_conf['host']}:{db_conf['port']}/{db_conf['name']}"
)

print(f"🔗 Using DB_URL: {DB_URL}")

engine = create_engine(DB_URL, echo=False, future=True)


# ============================================================
# Utility functions
# ============================================================

def drop_all_views(engine):
    """Drop all SQL views that depend on application tables."""
    print("⚠️ Dropping all dependent views if they exist...")
    with engine.connect() as conn:
        conn.execute(text("""
            DROP VIEW IF EXISTS
                vw_product_sales,
                vw_monthly_revenue,
                vw_avg_order_value_by_country,
                vw_customer_lifetime_value,
                vw_category_performance
            CASCADE;
        """))
        conn.commit()
    print("✅ All dependent views dropped.")


def drop_all_tables(engine):
    """Drop all SQLAlchemy-managed tables."""
    print("⚠️ Dropping all tables defined by models...")
    Base.metadata.drop_all(engine)
    print("✅ All tables dropped successfully.")

# ============================================================
# Main execution
# ============================================================

if __name__ == "__main__":
    print("🚀 Starting database reset...")
    try:
        # Option 1 (safe): drop views first, then tables
        drop_all_views(engine)
        drop_all_tables(engine)

        print("🎯 Database reset complete.")
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
