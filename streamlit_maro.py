import streamlit as st
import pandas as pd
from datetime import datetime

# -----------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA APLICACIÓN
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MARO - Sistema de Gestión de Joyería",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💎 MARO - Sistema de Gestión de Joyería")
st.caption("Especializado en análisis de datos y control de operaciones de joyería")

# -----------------------------------------------------------------------------
# INICIALIZACIÓN DE LA BASE DE DATOS EN MEMORIA (st.session_state)
# -----------------------------------------------------------------------------

# 1. INVENTARIO
if "inventario" not in st.session_state:
    st.session_state.inventario = pd.DataFrame([
        {
            "Código": "JOY-001",
            "Nombre": "Collar de Oro Solitario",
            "Tipo": "Collar",
            "Cantidad": 10,
            "Última Fecha Ingreso": "2026-09-15"
        },
        {
            "Código": "JOY-002",
            "Nombre": "Aretes Perla Cultivada",
            "Tipo": "Arete",
            "Cantidad": 15,
            "Última Fecha Ingreso": "2026-09-20"
        },
        {
            "Código": "JOY-003", "Nombre": "Pulsera Plata 925", "Tipo": "Pulsera", "Cantidad": 8, "Última Fecha Ingreso": "2026-09-25"},
        {
            "Código": "JOY-004",
            "Nombre": "Aro de Matrimonio 18K",
            "Tipo": "Aro",
            "Cantidad": 5,
            "Última Fecha Ingreso": "2026-09-28"
        }
    ])

# 2. CLIENTES
if "clientes" not in st.session_state:
    st.session_state.clientes = pd.DataFrame([
        {"ID Cliente": "CLI-001", "Nombre": "María", "Apellido": "García", "Celular": "987654321"},
        {"ID Cliente": "CLI-002", "Nombre": "Carlos", "Apellido": "Pérez", "Celular": "912345678"}
    ])

# 3. INVERSIONES
if "inversiones" not in st.session_state:
    st.session_state.inversiones = pd.DataFrame([
        {
            "ID Inversión": "INV-001",
            "Fecha de Inversión": "2026-09-15",
            "Monto de Inversión ($)": 500.0,
            "Producto Invertido": "JOY-001",
            "Cantidad Ingresada": 10
        }
    ])

# 4. VENTAS
if "ventas" not in st.session_state:
    st.session_state.ventas = pd.DataFrame([
        {
            "ID Venta": "V-001",
            "Fecha de Venta": "2026-09-29",
            "Cliente": "María García",
            "Producto": "JOY-001",
            "Cantidad": 1,
            "Pago": "Efectivo",
            "Estado": "Finalizado"
        }
    ])

# -----------------------------------------------------------------------------
# PESTAÑAS PRINCIPALES (Sujetas al diseño de tu boceto)
# -----------------------------------------------------------------------------
tab_inv, tab_cli, tab_inv_monto, tab_vta = st.tabs([
    "1️⃣ Inventario", 
    "2️⃣ Clientes", 
    "3️⃣ Inversiones", 
    "4️⃣ Ventas"
])

# =============================================================================
# PESTAÑA 1: INVENTARIO
# =============================================================================
with tab_inv:
    st.header("📦 Control de Inventario")
    st.caption("Listado completo de productos codificados y stock por tipo de joya.")
    
    # Vista general
    st.dataframe(st.session_state.inventario, use_container_width=True)

    # Formulario para codificar / agregar un producto directamente al catálogo
    with st.expander("➕ Codificar Nuevo Producto en Catálogo"):
        with st.form("form_inventario"):
            c1, c2, c3 = st.columns(3)
            codigo = c1.text_input("Codificar cada Producto (Código/SKU)", value=f"JOY-00{len(st.session_state.inventario)+1}")
            nombre = c2.text_input("Nombre / Descripción de la Joya")
            tipo = c3.selectbox("Tipo de Joya", ["Collar", "Arete", "Pulsera", "Aro", "Otro"])
            
            c4, c5 = st.columns(2)
            cantidad = c4.number_input("Cantidad Inicial", min_value=0, value=0, step=1)
            fecha_ingreso = c5.date_input("Última Fecha de Ingreso", value=datetime.now())

            btn_inv = st.form_submit_button("Guardar Producto")

            if btn_inv:
                if not nombre:
                    st.error("Ingrese el nombre de la joya.")
                else:
                    nuevo_item = pd.DataFrame([{
                        "Código": codigo,
                        "Nombre": nombre,
                        "Tipo": tipo,
                        "Cantidad": cantidad,
                        "Última Fecha Ingreso": str(fecha_ingreso)
                    }])
                    st.session_state.inventario = pd.concat([st.session_state.inventario, nuevo_item], ignore_index=True)
                    st.success(f"Producto '{nombre}' codificado con éxito.")
                    st.rerun()

# =============================================================================
# PESTAÑA 2: CLIENTES
# =============================================================================
with tab_cli:
    st.header("👥 Directorio de Clientes")
    st.dataframe(st.session_state.clientes, use_container_width=True)

    st.subheader("➕ Registrar Nuevo Cliente")
    with st.form("form_cliente", clear_on_submit=True):
        col_c1, col_c2, col_c3 = st.columns(3)
        nom_cli = col_c1.text_input("Nombre")
        ape_cli = col_c2.text_input("Apellido")
        cel_cli = col_c3.text_input("Celular")

        btn_cli = st.form_submit_button("Registrar Cliente")

        if btn_cli:
            if not nom_cli or not ape_cli:
                st.error("Por favor complete Nombre y Apellido.")
            else:
                nuevo_cli = pd.DataFrame([{
                    "ID Cliente": f"CLI-00{len(st.session_state.clientes)+1}",
                    "Nombre": nom_cli,
                    "Apellido": ape_cli,
                    "Celular": cel_cli
                }])
                st.session_state.clientes = pd.concat([st.session_state.clientes, nuevo_cli], ignore_index=True)
                st.success(f"Cliente {nom_cli} {ape_cli} guardado exitosamente.")
                st.rerun()

