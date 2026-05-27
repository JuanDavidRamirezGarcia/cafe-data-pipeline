import os
import sys
import pytest

# 1. Encontrar la ruta raíz absoluta de tu proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

from pipeline import ejecutar_pipeline


def test_limpieza_datos_cafe(tmp_path):
    """Prueba que el pipeline realmente filtre los registros dañados."""
    # 2. Construir la ruta absoluta al CSV y cambiar \ por / (crucial para DuckDB en Windows)
    csv_path = os.path.join(BASE_DIR, 'data', 'sales_coffee.csv').replace('\\', '/')
    
    # 3. Hacer lo mismo con la carpeta temporal
    output_dir = str(tmp_path).replace('\\', '/')
    
    # Ejecutamos el pipeline con rutas absolutas seguras
    resultado = ejecutar_pipeline(csv_path, output_dir)
    
    recibidos = resultado['metadata']['calidad_datos']['recibidos']
    limpios = resultado['metadata']['calidad_datos']['limpios']
    descartados = resultado['metadata']['calidad_datos']['descartados']

    # Verificaciones
    assert recibidos == 6
    assert limpios == 4
    assert descartados == 2
    assert resultado['metricas']['ingresos_totales_usd'] > 0