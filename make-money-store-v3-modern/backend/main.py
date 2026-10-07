
import os, json, secrets, shutil
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Header
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from . import orders
from .payments import create, checkout_signature, webhook_signature, payment
from .delivery import token, token_hash, send_email, PDF

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.getenv("DATA_DIR", str(ROOT / "data")))
DATA.mkdir(parents=True, exist_ok=True)
BUNDLED_CFG = ROOT / "backend" / "config.json"
CFG = DATA / "config.json"
BUNDLED_UP = ROOT / "uploads"
UP = DATA / "uploads"
UP.mkdir(parents=True, exist_ok=True)
if not CFG.exists():
    shutil.copy2(BUNDLED_CFG, CFG)
if not (UP / "ebook.pdf").exists() and (BUNDLED_UP / "ebook.pdf").exists():
    shutil.copy2(BUNDLED_UP / "ebook.pdf", UP / "ebook.pdf")
if not any(UP.glob("india-qr.*")):
    for q in BUNDLED_UP.glob("india-qr.*"):
        shutil.copy2(q, UP / q.name)
FRONT = ROOT / "frontend"
ADMIN = ROOT / "admin"

app = FastAPI(title="Make Money Online Store")

# Needed when the HTML is opened directly from the frontend/admin folders
# (file://). Payment secrets remain server-side; this only allows browser API calls.
_cors = [x.strip().rstrip("/") for x in os.getenv("FRONTEND_URLS", "http://127.0.0.1:8000,http://localhost:8000").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Razorpay-Signature"],
)
app.mount("/static", StaticFiles(directory=FRONT), name="static")
app.mount("/admin-static", StaticFiles(directory=ADMIN), name="admin-static")
app.mount("/uploads", StaticFiles(directory=UP), name="uploads")
orders.init_db()

def cfg():
    return json.loads(CFG.read_text(encoding="utf-8"))

def save_config(data):
    CFG.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

class NewOrder(BaseModel):
    country: str
    currency: str
    email: EmailStr

