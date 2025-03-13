import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Cargar datos limpios
partidos = pd.DataFrame({
    "FECHA": ["27-03-2025", "27-04-2025", "18-05-2025", "25-05-2025", "15-06-2025", "20-07-2025", "03-08-2025", "17-08-2025", "31-08-2025", "14-09-2025", "26-10-2025", "23-11-2025", "07-12-2025"],
    "NUMERO_PARTIDO": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    "EQUIPO_RIVAL": ["PALESTINO", "COQUIMBO UNIDO", "ÑUBLENSE", "UNION ESPAÑOLA", "COBRESAL", "LA SERENA", "HUACHIPATO", "UNIVERSIDAD CATÓLICA", "UNIVERSIDAD DE CHILE", "DEPORTES IQUIQUE", "DEPORTES LIMACHE", "UNION LA CALERA", "AUDAX ITALIANO"]
})

# Convertir la columna de fecha al formato adecuado
partidos["FECHA"] = pd.to_datetime(partidos["FECHA"], errors='coerce')

# Datos de gastos logísticos
gastos = pd.DataFrame({
    "EQUIPO": ["UNIVERSIDAD DE CHILE", "LA SERENA", "UNIVERSIDAD CATOLICA", "O'HIGGINS", "DEPORTES IQUIQUE", "COBRESAL", "UNION ESPAÑOLA", "AUDAX ITALIANO", "EVERTON CD", "PALESTINO", "HUACHIPATO", "DEPORTES LIMACHE", "COQUIMBO UNIDO"],
    "GASTOS_MM": [35.5, 11.4, 48.1, 67.3, 34.4, 43.1, 32.5, 11.7, 13.3, 19.3, 24.8, 36.7, 12.7]
})

# Cargar datos de riesgo desde un archivo externo
archivo_riesgo = "riesgo_partidos.xlsx"
riesgo_data = pd.read_excel(archivo_riesgo, sheet_name="Riesgo")

# Cargar datos de inversión en seguridad desde un archivo externo
archivo_seguridad = "seguridad_partidos.xlsx"
seguridad_data = pd.read_excel(archivo_seguridad, sheet_name="Seguridad")

# Transformar seguridad_data en formato largo
seguridad_data_long = seguridad_data.melt(id_vars=["NUMERO_PARTIDO"], var_name="ITEM", value_name="COSTO_MM")

# Calcular la sumatoria total de inversión en cada ítem de seguridad
seguridad_total = seguridad_data_long.groupby("ITEM")["COSTO_MM"].sum().reset_index()

# Definir categorías de riesgo
niveles_riesgo = {
    "Muy Bajo": [0, 1],
    "Bajo": [2],
    "Medio": [3],
    "Alto": [4],
    "Muy Alto": [5]
}

# Crear función para calcular resumen de riesgo por partido
def calcular_resumen_riesgo(num_partido):
    riesgo_partido = riesgo_data[riesgo_data["NUMERO_PARTIDO"] == num_partido].iloc[:, 1:]
    resumen = {nivel: riesgo_partido.isin(valores).sum().sum() for nivel, valores in niveles_riesgo.items()}
    return pd.DataFrame.from_dict(resumen, orient='index', columns=["Cantidad"])

# Calcular el promedio de riesgo correctamente
riesgo_data["PROMEDIO_RIESGO"] = riesgo_data.iloc[:, 1:].mean(axis=1)

# Crear el selector de fecha
def main():
    st.title("Encuentros Locales Colo-Colo")
    
    fecha_seleccionada = st.selectbox("Seleccione una fecha:", partidos["FECHA"].dt.strftime('%Y-%m-%d'))
    partido_seleccionado = partidos[partidos["FECHA"].dt.strftime('%Y-%m-%d') == fecha_seleccionada].iloc[0]
    num_partido = partido_seleccionado["NUMERO_PARTIDO"]
    
    st.markdown(f"## Fecha: {partido_seleccionado['NUMERO_PARTIDO']}° Fecha")
    st.markdown(f"### Rival: {partido_seleccionado['EQUIPO_RIVAL']}")
    
    # Mostrar gráfico de gastos logísticos
    st.subheader("Gastos Logísticos (en millones de pesos)")
    fig_gastos = px.bar(gastos, x="EQUIPO", y="GASTOS_MM", text="GASTOS_MM",
                         labels={"GASTOS_MM": "Gastos (MM$)", "EQUIPO": "Equipo"},
                         title="Gastos Logísticos por Partido")
    fig_gastos.update_traces(texttemplate='%{text:.1f} MM$', textposition='outside', hoverinfo='x+y')
    st.plotly_chart(fig_gastos, use_container_width=True)
    
    # Calcular y mostrar tabla resumen de indicadores de riesgo
    st.subheader("Resumen de Indicadores de Riesgo")
    riesgo_resumen = calcular_resumen_riesgo(num_partido)
    st.table(riesgo_resumen)
    
    # Obtener el promedio de riesgo para el partido seleccionado
    promedio_riesgo = riesgo_data[riesgo_data["NUMERO_PARTIDO"] == num_partido]["PROMEDIO_RIESGO"].values[0]
    
    # Gráfico de velocímetro con aguja
    fig_riesgo = go.Figure(go.Indicator(
        mode="gauge+number",
        value=promedio_riesgo,
        title={"text": "Nivel de Riesgo"},
        gauge={
            "axis": {"range": [0, 5]},
            "bar": {"color": "white"},
            "steps": [
                {"range": [0, 1], "color": "blue"},
                {"range": [1, 2], "color": "green"},
                {"range": [2, 3], "color": "yellow"},
                {"range": [3, 4], "color": "orange"},
                {"range": [4, 5], "color": "red"}
            ],
            "threshold": {
                "line": {"color": "black", "width": 4},
                "thickness": 0.8,
                "value": promedio_riesgo
            }
        }
    ))
    st.plotly_chart(fig_riesgo)
    
    # Distribución de inversión en seguridad
    st.subheader("Distribución de Inversión en Seguridad")
    fig_seguridad = px.pie(seguridad_total, names="ITEM", values="COSTO_MM", title="Distribución de Inversión en Seguridad")
    st.plotly_chart(fig_seguridad)
    
    # Gráfico de barras para la inversión total en cada ítem de seguridad
    st.subheader("Total Invertido en Seguridad por Ítem")
    fig_seguridad_barras = px.bar(seguridad_total, x="ITEM", y="COSTO_MM", text="COSTO_MM", labels={"COSTO_MM": "Millones de Pesos"}, title="Inversión Total en Seguridad")
    fig_seguridad_barras.update_traces(texttemplate='%{text:.1f} MM$', textposition='outside')
    st.plotly_chart(fig_seguridad_barras)

if __name__ == "__main__":
    main()
