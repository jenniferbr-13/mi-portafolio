import pandas as pd


def limpiar_orders(df):
    """
    Limpia la tabla de pedidos.
    Los nulos en fechas de aprobación/entrega se mantienen intencionalmente:
    representan pedidos cancelados o no completados, es información válida
    de negocio, no un error de datos.
    """
    columnas_fecha = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for col in columnas_fecha:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def limpiar_geolocation(df):
    """
    Limpia la tabla de geolocalización.
    Se eliminan duplicados: esta tabla es un catálogo de código postal -> coordenadas,
    las filas repetidas no aportan información nueva y solo agregan peso innecesario.
    """
    filas_antes = df.shape[0]
    df = df.drop_duplicates()
    print(f"geolocation: se eliminaron {filas_antes - df.shape[0]} duplicados")
    return df


def limpiar_reviews(df):
    """
    Limpia la tabla de reseñas.
    Los nulos en título/mensaje de comentario se mantienen: es normal que un
    cliente califique con estrellas sin escribir texto, no es un dato faltante
    por error. Se rellenan con string vacío para facilitar el manejo posterior.
    """
    df["review_comment_title"] = df["review_comment_title"].fillna("")
    df["review_comment_message"] = df["review_comment_message"].fillna("")

    columnas_fecha = ["review_creation_date", "review_answer_timestamp"]
    for col in columnas_fecha:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def limpiar_products(df):
    """
    Limpia la tabla de productos.
    - Los 610 nulos en categoría/descripción se rellenan con 'sem_categoria'
      en vez de eliminar esas filas (representan ~2% del total, se pierde
      información de ventas si se descartan).
    - Las 2 filas sin datos físicos (peso/dimensiones) se eliminan: son casos
      aislados y ese dato es indispensable para cualquier análisis de logística.
    """
    df["product_category_name"] = df["product_category_name"].fillna("sem_categoria")
    df["product_name_lenght"] = df["product_name_lenght"].fillna(0)
    df["product_description_lenght"] = df["product_description_lenght"].fillna(0)
    df["product_photos_qty"] = df["product_photos_qty"].fillna(0)

    columnas_fisicas = ["product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]
    df = df.dropna(subset=columnas_fisicas)

    return df


def limpiar_customers(df):
    """Tabla sin nulos ni duplicados. Se ajusta tipo de dato del código postal."""
    df["customer_zip_code_prefix"] = df["customer_zip_code_prefix"].astype(str)
    return df


def limpiar_order_items(df):
    """Tabla sin nulos ni duplicados. Se convierte la fecha límite de envío."""
    df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"], errors="coerce")
    return df


def limpiar_payments(df):
    """Tabla sin nulos ni duplicados. No requiere transformación adicional."""
    return df


def limpiar_sellers(df):
    """Tabla sin nulos ni duplicados. Se ajusta tipo de dato del código postal."""
    df["seller_zip_code_prefix"] = df["seller_zip_code_prefix"].astype(str)
    return df


def limpiar_category_translation(df):
    """Tabla sin nulos ni duplicados. No requiere transformación adicional."""
    return df


# Diccionario que conecta cada tabla con su función de limpieza correspondiente
FUNCIONES_LIMPIEZA = {
    "orders": limpiar_orders,
    "customers": limpiar_customers,
    "order_items": limpiar_order_items,
    "products": limpiar_products,
    "payments": limpiar_payments,
    "reviews": limpiar_reviews,
    "sellers": limpiar_sellers,
    "geolocation": limpiar_geolocation,
    "category_translation": limpiar_category_translation,
}


def limpiar_datos(dataframes):
    """
    Aplica la función de limpieza correspondiente a cada tabla del diccionario.
    """
    datos_limpios = {}
    for nombre, df in dataframes.items():
        funcion_limpieza = FUNCIONES_LIMPIEZA[nombre]
        datos_limpios[nombre] = funcion_limpieza(df)
        print(f"OK {nombre} limpiado: {datos_limpios[nombre].shape[0]} filas")
    return datos_limpios


if __name__ == "__main__":
    import sys
    sys.path.append(".")
    from ingest import cargar_datos

    datos = cargar_datos()
    datos_limpios = limpiar_datos(datos)