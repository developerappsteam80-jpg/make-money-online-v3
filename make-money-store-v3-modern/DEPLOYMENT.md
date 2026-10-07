# Production deployment

## Architecture
- `frontend/` is a complete static website: index + policy/contact pages + CSS + JS.
- `backend/` is the private FastAPI payment/delivery API.
- `uploads/ebook.pdf` is copied into persistent storage on first backend boot.
- SQLite and uploaded ebook files live under `DATA_DIR` so a persistent cloud disk keeps orders and the ebook across deploys.

## 1. Deploy the backend
The repository includes a `Dockerfile` and `render.yaml` for Render.

Create a Render Web Service from this project/repository. The service will use the Dockerfile. Attach the persistent disk shown in `render.yaml`.

Set these environment variables in Render:

- `RAZORPAY_KEY_ID` = your LIVE key ID
- `RAZORPAY_KEY_SECRET` = your LIVE secret
- `RAZORPAY_WEBHOOK_SECRET` = a webhook secret you choose
- `BASE_URL` = the final public backend URL, e.g. `https://make-money-online-api.onrender.com`
- `FRONTEND_URLS` = your final frontend URL(s), e.g. `https://yourdomain.com,https://www.yourdomain.com`
- SMTP variables if you want the automatic email download link.

Do not put `RAZORPAY_KEY_SECRET` in the frontend.

## 2. Deploy the frontend
Deploy the **whole contents of `frontend/`** to a static host such as Netlify.

Before uploading, edit `frontend/api-config.js`:

```js
window.STORE_API_BASE = "https://make-money-online-api.onrender.com";
```

Replace that URL with your actual backend URL.

The folder already contains:
- `index.html`
- `style.css`
- `app.js`
- `api-config.js`
- `contact.html`
- `privacy-policy.html`
- `refund-cancellation.html`
- `shipping-delivery.html`
- `netlify.toml`

Keep all of them.

## 3. Razorpay setup
Use LIVE keys only after completing Razorpay account/KYC/international-payment approval as applicable.

Set the Razorpay webhook URL to:

`https://YOUR-BACKEND-DOMAIN/api/webhook`

Use the same webhook secret as `RAZORPAY_WEBHOOK_SECRET`.

For the payment flow, the browser calls the backend to create an order; Razorpay Checkout handles payment; the backend verifies the signature and captured payment; only then is the protected ebook download URL created.

## 4. Custom domain
Point your frontend domain to the static host. Your backend can use a separate subdomain such as `api.yourdomain.com`.

Example:

- Store: `https://yourdomain.com`
- API: `https://api.yourdomain.com`

After the backend has its custom domain, put that exact URL into `frontend/api-config.js`, `BASE_URL`, and `FRONTEND_URLS` as appropriate.

## 5. Important admin warning
The existing admin was designed without a username/password. Do NOT expose `/admin` and `/api/admin/*` publicly in this form. Before launch, protect the admin routes with authentication or an access-control layer.

## 6. Email delivery
The checkout requires the customer's email because the current storefront promises an email download link. Configure SMTP variables so `send_email()` can send the secure link. The on-screen payment flow also returns the protected download URL after successful verification.
