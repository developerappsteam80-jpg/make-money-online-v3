let cfg=null;
const API=location.protocol==="file:"?"http://127.0.0.1:8000":"";
const $=s=>document.querySelector(s);

async function api(url,opt={}){
  const r=await fetch(API+url,opt);
  const text=await r.text();let d={};try{d=JSON.parse(text)}catch{}
  if(!r.ok)throw new Error(d.detail||"Server request failed");
  return d;
}
function minor(currency){return currency==="JPY"?0:2}
function amountDisplay(v,c){return `${Number(v).toLocaleString(undefined,{maximumFractionDigits:minor(c)})} ${c}`}
function render(){
  $("#sp").textContent=cfg.product.title;$("#sc").textContent=Object.keys(cfg.countries).length;
  $("#title").value=cfg.product.title;$("#subtitle").value=cfg.product.subtitle;$("#desc").value=cfg.product.description;
  $("#showqr").checked=!!cfg.landing.show_india_qr;$("#pixel").value=cfg.meta.pixel_id||"";
  $("#prices").innerHTML=Object.entries(cfg.prices).map(([cur,v])=>`<div class="price-item"><b>${cur}</b><input data-price="${cur}" type="number" step="${cur==="JPY"?"1":"0.01"}" value="${v}"></div>`).join("");
  renderCountries();
}
function renderCountries(filter=""){
  const q=filter.toLowerCase().trim();
  $("#countries").innerHTML=Object.entries(cfg.countries).filter(([code,c])=>!q||c.name.toLowerCase().includes(q)||code.toLowerCase().includes(q)||c.currency.toLowerCase().includes(q)).map(([code,c])=>`
  <div class="country-admin"><b>${flag(code)} ${c.name}</b><small>${code} · ${c.currency} · ${c.symbol}${cfg.prices[c.currency]??"—"}</small><label><input data-country="${code}" type="checkbox" ${c.enabled?"checked":""}> Enabled</label></div>`).join("")||`<div class="hint">No countries match.</div>`;
}
function flag(code){return code.toUpperCase().replace(/./g,c=>String.fromCodePoint(127397+c.charCodeAt(0)));}
async function save(){
  document.querySelectorAll("[data-price]").forEach(i=>cfg.prices[i.dataset.price]=Number(i.value));
  document.querySelectorAll("[data-country]").forEach(i=>cfg.countries[i.dataset.country].enabled=i.checked);
  cfg.product.title=$("#title").value.trim();cfg.product.subtitle=$("#subtitle").value.trim();cfg.product.description=$("#desc").value.trim();
  cfg.landing.show_india_qr=$("#showqr").checked;cfg.meta.pixel_id=$("#pixel").value.trim();
  try{await api("/api/admin/save-config",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(cfg)});status("Changes saved.");}
  catch(e){status(e.message,true);}
}
async function upload(id,url){
  const file=$("#"+id).files[0];if(!file){status("Choose a file first.",true);return}
  const f=new FormData();f.append("file",file);
  try{await api(url,{method:"POST",body:f});cfg=await api("/api/admin/config");render();status("Upload complete.");}
  catch(e){status(e.message,true);}
}
async function loadOrders(){
  try{
    const data=await api("/api/admin/orders");$("#so").textContent=data.length;
    $("#rows").innerHTML=data.length?data.map(o=>`<tr><td>${o.public_id||""}</td><td>${o.email||""}</td><td>${o.country||""}</td><td>${amountDisplay((Number(o.amount||0)/(10**minor(o.currency||"USD"))),o.currency||"")}</td><td class="status-${o.status}">${o.status||""}</td></tr>`).join(""):`<tr><td colspan="5">No orders yet.</td></tr>`;
  }catch(e){status(e.message,true)}
}
function status(msg,error=false){$("#serverTitle").textContent=msg;$("#serverText").textContent=error?"Check that start.bat is running and try again.":"Admin backend connected.";$("#dot").style.background=error?"#fb7185":"#22d3ee";}
async function init(){
  $("#storeLink").href=location.protocol==="file:"?"../frontend/index.html":"/";
  try{cfg=await api("/api/admin/config");render();await loadOrders();status("Admin backend connected.");}
  catch(e){status("Backend not running",true);$("#sp").textContent="—";$("#sc").textContent="29";}
  $("#countrySearch").oninput=e=>renderCountries(e.target.value);
  $("#refresh").onclick=async()=>{try{cfg=await api("/api/admin/config");render();await loadOrders();status("Refreshed.");}catch(e){status(e.message,true)}};
  $("#allOn").onclick=()=>{Object.values(cfg.countries).forEach(c=>c.enabled=true);renderCountries($("#countrySearch").value)};
  $("#allOff").onclick=()=>{Object.values(cfg.countries).forEach(c=>c.enabled=false);renderCountries($("#countrySearch").value)};
}
init();
