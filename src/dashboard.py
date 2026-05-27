import json
import os
import pandas as pd
import plotly.express as px


def generar_dashboard(json_path='output/cafe_gold.json', output_dir='output'):
    print("=== Generando Dashboard Interactivo ===")
    
    # 1. Verificar si existe el archivo de datos
    if not os.path.exists(json_path):
        print(f"❌ Error: No se encuentra '{json_path}'. ¿Corriste el pipeline primero?")
        return
        
    # 2. Leer los datos procesados del archivo Gold
    with open(json_path, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    ranking = datos['metricas']['ranking_productos']
    ingresos = datos['metricas']['ingresos_totales_usd']
    ambiente = datos['metadata']['ambiente']
    
    # 3. Convertir a un DataFrame de Pandas
    df = pd.DataFrame(ranking)
    
    # 4. Crear el gráfico de barras puro y directo
    fig = px.bar(
        df, 
        x='tipo_cafe', 
        y='total_vendido',  
        labels={'tipo_cafe': 'Tipo de Café', 'total_vendido': 'Unidades Vendidas'},
        title=f"Ventas por Tipo de Café - Total Ingresos: ${ingresos:,.2f} USD",
        template="plotly_dark"
    )

    # Ajuste visual limpio para el eje Y
    fig.update_layout(yaxis_title="Unidades Vendidas")

    # 5. Crear el diseño de la página web HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard de Café Especial</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #111; color: white; }}
            .container {{ max-width: 900px; margin: auto; background: #222; padding: 20px; border-radius: 10px; }}
            h1 {{ color: #ff9f43; text-align: center; }}
            .badge {{ background: #10ac84; padding: 5px 10px; border-radius: 5px; font-size: 0.8em; float: right; }}
        </style>
    </head>
    <body>
        <div class="container">
            <span class="badge">Entorno: {ambiente.upper()}</span>
            <h1>☕ Reporte Automático de Ventas: Tienda de Café</h1>
            <hr style="border-color: #444;">
            <div id="chart">
                {fig.to_html(full_html=False, include_plotlyjs='cdn')}
            </div>
        </div>
    </body>
    </html>
    """
    
    # 6. Guardar la página web en la carpeta output
    os.makedirs(output_dir, exist_ok=True)
    ruta_html = os.path.join(output_dir, 'index.html')
    with open(ruta_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"=== Dashboard generado con éxito en: {ruta_html} ===")


if __name__ == '__main__':
    generar_dashboard()