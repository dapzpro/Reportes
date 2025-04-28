import streamlit as st
import pandas as pd
import io

st.title("Filtrar Reportes de Carros")

# Subir archivo
uploaded_file = st.file_uploader("Sube el archivo de reporte (.xlsx)", type=["xlsx"])

if uploaded_file:
    # Leer archivo
    informe = pd.read_excel(uploaded_file)

    # Filtrar alertas que no sean NaN
    alertas = informe[informe["Alerta"].notna()].copy()

    # Convertir columna "Hora" a formato datetime (solo hora)
    alertas['Hora'] = pd.to_datetime(alertas['Hora'], format='%H:%M:%S').dt.time

    # Para poder calcular diferencias, convertimos 'Hora' a timedelta
    alertas['Hora_Timedelta'] = pd.to_timedelta(alertas['Hora'].astype(str))

    # Ordenar por Hora
    alertas = alertas.sort_values('Hora_Timedelta')

    # Calcular diferencia entre horas
    alertas['Diferencia'] = alertas['Hora_Timedelta'].diff()

    # Filtrar inconsistencias: diferencias menores a 1 segundo
    inconsistencias = alertas[alertas['Diferencia'].dt.total_seconds() < 1]

    # Incluir la fila anterior de las inconsistencias
    inconsistencias = pd.concat([alertas.iloc[1:][alertas['Diferencia'].dt.total_seconds() < 1], inconsistencias])

    # Eliminar las filas de inconsistencias del DataFrame 'alertas'
    alertas_limpias = alertas[~alertas.index.isin(inconsistencias.index)]

    # Eliminar las columnas 'Hora_Timedelta' y 'Diferencia' antes de la descarga
    alertas_limpias = alertas_limpias.drop(columns=['Hora_Timedelta', 'Diferencia'])

    # Agregar un selector para que tu mamá elija qué columna filtrar
    opciones_columnas = alertas.columns.tolist()  # Listar todas las columnas disponibles
    columna_filtro = st.selectbox("¿Por qué columna te gustaría filtrar las alertas?", opciones_columnas)

    # Agregar un selector para filtrar por valor de la columna elegida
    valores_filtro = alertas[columna_filtro].unique().tolist()
    valor_filtro = st.selectbox(f"Selecciona el valor para filtrar en la columna '{columna_filtro}'", valores_filtro)

    # Filtrar las alertas según la opción seleccionada
    alertas_filtradas = alertas[alertas[columna_filtro] == valor_filtro]

    # Mostrar las alertas filtradas
    st.subheader(f"Alertas filtradas por la columna '{columna_filtro}' y valor '{valor_filtro}'")
    st.write(alertas_filtradas)

    # Mostrar las inconsistencias
    st.subheader("Inconsistencias encontradas (menos de 1 segundo)")
    st.write(inconsistencias)

    # Botón de "Más Opciones"
    with st.expander("Más Opciones"):
        # Contar cuántas coincidencias encontró
        num_coincidencias = alertas_filtradas.shape[0]
        st.write(f"Se encontraron {num_coincidencias} coincidencias para el filtro seleccionado.")

        # Mostrar estadísticas adicionales (por ejemplo, estadísticas de la columna 'Hora' o cualquier otra)
        # Aquí puedes agregar otras métricas útiles
        st.write("Estadísticas de las alertas filtradas:")
        st.write(alertas_filtradas.describe())

    # Convertir el DataFrame limpio de alertas a un archivo Excel en memoria
    excel_file = io.BytesIO()
    alertas_limpias.to_excel(excel_file, index=False, engine='openpyxl')
    excel_file.seek(0)  # Asegurarse de que el archivo esté listo para descarga

    # Botón para descargar el archivo de alertas limpio
    st.download_button(
        label="Descargar alertas sin inconsistencias 📄",
        data=excel_file,
        file_name="alertas_limpias.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
