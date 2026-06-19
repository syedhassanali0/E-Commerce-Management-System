/* ===========================================================
   app.js  —  shared helpers used by every page
   =========================================================== */

/* 1) API base URL.
   - For LOCAL testing, leave this as the localhost address below.
   - After you deploy the backend to Render, change it to your live URL, e.g.
     const API_BASE = "https://your-app.onrender.com";
*/
const API_BASE = "postgresql://postgres.wythuwrupvfmpiemzsek:fXrucuPkoXXvrsoT@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres";

/* ---------- Auth state (stored in the browser) ---------- */
function saveAuth(data) {
  localStorage.setItem("token", data.access_token);
  localStorage.setItem("user", JSON.stringify(data.user));
}
function getToken() { return localStorage.getItem("token"); }
function getUser() {
  const u = localStorage.getItem("user");
  return u ? JSON.parse(u) : null;
}
function isLoggedIn() { return !!getToken(); }
function isAdmin() { const u = getUser(); return u && u.role === "admin"; }
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.href = "index.html";
}

/* ---------- Fetch wrapper ----------
   Automatically adds the JSON header and the Authorization token,
   and turns API errors into thrown exceptions with a readable message. */
async function api(path, { method = "GET", body = null } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = "Bearer " + token;

  const res = await fetch(API_BASE + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  let data = null;
  try { data = await res.json(); } catch (e) { data = null; }

  if (!res.ok) {
    const msg = (data && data.detail) ? data.detail : ("Request failed (" + res.status + ")");
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return data;
}

/* ---------- Navbar (rendered into <div id="nav"></div>) ---------- */
function renderNav(active) {
  const user = getUser();
  const links = [
    { href: "index.html", label: "Home", key: "home" },
    { href: "products.html", label: "Products", key: "products" },
    { href: "about.html", label: "About", key: "about" },
  ];
  if (isLoggedIn()) {
    links.push({ href: "cart.html", label: "Cart", key: "cart" });
    links.push({ href: "orders.html", label: "Orders", key: "orders" });
  }
  if (isAdmin()) {
    links.push({ href: "dashboard.html", label: "Dashboard", key: "dashboard" });
  }

  const linkHtml = links.map(l =>
    `<a href="${l.href}" class="${active === l.key ? "active" : ""}">${l.label}</a>`
  ).join("");

  let authHtml;
  if (isLoggedIn()) {
    authHtml = `<span class="muted hide-sm">Hi, ${user.name.split(" ")[0]}</span>
                <button class="btn small outline" onclick="logout()">Logout</button>`;
  } else {
    authHtml = `<a class="btn small" href="login.html">Login</a>`;
  }

  document.getElementById("nav").innerHTML = `
    <nav class="navbar">
      <div class="container">
        <a class="brand" href="index.html">ShopEase<span class="dot">.</span></a>
        <div class="nav-links">
          ${linkHtml}
          <span id="authArea">${authHtml}</span>
        </div>
      </div>
    </nav>`;
}

/* ---------- Small helpers ---------- */
function money(n) { return "$" + Number(n).toFixed(2); }
function productIcon() { return "🛍️"; }   // simple placeholder thumbnail
function requireLogin() {
  if (!isLoggedIn()) { window.location.href = "login.html"; return false; }
  return true;
}
