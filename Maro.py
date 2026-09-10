import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Jewelry Control - Inventory & POS",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_FILE = "joyeria_control.db"

# --- DATABASE SETUP & HELPERS ---
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Products Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                material TEXT NOT NULL,
                peso_gramos REAL NOT NULL,
                precio_costo REAL NOT NULL,
                precio_venta REAL NOT NULL,
                stock_actual INTEGER NOT NULL,
                stock_minimo INTEGER DEFAULT 1
            )
        """)
        
        # Sales Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                monto_total REAL NOT NULL,
                metodo_pago TEXT NOT NULL,
                cliente_nombre TEXT
            )
        """)
        
        # Sale Details Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER,
                producto_id INTEGER,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        """)
        
        # Inventory Audit Log Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditoria_inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                producto_id INTEGER,
                tipo_movimiento TEXT NOT NULL,
                cantidad_cambio INTEGER NOT NULL,
                motivo TEXT,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        """)
        conn.commit()

init_db()

# --- STATE MANAGEMENT ---
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- MAIN APP INTERFACE ---
st.title("💎 Jewelry Business Control System")
st.caption("Integrated Inventory Management, Point of Sale, and Audit Analytics")

menu = st.sidebar.radio("Navigation", ["📦 Inventory Management", "🛒 Point of Sale (POS)", "🔍 Audit & Inspections", "📊 Analytics & Reports"])

# ==========================================
# 1. INVENTORY MANAGEMENT
# ==========================================
if menu == "📦 Inventory Management":
    st.header("Inventory Management")
    
    tab1, tab2 = st.tabs(["📋 Inventory Catalog", "➕ Add New Product"])
    
    with tab1:
        st.subheader("Current Stock")
        
        conn = get_connection()
        df_products = pd.read_sql_query("SELECT * FROM productos", conn)
        conn.close()
        
        if not df_products.empty:
            # Search & Filter
            col_s1, col_s2 = st.columns([2, 1])
            with col_s1:
                search_query = st.text_input("🔍 Search by Name or SKU", "")
            with col_s2:
                category_filter = st.selectbox("Filter Category", ["All"] + list(df_products['categoria'].unique()))
            
            filtered_df = df_products.copy()
            if search_query:
                filtered_df = filtered_df[
                    filtered_df['nombre'].str.contains(search_query, case=False, na=False) |
                    filtered_df['sku'].str.contains(search_query, case=False, na=False)
                ]
            if category_filter != "All":
                filtered_df = filtered_df[filtered_df['categoria'] == category_filter]
                
            # Alert Flagging
            filtered_df['Stock Status'] = filtered_df.apply(
                lambda x: "⚠️ LOW STOCK" if x['stock_actual'] <= x['stock_minimo'] else "✅ OK", axis=1
            )
            
            st.dataframe(
                filtered_df[[
                    'id', 'sku', 'nombre', 'categoria', 'material', 
                    'peso_gramos', 'precio_costo', 'precio_venta', 
                    'stock_actual', 'stock_minimo', 'Stock Status'
                ]],
                use_container_width=True
            )
        else:
            st.info("No products found in inventory.")

    with tab2:
        st.subheader("Register New Jewelry Item")
        with st.form("add_product_form"):
            c1, c2 = st.columns(2)
            with c1:
                sku = st.text_input("SKU / Unique Identifier *")
                nombre = st.text_input("Product Name *")
                categoria = st.selectbox("Category", ["Rings", "Necklaces", "Bracelets", "Earrings", "Pendants", "Custom/Other"])
                material = st.selectbox("Material / Gold Karat", ["Gold 18K", "Gold 14K", "Silver 925", "Platinum", "Gold Filled"])
                peso_gramos = st.number_input("Weight (Grams)", min_value=0.01, step=0.01, format="%.2f")
            with c2:
                precio_costo = st.number_input("Cost Price ($)", min_value=0.0, step=1.0)
                precio_venta = st.number_input("Selling Price ($)", min_value=0.0, step=1.0)
                stock_actual = st.number_input("Initial Stock Quantity", min_value=1, step=1, value=1)
                stock_minimo = st.number_input("Minimum Alert Stock Level", min_value=1, step=1, value=1)
                
            submit_btn = st.form_submit_button("Save Product")
            
            if submit_btn:
                if not sku or not nombre:
                    st.error("Please fill in all required fields marked with *.")
                else:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO productos (sku, nombre, categoria, material, peso_gramos, precio_costo, precio_venta, stock_actual, stock_minimo)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (sku, nombre, categoria, material, peso_gramos, precio_costo, precio_venta, stock_actual, stock_minimo))
                        
                        product_id = cursor.lastrowid
                        cursor.execute("""
                            INSERT INTO auditoria_inventario (producto_id, tipo_movimiento, cantidad_cambio, motivo)
                            VALUES (?, 'INGRESO', ?, 'Initial Inventory Addition')
                        """, (product_id, stock_actual))
                        
                        conn.commit()
                        conn.close()
                        st.success(f"Product '{nombre}' added successfully!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Error: A product with this SKU already exists.")

