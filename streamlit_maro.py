import streamlit as st
import pandas as pd
from datetime import date

# -----------------------------------------------------------------------------
# CONFIGURACIÓN INICIAL DE LA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MARO - Gestión de Joyería",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados (Fuente Aptos Narrow 9px y ajuste de celdas)
st.markdown("""
    <style>
    /* Fuente global Aptos Narrow / Arial Narrow 9px */
    html, body, [class*="css"], div, span, p, label, input, button, select {
        font-family: 'Aptos Narrow', 'Arial Narrow', sans-serif !important;
        font-size: 9px !important;
    }

    /* Control de botones compactos */
    .stButton button {
        padding: 1px 4px !important;
        font-size: 9px !important;
        height: 20px !important;
        line-height: 1 !important;
        margin: 0px !important;
    }

    /* Celdas fijas con ajuste perfecto para evitar desbordamiento y aumento de altura */
    .cell-box {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        height: 22px;
        line-height: 22px;
        padding: 0 4px;
        display: block;
        font-size: 9px !important;
    }

    .cell-box-header {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        height: 22px;
        line-height: 22px;
        padding: 0 4px;
        font-weight: bold;
        display: block;
        font-size: 9px !important;
    }

    /* Fila seleccionada */
    .selected-row {
        background-color: #fff3cd !important;
        color: #856404 !important;
        border-radius: 2px;
    }

    /* Colores para Ventas */
    .text-verde {
        color: #00e676 !important;
        font-weight: bold;
    }
    .text-ambar {
        color: #ffc107 !important;
        font-weight: bold;
    }
    .text-rojo {
        color: #ff5252 !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PERSISTENCIA DE DATOS (st.session_state)
# -----------------------------------------------------------------------------
if "inventario" not in st.session_state:
    st.session_state.inventario = pd.DataFrame([
        {"Código": "COL-001", "Tipo": "Collar", "Última Fecha de Ingreso de Inversión": "2026-09-15"},
        {"Código": "ART-002", "Tipo": "Arete", "Última Fecha de Ingreso de Inversión": "2026-09-20"},
        {"Código": "PUL-003", "Tipo": "Pulsera", "Última Fecha de Ingreso de Inversión": "2026-09-22"},
        {"Código": "ARO-004", "Tipo": "Aro", "Última Fecha de Ingreso de Inversión": "2026-09-25"},
    ])

if "clientes" not in st.session_state:
    st.session_state.clientes = pd.DataFrame([
        {"ID": 1, "Nombre": "María", "Apellido": "García", "Celular": "987654321"},
        {"ID": 2, "Nombre": "Carlos", "Apellido": "Mendoza", "Celular": "912345678"},
    ])

if "inversiones" not in st.session_state:
    st.session_state.inversiones = pd.DataFrame([
        {"ID Inversión": "INV-101", "Fecha de Inversión": "2026-09-15", "Monto de Inversión (S/.)": 450.0, "Producto": "COL-001", "Tipo de Producto": "Collar", "Cantidad Ingresada": 20},
        {"ID Inversión": "INV-102", "Fecha de Inversión": "2026-09-20", "Monto de Inversión (S/.)": 300.0, "Producto": "ART-002", "Tipo de Producto": "Arete", "Cantidad Ingresada": 30},
        {"ID Inversión": "INV-103", "Fecha de Inversión": "2026-09-22", "Monto de Inversión (S/.)": 250.0, "Producto": "PUL-003", "Tipo de Producto": "Pulsera", "Cantidad Ingresada": 15},
        {"ID Inversión": "INV-104", "Fecha de Inversión": "2026-09-25", "Monto de Inversión (S/.)": 500.0, "Producto": "ARO-004", "Tipo de Producto": "Aro", "Cantidad Ingresada": 40},
    ])

if "ventas" not in st.session_state:
    st.session_state.ventas = pd.DataFrame([
        {"ID Venta": "V-501", "Fecha de Venta": "2026-09-28", "Cliente": "María García", "Pago": "Efectivo", "Estado": "Finalizado", "Producto": "COL-001", "Cantidad": 2, "Monto (S/.)": 180.0},
        {"ID Venta": "V-502", "Fecha de Venta": "2026-09-29", "Cliente": "Carlos Mendoza", "Pago": "Transferencia", "Estado": "Pendiente", "Producto": "ART-002", "Cantidad": 1, "Monto (S/.)": 45.0},
    ])

if "edit_target" not in st.session_state:
    st.session_state.edit_target = {"tab": None, "id": None}

if "selected_rows" not in st.session_state:
    st.session_state.selected_rows = {"inventario": set(), "clientes": set(), "inversiones": set(), "ventas": set()}

# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# -----------------------------------------------------------------------------
def get_cantidad_total(codigo_producto):
    if st.session_state.inversiones.empty:
        return 0
    invs = st.session_state.inversiones[st.session_state.inversiones["Producto"] == codigo_producto]
    return int(invs["Cantidad Ingresada"].sum())

def get_cantidad_vendida(codigo_producto):
    if st.session_state.ventas.empty:
        return 0
    vtas = st.session_state.ventas[
        (st.session_state.ventas["Producto"] == codigo_producto) & 
        (st.session_state.ventas["Estado"] == "Finalizado")
    ]
    return int(vtas["Cantidad"].sum())

def get_stock_disponible(codigo_producto):
    return get_cantidad_total(codigo_producto) - get_cantidad_vendida(codigo_producto)

def render_styled_text(val, tipo):
    if tipo == "pago":
        if val in ["Efectivo", "Transferencia"]:
            return f'<span class="text-verde">{val}</span>'
        elif val == "Crédito":
            return f'<span class="text-ambar">{val}</span>'
    elif tipo == "estado":
        if val == "Finalizado":
            return f'<span class="text-verde">{val}</span>'
        elif val == "Pendiente":
            return f'<span class="text-rojo">{val}</span>'
    return val

def render_cell(text, is_selected=False):
    sel_class = " selected-row" if is_selected else ""
    return f'<div class="cell-box{sel_class}" title="{text}">{text}</div>'

def render_header(text):
    return f'<div class="cell-box-header" title="{text}">{text}</div>'

# -----------------------------------------------------------------------------
# BARRA LATERAL (NAVEGACIÓN)
# -----------------------------------------------------------------------------
st.sidebar.title("💎 MARO")
st.sidebar.caption("Sistema Integrado de Gestión")

pestana = st.sidebar.radio(
    "Navegar a:",
    ["1: Inventario", "2: Clientes", "3: Inversiones", "4: Ventas"]
)

# -----------------------------------------------------------------------------
# PESTAÑA 1: INVENTARIO
# -----------------------------------------------------------------------------
if pestana == "1: Inventario":
    st.title("📦 1: Inventario")
    st.caption("Cantidad Total (Ingresos por Inversiones) y Stock Disponible (Cantidad Total - Vendidos)")

    st.markdown("### Listado de Inventario")
    cols = st.columns([0.4, 1.2, 1.2, 1.3, 1.3, 2.0, 0.6, 0.6])
    headers = ["Sel.", "Código", "Tipo", "Cantidad Total", "Stock (Disponible)", "Última Fecha Ingreso", "Editar", "Eliminar"]
    for c, h in zip(cols, headers):
        c.markdown(render_header(h), unsafe_allow_html=True)
    st.markdown("---")

    for idx, row in st.session_state.inventario.iterrows():
        c0, c1, c2, c3, c4, c5, c6, c7 = st.columns([0.4, 1.2, 1.2, 1.3, 1.3, 2.0, 0.6, 0.6])
        
        cod = row["Código"]
        is_selected = cod in st.session_state.selected_rows["inventario"]
        
        sel = c0.checkbox("", key=f"sel_inv_{cod}", value=is_selected)
        if sel and not is_selected:
            st.session_state.selected_rows["inventario"].add(cod)
            st.rerun()
        elif not sel and is_selected:
            st.session_state.selected_rows["inventario"].remove(cod)
            st.rerun()

        cant_total = get_cantidad_total(cod)
        stock_disp = get_stock_disponible(cod)

        is_editing = (st.session_state.edit_target["tab"] == "inventario" and st.session_state.edit_target["id"] == cod)
        prefix = "👉 " if is_editing else ""

        c1.markdown(render_cell(f"{prefix}{cod}", is_selected), unsafe_allow_html=True)
        c2.markdown(render_cell(row["Tipo"], is_selected), unsafe_allow_html=True)
        c3.markdown(render_cell(f"<b>{cant_total}</b>", is_selected), unsafe_allow_html=True)
        c4.markdown(render_cell(f"<b>{stock_disp}</b>", is_selected), unsafe_allow_html=True)
        c5.markdown(render_cell(str(row["Última Fecha de Ingreso de Inversión"]), is_selected), unsafe_allow_html=True)
        
        if c6.button("✏️", key=f"edit_inv_{cod}"):
            st.session_state.edit_target = {"tab": "inventario", "id": cod}
            st.rerun()

        if c7.button("🗑️", key=f"del_inv_{cod}"):
            st.session_state.inventario = st.session_state.inventario[st.session_state.inventario["Código"] != cod].reset_index(drop=True)
            if is_editing:
                st.session_state.edit_target = {"tab": None, "id": None}
            st.success(f"Producto {cod} eliminado.")
            st.rerun()

    if st.session_state.edit_target["tab"] == "inventario":
        st.markdown("---")
        target_id = st.session_state.edit_target["id"]
        row_data = st.session_state.inventario[st.session_state.inventario["Código"] == target_id].iloc[0]

        with st.expander(f"✏️ Editando Registro: {target_id}", expanded=True):
            with st.form("form_edit_inv"):
                col_e1, col_e2 = st.columns(2)
                tipo_edit = col_e1.selectbox("Tipo", ["Collar", "Arete", "Pulsera", "Aro"], index=["Collar", "Arete", "Pulsera", "Aro"].index(row_data["Tipo"]) if row_data["Tipo"] in ["Collar", "Arete", "Pulsera", "Aro"] else 0)
                fecha_edit = col_e2.date_input("Última Fecha de Ingreso", value=pd.to_datetime(row_data["Última Fecha de Ingreso de Inversión"]).date())

                btn_save = st.form_submit_button("💾 Guardar Cambios")
                if btn_save:
                    idx_target = st.session_state.inventario.index[st.session_state.inventario["Código"] == target_id][0]
                    st.session_state.inventario.at[idx_target, "Tipo"] = tipo_edit
                    st.session_state.inventario.at[idx_target, "Última Fecha de Ingreso de Inversión"] = str(fecha_edit)
                    st.session_state.edit_target = {"tab": None, "id": None}
                    st.success("¡Registro actualizado!")
                    st.rerun()

    st.markdown("---")
    with st.expander("➕ Añadir Nuevo Producto al Inventario"):
        with st.form("form_add_inv", clear_on_submit=True):
            col_a1, col_a2, col_a3 = st.columns(3)
            cod_new = col_a1.text_input("Código de Producto")
            tipo_new = col_a2.selectbox("Tipo de Producto", ["Collar", "Arete", "Pulsera", "Aro"])
            fecha_new = col_a3.date_input("Fecha de Ingreso", value=date.today())

            btn_add = st.form_submit_button("➕ Registrar Producto")
            if btn_add:
                if not cod_new:
                    st.error("Ingresa un código válido.")
                elif cod_new in st.session_state.inventario["Código"].values:
                    st.error("Este código de producto ya existe.")
                else:
                    new_item = pd.DataFrame([{
                        "Código": cod_new,
                        "Tipo": tipo_new,
                        "Última Fecha de Ingreso de Inversión": str(fecha_new)
                    }])
                    st.session_state.inventario = pd.concat([st.session_state.inventario, new_item], ignore_index=True)
                    st.success("Producto registrado exitosamente.")
                    st.rerun()

# -----------------------------------------------------------------------------
# PESTAÑA 2: CLIENTES
# -----------------------------------------------------------------------------
elif pestana == "2: Clientes":
    st.title("👤 2: Clientes")
    st.caption("Directorio de clientes de MARO")

    st.markdown("### Registro de Clientes")
    cols = st.columns([0.4, 0.8, 2, 2, 2, 0.6, 0.6])
    headers = ["Sel.", "ID", "Nombre", "Apellido", "Celular", "Editar", "Eliminar"]
    for c, h in zip(cols, headers):
        c.markdown(render_header(h), unsafe_allow_html=True)
    st.markdown("---")

    for idx, row in st.session_state.clientes.iterrows():
        c0, c1, c2, c3, c4, c5, c6 = st.columns([0.4, 0.8, 2, 2, 2, 0.6, 0.6])
        
        cid = row["ID"]
        is_selected = cid in st.session_state.selected_rows["clientes"]

        sel = c0.checkbox("", key=f"sel_cli_{cid}", value=is_selected)
        if sel and not is_selected:
            st.session_state.selected_rows["clientes"].add(cid)
            st.rerun()
        elif not sel and is_selected:
            st.session_state.selected_rows["clientes"].remove(cid)
            st.rerun()

        is_editing = (st.session_state.edit_target["tab"] == "clientes" and st.session_state.edit_target["id"] == cid)
        prefix = "👉 " if is_editing else ""

        c1.markdown(render_cell(f"{prefix}{cid}", is_selected), unsafe_allow_html=True)
        c2.markdown(render_cell(row["Nombre"], is_selected), unsafe_allow_html=True)
        c3.markdown(render_cell(row["Apellido"], is_selected), unsafe_allow_html=True)
        c4.markdown(render_cell(row["Celular"], is_selected), unsafe_allow_html=True)

        if c5.button("✏️", key=f"edit_cli_{cid}"):
            st.session_state.edit_target = {"tab": "clientes", "id": cid}
            st.rerun()

        if c6.button("🗑️", key=f"del_cli_{cid}"):
            st.session_state.clientes = st.session_state.clientes[st.session_state.clientes["ID"] != cid].reset_index(drop=True)
            if is_editing:
                st.session_state.edit_target = {"tab": None, "id": None}
            st.success(f"Cliente {row['Nombre']} {row['Apellido']} eliminado.")
            st.rerun()

    if st.session_state.edit_target["tab"] == "clientes":
        st.markdown("---")
        target_id = st.session_state.edit_target["id"]
        row_data = st.session_state.clientes[st.session_state.clientes["ID"] == target_id].iloc[0]

        with st.expander(f"✏️ Editando Cliente ID: {target_id}", expanded=True):
            with st.form("form_edit_cli"):
                col_e1, col_e2, col_e3 = st.columns(3)
                nom_edit = col_e1.text_input("Nombre", value=row_data["Nombre"])
                ape_edit = col_e2.text_input("Apellido", value=row_data["Apellido"])
                cel_edit = col_e3.text_input("Celular", value=row_data["Celular"])

                btn_save = st.form_submit_button("💾 Guardar Cambios")
                if btn_save:
                    idx_target = st.session_state.clientes.index[st.session_state.clientes["ID"] == target_id][0]
                    st.session_state.clientes.at[idx_target, "Nombre"] = nom_edit
                    st.session_state.clientes.at[idx_target, "Apellido"] = ape_edit
                    st.session_state.clientes.at[idx_target, "Celular"] = cel_edit
                    st.session_state.edit_target = {"tab": None, "id": None}
                    st.success("¡Datos actualizados!")
                    st.rerun()

    st.markdown("---")
    with st.expander("➕ Añadir Nuevo Cliente"):
        with st.form("form_add_cli", clear_on_submit=True):
            col_a1, col_a2, col_a3 = st.columns(3)
            nom_new = col_a1.text_input("Nombre")
            ape_new = col_a2.text_input("Apellido")
            cel_new = col_a3.text_input("Celular")

            btn_add = st.form_submit_button("➕ Registrar Cliente")
            if btn_add:
                if not nom_new or not ape_new:
                    st.error("Por favor ingresa nombre y apellido.")
                else:
                    new_id = int(st.session_state.clientes["ID"].max() + 1) if not st.session_state.clientes.empty else 1
                    new_cli = pd.DataFrame([{
                        "ID": new_id,
                        "Nombre": nom_new,
                        "Apellido": ape_new,
                        "Celular": cel_new
                    }])
                    st.session_state.clientes = pd.concat([st.session_state.clientes, new_cli], ignore_index=True)
                    st.success("Cliente agregado exitosamente.")
                    st.rerun()

# -----------------------------------------------------------------------------
# PESTAÑA 3: INVERSIONES
# -----------------------------------------------------------------------------
elif pestana == "3: Inversiones":
    st.title("💼 3: Inversiones")
    st.caption("Registro de inversiones y compras de productos por tipo")

    st.markdown("### Historial de Inversiones")
    cols = st.columns([0.4, 1.1, 1.2, 1.2, 1.1, 1.1, 1.2, 0.6, 0.6])
    headers = ["Sel.", "ID Inversión", "Fecha", "Monto (S/.)", "Producto", "Tipo Producto", "Cant. Ingresada", "Editar", "Eliminar"]
    for c, h in zip(cols, headers):
        c.markdown(render_header(h), unsafe_allow_html=True)
    st.markdown("---")

    for idx, row in st.session_state.inversiones.iterrows():
        c0, c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([0.4, 1.1, 1.2, 1.2, 1.1, 1.1, 1.2, 0.6, 0.6])
        
        invid = row["ID Inversión"]
        is_selected = invid in st.session_state.selected_rows["inversiones"]

        sel = c0.checkbox("", key=f"sel_inv_item_{invid}", value=is_selected)
        if sel and not is_selected:
            st.session_state.selected_rows["inversiones"].add(invid)
            st.rerun()
        elif not sel and is_selected:
            st.session_state.selected_rows["inversiones"].remove(invid)
            st.rerun()

        is_editing = (st.session_state.edit_target["tab"] == "inversiones" and st.session_state.edit_target["id"] == invid)
        prefix = "👉 " if is_editing else ""

        c1.markdown(render_cell(f"{prefix}{invid}", is_selected), unsafe_allow_html=True)
        c2.markdown(render_cell(str(row["Fecha de Inversión"]), is_selected), unsafe_allow_html=True)
        c3.markdown(render_cell(f"S/. {row['Monto de Inversión (S/.)']:.2f}", is_selected), unsafe_allow_html=True)
        c4.markdown(render_cell(row["Producto"], is_selected), unsafe_allow_html=True)
        c5.markdown(render_cell(row["Tipo de Producto"], is_selected), unsafe_allow_html=True)
        c6.markdown(render_cell(str(row["Cantidad Ingresada"]), is_selected), unsafe_allow_html=True)

        if c7.button("✏️", key=f"edit_inv_item_{invid}"):
            st.session_state.edit_target = {"tab": "inversiones", "id": invid}
            st.rerun()

        if c8.button("🗑️", key=f"del_inv_item_{invid}"):
            st.session_state.inversiones = st.session_state.inversiones[st.session_state.inversiones["ID Inversión"] != invid].reset_index(drop=True)
            if is_editing:
                st.session_state.edit_target = {"tab": None, "id": None}
            st.success(f"Inversión {invid} eliminada.")
            st.rerun()

    if st.session_state.edit_target["tab"] == "inversiones":
        st.markdown("---")
        target_id = st.session_state.edit_target["id"]
        row_data = st.session_state.inversiones[st.session_state.inversiones["ID Inversión"] == target_id].iloc[0]

        with st.expander(f"✏️ Editando Inversión: {target_id}", expanded=True):
            with st.form("form_edit_inversion"):
                col_e1, col_e2, col_e3, col_e4 = st.columns(4)
                fecha_edit = col_e1.date_input("Fecha de Inversión", value=pd.to_datetime(row_data["Fecha de Inversión"]).date())
                monto_edit = col_e2.number_input("Monto (S/.)", min_value=0.0, value=float(row_data["Monto de Inversión (S/.)"]))
                tipo_prod_edit = col_e3.selectbox("Tipo de Producto", ["Collar", "Arete", "Pulsera", "Aro"], index=["Collar", "Arete", "Pulsera", "Aro"].index(row_data["Tipo de Producto"]) if row_data["Tipo de Producto"] in ["Collar", "Arete", "Pulsera", "Aro"] else 0)
                cant_edit = col_e4.number_input("Cantidad Ingresada", min_value=1, value=int(row_data["Cantidad Ingresada"]))

                btn_save = st.form_submit_button("💾 Guardar Cambios")
                if btn_save:
                    idx_target = st.session_state.inversiones.index[st.session_state.inversiones["ID Inversión"] == target_id][0]
                    st.session_state.inversiones.at[idx_target, "Fecha de Inversión"] = str(fecha_edit)
                    st.session_state.inversiones.at[idx_target, "Monto de Inversión (S/.)"] = monto_edit
                    st.session_state.inversiones.at[idx_target, "Tipo de Producto"] = tipo_prod_edit
                    st.session_state.inversiones.at[idx_target, "Cantidad Ingresada"] = cant_edit

                    p_code = row_data["Producto"]
                    idx_inv = st.session_state.inventario.index[st.session_state.inventario["Código"] == p_code].tolist()
                    if idx_inv:
                        st.session_state.inventario.at[idx_inv[0], "Última Fecha de Ingreso de Inversión"] = str(fecha_edit)

                    st.session_state.edit_target = {"tab": None, "id": None}
                    st.success("¡Inversión actualizada!")
                    st.rerun()

    st.markdown("---")
    with st.expander("➕ Registrar Nueva Inversión"):
        if st.session_state.inventario.empty:
            st.warning("Debes agregar productos en la pestaña '1: Inventario' primero.")
        else:
            with st.form("form_add_inversion", clear_on_submit=True):
                col_a1, col_a2, col_a3 = st.columns(3)
                fecha_inv_new = col_a1.date_input("Fecha", value=date.today())
                monto_inv_new = col_a2.number_input("Monto Inversión (S/.)", min_value=0.0, value=100.0)
                prod_inv_new = col_a3.selectbox("Código de Producto", st.session_state.inventario["Código"].tolist())

                col_a4, col_a5 = st.columns(2)
                tipo_inv_new = col_a4.selectbox("Tipo de Producto", ["Collar", "Arete", "Pulsera", "Aro"])
                cant_inv_new = col_a5.number_input("Cantidad Ingresada (Productos)", min_value=1, value=5)

                btn_add_inv = st.form_submit_button("💾 Registrar Inversión")
                if btn_add_inv:
                    new_id = f"INV-10{len(st.session_state.inversiones)+1}"
                    new_rec = pd.DataFrame([{
                        "ID Inversión": new_id,
                        "Fecha de Inversión": str(fecha_inv_new),
                        "Monto de Inversión (S/.)": monto_inv_new,
                        "Producto": prod_inv_new,
                        "Tipo de Producto": tipo_inv_new,
                        "Cantidad Ingresada": cant_inv_new
                    }])
                    st.session_state.inversiones = pd.concat([st.session_state.inversiones, new_rec], ignore_index=True)

                    idx_p = st.session_state.inventario.index[st.session_state.inventario["Código"] == prod_inv_new][0]
                    st.session_state.inventario.at[idx_p, "Última Fecha de Ingreso de Inversión"] = str(fecha_inv_new)

                    st.success(f"Inversión registrada correctamente.")
                    st.rerun()

# -----------------------------------------------------------------------------
# PESTAÑA 4: VENTAS
# -----------------------------------------------------------------------------
elif pestana == "4: Ventas":
    st.title("🛒 4: Ventas")
    st.caption("Registro de ventas y deducción de stock")

    st.markdown("### Historial de Ventas")
    cols = st.columns([0.4, 0.8, 1.1, 1.4, 1.1, 1.1, 0.9, 0.8, 0.6, 0.6])
    headers = ["Sel.", "ID", "Fecha", "Cliente", "Pago", "Estado", "Prod.", "Cant.", "Editar", "Eliminar"]
    for c, h in zip(cols, headers):
        c.markdown(render_header(h), unsafe_allow_html=True)
    st.markdown("---")

    for idx, row in st.session_state.ventas.iterrows():
        c0, c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([0.4, 0.8, 1.1, 1.4, 1.1, 1.1, 0.9, 0.8, 0.6, 0.6])
        
        vtid = row["ID Venta"]
        is_selected = vtid in st.session_state.selected_rows["ventas"]

        sel = c0.checkbox("", key=f"sel_vta_{vtid}", value=is_selected)
        if sel and not is_selected:
            st.session_state.selected_rows["ventas"].add(vtid)
            st.rerun()
        elif not sel and is_selected:
            st.session_state.selected_rows["ventas"].remove(vtid)
            st.rerun()

        is_editing = (st.session_state.edit_target["tab"] == "ventas" and st.session_state.edit_target["id"] == vtid)
        prefix = "👉 " if is_editing else ""

        pago_html = render_styled_text(row["Pago"], "pago")
        estado_html = render_styled_text(row["Estado"], "estado")

        c1.markdown(render_cell(f"{prefix}{vtid}", is_selected), unsafe_allow_html=True)
        c2.markdown(render_cell(str(row["Fecha de Venta"]), is_selected), unsafe_allow_html=True)
        c3.markdown(render_cell(row["Cliente"], is_selected), unsafe_allow_html=True)
        c4.markdown(render_cell(pago_html, is_selected), unsafe_allow_html=True)
        c5.markdown(render_cell(estado_html, is_selected), unsafe_allow_html=True)
        c6.markdown(render_cell(row["Producto"], is_selected), unsafe_allow_html=True)
        c7.markdown(render_cell(str(row["Cantidad"]), is_selected), unsafe_allow_html=True)

        if c8.button("✏️", key=f"edit_vta_{vtid}"):
            st.session_state.edit_target = {"tab": "ventas", "id": vtid}
            st.rerun()

        if c9.button("🗑️️", key=f"del_vta_{vtid}"):
            st.session_state.ventas = st.session_state.ventas[st.session_state.ventas["ID Venta"] != vtid].reset_index(drop=True)
            if is_editing:
                st.session_state.edit_target = {"tab": None, "id": None}
            st.success(f"Venta {vtid} eliminada.")
            st.rerun()

    if st.session_state.edit_target["tab"] == "ventas":
        st.markdown("---")
        target_id = st.session_state.edit_target["id"]
        row_data = st.session_state.ventas[st.session_state.ventas["ID Venta"] == target_id].iloc[0]

        with st.expander(f"✏️ Editando Venta: {target_id}", expanded=True):
            with st.form("form_edit_venta"):
                col_e1, col_e2, col_e3, col_e4 = st.columns(4)
                fecha_v_edit = col_e1.date_input("Fecha", value=pd.to_datetime(row_data["Fecha de Venta"]).date())
                pago_edit = col_e2.selectbox("Pago", ["Efectivo", "Transferencia", "Crédito"], index=["Efectivo", "Transferencia", "Crédito"].index(row_data["Pago"]))
                estado_edit = col_e3.selectbox("Estado", ["Pendiente", "Finalizado"], index=["Pendiente", "Finalizado"].index(row_data["Estado"]))
                monto_edit = col_e4.number_input("Monto Total (S/.)", min_value=0.0, value=float(row_data["Monto (S/.)"]))

                btn_save = st.form_submit_button("💾 Guardar Cambios")
                if btn_save:
                    idx_target = st.session_state.ventas.index[st.session_state.ventas["ID Venta"] == target_id][0]
                    st.session_state.ventas.at[idx_target, "Fecha de Venta"] = str(fecha_v_edit)
                    st.session_state.ventas.at[idx_target, "Pago"] = pago_edit
                    st.session_state.ventas.at[idx_target, "Estado"] = estado_edit
                    st.session_state.ventas.at[idx_target, "Monto (S/.)"] = monto_edit

                    st.session_state.edit_target = {"tab": None, "id": None}
                    st.success("¡Venta actualizada!")
                    st.rerun()

    st.markdown("---")
    with st.expander("➕ Registrar Nueva Venta"):
        if st.session_state.inventario.empty:
            st.warning("No hay productos disponibles en inventario.")
        else:
            list_clientes = [f"{r['Nombre']} {r['Apellido']}" for _, r in st.session_state.clientes.iterrows()] if not st.session_state.clientes.empty else ["Cliente Anónimo"]
            
            with st.form("form_add_venta", clear_on_submit=True):
                col_a1, col_a2, col_a3, col_a4 = st.columns(4)
                fecha_v_new = col_a1.date_input("Fecha de Venta", value=date.today())
                cliente_v_new = col_a2.selectbox("Cliente", list_clientes)
                pago_v_new = col_a3.selectbox("Pago", ["Efectivo", "Transferencia", "Crédito"])
                estado_v_new = col_a4.selectbox("Estado", ["Finalizado", "Pendiente"])

                col_a5, col_a6, col_a7 = st.columns(3)
                prod_v_new = col_a5.selectbox("Producto", st.session_state.inventario["Código"].tolist())
                cant_v_new = col_a6.number_input("Cantidad Vendida", min_value=1, value=1)
                monto_v_new = col_a7.number_input("Monto Total (S/.)", min_value=0.0, value=50.0)

                btn_add_vta = st.form_submit_button("🛒 Finalizar y Registrar Venta")
                if btn_add_vta:
                    stock_disp = get_stock_disponible(prod_v_new)

                    if estado_v_new == "Finalizado" and stock_disp < cant_v_new:
                        st.error(f"Stock insuficiente. Solo quedan {stock_disp} unidades disponibles de {prod_v_new}.")
                    else:
                        new_id_v = f"V-50{len(st.session_state.ventas)+1}"
                        new_vta = pd.DataFrame([{
                            "ID Venta": new_id_v,
                            "Fecha de Venta": str(fecha_v_new),
                            "Cliente": cliente_v_new,
                            "Pago": pago_v_new,
                            "Estado": estado_v_new,
                            "Producto": prod_v_new,
                            "Cantidad": cant_v_new,
                            "Monto (S/.)": monto_v_new
                        }])
                        st.session_state.ventas = pd.concat([st.session_state.ventas, new_vta], ignore_index=True)

                        st.success(f"Venta {new_id_v} registrada correctamente.")
                        st.rerun()