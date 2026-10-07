let S={};
const $=s=>document.querySelector(s);
const API=(window.STORE_API_BASE||"").replace(/\/$/,"");
const asset=p=>`${API}/${String(p).replace(/^\//,"")}`;

const MOCK={
 product:{title:"MAKE MONEY ONLINE",subtitle:"A Practical Beginner's Guide to Building Legitimate Online Income Streams",description:"A practical beginner's guide to building legitimate online income streams."},
 prices:{"INR": 399, "USD": 9.99, "GBP": 7.99, "EUR": 8.99, "CAD": 12.99, "AUD": 14.99, "NZD": 16.99, "SGD": 13.99, "AED": 36, "SAR": 38, "JPY": 1500, "CNY": 72, "HKD": 78, "CHF": 8.99, "SEK": 109, "NOK": 109, "DKK": 69, "MXN": 189, "BRL": 49, "ZAR": 189, "TRY": 349, "THB": 329, "MYR": 39, "PHP": 549},
 countries:{"IN": {"name": "India", "currency": "INR", "symbol": "₹"}, "US": {"name": "United States", "currency": "USD", "symbol": "$"}, "GB": {"name": "United Kingdom", "currency": "GBP", "symbol": "£"}, "DE": {"name": "Germany", "currency": "EUR", "symbol": "€"}, "FR": {"name": "France", "currency": "EUR", "symbol": "€"}, "IT": {"name": "Italy", "currency": "EUR", "symbol": "€"}, "ES": {"name": "Spain", "currency": "EUR", "symbol": "€"}, "NL": {"name": "Netherlands", "currency": "EUR", "symbol": "€"}, "IE": {"name": "Ireland", "currency": "EUR", "symbol": "€"}, "CA": {"name": "Canada", "currency": "CAD", "symbol": "C$"}, "AU": {"name": "Australia", "currency": "AUD", "symbol": "A$"}, "NZ": {"name": "New Zealand", "currency": "NZD", "symbol": "NZ$"}, "SG": {"name": "Singapore", "currency": "SGD", "symbol": "S$"}, "AE": {"name": "United Arab Emirates", "currency": "AED", "symbol": "د.إ"}, "SA": {"name": "Saudi Arabia", "currency": "SAR", "symbol": "﷼"}, "JP": {"name": "Japan", "currency": "JPY", "symbol": "¥"}, "CN": {"name": "China", "currency": "CNY", "symbol": "¥"}, "HK": {"name": "Hong Kong", "currency": "HKD", "symbol": "HK$"}, "CH": {"name": "Switzerland", "currency": "CHF", "symbol": "CHF "}, "SE": {"name": "Sweden", "currency": "SEK", "symbol": "kr "}, "NO": {"name": "Norway", "currency": "NOK", "symbol": "kr "}, "DK": {"name": "Denmark", "currency": "DKK", "symbol": "kr "}, "MX": {"name": "Mexico", "currency": "MXN", "symbol": "MX$"}, "BR": {"name": "Brazil", "currency": "BRL", "symbol": "R$"}, "ZA": {"name": "South Africa", "currency": "ZAR", "symbol": "R "}, "TR": {"name": "Türkiye", "currency": "TRY", "symbol": "₺"}, "TH": {"name": "Thailand", "currency": "THB", "symbol": "฿"}, "MY": {"name": "Malaysia", "currency": "MYR", "symbol": "RM "}, "PH": {"name": "Philippines", "currency": "PHP", "symbol": "₱"}},
 landing:{lead:"A practical beginner's guide to building legitimate online income streams — from freelancing and digital products to content creation and AI services.",show_india_qr:true,qr_filename:"india-qr.png"},
 meta:{pixel_id:""},razorpay_key_id:""
};

async function loadConfig(){
  try{const r=await fetch(API+"/api/config");if(!r.ok)throw new Error();return await r.json();}
  catch(e){return MOCK;}
}
function flag(code){return code.toUpperCase().replace(/./g,c=>String.fromCodePoint(127397+c.charCodeAt(0)));}
function money(c){return `${c.symbol}${Number(S.prices[c.currency]).toLocaleString(undefined,{maximumFractionDigits:c.currency==="JPY"?0:2})}`;}
function toast(msg){const t=$("#toast");t.textContent=msg;t.classList.remove("hidden");clearTimeout(window.__toast);window.__toast=setTimeout(()=>t.classList.add("hidden"),3200);}
function installPixel(id){if(!/^\d+$/.test(id)||window.fbq)return;!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version="2.0";n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,"script","https://connect.facebook.net/en_US/fbevents.js");window.fbq("init",id);window.fbq("track","PageView");}
function pixel(e,d={}){if(window.fbq)window.fbq("track",e,d);}

