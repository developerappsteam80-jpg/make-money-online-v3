# MAKE MONEY ONLINE — Store V3

This build keeps the modern storefront but fixes direct-file preview behavior,
adds 29 country options with editable local prices, and gives the admin folder
its own launcher.

## Storefront
- Double-clicking `frontend/index.html` shows the same polished visual preview.
- If FastAPI is already running, the direct HTML page can also call the local API.
- For the complete live payment flow, run the server with `start.bat` and use:
  `http://127.0.0.1:8000/`
- Footer buttons for Contact, Privacy Policy, Refund & Cancellation, and Shipping & Delivery are preserved.

## Admin
- Admin files stay in the `admin/` folder.
- Double-click `admin/open-admin.bat` to start the backend and open the admin panel.
- `admin/index.html` is also a standalone visual page; its API functions require the backend.
- No admin password is included, as requested. Do not publicly expose `/admin` without authentication.

## Countries
29 country options are included with editable starter prices. The prices are
suggested local ebook prices, not live exchange-rate conversions.

Important: only enable currencies that are actually available/approved on your
Razorpay account. Razorpay's international-payment coverage is account/product
dependent, and its current site lists support for many currencies.

## Payment
Razorpay test credentials should be used first. The server creates an order,
the browser opens Razorpay Checkout, the server verifies the signature and
captured payment, and only then creates a protected ebook download token.

## Currency units
Most configured currencies use 2 decimal places; JPY is configured with 0
minor decimal places. Confirm the exact live currency rules and availability
with your payment provider before launch.

## Files
The supplied ebook remains at `uploads/ebook.pdf`.
