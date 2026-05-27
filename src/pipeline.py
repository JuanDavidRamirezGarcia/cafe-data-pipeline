import json
import os
import duckdb


def ejecutar_pipeline(csv_path, output_dir='output'):
    os.makedirs(output_dir, exist_ok=True)
    env = os.getenv('APP_ENV', 'local')
    print(f"=== Ejecutando Pipeline de Café en Modo: {env} ===")

    # Iniciar DuckDB en memoria
    con = duckdb.connect(':memory:')

    # BRONZE: Carga cruda
    con.execute(f"CREATE TABLE bronze AS SELECT * FROM read_csv_auto('{csv_path}')")
    total_bronze = con.execute("SELECT COUNT(*) FROM bronze").fetchone()[0]

    # SILVER: Limpieza profunda (Filtramos clientes vacíos y cantidades erróneas)
    con.execute("""
        CREATE TABLE silver AS
        SELECT 
            fecha::DATE as fecha,
            TRIM(cliente) as cliente,
            TRIM(tipo_cafe) as tipo_cafe,
            cantidad::INTEGER as cantidad,
            precio_usd::DOUBLE as precio_usd,
            (cantidad * precio_usd) as total_linea
        FROM bronze
        WHERE cliente IS NOT NULL AND LENGTH(TRIM(cliente)) > 0
          AND cantidad > 0
    """)
    total_silver = con.execute("SELECT COUNT(*) FROM silver").fetchone()[0]

    # GOLD: Métricas de negocio
    ingresos_totales = con.execute("SELECT SUM(total_linea) FROM silver").fetchone()[0] or 0.0
    
    # Tipo de café más vendido
    top_cafe = con.execute("""
        SELECT tipo_cafe, SUM(cantidad) as total_vendido
        FROM silver
        GROUP BY tipo_cafe
        ORDER BY total_vendido DESC
    """).fetchdf().to_dict('records')

    con.close()

    # Estructurar el artefacto final
    resumen_gold = {
        "metadata": {"ambiente": env, "calidad_datos": {"recibidos": total_bronze, "limpios": total_silver, "descartados": total_bronze - total_silver}},
        "metricas": {
            "ingresos_totales_usd": float(ingresos_totales),
            "ranking_productos": top_cafe
        }
    }

    # Guardar el archivo JSON final
    ruta_json = os.path.join(output_dir, 'cafe_gold.json')
    with open(ruta_json, 'w') as f:
        json.dump(resumen_gold, f, indent=4)

    print(f"=== Proceso terminado con éxito. Archivo guardado en: {ruta_json} ===")
    return resumen_gold


if __name__ == '__main__':
    ejecutar_pipeline('data/sales_coffee.csv')