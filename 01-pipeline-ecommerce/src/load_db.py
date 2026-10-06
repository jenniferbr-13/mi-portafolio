import sqlite3
import os


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "ecommerce.db")


def cargar_a_bd(tabla_maestra):
    """
    Se carga la tabla maestra a una base de datos SQLite.
    Si la tabla ya existe, la reemplaza (útil para re-ejecutar el pipeline
    completo sin acumular datos duplicados).
    """
    conexion = sqlite3.connect(DB_PATH)

    tabla_maestra.to_sql(
        "ventas",
        conexion,
        if_exists="replace",
        index=False
    )

    conexion.close()
    print(f"OK: tabla 'ventas' cargada a la base de datos ({DB_PATH})")


def verificar_carga():
    """Queries de prueba para confirmar que los datos quedaron bien."""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    cursor.execute("SELECT COUNT(*) FROM ventas")
    total_filas = cursor.fetchone()[0]
    print(f"\nTotal de filas en la tabla 'ventas': {total_filas}")

    cursor.execute("""
        SELECT anio_compra, mes_compra, COUNT(*) as num_pedidos, SUM(total_item) as ventas_totales
        FROM ventas
        GROUP BY anio_compra, mes_compra
        ORDER BY anio_compra, mes_compra
        LIMIT 5
    """)
    print("\nVentas por mes (primeros 5 registros):")
    for fila in cursor.fetchall():
        print(fila)

    cursor.execute("""
        SELECT customer_state, COUNT(*) as num_pedidos, ROUND(SUM(total_item), 2) as ventas_totales
        FROM ventas
        GROUP BY customer_state
        ORDER BY ventas_totales DESC
        LIMIT 5
    """)
    print("\nTop 5 estados por ventas:")
    for fila in cursor.fetchall():
        print(fila)

    conexion.close()


if __name__ == "__main__":
    import sys
    sys.path.append(".")
    from ingest import cargar_datos
    from clean import limpiar_datos
    from transform import transformar_datos

    datos = cargar_datos()
    datos_limpios = limpiar_datos(datos)
    tabla_final = transformar_datos(datos_limpios)

    cargar_a_bd(tabla_final)
    verificar_carga()