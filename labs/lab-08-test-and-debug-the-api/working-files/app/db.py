from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[1] / "northstar.db"


def database_path() -> Path:
    return Path(os.getenv("APP_DATABASE", str(DEFAULT_DB))).expanduser().resolve()


@contextmanager
def connect(path: Path | None = None):
    conn = sqlite3.connect(path or database_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE CHECK(length(sku) BETWEEN 3 AND 24),
    name TEXT NOT NULL CHECK(length(name) BETWEEN 3 AND 120),
    description TEXT NOT NULL DEFAULT '',
    price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK(stock_quantity >= 0),
    status TEXT NOT NULL DEFAULT 'active'
        CHECK(status IN ('active','inactive','discontinued')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK(length(name) BETWEEN 2 AND 120),
    email TEXT NOT NULL UNIQUE,
    company TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    status TEXT NOT NULL DEFAULT 'paid'
        CHECK(status IN ('pending','paid','fulfilled','cancelled')),
    total_cents INTEGER NOT NULL DEFAULT 0 CHECK(total_cents >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_price_cents INTEGER NOT NULL CHECK(unit_price_cents >= 0),
    UNIQUE(order_id, product_id)
);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
"""


def init_db(path: Path | None = None, *, seed: bool = False) -> None:
    with connect(path) as conn:
        conn.executescript(SCHEMA)
        if seed and conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO products(sku,name,description,price_cents,stock_quantity,status) VALUES(?,?,?,?,?,?)",
                [
                    ("NS-LAMP-01", "Orbit Desk Lamp", "Adjustable task light", 8900, 18, "active"),
                    ("NS-MUG-02", "Field Notes Mug", "Stoneware studio mug", 2600, 35, "active"),
                    ("NS-STAND-03", "Arc Laptop Stand", "Aluminium workspace stand", 7200, 11, "active"),
                ],
            )
            conn.execute(
                "INSERT INTO customers(name,email,company) VALUES(?,?,?)",
                ("Aisha Rahman", "aisha@example.com", "Marina Studio"),
            )