function renderCountries(filter=""){
  const q=filter.trim().toLowerCase();
  const entries=Object.entries(S.countries).filter(([code,c])=>!q||c.name.toLowerCase().includes(q)||code.toLowerCase().includes(q));
  $("#countries").innerHTML=entries.map(([code,c])=>`<button class="country" data-code="${code}">${flag(code)} ${c.name}<small>${money(c)} · ${c.currency}</small></button>`).join("")||`<div class="muted" style="grid-column:1/-1;padding:20px">No country found.</div>`;
  document.querySelectorAll(".country").forEach(b=>b.onclick=()=>chooseCountry(b.dataset.code));
}
function chooseCountry(code){
  const c=S.countries[code];if(!c)return;
  S.country=code;localStorage.setItem("country",code);
  $("#countryFlag").textContent=flag(code);$("#countryName").textContent=c.name;
  $("#price").textContent=money(c);$("#currencyLabel").textContent=c.currency+" · local price";
  $("#checkoutPrice").textContent=money(c);$("#checkoutCurrency").textContent=`Digital ebook · ${c.currency} checkout · instant access after verified payment`;
  $("#countryModal").classList.add("hidden");
  const show=code==="IN"&&S.landing.show_india_qr&&S.landing.qr_filename;
  $("#india").classList.toggle("hidden",!show);if(show)$("#qr").src=asset("uploads/"+S.landing.qr_filename);
  pixel("ViewContent",{content_name:S.product.title,currency:c.currency,value:Number(S.prices[c.currency])});
}
function openCountry(){renderCountries($("#countrySearch").value||"");$("#countryModal").classList.remove("hidden");setTimeout(()=>$("#countrySearch").focus(),50);}
function resetButton(){const b=$("#continue");b.disabled=false;b.innerHTML="Continue to secure payment <b>→</b>";}
async function startPayment(){
  const email=$("#email").value.trim();
  if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)){toast("Please enter a valid email address.");return;}
  const c=S.countries[S.country];if(!c){openCountry();return;}
  if(!S.razorpay_key_id){toast("Razorpay is not configured yet. Add the TEST keys in .env and restart the server.");return;}
  $("#continue").disabled=true;$("#continue").textContent="Creating secure checkout…";
  try{
    const r=await fetch(API+"/api/create-order",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({country:S.country,currency:c.currency,email})});
    const d=await r.json();if(!r.ok)throw new Error(d.detail||"Could not create payment order.");
    const checkout=new Razorpay({key:d.key_id,order_id:d.order_id,amount:d.amount,currency:d.currency,name:"Make Money Online",description:"Digital ebook",prefill:{email},theme:{color:"#8b5cf6"},handler:async response=>{
      try{
        const v=await fetch(API+"/api/verify-payment",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(response)});
        const result=await v.json();if(!v.ok)throw new Error(result.detail||"Payment verification failed.");
        pixel("Purchase",{content_name:S.product.title,currency:c.currency,value:Number(S.prices[c.currency])});
        if(result.download_url)window.location.href=result.download_url;else toast("Payment verified. Check your email for the download.");
      }catch(err){toast(err.message||"Payment verification failed.");resetButton();}
    },modal:{ondismiss:resetButton}});
    checkout.open();
  }catch(e){toast(e.message||"Could not start checkout.");resetButton();}
}
function buy(){if(!S.country)return openCountry();$("#checkoutModal").classList.remove("hidden");$("#email").focus();pixel("InitiateCheckout",{content_name:S.product.title});}
async function boot(){
  S=await loadConfig();$("#lead").textContent=S.landing.lead||S.product.description;
  if(S.meta?.pixel_id)installPixel(S.meta.pixel_id);
  const saved=localStorage.getItem("country");if(saved&&S.countries[saved])chooseCountry(saved);else chooseCountry("IN");
  $("#countryBtn").onclick=openCountry;$("#buy").onclick=buy;$("#insideBuy").onclick=buy;
  $("#closeCountry").onclick=()=>$("#countryModal").classList.add("hidden");
  $("#closeCheckout").onclick=()=>{$("#checkoutModal").classList.add("hidden");resetButton();};
  $("#continue").onclick=startPayment;$("#countrySearch").oninput=e=>renderCountries(e.target.value);
  document.addEventListener("keydown",e=>{if(e.key==="Escape"){$("#countryModal").classList.add("hidden");$("#checkoutModal").classList.add("hidden");resetButton();}});
}
boot();
