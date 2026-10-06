#importar librerías necesarias
import pandas as pd
import os
# Definir la ruta del directorio de datos crudos        
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
# Definir los nombres de los archivos CSV crudos de Olist
ARCHIVOS = {
    "orders": "olist_orders_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

#Cargar los datos de los archivos CSV crudos en un diccionario de DataFrames

#La función cargar_datos() lee todos los archivos CSV crudos de Olist y los carga en un diccionario de DataFrames de pandas. La función debe manejar errores de carga y mostrar un mensaje indicando si la carga fue exitosa o si hubo algún error. Además, la función devuelve el diccionario de DataFrames cargados.

def cargar_datos():
    """Carga todos los CSV crudos de Olist en un diccionario de DataFrames."""
    dataframes = {}
    for nombre, archivo in ARCHIVOS.items():
        ruta_completa = os.path.join(RAW_DATA_DIR, archivo)
        try:
            df = pd.read_csv(ruta_completa)
            dataframes[nombre] = df
            print(f"OK {nombre}: {df.shape[0]} filas, {df.shape[1]} columnas")
        except FileNotFoundError:
            print(f"ERROR: no se encontro el archivo {archivo}")
        except Exception as e:
            print(f"ERROR al cargar {nombre}: {e}")
    return dataframes

#Ejecutar la función cargar_datos() si el script se ejecuta directamente
if __name__ == "__main__":
    datos = cargar_datos()
    print(f"\nTotal de tablas cargadas: {len(datos)} de {len(ARCHIVOS)}")


#La libreria pandas nos ayuda a tener una estructura de datos en forma de tabla, la cual tiene dos tipos de estructura la primera es DataFrame que es una estructura de datos bidimensional, es decir, tiene filas y columnas, y la segunda es Series que es una estructura de datos unidimensional, es decir, tiene solo una columna.

