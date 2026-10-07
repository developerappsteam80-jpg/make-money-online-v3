# Make Money Online — Frontend

This folder is the complete static storefront. Keep **all** HTML, CSS and JS files together when deploying.

## Before publishing
Open `api-config.js` and replace:

```js
window.STORE_API_BASE = "https://YOUR-BACKEND-DOMAIN.example.com";
```

with the public HTTPS URL of your deployed FastAPI backend.

Example:

```js
window.STORE_API_BASE = "https://make-money-api.onrender.com";
```

Then upload the **entire contents of this folder** to your static frontend host. Do not remove the policy HTML files or `style.css`/`app.js`.
