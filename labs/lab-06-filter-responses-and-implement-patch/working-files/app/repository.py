from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from .db import connect

ALLOWED_PRODUCT_PATCH_FIELDS = {"name", "description", "price", "stock_quantity", "status"}


class CommerceConflict(ValueError):
    pass


class CommerceNotFound(ValueError):
    pass


def _to_cents(value: Decimal | float | str) -> int:
    return int((Decimal(str(value)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _money(cents: int) -> Decimal:
    return (Decimal(cents) / 100).quantize(Decimal("0.01"))


def _product(row):
    if row is None:
        return None
    data = dict(row)
    data["price"] = _money(data.pop("price_cents"))
    return data


def list_products(path: Path, status: str | None = None, limit: int = 50, offset: int = 0):
    where = " WHERE status = ?" if status else ""
    params: list[object] = [status] if status else []
    with connect(path) as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM products{where}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT id,sku,name,description,price_cents,stock_quantity,status,created_at "
            f"FROM products{where} ORDER BY id DESC LIMIT ? OFFSET ?",
            [*params, limit, offset],
        ).fetchall()
    return [_product(row) for row in rows], total


def get_product(path: Path, product_id: int):
    with connect(path) as conn:
        row = conn.execute(
            "SELECT id,sku,name,description,price_cents,stock_quantity,status,created_at "
            "FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
    return _product(row)


def create_product(path: Path, data: dict):
    with connect(path) as conn:
        cur = conn.execute(
            "INSERT INTO products(sku,name,description,price_cents,stock_quantity,status) VALUES(?,?,?,?,?,?)",
            (
                data["sku"], data["name"], data.get("description", ""), _to_cents(data["price"]),
                data.get("stock_quantity", 0), data.get("status", "active"),
            ),
        )
        product_id = cur.lastrowid
    return get_product(path, product_id)


def update_product(path: Path, product_id: int, changes: dict):
    changes = {k: v for k, v in changes.items() if k in ALLOWED_PRODUCT_PATCH_FIELDS}
    if "price" in changes:
        changes["price_cents"] = _to_cents(changes.pop("price"))
    if not changes:
        return get_product(path, product_id)
    assignments = ", ".join(f"{name} = ?" for name in changes)
    with connect(path) as conn:
        cur = conn.execute(
            f"UPDATE products SET {assignments} WHERE id = ?",
            [*changes.values(), product_id],
        )
        if cur.rowcount == 0:
            return None
    return get_product(path, product_id)


def delete_product(path: Path, product_id: int) -> bool:
    with connect(path) as conn:
        cur = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        return cur.rowcount == 1


def list_customers(path: Path):
    with connect(path) as conn:
        rows = conn.execute(
            "SELECT id,name,email,company,created_at FROM customers ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def create_customer(path: Path, data: dict):
    with connect(path) as conn:
        cur = conn.execute(
            "INSERT INTO customers(name,email,company) VALUES(?,?,?)",
            (data["name"], str(data["email"]), data.get("company", "")),
        )
        customer_id = cur.lastrowid
        row = conn.execute(
            "SELECT id,name,email,company,created_at FROM customers WHERE id = ?",
            (customer_id,),
        ).fetchone()
    return dict(row)


def _order_from_connection(conn, order_id: int):
    order = conn.execute(
        "SELECT o.id,o.customer_id,c.name customer_name,o.status,o.total_cents,o.created_at "
        "FROM orders o JOIN customers c ON c.id=o.customer_id WHERE o.id=?",
        (order_id,),
    ).fetchone()
    if order is None:
        return None
    data = dict(order)
    data["total"] = _money(data.pop("total_cents"))
    rows = conn.execute(
        "SELECT oi.product_id,p.name product_name,oi.quantity,oi.unit_price_cents "
        "FROM order_items oi JOIN products p ON p.id=oi.product_id WHERE oi.order_id=? ORDER BY oi.id",
        (order_id,),
    ).fetchall()
    data["items"] = [
        {
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "quantity": row["quantity"],
            "unit_price": _money(row["unit_price_cents"]),
            "line_total": _money(row["unit_price_cents"] * row["quantity"]),
        }
        for row in rows
    ]
    return data


def create_order(path: Path, data: dict):
    with connect(path) as conn:
        if conn.execute("SELECT 1 FROM customers WHERE id=?", (data["customer_id"],)).fetchone() is None:
            raise CommerceNotFound("Customer not found")
        prepared = []
        total_cents = 0
        for item in data["items"]:
            product = conn.execute(
                "SELECT id,name,price_cents,stock_quantity,status FROM products WHERE id=?",
                (item["product_id"],),
            ).fetchone()
            if product is None:
                raise CommerceNotFound(f"Product {item['product_id']} not found")
            if product["status"] != "active" or product["stock_quantity"] < item["quantity"]:
                raise CommerceConflict(f"Insufficient active stock for {product['name']}")
            total_cents += product["price_cents"] * item["quantity"]
            prepared.append((product, item["quantity"]))
        cur = conn.execute(
            "INSERT INTO orders(customer_id,status,total_cents) VALUES(?,?,?)",
            (data["customer_id"], "paid", total_cents),
        )
        order_id = cur.lastrowid
        for product, quantity in prepared:
            stock_update = conn.execute(
                "UPDATE products SET stock_quantity=stock_quantity-? "
                "WHERE id=? AND status='active' AND stock_quantity>=?",
                (quantity, product["id"], quantity),
            )
            if stock_update.rowcount != 1:
                raise CommerceConflict(f"Stock changed while ordering {product['name']}")
            conn.execute(
                "INSERT INTO order_items(order_id,product_id,quantity,unit_price_cents) VALUES(?,?,?,?)",
                (order_id, product["id"], quantity, product["price_cents"]),
            )
        return _order_from_connection(conn, order_id)


def list_orders(path: Path):
    with connect(path) as conn:
        ids = [row[0] for row in conn.execute("SELECT id FROM orders ORDER BY id DESC").fetchall()]
        return [_order_from_connection(conn, order_id) for order_id in ids]


def dashboard_summary(path: Path):
    with connect(path) as conn:
        products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        customers = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        revenue_cents = conn.execute(
            "SELECT COALESCE(SUM(total_cents),0) FROM orders WHERE status != 'cancelled'"
        ).fetchone()[0]
        low_stock = conn.execute(
            "SELECT COUNT(*) FROM products WHERE status='active' AND stock_quantity < 10"
        ).fetchone()[0]
    return {
        "products": products,
        "customers": customers,
        "orders": orders,
        "revenue": _money(revenue_cents),
        "low_stock": low_stock,
    }
