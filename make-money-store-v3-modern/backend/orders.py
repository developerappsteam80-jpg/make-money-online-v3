
from pathlib import Path
import sqlite3, secrets, os
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.getenv("DATA_DIR", str(ROOT / "data")))
DB = DATA / "store.db"

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    with conn() as d:
        d.execute("""CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            public_id TEXT UNIQUE,
            razorpay_order_id TEXT UNIQUE,
            razorpay_payment_id TEXT,
            email TEXT,
            country TEXT,
            currency TEXT,
            amount INTEGER,
            status TEXT DEFAULT 'created',
            download_token_hash TEXT,
            download_count INTEGER DEFAULT 0,
            created_at TEXT,
            paid_at TEXT
        )""")
        d.commit()

def create(rid, email, country, currency, amount):
    public_id = "MMO-" + secrets.token_hex(6).upper()
    with conn() as d:
        d.execute(
            """INSERT INTO orders
            (public_id, razorpay_order_id, email, country, currency, amount, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (public_id, rid, email, country, currency, amount,
             datetime.now(timezone.utc).isoformat())
        )
        d.commit()
    return public_id

def by_rzp(rid):
    with conn() as d:
        r = d.execute("SELECT * FROM orders WHERE razorpay_order_id=?", (rid,)).fetchone()
    return dict(r) if r else None

def mark_paid(rid, pid, token_hash):
    with conn() as d:
        d.execute(
            """UPDATE orders
               SET status='paid', razorpay_payment_id=?, download_token_hash=?, paid_at=?
               WHERE razorpay_order_id=? AND status!='paid'""",
            (pid, token_hash, datetime.now(timezone.utc).isoformat(), rid)
        )
        d.commit()

def by_token_hash(h):
    with conn() as d:
        r = d.execute("SELECT * FROM orders WHERE download_token_hash=?", (h,)).fetchone()
    return dict(r) if r else None

def inc_download(public_id):
    with conn() as d:
        d.execute("UPDATE orders SET download_count=download_count+1 WHERE public_id=?", (public_id,))
        d.commit()

def all_orders():
    with conn() as d:
        return [dict(r) for r in d.execute(
            "SELECT * FROM orders ORDER BY id DESC LIMIT 200"
        ).fetchall()]
