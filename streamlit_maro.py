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
st.caption("Panel interactivo con opciones de Edición (✏️) y Eliminación (🗑️) para control total de datos.")

# -----------------------------------------------------------------------------
# INICIALIZACIÓN DE DATOS (st.session_state)
# -----------------------------------------------------------------------------

if "inventario" not in st.session_state:
    st.session_state.inventario = pd.DataFrame([
        {"Código": "JOY-001", "Nombre": "Collar de Oro Solitario", "Tipo": "Collar", "Cantidad": 10, "Última Fecha Ingreso": "2026-09-15"},
        {"Código": "JOY-002", "Nombre": "Aretes Perla Cultivada", "Tipo": "Arete", "Cantidad": 15, "Última Fecha Ingreso": "2026-09-20"},
        {"Código": "JOY-003", "Nombre": "Pulsera Plata 925", "Tipo": "Pulsera", "Cantidad": 8, "Última Fecha Ingreso": "2026-09-25"},
        {"Código": "JOY-004", "Nombre": "Aro de Matrimonio 18K", "Tipo": "Aro", "Cantidad": 5, "Última Fecha Ingreso": "2026-09-28"}
    ])

if "clientes" not in st.session_state:
    st.session_state.clientes = pd.DataFrame([
        {"ID Cliente": "CLI-001", "Nombre": "María", "Apellido": "García", "Celular": "987654321"},
        {"ID Cliente": "CLI-002", "Nombre": "Carlos", "Apellido": "Pérez", "Celular": "912345678"}
    ])

if "inversiones" not in st.session_state:
    st.session_state.inversiones = pd.DataFrame([
        {"ID Inversión": "INV-001", "Fecha de Inversión": "2026-09-15", "Monto de Inversión ($)": 500.0, "Producto Invertido": "JOY-001", "Cantidad Ingresada": 10}
    ])

if "ventas" not in st.session_state:
    st.session_state.ventas = pd.DataFrame([
        {"ID Venta": "V-001", "Fecha de Venta": "2026-09-29", "Cliente": "María García", "Producto": "JOY-001", "Cantidad": 1, "Pago": "Efectivo", "Estado": "Finalizado"}
    ])

# Estado para controlar la edición actual
if "edit_state" not in st.session_state:
    st.session_state.edit_state = {"tab": None, "id": None}