class VerifyPayment(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
def home():
    return FileResponse(FRONT / "index.html")

@app.get("/admin", response_class=HTMLResponse)
def admin():
    return FileResponse(ADMIN / "index.html")

@app.get("/shipping-delivery", response_class=HTMLResponse)
@app.get("/shipping-delivery.html", response_class=HTMLResponse)
def shipping_delivery():
    return FileResponse(FRONT / "shipping-delivery.html")

@app.get("/refund-cancellation", response_class=HTMLResponse)
@app.get("/refund-cancellation.html", response_class=HTMLResponse)
def refund_cancellation():
    return FileResponse(FRONT / "refund-cancellation.html")

@app.get("/privacy-policy", response_class=HTMLResponse)
@app.get("/privacy-policy.html", response_class=HTMLResponse)
def privacy_policy():
    return FileResponse(FRONT / "privacy-policy.html")

@app.get("/contact", response_class=HTMLResponse)
@app.get("/contact.html", response_class=HTMLResponse)
def contact():
    return FileResponse(FRONT / "contact.html")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/api/config")
def public_config():
    c = cfg()
    return {
        "product": c["product"],
        "prices": c["prices"],
        "countries": {k:v for k,v in c["countries"].items() if v["enabled"]},
        "landing": c["landing"],
        "meta": c["meta"],
        "razorpay_key_id": os.getenv("RAZORPAY_KEY_ID", "")
    }

@app.post("/api/create-order")
def create_order(data: NewOrder):
    c = cfg()
    country = c["countries"].get(data.country)

    if not country or not country["enabled"] or country["currency"] != data.currency:
        raise HTTPException(400, "Invalid country or currency.")

    price = c["prices"].get(data.currency)
    if price is None:
        raise HTTPException(400, "Price is not configured.")

    # Razorpay expects the amount in the currency's smallest unit.
    # Most configured currencies use 2 decimals; JPY uses 0.
    minor_units = int(c.get("currency_minor_units", {}).get(data.currency, 2))
    amount = int(round(float(price) * (10 ** minor_units)))

    try:
        r = create(amount, data.currency, "ebook_" + secrets.token_hex(8))
    except Exception:
        raise HTTPException(502, "Could not create the payment order.")

    public_id = orders.create(
        r["id"], data.email, data.country, data.currency, amount
    )

    return {
        "key_id": os.getenv("RAZORPAY_KEY_ID", ""),
        "order_id": r["id"],
        "amount": r["amount"],
        "currency": r["currency"],
        "public_order_id": public_id
    }

@app.post("/api/verify-payment")
def verify_payment(data: VerifyPayment):
    if not checkout_signature(
        data.razorpay_order_id,
        data.razorpay_payment_id,
        data.razorpay_signature
    ):
        raise HTTPException(400, "Invalid payment signature.")

    row = orders.by_rzp(data.razorpay_order_id)
    if not row:
        raise HTTPException(404, "Order not found.")

    try:
        p = payment(data.razorpay_payment_id)
        if (
            p.get("order_id") != data.razorpay_order_id
            or p.get("status") != "captured"
        ):
            raise HTTPException(400, "Payment has not been captured.")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(502, "Payment provider verification failed.")

    if row["status"] == "paid":
        return {"ok": True, "message": "Already processed. Check your email."}

    download_token = token()
    orders.mark_paid(
        data.razorpay_order_id,
        data.razorpay_payment_id,
        token_hash(download_token)
    )

    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    download_url = f"{base_url}/download/{download_token}"

    email_sent = False
    try:
        email_sent = send_email(row["email"], download_url, row["public_id"])
    except Exception:
        pass

    return {
        "ok": True,
        "order_id": row["public_id"],
        "download_url": download_url,
        "email_sent": email_sent
    }

@app.post("/api/webhook")
async def webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None)
):
    body = await request.body()

    if not webhook_signature(body, x_razorpay_signature):
        raise HTTPException(400, "Invalid webhook signature.")

    event = json.loads(body)
    name = event.get("event", "")
    payload = event.get("payload", {})

    if name in ("payment.captured", "order.paid"):
        payment_entity = payload.get("payment", {}).get("entity", {})
        order_entity = payload.get("order", {}).get("entity", {})

        payment_id = payment_entity.get("id")
        razorpay_order_id = payment_entity.get("order_id") or order_entity.get("id")
        row = orders.by_rzp(razorpay_order_id) if razorpay_order_id else None

        if row and row["status"] != "paid" and payment_id:
            download_token = token()
            orders.mark_paid(
                razorpay_order_id,
                payment_id,
                token_hash(download_token)
            )

            base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
            download_url = f"{base_url}/download/{download_token}"

            try:
                send_email(row["email"], download_url, row["public_id"])
            except Exception:
                pass

    return {"ok": True}

@app.get("/download/{download_token}")
def download(download_token: str):
    row = orders.by_token_hash(token_hash(download_token))

    if not row or row["status"] != "paid":
        raise HTTPException(403, "Invalid or unpaid download link.")

    if not PDF.exists() or PDF.stat().st_size < 1000:
        raise HTTPException(503, "Ebook PDF is missing.")

    orders.inc_download(row["public_id"])

    return FileResponse(
        PDF,
        media_type="application/pdf",
        filename="Make_Money_Online.pdf"
    )

# Local/private admin controls.
# No username/password is used, per the requested design.
# Protect /admin with proper authentication before public deployment.

@app.get("/api/admin/config")
def admin_config():
    return cfg()

@app.get("/api/admin/orders")
def admin_orders():
    return orders.all_orders()

@app.post("/api/admin/save-config")
async def admin_save(request: Request):
    incoming = await request.json()
    current = cfg()

    for key in ("product", "prices", "countries", "landing", "meta"):
        if key in incoming:
            current[key] = incoming[key]

    save_config(current)
    return {"ok": True}

@app.post("/api/admin/upload-ebook")
async def upload_ebook(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "PDF files only.")

    data = await file.read()
    if len(data) < 1000:
        raise HTTPException(400, "The uploaded file appears empty.")

    (UP / "ebook.pdf").write_bytes(data)
    return {"ok": True}

@app.post("/api/admin/upload-qr")
async def upload_qr(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()

    if ext not in (".png", ".jpg", ".jpeg", ".webp"):
        raise HTTPException(400, "PNG, JPG or WEBP only.")

    filename = "india-qr" + ext
    (UP / filename).write_bytes(await file.read())

    current = cfg()
    current["landing"]["show_india_qr"] = True
    current["landing"]["qr_filename"] = filename
    save_config(current)

    return {"ok": True, "filename": filename}
