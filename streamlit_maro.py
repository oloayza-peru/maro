import streamlit as st
import pandas as pd
import numpy as np

# Configuración inicial de la página
st.set_page_config(
    page_title="MARO - Dashboard & Gestión de Joyería",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# INICIALIZACIÓN Y PERSISTENCIA DE DATOS (Simulación de Base de Datos en Memoria)
# -----------------------------------------------------------------------------
if "inventario" not in st.session_state:
    st.session_state.inventario = pd.DataFrame([
        {"SKU": "JOY-001", "Nombre": "Anillo Oro 18K Solitario", "Categoría": "Anillos", "Costo ($)": 120.0, "Precio ($)": 250.0, "Stock": 15},
        {"SKU": "JOY-002", "Nombre": "Cadena Plata 925 Delgado", "Categoría": "Cadenas", "Costo ($)": 25.0, "Precio ($)": 60.0, "Stock": 30},
        {"SKU": "JOY-003", "Nombre": "Aretes Perla Cultivada", "Categoría": "Aretes", "Costo ($)": 40.0, "Precio ($)": 95.0, "Stock": 8},
    ])

if "ventas" not in st.session_state:
    st.session_state.ventas = pd.DataFrame([
        {"ID Venta": "V-1001", "SKU": "JOY-001", "Cantidad": 2, "Precio Unit. ($)": 250.0, "Ingreso Total ($)": 500.0, "Costo Total ($)": 240.0, "Ganancia ($)": 260.0, "Fecha": "2026-09-28"},
        {"ID Venta": "V-1002", "SKU": "JOY-002", "Cantidad": 5, "Precio Unit. ($)": 60.0, "Ingreso Total ($)": 300.0, "Costo Total ($)": 125.0, "Ganancia ($)": 175.0, "Fecha": "2026-09-29"},
    ])

if "inversiones" not in st.session_state:
    st.session_state.inversiones = pd.DataFrame([
        {"ID Inversión": "INV-001", "Tipo": "Sustitución/Compra Stock", "Descripción": "Lote inicial de anillos", "Monto ($)": 1800.0, "Fecha": "2026-09-01"},
        {"ID Inversión": "INV-002", "Tipo": "Marketing / Publicidad", "Descripción": "Campaña en Meta Ads", "Monto ($)": 150.0, "Fecha": "2026-09-15"},
    ])

# -----------------------------------------------------------------------------
# BARRA LATERAL (Navegación)
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/emoticons/100/diamond.png", width=80)
st.sidebar.title("💎 Joyería MARO")
st.sidebar.caption("Panel Control Ejecutivo & Analytics")

menu = st.sidebar.radio(
    "Navegación Principal",
    ["📊 Dashboard KPIs (MBA View)", "📦 Inventario & Compras", "💰 Registro de Ventas", "📈 Inversiones & Gastos"]
)

st.sidebar.markdown("---")
st.sidebar.info("**Tip Gerencial:** Un margen bruto saludable en joyería fina se sitúa por encima del 55%. Supervisa constantemente el índice de rotación de inventario.")

# -----------------------------------------------------------------------------
# PESTAÑA 1: DASHBOARD DE KPIs Y MÉTRICAS FINANCIERAS
# -----------------------------------------------------------------------------
if menu == "📊 Dashboard KPIs (MBA View)":
    st.title("📊 Control de Mando & Indicadores Clave (KPIs)")
    st.markdown("Visión estratégica del desempeño comercial, rentabilidad y valoración del patrimonio comercial de **MARO**.")

    # Cálculos dinámicos
    total_ingresos = st.session_state.ventas["Ingreso Total ($)"].sum() if not st.session_state.ventas.empty else 0.0
    total_costo_ventas = st.session_state.ventas["Costo Total ($)"].sum() if not st.session_state.ventas.empty else 0.0
    utilidad_bruta = total_ingresos - total_costo_ventas
    
    total_inversiones = st.session_state.inversiones["Monto ($)"].sum() if not st.session_state.inversiones.empty else 0.0
    utilidad_neta = utilidad_bruta - total_inversiones
    
    valor_inventario_costo = (st.session_state.inventario["Stock"] * st.session_state.inventario["Costo ($)"]).sum() if not st.session_state.inventario.empty else 0.0
    valor_inventario_pventa = (st.session_state.inventario["Stock"] * st.session_state.inventario["Precio ($)"]).sum() if not st.session_state.inventario.empty else 0.0

    margen_bruto = (utilidad_bruta / total_ingresos * 100) if total_ingresos > 0 else 0.0
    roi = (utilidad_neta / total_inversiones * 100) if total_inversiones > 0 else 0.0

    # Tarjetas de Resumen
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ingresos Totales", f"${total_ingresos:,.2f}")
    col2.metric("Utilidad Bruta", f"${utilidad_bruta:,.2f}", f"Margen Bruto: {margen_bruto:.1f}%")
    col3.metric("Valor Inventario (al Costo)", f"${valor_inventario_costo:,.2f}")
    col4.metric("ROI del Negocio", f"{roi:.1f}%", f"Utilidad Neta: ${utilidad_neta:,.2f}")

    st.markdown("---")

    # Gráficos y análisis
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("🛍️ Distribución del Stock por Categoría")
        if not st.session_state.inventario.empty:
            cat_summary = st.session_state.inventario.groupby("Categoría")["Stock"].sum().reset_index()
            st.bar_chart(data=cat_summary, x="Categoría", y="Stock")
        else:
            st.info("Sin datos de inventario.")

    with col_g2:
        st.subheader("💵 Ventas Recientes por Fecha")
        if not st.session_state.ventas.empty:
            sales_summary = st.session_state.ventas.groupby("Fecha")["Ingreso Total ($)"].sum().reset_index()
            st.line_chart(data=sales_summary, x="Fecha", y="Ingreso Total ($)")
        else:
            st.info("Sin ventas registradas.")

# -----------------------------------------------------------------------------
# PESTAÑA 2: INVENTARIO & AÑADIR COMPRAS / NUEVOS PRODUCTOS
# -----------------------------------------------------------------------------
elif menu == "📦 Inventario & Compras":
    st.title("📦 Gestión de Inventario y Stock")
    
    st.subheader("Catálogo de Productos en Existencia")
    st.dataframe(st.session_state.inventario, use_container_width=True)

    st.markdown("---")
    st.subheader("➕ Añadir Nueva Inversión en Stock / Producto")
    st.caption("Al ingresar una compra aquí, se actualizará el inventario y se registrará automáticamente la inversión correspondiente.")

    with st.form("form_nuevo_producto", clear_on_submit=True):
        col_a, col_b, col_c = st.columns(3)
        sku = col_a.text_input("SKU / Código Unico", value=f"JOY-00{len(st.session_state.inventario)+1}")
        nombre = col_b.text_input("Nombre del Producto (ej. Dije de Plata 925)")
        categoria = col_c.selectbox("Categoría", ["Anillos", "Cadenas", "Aretes", "Pulseras", "Dijes", "Otros"])

        col_d, col_e, col_f = st.columns(3)
        costo_u = col_d.number_input("Costo Unitario ($)", min_value=0.1, value=10.0, step=0.5)
        precio_u = col_e.number_input("Precio de Venta ($)", min_value=0.1, value=25.0, step=0.5)
        cantidad = col_f.number_input("Cantidad Adquirida", min_value=1, value=5, step=1)

        fecha_compra = st.date_input("Fecha de Adquisición")
        btn_compra = st.form_submit_button("📥 Registrar Compra e Incrementar Inventario")

        if btn_compra:
            if not nombre:
                st.error("Por favor, ingrese un nombre para el producto.")
            else:
                # 1. Actualizar o agregar al inventario
                idx = st.session_state.inventario.index[st.session_state.inventario['SKU'] == sku].tolist()
                if idx:
                    # El producto existe, actualizamos stock
                    st.session_state.inventario.at[idx[0], "Stock"] += cantidad
                    st.session_state.inventario.at[idx[0], "Costo ($)"] = costo_u
                    st.session_state.inventario.at[idx[0], "Precio ($)"] = precio_u
                else:
                    # Producto nuevo
                    nuevo_prod = pd.DataFrame([{
                        "SKU": sku, "Nombre": nombre, "Categoría": categoria, 
                        "Costo ($)": costo_u, "Precio ($)": precio_u, "Stock": cantidad
                    }])
                    st.session_state.inventario = pd.concat([st.session_state.inventario, nuevo_prod], ignore_index=True)

                # 2. Registrar reflejo en Inversiones
                monto_total_inv = costo_u * cantidad
                nueva_inv = pd.DataFrame([{
                    "ID Inversión": f"INV-00{len(st.session_state.inversiones)+1}",
                    "Tipo": "Compra de Mercadería / Stock",
                    "Descripción": f"Adquisición de {cantidad} un. de {nombre} ({sku})",
                    "Monto ($)": monto_total_inv,
                    "Fecha": str(fecha_compra)
                }])
                st.session_state.inversiones = pd.concat([st.session_state.inversiones, nueva_inv], ignore_index=True)

                st.success(f"✅ ¡Compra de {cantidad} unidad(es) de '{nombre}' registrada con éxito! El inventario y las inversiones han sido actualizadas.")
                st.rerun()

# -----------------------------------------------------------------------------
# PESTAÑA 3: REGISTRO DE VENTAS (MODIFICA INVENTARIO AUTOMÁTICAMENTE)
# -----------------------------------------------------------------------------
elif menu == "💰 Registro de Ventas":
    st.title("💰 Registrar Nueva Venta")
    st.caption("Al confirmar una venta, la cantidad vendida se descuenta automáticamente del inventario disponible.")

    if st.session_state.inventario.empty:
        st.warning("No hay productos disponibles en inventario para vender.")
    else:
        # Formulario de Ventas
        lista_skus = st.session_state.inventario["SKU"].tolist()
        
        with st.form("form_venta", clear_on_submit=True):
            col_v1, col_v2 = st.columns(2)
            sku_sel = col_v1.selectbox("Seleccionar Producto por SKU", lista_skus)
            
            # Obtener datos del SKU seleccionado
            prod_info = st.session_state.inventario[st.session_state.inventario["SKU"] == sku_sel].iloc[0]
            col_v2.info(f"**Producto:** {prod_info['Nombre']} | **Stock Actual:** {prod_info['Stock']} | **Precio Sugerido:** ${prod_info['Precio ($)']:.2f}")

            col_v3, col_v4, col_v5 = st.columns(3)
            cant_venta = col_v3.number_input("Cantidad a Vender", min_value=1, max_value=int(prod_info['Stock']) if prod_info['Stock'] > 0 else 1, value=1)
            precio_real = col_v4.number_input("Precio Final de Venta ($)", min_value=0.0, value=float(prod_info['Precio ($)']))
            fecha_vta = col_v5.date_input("Fecha de Venta")

            btn_venta = st.form_submit_button("🛒 Finalizar y Registrar Venta")

            if btn_venta:
                if prod_info['Stock'] < cant_venta:
                    st.error(f"Stock insuficiente. Solo quedan {prod_info['Stock']} unidades disponibles.")
                else:
                    # 1. Restar stock en inventario
                    idx = st.session_state.inventario.index[st.session_state.inventario['SKU'] == sku_sel].tolist()[0]
                    st.session_state.inventario.at[idx, "Stock"] -= cant_venta

                    # 2. Registrar Venta
                    ingreso = precio_real * cant_venta
                    costo_t = prod_info['Costo ($)'] * cant_venta
                    ganancia = ingreso - costo_t

                    reg_venta = pd.DataFrame([{
                        "ID Venta": f"V-{1000 + len(st.session_state.ventas)+1}",
                        "SKU": sku_sel,
                        "Cantidad": cant_venta,
                        "Precio Unit. ($)": precio_real,
                        "Ingreso Total ($)": ingreso,
                        "Costo Total ($)": costo_t,
                        "Ganancia ($)": ganancia,
                        "Fecha": str(fecha_vta)
                    }])
                    st.session_state.ventas = pd.concat([st.session_state.ventas, reg_venta], ignore_index=True)

                    st.success(f"🎉 ¡Venta registrada exitosamente! Se descontaron {cant_venta} unidades del SKU {sku_sel}.")
                    st.rerun()

    st.markdown("---")
    st.subheader("📋 Historial de Ventas")
    st.dataframe(st.session_state.ventas, use_container_width=True)

# -----------------------------------------------------------------------------
# PESTAÑA 4: INVERSIONES & GASTOS OPERATIVOS
# -----------------------------------------------------------------------------
elif menu == "📈 Inversiones & Gastos":
    st.title("📈 Control de Inversiones y Gastos Operativos")
    st.markdown("Añade gastos adicionales como empaques, marketing, transportes o personal para obtener la **utilidad neta exacta**.")

    with st.form("form_gastos", clear_on_submit=True):
        col_g1, col_g2 = st.columns(2)
        tipo_inv = col_g1.selectbox("Tipo de Inversión/Gasto", ["Marketing / Publicidad", "Empaques y Presentación", "Logística y Envíos", "Sueldos / Comisiones", "Herramientas y Maquinaria", "Otros"])
        monto_inv = col_g2.number_input("Monto ($)", min_value=0.1, value=50.0, step=5.0)

        desc_inv = st.text_input("Descripción breve (ej. Compra de cajitas de terciopelo con logo MARO)")
        fecha_inv = st.date_input("Fecha del Gasto")

        btn_gasto = st.form_submit_button("💳 Registrar Inversión / Gasto")

        if btn_gasto:
            nueva_inv = pd.DataFrame([{
                "ID Inversión": f"INV-00{len(st.session_state.inversiones)+1}",
                "Tipo": tipo_inv,
                "Descripción": desc_inv if desc_inv else tipo_inv,
                "Monto ($)": monto_inv,
                "Fecha": str(fecha_inv)
            }])
            st.session_state.inversiones = pd.concat([st.session_state.inversiones, nueva_inv], ignore_index=True)
            st.success("✅ Inversión/Gasto registrado correctamente.")
            st.rerun()

    st.markdown("---")
    st.subheader("Registro Central de Inversiones y Gastos")
    st.dataframe(st.session_state.inversiones, use_container_width=True)