# ==========================================
# 2. POINT OF SALE (POS)
# ==========================================
elif menu == "🛒 Point of Sale (POS)":
    st.header("Point of Sale")
    
    conn = get_connection()
    products_df = pd.read_sql_query("SELECT * FROM productos WHERE stock_actual > 0", conn)
    conn.close()
    
    col_pos1, col_pos2 = st.columns([1.2, 1])
    
    with col_pos1:
        st.subheader("Select Products")
        if not products_df.empty:
            product_options = {f"{row['sku']} - {row['nombre']} (${row['precio_venta']:.2f}) [Stock: {row['stock_actual']}]": row['id'] for _, row in products_df.iterrows()}
            selected_item = st.selectbox("Search & Select Item", list(product_options.keys()))
            selected_id = product_options[selected_item]
            
            item_data = products_df[products_df['id'] == selected_id].iloc[0]
            
            col_qty1, col_qty2 = st.columns(2)
            with col_qty1:
                qty = st.number_input("Quantity", min_value=1, max_value=int(item_data['stock_actual']), value=1, step=1)
            with col_qty2:
                st.write("")
                st.write("")
                if st.button("➕ Add to Cart", use_container_width=True):
                    # Check if already in cart
                    existing_cart_item = next((item for item in st.session_state.cart if item['id'] == selected_id), None)
                    if existing_cart_item:
                        if existing_cart_item['cantidad'] + qty <= item_data['stock_actual']:
                            existing_cart_item['cantidad'] += qty
                            st.success("Updated quantity in cart!")
                        else:
                            st.error("Cannot add more than available stock!")
                    else:
                        st.session_state.cart.append({
                            'id': selected_id,
                            'sku': item_data['sku'],
                            'nombre': item_data['nombre'],
                            'precio': item_data['precio_venta'],
                            'cantidad': qty
                        })
                        st.success("Item added to cart!")
        else:
            st.warning("No items currently available for sale.")

    with col_pos2:
        st.subheader("Current Order")
        if st.session_state.cart:
            cart_df = pd.DataFrame(st.session_state.cart)
            cart_df['Subtotal'] = cart_df['precio'] * cart_df['cantidad']
            
            st.dataframe(cart_df[['sku', 'nombre', 'cantidad', 'precio', 'Subtotal']], use_container_width=True)
            
            total_amount = cart_df['Subtotal'].sum()
            st.markdown(f"### Total: **${total_amount:,.2f}**")
            
            client_name = st.text_input("Customer Name (Optional)")
            payment_method = st.selectbox("Payment Method", ["Cash", "Credit Card", "Bank Transfer"])
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("✅ Complete Sale", type="primary", use_container_width=True):
                    conn = get_connection()
                    cursor = conn.cursor()
                    
                    # Insert Sale Record
                    cursor.execute("""
                        INSERT INTO ventas (monto_total, metodo_pago, cliente_nombre)
                        VALUES (?, ?, ?)
                    """, (total_amount, payment_method, client_name if client_name else "Walk-in Customer"))
                    venta_id = cursor.lastrowid
                    
                    # Process Details & Inventory Audit
                    for item in st.session_state.cart:
                        cursor.execute("""
                            INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario)
                            VALUES (?, ?, ?, ?)
                        """, (venta_id, item['id'], item['cantidad'], item['precio']))
                        
                        cursor.execute("""
                            UPDATE productos SET stock_actual = stock_actual - ? WHERE id = ?
                        """, (item['cantidad'], item['id']))
                        
                        cursor.execute("""
                            INSERT INTO auditoria_inventario (producto_id, tipo_movimiento, cantidad_cambio, motivo)
                            VALUES (?, 'VENTA', ?, ?)
                        """, (item['id'], -item['cantidad'], f"Sale #{venta_id}"))
                        
                    conn.commit()
                    conn.close()
                    st.session_state.cart = []
                    st.success(f"Sale #{venta_id} registered successfully!")
                    st.rerun()
            
            with c_btn2:
                if st.button("🗑️ Clear Cart", use_container_width=True):
                    st.session_state.cart = []
                    st.rerun()
        else:
            st.info("Cart is currently empty.")