# -----------------------------------------------------------------------------
# PESTAÑAS PRINCIPALES
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
    st.caption("Listado de productos con opciones para eliminar (🗑️) o editar (✏️).")

    if not st.session_state.inventario.empty:
        # Renderizado fila por fila con botones de acción a la izquierda
        header_cols = st.columns([0.6, 0.6, 1.2, 2, 1.2, 1, 1.5])
        header_cols[0].write("**🗑️**")
        header_cols[1].write("**✏️**")
        header_cols[2].write("**Código**")
        header_cols[3].write("**Nombre**")
        header_cols[4].write("**Tipo**")
        header_cols[5].write("**Cantidad**")
        header_cols[6].write("**Última Fecha Ingreso**")
        st.divider()

        for idx, row in st.session_state.inventario.iterrows():
            c_del, c_edit, c_code, c_name, c_type, c_qty, c_date = st.columns([0.6, 0.6, 1.2, 2, 1.2, 1, 1.5])
            
            # Botón Eliminar
            if c_del.button("🗑️", key=f"del_inv_{idx}"):
                st.session_state.inventario = st.session_state.inventario.drop(idx).reset_index(drop=True)
                st.success("Producto eliminado del inventario.")
                st.rerun()
            
            # Botón Editar
            if c_edit.button("✏️", key=f"edit_inv_{idx}"):
                st.session_state.edit_state = {"tab": "inventario", "id": idx}
                st.rerun()

            c_code.write(row["Código"])
            c_name.write(row["Nombre"])
            c_type.write(row["Tipo"])
            c_qty.write(row["Cantidad"])
            c_date.write(str(row["Última Fecha Ingreso"]))

    else:
        st.info("El inventario está vacío.")

    st.markdown("---")

    # Formulario de edición si se seleccionó un producto
    if st.session_state.edit_state["tab"] == "inventario":
        e_idx = st.session_state.edit_state["id"]
        if e_idx in st.session_state.inventario.index:
            curr_row = st.session_state.inventario.loc[e_idx]
            st.subheader(f"✏️ Editar Producto: {curr_row['Código']}")
            with st.form("form_edit_inv"):
                col1, col2, col3 = st.columns(3)
                e_code = col1.text_input("Código", value=curr_row["Código"])
                e_name = col2.text_input("Nombre", value=curr_row["Nombre"])
                
                tipos = ["Collar", "Arete", "Pulsera", "Aro", "Otro"]
                t_idx = tipos.index(curr_row["Tipo"]) if curr_row["Tipo"] in tipos else 0
                e_type = col3.selectbox("Tipo de Joya", tipos, index=t_idx)

                col4, col5 = st.columns(2)
                e_qty = col4.number_input("Cantidad", min_value=0, value=int(curr_row["Cantidad"]))
                
                try:
                    f_val = datetime.strptime(str(curr_row["Última Fecha Ingreso"]), "%Y-%m-%d")
                except:
                    f_val = datetime.now()
                e_date = col5.date_input("Última Fecha Ingreso", value=f_val)

                btn_save = st.form_submit_button("💾 Guardar Cambios")
                btn_cancel = st.form_submit_button("❌ Cancelar")

                if btn_save:
                    st.session_state.inventario.at[e_idx, "Código"] = e_code
                    st.session_state.inventario.at[e_idx, "Nombre"] = e_name
                    st.session_state.inventario.at[e_idx, "Tipo"] = e_type
                    st.session_state.inventario.at[e_idx, "Cantidad"] = e_qty
                    st.session_state.inventario.at[e_idx, "Última Fecha Ingreso"] = str(e_date)
                    st.session_state.edit_state = {"tab": None, "id": None}
                    st.success("Producto actualizado correctamente.")
                    st.rerun()

                if btn_cancel:
                    st.session_state.edit_state = {"tab": None, "id": None}
                    st.rerun()

    # Formulario para añadir nuevo producto
    with st.expander("➕ Codificar Nuevo Producto en Catálogo"):
        with st.form("form_inventario", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            codigo = c1.text_input("Código/SKU", value=f"JOY-00{len(st.session_state.inventario)+1}")
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
    st.caption("Opciones directas para modificar (✏️) o eliminar (🗑️) datos de clientes.")

    if not st.session_state.clientes.empty:
        header_cols = st.columns([0.6, 0.6, 1.5, 2, 2, 2])
        header_cols[0].write("**🗑️**")
        header_cols[1].write("**✏️**")
        header_cols[2].write("**ID Cliente**")
        header_cols[3].write("**Nombre**")
        header_cols[4].write("**Apellido**")
        header_cols[5].write("**Celular**")
        st.divider()

        for idx, row in st.session_state.clientes.iterrows():
            c_del, c_edit, c_id, c_nom, c_ape, c_cel = st.columns([0.6, 0.6, 1.5, 2, 2, 2])
            
            if c_del.button("🗑️", key=f"del_cli_{idx}"):
                st.session_state.clientes = st.session_state.clientes.drop(idx).reset_index(drop=True)
                st.success("Cliente eliminado.")
                st.rerun()

            if c_edit.button("✏️", key=f"edit_cli_{idx}"):
                st.session_state.edit_state = {"tab": "clientes", "id": idx}
                st.rerun()

            c_id.write(row["ID Cliente"])
            c_nom.write(row["Nombre"])
            c_ape.write(row["Apellido"])
            c_cel.write(str(row["Celular"]))
    else:
        st.info("No hay clientes registrados.")

    st.markdown("---")

    # Formulario de edición de cliente
    if st.session_state.edit_state["tab"] == "clientes":
        e_idx = st.session_state.edit_state["id"]
        if e_idx in st.session_state.clientes.index:
            curr_row = st.session_state.clientes.loc[e_idx]
            st.subheader(f"✏️ Editar Cliente: {curr_row['ID Cliente']}")
            with st.form("form_edit_cli"):
                col1, col2, col3 = st.columns(3)
                e_nom = col1.text_input("Nombre", value=curr_row["Nombre"])
                e_ape = col2.text_input("Apellido", value=curr_row["Apellido"])
                e_cel = col3.text_input("Celular", value=str(curr_row["Celular"]))

                btn_save = st.form_submit_button("💾 Guardar Cambios")
                btn_cancel = st.form_submit_button("❌ Cancelar")

                if btn_save:
                    st.session_state.clientes.at[e_idx, "Nombre"] = e_nom
                    st.session_state.clientes.at[e_idx, "Apellido"] = e_ape
                    st.session_state.clientes.at[e_idx, "Celular"] = e_cel
                    st.session_state.edit_state = {"tab": None, "id": None}
                    st.success("Datos del cliente actualizados.")
                    st.rerun()

                if btn_cancel:
                    st.session_state.edit_state = {"tab": None, "id": None}
                    st.rerun()

    # Agregar cliente
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
    st.caption("Al eliminar o modificar inversiones, el stock del producto asociado se reajusta automáticamente.")

    if not st.session_state.inversiones.empty:
        header_cols = st.columns([0.6, 0.6, 1.2, 1.5, 1.5, 1.8, 1.2])
        header_cols[0].write("**🗑️**")
        header_cols[1].write("**✏️**")
        header_cols[2].write("**ID Inv.**")
        header_cols[3].write("**Fecha**")
        header_cols[4].write("**Monto ($)**")
        header_cols[5].write("**Producto**")
        header_cols[6].write("**Cant. Ingresada**")
        st.divider()

        for idx, row in st.session_state.inversiones.iterrows():
            c_del, c_edit, c_id, c_date, c_amount, c_prod, c_qty = st.columns([0.6, 0.6, 1.2, 1.5, 1.5, 1.8, 1.2])

            # Eliminar Inversión
            if c_del.button("🗑️", key=f"del_invm_{idx}"):
                p_code = row["Producto Invertido"]
                qty = row["Cantidad Ingresada"]
                
                # Descontar stock previamente sumado
                idx_inv = st.session_state.inventario.index[st.session_state.inventario["Código"] == p_code].tolist()
                if idx_inv:
                    st.session_state.inventario.at[idx_inv[0], "Cantidad"] = max(0, st.session_state.inventario.at[idx_inv[0], "Cantidad"] - qty)

                st.session_state.inversiones = st.session_state.inversiones.drop(idx).reset_index(drop=True)
                st.success("Inversión eliminada y stock reajustado.")
                st.rerun()

            # Editar Inversión
            if c_edit.button("✏️", key=f"edit_invm_{idx}"):
                st.session_state.edit_state = {"tab": "inversiones", "id": idx}
                st.rerun()

            c_id.write(row["ID Inversión"])
            c_date.write(str(row["Fecha de Inversión"]))
            c_amount.write(f"${row['Monto de Inversión ($)']:.2f}")
            c_prod.write(row["Producto Invertido"])
            c_qty.write(row["Cantidad Ingresada"])
    else:
        st.info("No hay inversiones registradas.")

    st.markdown("---")

    # Formulario de edición de Inversión
    if st.session_state.edit_state["tab"] == "inversiones":
        e_idx = st.session_state.edit_state["id"]
        if e_idx in st.session_state.inversiones.index:
            curr_row = st.session_state.inversiones.loc[e_idx]
            st.subheader(f"✏️ Editar Inversión: {curr_row['ID Inversión']}")
            with st.form("form_edit_inversion"):
                col1, col2 = st.columns(2)
                try:
                    f_val = datetime.strptime(str(curr_row["Fecha de Inversión"]), "%Y-%m-%d")
                except:
                    f_val = datetime.now()
                e_date = col1.date_input("Fecha de Inversión", value=f_val)
                e_monto = col2.number_input("Monto de Inversión ($)", min_value=0.1, value=float(curr_row["Monto de Inversión ($)"]))

                col3, col4 = st.columns(2)
                opciones_p = st.session_state.inventario["Código"].tolist()
                p_idx = opciones_p.index(curr_row["Producto Invertido"]) if curr_row["Producto Invertido"] in opciones_p else 0
                e_prod = col3.selectbox("Producto Invertido", opciones_p, index=p_idx)
                e_qty = col4.number_input("Cantidad Ingresada", min_value=1, value=int(curr_row["Cantidad Ingresada"]))

                btn_save = st.form_submit_button("💾 Guardar Cambios")
                btn_cancel = st.form_submit_button("❌ Cancelar")

                if btn_save:
                    # Ajustar diferencia de stock
                    old_prod = curr_row["Producto Invertido"]
                    old_qty = curr_row["Cantidad Ingresada"]

                    # Revertir previo
                    idx_old = st.session_state.inventario.index[st.session_state.inventario["Código"] == old_prod].tolist()
                    if idx_old:
                        st.session_state.inventario.at[idx_old[0], "Cantidad"] = max(0, st.session_state.inventario.at[idx_old[0], "Cantidad"] - old_qty)

                    # Aplicar nuevo
                    idx_new = st.session_state.inventario.index[st.session_state.inventario["Código"] == e_prod].tolist()
                    if idx_new:
                        st.session_state.inventario.at[idx_new[0], "Cantidad"] += e_qty
                        st.session_state.inventario.at[idx_new[0], "Última Fecha Ingreso"] = str(e_date)

                    st.session_state.inversiones.at[e_idx, "Fecha de Inversión"] = str(e_date)
                    st.session_state.inversiones.at[e_idx, "Monto de Inversión ($)"] = e_monto
                    st.session_state.inversiones.at[e_idx, "Producto Invertido"] = e_prod
                    st.session_state.inversiones.at[e_idx, "Cantidad Ingresada"] = e_qty

                    st.session_state.edit_state = {"tab": None, "id": None}
                    st.success("Inversión y stock actualizados correctamente.")
                    st.rerun()

                if btn_cancel:
                    st.session_state.edit_state = {"tab": None, "id": None}
                    st.rerun()

    # Añadir nueva inversión
    st.subheader("➕ Añadir Nueva Inversión")
    if st.session_state.inventario.empty:
        st.warning("Primero debes codificar productos en la pestaña '1. Inventario'.")
    else:
        with st.form("form_inversion", clear_on_submit=True):
            col_i1, col_i2 = st.columns(2)
            fecha_inv = col_i1.date_input("Fecha de Inversión", value=datetime.now())
            monto_inv = col_i2.number_input("Monto de Inversión ($)", min_value=0.1, value=100.0, step=10.0)

            col_i3, col_i4 = st.columns(2)
            opciones_prod = st.session_state.inventario["Código"].tolist()
            prod_sel = col_i3.selectbox("Producto(s) de Inversión (Código)", opciones_prod)
            cant_inv = col_i4.number_input("Cantidad Adquirida", min_value=1, value=1, step=1)

            btn_registrar_inv = st.form_submit_button("Registrar Inversión e Incrementar Stock")

            if btn_registrar_inv:
                nueva_inv = pd.DataFrame([{
                    "ID Inversión": f"INV-00{len(st.session_state.inversiones)+1}",
                    "Fecha de Inversión": str(fecha_inv),
                    "Monto de Inversión ($)": monto_inv,
                    "Producto Invertido": prod_sel,
                    "Cantidad Ingresada": cant_inv
                }])
                st.session_state.inversiones = pd.concat([st.session_state.inversiones, nueva_inv], ignore_index=True)

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
    st.caption("Control de transacciones con opciones para actualizar (✏️) o anular/eliminar (🗑️).")

    if not st.session_state.ventas.empty:
        header_cols = st.columns([0.6, 0.6, 1, 1.2, 1.8, 1.2, 0.8, 1.2, 1.2])
        header_cols[0].write("**🗑️**")
        header_cols[1].write("**✏️**")
        header_cols[2].write("**ID Venta**")
        header_cols[3].write("**Fecha**")
        header_cols[4].write("**Cliente**")
        header_cols[5].write("**Producto**")
        header_cols[6].write("**Cant.**")
        header_cols[7].write("**Pago**")
        header_cols[8].write("**Estado**")
        st.divider()

        for idx, row in st.session_state.ventas.iterrows():
            c_del, c_edit, c_id, c_date, c_cli, c_prod, c_qty, c_pay, c_status = st.columns([0.6, 0.6, 1, 1.2, 1.8, 1.2, 0.8, 1.2, 1.2])

            # Eliminar Venta
            if c_del.button("🗑️", key=f"del_vta_{idx}"):
                p_code = row["Producto"]
                qty = row["Cantidad"]

                # Reponer stock al cancelar/eliminar venta
                idx_p = st.session_state.inventario.index[st.session_state.inventario["Código"] == p_code].tolist()
                if idx_p:
                    st.session_state.inventario.at[idx_p[0], "Cantidad"] += qty

                st.session_state.ventas = st.session_state.ventas.drop(idx).reset_index(drop=True)
                st.success("Venta eliminada y stock restituido.")
                st.rerun()

            # Editar Venta
            if c_edit.button("✏️️", key=f"edit_vta_{idx}"):
                st.session_state.edit_state = {"tab": "ventas", "id": idx}
                st.rerun()

            c_id.write(row["ID Venta"])
            c_date.write(str(row["Fecha de Venta"]))
            c_cli.write(row["Cliente"])
            c_prod.write(row["Producto"])
            c_qty.write(row["Cantidad"])
            c_pay.write(row["Pago"])
            c_status.write(row["Estado"])

    else:
        st.info("No hay ventas registradas.")

    st.markdown("---")

    # Formulario de edición de Venta
    if st.session_state.edit_state["tab"] == "ventas":
        e_idx = st.session_state.edit_state["id"]
        if e_idx in st.session_state.ventas.index:
            curr_row = st.session_state.ventas.loc[e_idx]
            st.subheader(f"✏️ Editar Venta: {curr_row['ID Venta']}")
            
            lista_clientes = (st.session_state.clientes["Nombre"] + " " + st.session_state.clientes["Apellido"]).tolist() if not st.session_state.clientes.empty else ["Cliente Anonimo"]
            lista_prods = st.session_state.inventario["Código"].tolist()

            with st.form("form_edit_venta"):
                col1, col2 = st.columns(2)
                try:
                    f_val = datetime.strptime(str(curr_row["Fecha de Venta"]), "%Y-%m-%d")
                except:
                    f_val = datetime.now()
                e_date = col1.date_input("Fecha de Venta", value=f_val)
                
                cli_idx = lista_clientes.index(curr_row["Cliente"]) if curr_row["Cliente"] in lista_clientes else 0
                e_cli = col2.selectbox("Cliente", lista_clientes, index=cli_idx)

                col3, col4 = st.columns(2)
                p_idx = lista_prods.index(curr_row["Producto"]) if curr_row["Producto"] in lista_prods else 0
                e_prod = col3.selectbox("Producto", lista_prods, index=p_idx)
                e_qty = col4.number_input("Cantidad", min_value=1, value=int(curr_row["Cantidad"]))

                col5, col6 = st.columns(2)
                pagos = ["Efectivo", "Transferencia", "Crédito"]
                pay_idx = pagos.index(curr_row["Pago"]) if curr_row["Pago"] in pagos else 0
                e_pay = col5.selectbox("Pago", pagos, index=pay_idx)

                estados = ["Pendiente", "Finalizado"]
                st_idx = estados.index(curr_row["Estado"]) if curr_row["Estado"] in estados else 0
                e_status = col6.selectbox("Estado", estados, index=st_idx)

                btn_save = st.form_submit_button("💾 Guardar Cambios")
                btn_cancel = st.form_submit_button("❌ Cancelar")

                if btn_save:
                    # Reajustar inventario
                    old_prod = curr_row["Producto"]
                    old_qty = curr_row["Cantidad"]

                    # Reponer previo
                    idx_old = st.session_state.inventario.index[st.session_state.inventario["Código"] == old_prod].tolist()
                    if idx_old:
                        st.session_state.inventario.at[idx_old[0], "Cantidad"] += old_qty

                    # Descontar nuevo
                    idx_new = st.session_state.inventario.index[st.session_state.inventario["Código"] == e_prod].tolist()
                    if idx_new:
                        st.session_state.inventario.at[idx_new[0], "Cantidad"] = max(0, st.session_state.inventario.at[idx_new[0], "Cantidad"] - e_qty)

                    st.session_state.ventas.at[e_idx, "Fecha de Venta"] = str(e_date)
                    st.session_state.ventas.at[e_idx, "Cliente"] = e_cli
                    st.session_state.ventas.at[e_idx, "Producto"] = e_prod
                    st.session_state.ventas.at[e_idx, "Cantidad"] = e_qty
                    st.session_state.ventas.at[e_idx, "Pago"] = e_pay
                    st.session_state.ventas.at[e_idx, "Estado"] = e_status

                    st.session_state.edit_state = {"tab": None, "id": None}
                    st.success("Venta y stock actualizados correctamente.")
                    st.rerun()

                if btn_cancel:
                    st.session_state.edit_state = {"tab": None, "id": None}
                    st.rerun()

    # Formulario registrar venta
    st.subheader("➕ Registrar Nueva Venta")
    if st.session_state.inventario.empty:
        st.warning("No hay productos disponibles.")
    else:
        lista_clientes = (st.session_state.clientes["Nombre"] + " " + st.session_state.clientes["Apellido"]).tolist() if not st.session_state.clientes.empty else ["Cliente Anonimo"]
        lista_prods = st.session_state.inventario["Código"].tolist()

        with st.form("form_venta", clear_on_submit=True):
            v_col1, v_col2 = st.columns(2)
            fecha_vta = v_col1.date_input("Fecha de Venta", value=datetime.now())
            cliente_sel = v_col2.selectbox("Cliente", lista_clientes)

            v_col3, v_col4 = st.columns(2)
            prod_vta = v_col3.selectbox("Producto (Código)", lista_prods)
            
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
                    idx_prod = st.session_state.inventario.index[st.session_state.inventario['Código'] == prod_vta].tolist()[0]
                    st.session_state.inventario.at[idx_prod, "Cantidad"] -= cant_vta

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