
import streamlit as st
import pandas as pd
from datetime import datetime, time

st.set_page_config(page_title="Registro de Horas Cuidadores", layout="centered")

st.title("📅 Registro Diario de Horas de Cuidadores")

# Cargar datos existentes o inicializar
@st.cache_data
def load_data():
    try:
        return pd.read_csv("registros.csv", parse_dates=["Fecha"])
    except:
        return pd.DataFrame(columns=["Nombre", "Domicilio", "Fecha", "Hora_Entrada", "Hora_Salida", "Horas_Trabajadas"])

df = load_data()

# Formulario para ingresar datos
with st.form("registro_form"):
    nombre = st.text_input("Nombre del Cuidador")
    domicilio = st.text_input("Domicilio")
    fecha = st.date_input("Fecha", datetime.today())
    hora_entrada = st.time_input("Hora de Entrada", time(8, 0))
    hora_salida = st.time_input("Hora de Salida", time(14, 0))

    submitted = st.form_submit_button("Registrar")

    if submitted:
        entrada_dt = datetime.combine(fecha, hora_entrada)
        salida_dt = datetime.combine(fecha, hora_salida)
        if salida_dt < entrada_dt:
            salida_dt += pd.Timedelta(days=1)

        horas = round((salida_dt - entrada_dt).total_seconds() / 3600, 2)

        nuevo_registro = pd.DataFrame([{ 
            "Nombre": nombre.strip(),
            "Domicilio": domicilio.strip(),
            "Fecha": fecha,
            "Hora_Entrada": hora_entrada,
            "Hora_Salida": hora_salida,
            "Horas_Trabajadas": horas
        }])

        df = pd.concat([df, nuevo_registro], ignore_index=True)
        df.to_csv("registros.csv", index=False)
        st.success(f"Registro guardado: {horas} hs trabajadas")

# Mostrar registros existentes
st.subheader("📊 Registros del Mes")
if df.empty:
    st.info("No hay registros cargados.")
else:
    st.dataframe(df.sort_values(by="Fecha", ascending=False))
    resumen = df.groupby("Nombre")["Horas_Trabajadas"].sum().reset_index().sort_values(by="Horas_Trabajadas", ascending=False)
    resumen["Horas_Trabajadas"] = resumen["Horas_Trabajadas"].round(2)

    st.subheader("📈 Total de Horas por Cuidador")
    st.dataframe(resumen)

    if st.button("🔹 Descargar Resumen en Excel"):
        resumen.to_excel("Resumen_Horas.xlsx", index=False)
        st.success("Resumen exportado como 'Resumen_Horas.xlsx'")
