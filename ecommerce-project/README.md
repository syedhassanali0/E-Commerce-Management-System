# ShopEase — E-Commerce Management System

Final Semester Project · Open Source Software Development (OSSD – Y9)
Full-stack web application built with **FastAPI**, **PostgreSQL (Supabase)**, and **HTML/CSS/JavaScript**.

By **Syed Hassan Ali** (F2024408041)

---

## What this project does

ShopEase is an online store. Customers register, browse and search products,
add items to a cart, and place orders they can track. Admins manage products,
categories, and orders from a dashboard with live analytics. All data lives in
a PostgreSQL database and is served through a FastAPI REST API. Passwords are
hashed with **bcrypt** and sessions use **JWT** tokens.

---

## Folder structure

```
ecommerce-project/
├── backend/
│   ├── main.py            # FastAPI app + all 18 API endpoints
│   ├── database.py        # Database connection (SQLite or Supabase PostgreSQL)
│   ├── models.py          # SQLAlchemy tables (6 tables)
│   ├── schemas.py         # Pydantic request/response models
│   ├── auth.py            # bcrypt hashing + JWT tokens
│   ├── seed.py            # Inserts sample data + admin/customer accounts
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # Copy to .env and fill in your values
├── frontend/
│   ├── index.html         # Home
│   ├── about.html         # About
│   ├── login.html         # Login / Register
│   ├── products.html      # Product listing (search + filter)
│   ├── product_details.html
│   ├── cart.html          # Cart + place order
│   ├── orders.html        # Order history / management
│   ├── dashboard.html     # Admin analytics + manage products/categories
│   ├── style.css
│   └── app.js             # Shared JS (API URL, auth, fetch helper)
├── screenshots/           # Put your screenshots here for submission
└── README.md
```

---

## API endpoints (18 total)

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 1 | POST | `/register` | Register a new user |
| 2 | POST | `/login` | Login, returns JWT token |
| 3 | POST | `/products` | Add product (admin) |
| 4 | GET | `/products` | List products (supports `?search=` and `?category_id=`) |
| 5 | GET | `/products/{id}` | Get one product |
| 6 | PUT | `/products/{id}` | Update product (admin) |
| 7 | DELETE | `/products/{id}` | Delete product (admin) |
| 8 | POST | `/categories` | Add category (admin) |
| 9 | GET | `/categories` | List categories |
| 10 | POST | `/cart` | Add item to cart |
| 11 | GET | `/cart/{user_id}` | View a user's cart |
| 12 | PUT | `/cart/{id}` | Update cart item quantity |
| 13 | DELETE | `/cart/{id}` | Remove cart item |
| 14 | POST | `/orders` | Place an order |
| 15 | GET | `/orders` | List orders |
| 16 | GET | `/orders/{id}` | View one order |
| 17 | PUT | `/orders/{id}` | Update order status (admin) |
| 18 | DELETE | `/orders/{id}` | Delete order (admin) |
| + | GET | `/dashboard` | Admin analytics |

---

## Run it locally (easiest — uses SQLite, no database setup needed)

You need **Python 3.10+** installed.

```bash
# 1. Go into the backend folder
cd backend

# 2. (Recommended) create a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) create your .env file
#    Copy .env.example to .env. With no DATABASE_URL set it uses a local
#    SQLite file automatically, which is perfect for testing.

# 5. Add sample data + an admin account
python seed.py

# 6. Start the server
uvicorn main:app --reload
```

The API is now at **http://127.0.0.1:8000**
Interactive docs (test every endpoint): **http://127.0.0.1:8000/docs**

**Open the frontend:** just open `frontend/index.html` in your browser.
For best results serve it on its own little server so paths work cleanly:

```bash
cd frontend
python -m http.server 5500
# then visit http://127.0.0.1:5500
```

### Demo accounts (created by `seed.py`)
- Admin: `admin@shop.com` / `admin123`
- Customer: `user@shop.com` / `user123`

---

## Use Supabase PostgreSQL (required for final submission)

1. Create a free project at <https://supabase.com>.
2. In the dashboard go to **Project Settings → Database → Connection string → URI**
   and copy it. It looks like:
   `postgresql://postgres:YOUR_PASSWORD@db.xxxxxxxx.supabase.co:5432/postgres`
3. In `backend/`, copy `.env.example` to `.env` and paste it:
   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxxxxx.supabase.co:5432/postgres
   JWT_SECRET=some-long-random-string
   ```
4. Run `python seed.py` once — this creates all tables in Supabase and inserts
   sample data. You can confirm the tables under **Table Editor** in Supabase.
5. Start the server with `uvicorn main:app --reload`. It now reads/writes Supabase.

> Tables are created automatically by SQLAlchemy the first time the app runs —
> you do not need to write any SQL by hand.

---

## Deployment

### Backend → Render
1. Push this project to a **GitHub** repository.
2. On <https://render.com> create a **New → Web Service** from your repo.
3. Settings:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables `DATABASE_URL` (your Supabase URI) and `JWT_SECRET`.
5. Deploy. You get a live URL like `https://shopease-api.onrender.com`.

### Frontend → Vercel (or Netlify / GitHub Pages)
1. In `frontend/app.js`, change the first line to your live backend URL:
   ```js
   const API_BASE = "https://shopease-api.onrender.com";
   ```
2. Deploy the `frontend/` folder to Vercel/Netlify, or enable GitHub Pages on it.

### Database → Supabase
Already hosted in the cloud once you complete the Supabase steps above.

---

## Submission checklist
- [x] At least 5 frontend pages (this project has 8)
- [x] At least 10 backend API endpoints (this project has 18 + dashboard)
- [x] PostgreSQL database connected (Supabase)
- [x] Full CRUD on products, categories, cart, orders
- [x] JWT authentication + bcrypt password hashing
- [x] Deployment ready (Render + Vercel + Supabase)
- [ ] Add your screenshots to `screenshots/`
- [ ] Paste your live links below

**Live frontend:** _add link_
**Live backend (`/docs`):** _add link_
**GitHub repo:** _add link_
