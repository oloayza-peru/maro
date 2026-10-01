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

# Estilo personalizado para botones de acción compactos
st.markdown("""
    <style>
    .stButton button {
        padding: 2px 8px;
        font-size: 14px;
        margin: 0px;
    }
    .highlight-row {
        background-color: #2b303c;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PERSISTENCIA DE DATOS (st.session_state)
# -----------------------------------------------------------------------------
if "inventario" not in st.session_state:
    st.session_state.inventario = pd.DataFrame([
        {"Código": "COL-001", "Tipo": "Collar", "Stock": 12, "Última Fecha de Ingreso de Inversión": "2026-09-15"},
        {"Código": "ART-002", "Tipo": "Arete", "Stock": 25, "Última Fecha de Ingreso de Inversión": "2026-09-20"},
        {"Código": "PUL-003", "Tipo": "Pulsera", "Stock": 18, "Última Fecha de Ingreso de Inversión": "2026-09-22"},
        {"Código": "ARO-004", "Tipo": "Aro", "Stock": 30, "Última Fecha de Ingreso de Inversión": "2026-09-25"},
    ])

if "clientes" not in st.session_state:
    st.session_state.clientes = pd.DataFrame([
        {"ID": 1, "Nombre": "María", "Apellido": "García", "Celular": "987654321"},
        {"ID": 2, "Nombre": "Carlos", "Apellido": "Mendoza", "Celular": "912345678"},
    ])

if "inversiones" not in st.session_state:
    st.session_state.inversiones = pd.DataFrame([
        {"ID Inversión": "INV-101", "Fecha de Inversión": "2026-09-15", "Monto de Inversión ($)": 450.0, "Producto": "COL-001", "Cantidad Ingresada": 12},
        {"ID Inversión": "INV-102", "Fecha de Inversión": "2026-09-20", "Monto de Inversión ($)": 300.0, "Producto": "ART-002", "Cantidad Ingresada": 25},
    ])

if "ventas" not in st.session_state:
    st.session_state.ventas = pd.DataFrame([
        {"ID Venta": "V-501", "Fecha de Venta": "2026-09-28", "Cliente": "María García", "Pago": "Efectivo", "Estado": "Finalizado", "Producto": "COL-001", "Cantidad": 2, "Monto ($)": 180.0},
        {"ID Venta": "V-502", "Fecha de Venta": "2026-09-29", "Cliente": "Carlos Mendoza", "Pago": "Transferencia", "Estado": "Pendiente", "Producto": "ART-002", "Cantidad": 1, "Monto ($)": 45.0},
    ])

# Estado para controlar filas en edición
if "edit_target" not in st.session_state:
    st.session_state.edit_target = {"tab": None, "id": None}

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
    st.caption("Control de stock por tipo de producto (Collar, Arete, Pulsera, Aro)")

    # Tabla con botones al final de cada fila
    st.markdown("### Listado de Inventario")
    cols = st.columns([1.5, 1.5, 1.2, 2.5, 0.8, 0.8])
    headers = ["Código", "Tipo", "Stock", "Última Fecha Ingreso", "Editar", "Eliminar"]
    for c, h in zip(cols, headers):
        c.markdown(f"**{h}**")
    st.markdown("---")

    for idx, row in st.session_state.inventario.iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns([1.5, 1.5, 1.2, 2.5, 0.8, 0.8])
        
        is_editing = (st.session_state.edit_target["tab"] == "inventario" and st.session_state.edit_target["id"] == row["Código"])
        prefix = "👉 " if is_editing else ""

        c1.write(f"{prefix}{row['Código']}")
        c2.write(row["Tipo"])
        c3.write(row["Stock"])
        c4.write(str(row["Última Fecha de Ingreso de Inversión"]))
        
        if c5.button("✏️", key=f"edit_inv_{row['Código']}"):
            st.session_state.edit_target = {"tab": "inventario", "id": row["Código"]}
            st.rerun()

        if c6.button("🗑️", key=f"del_inv_{row['Código']}"):
            st.session_state.inventario = st.session_state.inventario[st.session_state.inventario["Código"] != row["Código"]].reset_index(drop=True)
            if is_editing:
                st.session_state.edit_target = {"tab": None, "id": None}
            st.success(f"Producto {row['Código']} eliminado.")
            st.rerun()

    # Formulario desplegable para EDITAR
    if st.session_state.edit_target["tab"] == "inventario":
        st.markdown("---")
        target_id = st.session_state.edit_target["id"]
        row_data = st.session_state.inventario[st.session_state.inventario["Código"] == target_id].iloc[0]

        with st.expander(f"✏️ Editando Registro: {target_id}", expanded=True):
            with st.form("form_edit_inv"):
                col_e1, col_e2, col_e3 = st.columns(3)
                tipo_edit = col_e1.selectbox("Tipo", ["Collar", "Arete", "Pulsera", "Aro"], index=["Collar", "Arete", "Pulsera", "Aro"].index(row_data["Tipo"]) if row_data["Tipo"] in ["Collar", "Arete", "Pulsera", "Aro"] else 0)
                stock_edit = col_e2.number_input("Stock Actual", min_value=0, value=int(row_data["Stock"]))
                fecha_edit = col_e3.date_input("Última Fecha de Ingreso", value=pd.to_datetime(row_data["Última Fecha de Ingreso de Inversión"]).date())

                btn_save = st.form_submit_button("💾 Guardar Cambios")
                if btn_save:
                    idx_target = st.session_state.inventario.index[st.session_state.inventario["Código"] == target_id][0]
                    st.session_state.inventario.at[idx_target, "Tipo"] = tipo_edit
                    st.session_state.inventario.at[idx_target, "Stock"] = stock_edit
                    st.session_state.inventario.at[idx_target, "Última Fecha de Ingreso de Inversión"] = str(fecha_edit)
                    st.session_state.edit_target = {"tab": None, "id": None}
                    st.success("¡Registro de inventario actualizado correctamente!")
                    st.rerun()

    # Formulario para AÑADIR NUEVO
    st.markdown("---")
    with st.expander("➕ Añadir Nuevo Producto al Inventario"):
        with st.form("form_add_inv", clear_on_submit=True):
            col_a1, col_a2, col_a3, col_a4 = st.columns(4)
            cod_new = col_a1.text_input("Código de Producto (ej. COL-005)")
            tipo_new = col_a2.selectbox("Tipo de Producto", ["Collar", "Arete", "Pulsera", "Aro"])
            stock_new = col_a3.number_input("Stock Inicial", min_value=0, value=1)
            fecha_new = col_a4.date_input("Fecha de Ingreso", value=date.today())

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
                        "Stock": stock_new,
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
    cols = st.columns([1, 2, 2, 2, 0.8, 0.8])
    headers = ["ID", "Nombre", "Apellido", "Celular", "Editar", "Eliminar"]
    for c, h in zip(cols, headers):
        c.markdown(f"**{h}**")
    st.markdown("---")

    for idx, row in st.session_state.clientes.iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 2, 2, 0.8, 0.8])
        
        is_editing = (st.session_state.edit_target["tab"] == "clientes" and st.session_state.edit_target["id"] == row["ID"])
        prefix = "👉 " if is_editing else ""

        c1.write(f"{prefix}{row['ID']}")
        c2.write(row["Nombre"])
        c3.write(row["Apellido"])
        c4.write(row["Celular"])

        if c5.button("✏️", key=f"edit_cli_{row['ID']}"):
            st.session_state.edit_target = {"tab": "clientes", "id": row["ID"]}
            st.rerun()

        if c6.button("🗑️", key=f"del_cli_{row['ID']}"):
            st.session_state.clientes = st.session_state.clientes[st.session_state.clientes["ID"] != row["ID"]].reset_index(drop=True)
            if is_editing:
                st.session_state.edit_target = {"tab": None, "id": None}
            st.success(f"Cliente {row['Nombre']} {row['Apellido']} eliminado.")
            st.rerun()

    # Formulario desplegable para EDITAR
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
                    st.success("¡Datos del cliente actualizados!")
                    st.rerun()

    # Formulario para AÑADIR NUEVO
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
    st.caption("Registro de gastos en mercadería que incrementan el stock automáticamente")

    st.markdown("### Historial de Inversiones")
    cols = st.columns([1.2, 1.5, 1.5, 1.5, 1.2, 0.8, 0.8])
    headers = ["ID Inversión", "Fecha", "Monto ($)", "Producto", "Cant. Ingresada", "Editar", "Eliminar"]
    for c, h in zip(cols, headers):
        c.markdown(f"**{h}**")
    st.markdown("---")

    for idx, row in st.session_state.inversiones.iterrows():
        c1, c2, c3, c4, c5, c6, c7 = st.columns([1.2, 1.5, 1.5, 1.5, 1.2, 0.8, 0.8])
        
        is_editing = (st.session_state.edit_target["tab"] == "inversiones" and st.session_state.edit_target["id"] == row["ID Inversión"])
        prefix = "👉 " if is_editing else ""

        c1.write(f"{prefix}{row['ID Inversión']}")
        c2.write(str(row["Fecha de Inversión"]))
        c3.write(f"${row['Monto de Inversión ($)']:.2f}")
        c4.write(row["Producto"])
        c5.write(row["Cantidad Ingresada"])

        if c6.button("✏️", key=f"edit_inv_item_{row['ID Inversión']}"):
            st.session_state.edit_target = {"tab": "inversiones", "id": row["ID Inversión"]}
            st.rerun()

        if c7.button("🗑️", key=f"del_inv_item_{row['ID Inversión']}"):
            # Revertir stock
            p_code = row["Producto"]
            cant = row["Cantidad Ingresada"]
            idx_inv = st.session_state.inventario.index[st.session_state.inventario["Código"] == p_code].tolist()
            if idx_inv:
                st.session_state.inventario.at[idx_inv[0], "Stock"] = max(0, st.session_state.inventario.at[idx_inv[0], "Stock"] - cant)

            st.session_state.inversiones = st.session_state.inversiones[st.session_state.inversiones["ID Inversión"] != row["ID Inversión"]].reset_index(drop=True)
            if is_editing:
                st.session_state.edit_target = {"tab": None, "id": None}
            st.success(f"Inversión {row['ID Inversión']} eliminada y stock descontado.")
            st.rerun()

    # Formulario desplegable para EDITAR
    if st.session_state.edit_target["tab"] == "inversiones":
        st.markdown("---")
        target_id = st.session_state.edit_target["id"]
        row_data = st.session_state.inversiones[st.session_state.inversiones["ID Inversión"] == target_id].iloc[0]

        with st.expander(f"✏️ Editando Inversión: {target_id}", expanded=True):
            with st.form("form_edit_inversion"):
                col_e1, col_e2, col_e3 = st.columns(3)
                fecha_edit = col_e1.date_input("Fecha de Inversión", value=pd.to_datetime(row_data["Fecha de Inversión"]).date())
                monto_edit = col_e2.number_input("Monto ($)", min_value=0.0, value=float(row_data["Monto de Inversión ($)"]))
                cant_edit = col_e3.number_input("Cantidad Ingresada", min_value=1, value=int(row_data["Cantidad Ingresada"]))

                btn_save = st.form_submit_button("💾 Guardar Cambios")
                if btn_save:
                    # Ajustar diferencia en inventario
                    diff = cant_edit - int(row_data["Cantidad Ingresada"])
                    p_code = row_data["Producto"]
                    idx_inv = st.session_state.inventario.index[st.session_state.inventario["Código"] == p_code].tolist()
                    if idx_inv:
                        st.session_state.inventario.at[idx_inv[0], "Stock"] += diff
                        st.session_state.inventario.at[idx_inv[0], "Última Fecha de Ingreso de Inversión"] = str(fecha_edit)

                    idx_target = st.session_state.inversiones.index[st.session_state.inversiones["ID Inversión"] == target_id][0]
                    st.session_state.inversiones.at[idx_target, "Fecha de Inversión"] = str(fecha_edit)
                    st.session_state.inversiones.at[idx_target, "Monto de Inversión ($)"] = monto_edit
                    st.session_state.inversiones.at[idx_target, "Cantidad Ingresada"] = cant_edit

                    st.session_state.edit_target = {"tab": None, "id": None}
                    st.success("¡Inversión e inventario actualizados con éxito!")
                    st.rerun()

    # Formulario para AÑADIR NUEVA INVERSIÓN
    st.markdown("---")
    with st.expander("➕ Registrar Nueva Inversión"):
        if st.session_state.inventario.empty:
            st.warning("Debes agregar productos en la pestaña '1: Inventario' primero.")
        else:
            with st.form("form_add_inversion", clear_on_submit=True):
                col_a1, col_a2, col_a3, col_a4 = st.columns(4)
                fecha_inv_new = col_a1.date_input("Fecha", value=date.today())
                monto_inv_new = col_a2.number_input("Monto Inversión ($)", min_value=0.0, value=100.0)
                prod_inv_new = col_a3.selectbox("Producto de Inversión", st.session_state.inventario["Código"].tolist())
                cant_inv_new = col_a4.number_input("Cantidad Comprada", min_value=1, value=5)

                btn_add_inv = st.form_submit_button("💾 Registrar e Incrementar Stock")
                if btn_add_inv:
                    new_id = f"INV-10{len(st.session_state.inversiones)+1}"
                    new_rec = pd.DataFrame([{
                        "ID Inversión": new_id,
                        "Fecha de Inversión": str(fecha_inv_new),
                        "Monto de Inversión ($)": monto_inv_new,
                        "Producto": prod_inv_new,
                        "Cantidad Ingresada": cant_inv_new
                    }])
                    st.session_state.inversiones = pd.concat([st.session_state.inversiones, new_rec], ignore_index=True)

                    # Incrementar stock y actualizar fecha
                    idx_p = st.session_state.inventario.index[st.session_state.inventario["Código"] == prod_inv_new][0]
                    st.session_state.inventario.at[idx_p, "Stock"] += cant_inv_new
                    st.session_state.inventario.at[idx_p, "Última Fecha de Ingreso de Inversión"] = str(fecha_inv_new)

                    st.success(f"Inversión registrada. Se agregaron {cant_inv_new} unidades al producto {prod_inv_new}.")
                    st.rerun()

# -----------------------------------------------------------------------------
# PESTAÑA 4: VENTAS
# -----------------------------------------------------------------------------
elif pestana == "4: Ventas":
    st.title("🛒 4: Ventas")
    st.caption("Registro de ventas, cliente asociado, método de pago y estado")

    st.markdown("### Historial de Ventas")
    cols = st.columns([1, 1.2, 1.5, 1.2, 1.2, 1, 1, 0.8, 0.8])
    headers = ["ID", "Fecha", "Cliente", "Pago", "Estado", "Prod.", "Cant.", "Editar", "Eliminar"]
    for c, h in zip(cols, headers):
        c.markdown(f"**{h}**")
    st.markdown("---")

    for idx, row in st.session_state.ventas.iterrows():
        c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([1, 1.2, 1.5, 1.2, 1.2, 1, 1, 0.8, 0.8])
        
        is_editing = (st.session_state.edit_target["tab"] == "ventas" and st.session_state.edit_target["id"] == row["ID Venta"])
        prefix = "👉 " if is_editing else ""

        c1.write(f"{prefix}{row['ID Venta']}")
        c2.write(str(row["Fecha de Venta"]))
        c3.write(row["Cliente"])
        c4.write(row["Pago"])
        c5.write(row["Estado"])
        c6.write(row["Producto"])
        c7.write(row["Cantidad"])

        if c8.button("✏️", key=f"edit_vta_{row['ID Venta']}"):
            st.session_state.edit_target = {"tab": "ventas", "id": row["ID Venta"]}
            st.rerun()

        if c9.button("🗑️", key=f"del_vta_{row['ID Venta']}"):
            # Revertir stock si estaba finalizada
            if row["Estado"] == "Finalizado":
                p_code = row["Producto"]
                cant = row["Cantidad"]
                idx_inv = st.session_state.inventario.index[st.session_state.inventario["Código"] == p_code].tolist()
                if idx_inv:
                    st.session_state.inventario.at[idx_inv[0], "Stock"] += cant

            st.session_state.ventas = st.session_state.ventas[st.session_state.ventas["ID Venta"] != row["ID Venta"]].reset_index(drop=True)
            if is_editing:
                st.session_state.edit_target = {"tab": None, "id": None}
            st.success(f"Venta {row['ID Venta']} eliminada.")
            st.rerun()

    # Formulario desplegable para EDITAR
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
                monto_edit = col_e4.number_input("Monto Total ($)", min_value=0.0, value=float(row_data["Monto ($)"]))

                btn_save = st.form_submit_button("💾 Guardar Cambios")
                if btn_save:
                    idx_target = st.session_state.ventas.index[st.session_state.ventas["ID Venta"] == target_id][0]
                    estado_prev = st.session_state.ventas.at[idx_target, "Estado"]

                    # Ajuste de stock por cambio de estado
                    p_code = row_data["Producto"]
                    cant = row_data["Cantidad"]
                    idx_inv = st.session_state.inventario.index[st.session_state.inventario["Código"] == p_code].tolist()

                    if idx_inv:
                        if estado_prev != "Finalizado" and estado_edit == "Finalizado":
                            st.session_state.inventario.at[idx_inv[0], "Stock"] = max(0, st.session_state.inventario.at[idx_inv[0], "Stock"] - cant)
                        elif estado_prev == "Finalizado" and estado_edit == "Pendiente":
                            st.session_state.inventario.at[idx_inv[0], "Stock"] += cant

                    st.session_state.ventas.at[idx_target, "Fecha de Venta"] = str(fecha_v_edit)
                    st.session_state.ventas.at[idx_target, "Pago"] = pago_edit
                    st.session_state.ventas.at[idx_target, "Estado"] = estado_edit
                    st.session_state.ventas.at[idx_target, "Monto ($)"] = monto_edit

                    st.session_state.edit_target = {"tab": None, "id": None}
                    st.success("¡Venta actualizada!")
                    st.rerun()

    # Formulario para AÑADIR NUEVA VENTA
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
                monto_v_new = col_a7.number_input("Monto Total ($)", min_value=0.0, value=50.0)

                btn_add_vta = st.form_submit_button("🛒 Finalizar y Registrar Venta")
                if btn_add_vta:
                    idx_p = st.session_state.inventario.index[st.session_state.inventario["Código"] == prod_v_new][0]
                    stock_actual = st.session_state.inventario.at[idx_p, "Stock"]

                    if estado_v_new == "Finalizado" and stock_actual < cant_v_new:
                        st.error(f"Stock insuficiente. Solo quedan {stock_actual} unidades disponibles de {prod_v_new}.")
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
                            "Monto ($)": monto_v_new
                        }])
                        st.session_state.ventas = pd.concat([st.session_state.ventas, new_vta], ignore_index=True)

                        # Descontar stock si está finalizada
                        if estado_v_new == "Finalizado":
                            st.session_state.inventario.at[idx_p, "Stock"] -= cant_v_new

                        st.success(f"Venta {new_id_v} registrada correctamente.")
                        st.rerun()