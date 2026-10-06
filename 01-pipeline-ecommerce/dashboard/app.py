import streamlit as st
import sqlite3
import pandas as pd
import os

# --- Configuración de la página ---
st.set_page_config(page_title="Dashboard E-commerce Olist", layout="wide")

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "ecommerce.db")


@st.cache_data
def cargar_datos():
    conexion = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM ventas", conexion)
    conexion.close()
    return df


df = cargar_datos()

# --- Título ---
st.title("📊 Dashboard de Ventas — E-commerce Olist")
st.markdown("Pipeline de datos: ingestión → limpieza → transformación → almacenamiento → visualización")

# --- Filtros (sidebar) ---
st.sidebar.header("Filtros")

anios_disponibles = sorted(df["anio_compra"].dropna().unique())
anio_seleccionado = st.sidebar.multiselect(
    "Año", anios_disponibles, default=anios_disponibles
)

estados_disponibles = sorted(df["customer_state"].dropna().unique())
estado_seleccionado = st.sidebar.multiselect(
    "Estado del cliente", estados_disponibles, default=estados_disponibles
)

# Aplicar filtros
df_filtrado = df[
    (df["anio_compra"].isin(anio_seleccionado)) &
    (df["customer_state"].isin(estado_seleccionado))
]

# --- KPIs principales ---
col1, col2, col3 = st.columns(3)

total_ventas = df_filtrado["total_item"].sum()
num_pedidos = df_filtrado["order_id"].nunique()
ticket_promedio = total_ventas / num_pedidos if num_pedidos > 0 else 0

col1.metric("Ventas totales", f"${total_ventas:,.2f}")
col2.metric("Pedidos únicos", f"{num_pedidos:,}")
col3.metric("Ticket promedio", f"${ticket_promedio:,.2f}")

st.divider()

# --- Ventas por mes ---
st.subheader("Ventas a lo largo del tiempo")

ventas_mes = (
    df_filtrado.groupby(["anio_compra", "mes_compra"])["total_item"]
    .sum()
    .reset_index()
)
ventas_mes["periodo"] = (
    ventas_mes["anio_compra"].astype(int).astype(str) + "-" +
    ventas_mes["mes_compra"].astype(int).astype(str).str.zfill(2)
)
ventas_mes = ventas_mes.sort_values("periodo")

st.line_chart(ventas_mes.set_index("periodo")["total_item"])

st.markdown("**Tu interpretación aquí:** _(ej. se observa un crecimiento sostenido desde 2017, con un arranque muy bajo en 2016, lo que sugiere que el negocio apenas estaba iniciando operaciones)_")

st.divider()

# --- Top estados ---
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("Top 10 estados por ventas")
    ventas_estado = (
        df_filtrado.groupby("customer_state")["total_item"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    st.bar_chart(ventas_estado)
    st.markdown("**Tu interpretación aquí:**")

# --- Top categorías ---
with col_der:
    st.subheader("Top 10 categorías de producto")
    ventas_categoria = (
        df_filtrado.groupby("product_category_name_english")["total_item"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    st.bar_chart(ventas_categoria)
    st.markdown("**Tu interpretación aquí:**")

st.divider()

# --- Tiempo de entrega ---
st.subheader("Distribución del tiempo de entrega (días)")
tiempos_validos = df_filtrado["tiempo_entrega_dias"].dropna()
st.bar_chart(tiempos_validos.value_counts().sort_index().head(30))
st.markdown("**Tu interpretación aquí:** _(ej. ¿cuántos días tarda típicamente una entrega? ¿hay casos extremos?)_")