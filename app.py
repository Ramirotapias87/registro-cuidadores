
import streamlit as st
import pandas as pd
from datetime import datetime, time

st.set_page_config(page_title="Registro de Horas Cuidadores V2", layout="centered")

# ------------------ Config ------------------ #
PASSWORD = "clave123"  # cambiar por una contraseña real
DOMICILIOS = ["Ramos Rosa", "Perez Juan", "Lopez Marta"]

# ------------------ Autenticación ------------------ #
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    clave = st.text_input("Ingrese la contraseña", type="password")
    if st.button("Entrar"):
        if clave == PASSWORD:
            st.session_state.autenticado = True
            st.success("Acceso concedido.")
        else:
            st.error("Contraseña incorrecta.")
    st.stop()

# ------------------ Carga de datos ------------------ #
st.title("📅 Registro de Horas - Versión 2")

@st.cache_data
def cargar_datos():
    try:
        return pd.read_csv("registros_v2.csv", parse_dates=["Fecha"])
    except:
        return pd.DataFrame(columns=["Nombre", "Domicilio", "Fecha", "Hora_Entrada", "Hora_Salida", "Horas_Trabajadas"])

df = cargar_datos()

# ------------------ Registro de horas ------------------ #
with st.form("formulario_horas"):
    nombre = st.text_input("Nombre del Cuidador")
    domicilio = st.selectbox("Domicilio", DOMICILIOS)
    fecha = st.date_input("Fecha", datetime.today())
    hora_entrada = st.time_input("Hora de Entrada", time(8, 0))
    hora_salida = st.time_input("Hora de Salida", time(14, 0))
    registrar = st.form_submit_button("Registrar")

    if registrar:
        entrada_dt = datetime.combine(fecha, hora_entrada)
        salida_dt = datetime.combine(fecha, hora_salida)
        if salida_dt < entrada_dt:
            salida_dt += pd.Timedelta(days=1)
        horas = round((salida_dt - entrada_dt).total_seconds() / 3600, 2)

        nuevo = pd.DataFrame([{ 
            "Nombre": nombre.strip(),
            "Domicilio": domicilio,
            "Fecha": fecha,
            "Hora_Entrada": hora_entrada,
            "Hora_Salida": hora_salida,
            "Horas_Trabajadas": horas
        }])

        df = pd.concat([df, nuevo], ignore_index=True)
        df.to_csv("registros_v2.csv", index=False)
        st.success(f"Registro guardado: {horas} hs en {domicilio}")

# ------------------ Visualización ------------------ #
st.subheader("📊 Registros del Mes")
if df.empty:
    st.info("No hay registros aún.")
else:
    st.dataframe(df.sort_values(by="Fecha", ascending=False))

    st.subheader("📈 Total de Horas por Cuidador")
    resumen_cuidadores = df.groupby("Nombre")["Horas_Trabajadas"].sum().reset_index().sort_values("Horas_Trabajadas", ascending=False)
    resumen_cuidadores["Horas_Trabajadas"] = resumen_cuidadores["Horas_Trabajadas"].round(2)
    st.dataframe(resumen_cuidadores)

    st.subheader("🏠 Total de Horas por Domicilio")
    resumen_domicilios = df.groupby("Domicilio")["Horas_Trabajadas"].sum().reset_index().sort_values("Horas_Trabajadas", ascending=False)
    resumen_domicilios["Horas_Trabajadas"] = resumen_domicilios["Horas_Trabajadas"].round(2)
    st.dataframe(resumen_domicilios)

    if st.button("⬇️ Exportar resumen a Excel"):
        resumen_cuidadores.to_excel("Resumen_Cuidadores.xlsx", index=False)
        resumen_domicilios.to_excel("Resumen_Domicilios.xlsx", index=False)
        st.success("Exportado como 'Resumen_Cuidadores.xlsx' y 'Resumen_Domicilios.xlsx'")
