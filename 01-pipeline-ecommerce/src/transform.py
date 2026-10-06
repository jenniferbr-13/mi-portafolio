import pandas as pd


def agregar_pagos(df_payments):
    """
    Se agrega la tabla de pagos a nivel de pedido, porque un pedido puede
    tener varias filas de pago (ej. tarjeta + voucher). Sin este paso,
    el merge posterior duplicaría filas.
    """
    pagos_agregados = df_payments.groupby("order_id").agg(
        payment_total=("payment_value", "sum"),
        payment_installments_max=("payment_installments", "max"),
        payment_types_count=("payment_type", "nunique"),
    ).reset_index()
    return pagos_agregados


def construir_tabla_maestra(datos_limpios):
    """
    Se une las tablas limpias en una sola tabla a nivel de 'producto dentro
    de un pedido'. Cada fila representa un producto vendido en un pedido
    específico.
    """
    order_items = datos_limpios["order_items"]
    orders = datos_limpios["orders"]
    customers = datos_limpios["customers"]
    products = datos_limpios["products"]
    category_translation = datos_limpios["category_translation"]
    payments_agregados = agregar_pagos(datos_limpios["payments"])

    # Base: producto dentro de pedido
    tabla = order_items.merge(orders, on="order_id", how="left")
    tabla = tabla.merge(customers, on="customer_id", how="left")
    tabla = tabla.merge(products, on="product_id", how="left")
    tabla = tabla.merge(category_translation, on="product_category_name", how="left")
    tabla = tabla.merge(payments_agregados, on="order_id", how="left")

    return tabla


def crear_features(tabla):
    """
    Crea columnas nuevas útiles para el análisis a partir de la tabla maestra.
    """
    # Tiempo de entrega en días (solo tiene sentido si el pedido fue entregado)
    tabla["tiempo_entrega_dias"] = (
        tabla["order_delivered_customer_date"] - tabla["order_purchase_timestamp"]
    ).dt.days

    # Retraso vs. fecha estimada: negativo = llegó antes, positivo = llegó tarde
    tabla["retraso_dias"] = (
        tabla["order_delivered_customer_date"] - tabla["order_estimated_delivery_date"]
    ).dt.days

    # Mes y año de compra, para analizar tendencias en el tiempo
    tabla["anio_compra"] = tabla["order_purchase_timestamp"].dt.year
    tabla["mes_compra"] = tabla["order_purchase_timestamp"].dt.month

    # Precio total de esta línea de producto (precio + flete)
    tabla["total_item"] = tabla["price"] + tabla["freight_value"]

    return tabla


def transformar_datos(datos_limpios):
    """Pipeline completo de transformación: construye la tabla maestra y agrega features."""
    tabla = construir_tabla_maestra(datos_limpios)
    tabla = crear_features(tabla)
    print(f"Tabla maestra construida: {tabla.shape[0]} filas, {tabla.shape[1]} columnas")
    return tabla


if __name__ == "__main__":
    import sys
    sys.path.append(".")
    from ingest import cargar_datos
    from clean import limpiar_datos

    datos = cargar_datos()
    datos_limpios = limpiar_datos(datos)
    tabla_final = transformar_datos(datos_limpios)

    print("\nColumnas de la tabla final:")
    print(tabla_final.columns.tolist())
    print("\nPrimeras filas:")
    print(tabla_final.head())