# =============================================================================
# PESTAÑA 3: INVERSIONES
# =============================================================================
with tab_inv_monto:
    st.header("📉 Registro de Inversiones")
    st.caption("Al registrar una inversión ligada a un producto, el stock en inventario se actualiza automáticamente.")

    st.dataframe(st.session_state.inversiones, use_container_width=True)

    st.subheader("➕ Añadir Nueva Inversión")
    if st.session_state.inventario.empty:
        st.warning("Primero debes codificar productos en la pestaña '1. Inventario'.")
    else:
        with st.form("form_inversion", clear_on_submit=True):
            col_i1, col_i2 = st.columns(2)
            fecha_inv = col_i1.date_input("Fecha de Inversión", value=datetime.now())
            monto_inv = col_i2.number_input("Monto de Inversión ($)", min_value=0.1, value=100.0, step=10.0)

            col_i3, col_i4 = st.columns(2)
            # Lista de productos de la pestaña Inventario
            opciones_prod = st.session_state.inventario["Código"].tolist()
            prod_sel = col_i3.selectbox("Producto(s) de Inversión (Código)", opciones_prod)
            cant_inv = col_i4.number_input("Cantidad Adquirida", min_value=1, value=1, step=1)

            btn_registrar_inv = st.form_submit_button("Registrar Inversión e Incrementar Stock")

            if btn_registrar_inv:
                # 1. Registrar Inversión
                nueva_inv = pd.DataFrame([{
                    "ID Inversión": f"INV-00{len(st.session_state.inversiones)+1}",
                    "Fecha de Inversión": str(fecha_inv),
                    "Monto de Inversión ($)": monto_inv,
                    "Producto Invertido": prod_sel,
                    "Cantidad Ingresada": cant_inv
                }])
                st.session_state.inversiones = pd.concat([st.session_state.inversiones, nueva_inv], ignore_index=True)

                # 2. Actualizar Inventario (Stock y Fecha)
                idx = st.session_state.inventario.index[st.session_state.inventario['Código'] == prod_sel].tolist()[0]
                st.session_state.inventario.at[idx, "Cantidad"] += cant_inv
                st.session_state.inventario.at[idx, "Última Fecha Ingreso"] = str(fecha_inv)

                st.success("Inversión guardada y stock de inventario incrementado.")
                st.rerun()

# =============================================================================
# PESTAÑA 4: VENTAS
# =============================================================================
with tab_vta:
    st.header("💰 Registro de Ventas")
    st.caption("Gestiona tus operaciones comerciales, medio de pago y estados de venta.")

    st.dataframe(st.session_state.ventas, use_container_width=True)

    st.subheader("➕ Registrar Nueva Venta")
    
    if st.session_state.inventario.empty:
        st.warning("No hay productos disponibles.")
    else:
        # Preparar lista de clientes para selector
        lista_clientes = (st.session_state.clientes["Nombre"] + " " + st.session_state.clientes["Apellido"]).tolist() if not st.session_state.clientes.empty else ["Cliente Anonimo"]
        
        # Preparar lista de productos con stock
        lista_prods = st.session_state.inventario["Código"].tolist()

        with st.form("form_venta", clear_on_submit=True):
            v_col1, v_col2 = st.columns(2)
            fecha_vta = v_col1.date_input("Fecha de Venta", value=datetime.now())
            cliente_sel = v_col2.selectbox("Cliente", lista_clientes)

            v_col3, v_col4 = st.columns(2)
            prod_vta = v_col3.selectbox("Producto (Código)", lista_prods)
            
            # Obtener stock actual
            stock_actual = st.session_state.inventario[st.session_state.inventario["Código"] == prod_vta]["Cantidad"].values[0]
            cant_vta = v_col4.number_input(f"Cantidad (Stock Disp: {stock_actual})", min_value=1, max_value=max(1, int(stock_actual)), value=1)

            v_col5, v_col6 = st.columns(2)
            pago_sel = v_col5.selectbox("Pago", ["Efectivo", "Transferencia", "Crédito"])
            estado_sel = v_col6.selectbox("Estado", ["Pendiente", "Finalizado"])

            btn_vta = st.form_submit_button("Registrar Venta")

            if btn_vta:
                if stock_actual < cant_vta:
                    st.error("No hay suficiente stock disponible en inventario.")
                else:
                    # 1. Descontar Stock si la venta finaliza o se descuenta por reserva
                    idx_prod = st.session_state.inventario.index[st.session_state.inventario['Código'] == prod_vta].tolist()[0]
                    st.session_state.inventario.at[idx_prod, "Cantidad"] -= cant_vta

                    # 2. Registrar la venta
                    nueva_vta = pd.DataFrame([{
                        "ID Venta": f"V-00{len(st.session_state.ventas)+1}",
                        "Fecha de Venta": str(fecha_vta),
                        "Cliente": cliente_sel,
                        "Producto": prod_vta,
                        "Cantidad": cant_vta,
                        "Pago": pago_sel,
                        "Estado": estado_sel
                    }])
                    st.session_state.ventas = pd.concat([st.session_state.ventas, nueva_vta], ignore_index=True)

                    st.success("Venta realizada. Se ha actualizado el stock del inventario.")
                    st.rerun()
