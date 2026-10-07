
import os, hmac, hashlib, razorpay

def client():
    return razorpay.Client(auth=(
        os.getenv("RAZORPAY_KEY_ID", ""),
        os.getenv("RAZORPAY_KEY_SECRET", "")
    ))

def create(amount, currency, receipt):
    return client().order.create({
        "amount": int(amount),
        "currency": currency,
        "receipt": receipt
    })

def checkout_signature(order_id, payment_id, signature):
    message = f"{order_id}|{payment_id}".encode()
    expected = hmac.new(
        os.getenv("RAZORPAY_KEY_SECRET", "").encode(),
        message,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature or "")

def webhook_signature(body, signature):
    expected = hmac.new(
        os.getenv("RAZORPAY_WEBHOOK_SECRET", "").encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    return bool(signature) and hmac.compare_digest(expected, signature)

def payment(payment_id):
    return client().payment.fetch(payment_id)