# ==========================================
# 3. AUDIT & INSPECTIONS
# ==========================================
elif menu == "🔍 Audit & Inspections":
    st.header("Inventory Physical Inspections & Audits")
    
    tab_insp1, tab_insp2 = st.tabs(["📝 Perform Stock Inspection", "📜 Audit Log History"])
    
    with tab_insp1:
        st.subheader("Adjust Inventory after Physical Inspection")
        conn = get_connection()
        products_df = pd.read_sql_query("SELECT id, sku, nombre, stock_actual FROM productos", conn)
        conn.close()
        
        if not products_df.empty:
            prod_map = {f"{r['sku']} - {r['nombre']} (Current System Stock: {r['stock_actual']})": r['id'] for _, r in products_df.iterrows()}
            selected_prod_label = st.selectbox("Select Product for Inspection", list(prod_map.keys()))
            prod_id = prod_map[selected_prod_label]
            
            curr_stock = products_df[products_df['id'] == prod_id]['stock_actual'].values[0]
            
            with st.form("inspection_form"):
                new_physical_stock = st.number_input("Actual Counted Stock", min_value=0, value=int(curr_stock), step=1)
                reason_type = st.selectbox("Adjustment Type / Reason", ["INSPECTION_ADJUSTMENT", "LOSS_DISCREPANCY", "DAMAGED_REPAIR", "FOUND_STOCK"])
                audit_notes = st.text_area("Audit Notes & Reason Details")
                
                submit_audit = st.form_submit_button("Submit Stock Adjustment")
                
                if submit_audit:
                    diff = new_physical_stock - curr_stock
                    if diff == 0:
                        st.info("No change detected in stock count.")
                    else:
                        conn = get_connection()
                        cursor = conn.cursor()
                        
                        cursor.execute("UPDATE productos SET stock_actual = ? WHERE id = ?", (new_physical_stock, prod_id))
                        cursor.execute("""
                            INSERT INTO auditoria_inventario (producto_id, tipo_movimiento, cantidad_cambio, motivo)
                            VALUES (?, ?, ?, ?)
                        """, (prod_id, reason_type, diff, f"{audit_notes} (Prev: {curr_stock}, New: {new_physical_stock})"))
                        
                        conn.commit()
                        conn.close()
                        st.success("Stock adjustment successfully logged!")
                        st.rerun()
                        
    with tab_insp2:
        st.subheader("Complete Audit Trail")
        conn = get_connection()
        audit_df = pd.read_sql_query("""
            SELECT a.id, a.fecha, p.sku, p.nombre, a.tipo_movimiento, a.cantidad_cambio, a.motivo
            FROM auditoria_inventario a
            LEFT JOIN productos p ON a.producto_id = p.id
            ORDER BY a.fecha DESC
        """, conn)
        conn.close()
        
        if not audit_df.empty:
            st.dataframe(audit_df, use_container_width=True)
        else:
            st.info("No audit logs available yet.")

# ==========================================
# 4. ANALYTICS & REPORTS
# ==========================================
elif menu == "📊 Analytics & Reports":
    st.header("Business Analytics & Intelligence")
    
    conn = get_connection()
    prod_df = pd.read_sql_query("SELECT * FROM productos", conn)
    sales_df = pd.read_sql_query("SELECT * FROM ventas", conn)
    details_df = pd.read_sql_query("""
        SELECT d.*, p.nombre, p.categoria 
        FROM detalle_ventas d 
        JOIN productos p ON d.producto_id = p.id
    """, conn)
    conn.close()
    
    # Financial Overview Metrics
    st.subheader("Financial Overview")
    m1, m2, m3, m4 = st.columns(4)
    
    total_sales_val = sales_df['monto_total'].sum() if not sales_df.empty else 0.0
    inventory_cost_val = (prod_df['precio_costo'] * prod_df['stock_actual']).sum() if not prod_df.empty else 0.0
    inventory_retail_val = (prod_df['precio_venta'] * prod_df['stock_actual']).sum() if not prod_df.empty else 0.0
    total_units_in_stock = prod_df['stock_actual'].sum() if not prod_df.empty else 0
    
    m1.metric("Total Sales Revenue", f"${total_sales_val:,.2f}")
    m2.metric("Inventory Value (Cost)", f"${inventory_cost_val:,.2f}")
    m3.metric("Inventory Value (Retail)", f"${inventory_retail_val:,.2f}")
    m4.metric("Total Items in Stock", f"{total_units_in_stock} pcs")
    
    st.markdown("---")
    
    col_an1, col_an2 = st.columns(2)
    
    with col_an1:
        st.subheader("Top 5 Selling Items")
        if not details_df.empty:
            top_selling = details_df.groupby('nombre')['cantidad'].sum().reset_index()
            top_selling = top_selling.sort_values(by='cantidad', ascending=False).head(5)
            st.bar_chart(data=top_selling, x='nombre', y='cantidad')
        else:
            st.info("No sales data available for analytics.")
            
    with col_an2:
        st.subheader("Sales by Category")
        if not details_df.empty:
            cat_sales = details_df.groupby('categoria')['cantidad'].sum().reset_index()
            st.dataframe(cat_sales, use_container_width=True)
        else:
            st.info("No sales data available for analytics.")