import sqlite3
import os

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reloop.db")

def get_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def seed_demo_data(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        # 1. Create Demo Users
        users_data = [
            ("GreenTech Solutions", "buyer@eco.com", "password123", "buyer"),
            ("EcoWeave Textiles", "buyer2@eco.com", "password123", "buyer"),
            ("TimberCraft Industries", "supplier@eco.com", "password123", "supplier"),
            ("PolyRecycle Ltd", "supplier2@eco.com", "password123", "supplier")
        ]
        cur.executemany("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)", users_data)
        
        # 2. Seed Verifications
        verifications_data = [
            (3, "TimberCraft Industries", "29AAACT1234F1Z5", "Plot 12, Peenya Industrial Area, Bengaluru", "approved", 9.4),
            (4, "PolyRecycle Ltd", "27AAACP5678G2Z1", "Gala 4, MIDC Industrial Zone, Mumbai", "approved", 8.8)
        ]
        cur.executemany("""
        INSERT INTO verification_requests (supplier_id, company_name, gst_number, address, document_status, trust_score)
        VALUES (?, ?, ?, ?, ?, ?)
        """, verifications_data)
        
        # 3. Seed Material Listings
        listings_data = [
            (3, "Wood Waste", 450.0, "kg", 8.50, "Bengaluru", "good", "High grade untreated pine wood offcuts from furniture manufacturing.", 0.20, "active", "2026-10-15"),
            (3, "Cotton Waste", 300.0, "kg", 14.00, "Bengaluru", "excellent", "Clean white cotton textile cutoffs suitable for rag rolling or paper production.", 0.60, "active", "2026-11-01"),
            (4, "Plastic Waste", 1200.0, "kg", 18.00, "Mumbai", "good", "Baled HDPE plastic containers and industrial drum trimmings.", 2.16, "active", "2026-12-31"),
            (4, "Metal Scrap", 850.0, "kg", 28.00, "Mumbai", "fair", "Aluminum machine turnings and clean sheet metal scrap from stamping line.", 1.28, "active", "2026-09-30"),
            (3, "Paper Waste", 600.0, "kg", 7.00, "Bengaluru", "good", "Clean corrugated cardboard boxes and unprinted kraft paper reels.", 0.72, "active", "2026-10-31")
        ]
        cur.executemany("""
        INSERT INTO listings (supplier_id, material, quantity, unit, price_per_kg, location, condition, description, carbon_saved, status, expiry_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, listings_data)
        
        # 4. Seed Sourcing Requests
        requests_data = [
            (1, "Wood Waste", 500.0, 10.00, "open"),
            (1, "Plastic Waste", 1000.0, 20.00, "open")
        ]
        cur.executemany("""
        INSERT INTO buyer_requests (buyer_id, material_type, quantity, max_price, status)
        VALUES (?, ?, ?, ?, ?)
        """, requests_data)

def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            schema = f.read()
        conn = sqlite3.connect(DB)
        conn.executescript(schema)
        try:
            conn.execute("ALTER TABLE listings ADD COLUMN expiry_date TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        seed_demo_data(conn)
        conn.commit()
        conn.close()

# Initialize DB on import
init_db()

# --- USER MANAGEMENT ---
def create_user(name, email, password, role):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
        INSERT INTO users (name, email, password, role)
        VALUES (?, ?, ?, ?)
        """, (name, email, password, role))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    finally:
        conn.close()
    return success

def login_user(email, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT id, name, email, password, role FROM users
    WHERE email=? AND password=?
    """, (email, password))
    user = cur.fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

def get_user_by_id(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, role FROM users WHERE id=?", (user_id,))
    user = cur.fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

# --- LISTINGS MANAGEMENT ---
def add_listing(supplier_id, material, quantity, unit, price_per_kg, location, condition, description, carbon_saved, expiry_date=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO listings (supplier_id, material, quantity, unit, price_per_kg, location, condition, description, carbon_saved, expiry_date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
    """, (supplier_id, material, quantity, unit, price_per_kg, location, condition, description, carbon_saved, expiry_date))
    conn.commit()
    conn.close()

def get_listings(search_query=None, material_type=None, min_price=None, max_price=None, location=None, condition=None, verified_only=False):
    conn = get_connection()
    cur = conn.cursor()
    
    # Query active, non-expired listings
    query = """
    SELECT l.*, u.name as supplier_name, vr.trust_score, vr.document_status as verification_status
    FROM listings l
    JOIN users u ON l.supplier_id = u.id
    LEFT JOIN verification_requests vr ON l.supplier_id = vr.supplier_id
    WHERE l.status = 'active'
    AND (l.expiry_date IS NULL OR l.expiry_date >= DATE('now', 'localtime'))
    """
    params = []
    
    if search_query:
        query += " AND (l.material LIKE ? OR l.description LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
        
    if material_type and material_type != "All":
        query += " AND l.material LIKE ?"
        params.append(f"%{material_type}%")
        
    if min_price is not None:
        query += " AND l.price_per_kg >= ?"
        params.append(min_price)
        
    if max_price is not None:
        query += " AND l.price_per_kg <= ?"
        params.append(max_price)
        
    if location:
        query += " AND l.location LIKE ?"
        params.append(f"%{location}%")
        
    if condition and condition != "All":
        query += " AND l.condition = ?"
        params.append(condition.lower())
        
    if verified_only:
        query += " AND vr.document_status = 'approved'"
        
    query += " ORDER BY l.created_at DESC"
    
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_supplier_listings(supplier_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT * FROM listings 
    WHERE supplier_id = ?
    ORDER BY created_at DESC
    """, (supplier_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_listing_status(listing_id, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE listings SET status = ? WHERE id = ?", (status, listing_id))
    conn.commit()
    conn.close()

def delete_listing(listing_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
    conn.commit()
    conn.close()

# --- ORDERS MANAGEMENT ---
def create_order(listing_id, buyer_id, quantity, total_price):
    conn = get_connection()
    cur = conn.cursor()
    # Insert order
    cur.execute("""
    INSERT INTO orders (listing_id, buyer_id, quantity, total_price, status)
    VALUES (?, ?, ?, ?, 'completed')
    """, (listing_id, buyer_id, quantity, total_price))
    
    # Mark listing as sold
    cur.execute("UPDATE listings SET status = 'sold' WHERE id = ?", (listing_id,))
    
    conn.commit()
    conn.close()

def get_buyer_orders(buyer_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT o.*, l.material, l.unit, l.price_per_kg, l.location, l.carbon_saved, u.name as supplier_name
    FROM orders o
    JOIN listings l ON o.listing_id = l.id
    JOIN users u ON l.supplier_id = u.id
    WHERE o.buyer_id = ?
    ORDER BY o.created_at DESC
    """, (buyer_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_supplier_orders(supplier_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT o.*, l.material, l.unit, l.price_per_kg, l.location, u.name as buyer_name
    FROM orders o
    JOIN listings l ON o.listing_id = l.id
    JOIN users u ON o.buyer_id = u.id
    WHERE l.supplier_id = ?
    ORDER BY o.created_at DESC
    """, (supplier_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_order_status(order_id, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()

# --- VERIFICATION SYSTEM ---
def submit_verification(supplier_id, company_name, gst_number, address, trust_score, status='pending'):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
        INSERT INTO verification_requests (supplier_id, company_name, gst_number, address, document_status, trust_score)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(supplier_id) DO UPDATE SET
            company_name=excluded.company_name,
            gst_number=excluded.gst_number,
            address=excluded.address,
            document_status=excluded.document_status,
            trust_score=excluded.trust_score
        """, (supplier_id, company_name, gst_number, address, status, trust_score))
        conn.commit()
    finally:
        conn.close()

def get_verification_status(supplier_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM verification_requests WHERE supplier_id = ?", (supplier_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_all_verifications():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT vr.*, u.email as supplier_email 
    FROM verification_requests vr
    JOIN users u ON vr.supplier_id = u.id
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --- BUYER REQUESTS ---
def add_buyer_request(buyer_id, material_type, quantity, max_price):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO buyer_requests (buyer_id, material_type, quantity, max_price, status)
    VALUES (?, ?, ?, ?, 'open')
    """, (buyer_id, material_type, quantity, max_price))
    conn.commit()
    conn.close()

def get_all_buyer_requests():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT br.*, u.name as buyer_name 
    FROM buyer_requests br
    JOIN users u ON br.buyer_id = u.id
    WHERE br.status = 'open'
    ORDER BY br.created_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_buyer_requests_by_buyer(buyer_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT * FROM buyer_requests 
    WHERE buyer_id = ?
    ORDER BY created_at DESC
    """, (buyer_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]