CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,
    material TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL,
    price_per_kg REAL NOT NULL,
    location TEXT NOT NULL,
    condition TEXT NOT NULL,
    description TEXT,
    carbon_saved REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    expiry_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(supplier_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id INTEGER NOT NULL,
    buyer_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    total_price REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(listing_id) REFERENCES listings(id) ON DELETE CASCADE,
    FOREIGN KEY(buyer_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS verification_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL UNIQUE,
    company_name TEXT NOT NULL,
    gst_number TEXT NOT NULL,
    address TEXT NOT NULL,
    document_status TEXT NOT NULL DEFAULT 'pending',
    trust_score REAL NOT NULL DEFAULT 5.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(supplier_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS buyer_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_id INTEGER NOT NULL,
    material_type TEXT NOT NULL,
    quantity REAL NOT NULL,
    max_price REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(buyer_id) REFERENCES users(id) ON DELETE CASCADE
);