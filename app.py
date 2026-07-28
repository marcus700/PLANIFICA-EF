import streamlit as st
from google import genai
from google.genai import types
from docx import Document
import io

# Importamos la base de datos oficial completa
from cneb_datos import CNEB_PRIMARIA

# 1. Configuración de la Plataforma
st.set_page_config(page_title="Generador CNEB Primaria", page_icon="🏃‍♂️", layout="centered")

st.title("🏃 Generador CNEB - Educación Física (Primaria)")
st.subheader("Con Estándares y Desempeños oficiales del MINEDU (1° a 6° de Primaria)")
st.write("Herramienta inteligente para diseñar tus documentos curriculares al instante usando tu base de datos.")

# Enlace automático a la clave secreta guardada de forma segura en Streamlit
api_key = st.secrets["GEMINI_API_KEY"]

# Función para convertir el texto en archivo de Word (.docx)
def crear_archivo_word(texto_contenido):
    doc = Document()
    for linea in texto_contenido.split('\n'):
        doc.add_paragraph(linea)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Función auxiliar para deducir el ciclo oficial según el grado elegido
def obtener_ciclo_minedu(grado_seleccionado):
    if "1°" in grado_seleccionado or "2°" in grado_seleccionado:
        return "III Ciclo"
    elif "3°" in grado_seleccionado or "4°" in grado_seleccionado:
        return "IV Ciclo"
    return "V Ciclo"

# Creación de las 3 Pestañas de Navegación
tab1, tab2, tab3 = st.tabs([
    "📂 Crear Unidad de Aprendizaje", 
    "📝 Crear Sesión de Aprendizaje", 
    "📊 Crear Rúbrica de Evaluación"
])

# --- PESTAÑA 1: UNIDADES ---
with tab1:
    st.write("Estructura una unidad didáctica completa para varias semanas basada en necesidades del contexto escolar.")
    with st.form("form_unidad"):
        grado_u = st.selectbox("🏫 Grado de Primaria:", ["1° de Primaria", "2° de Primaria", "3° de Primaria", "4° de Primaria", "5° de Primaria", "6° de Primaria"], key="u1")
        duracion_u = st.selectbox("⏱️ Duración de la Unidad:", ["4 Semanas (4 sesiones)", "6 Semanas (6 sesiones)", "8 Semanas (8 sesiones)"], key="u2")
        problema_u = st.text_area("📋 Describe el problema del contexto o interés de los niños:", placeholder="Ej. Los estudiantes muestran dificultades para trabajar en equipo y respetar reglas en los juegos del recreo.", key="u3")
        boton_unidad = st.form_submit_button("📂 Generar Unidad en Word")

    if boton_unidad and problema_u:
        with st.spinner("Escribiendo la unidad oficial..."):
            try:
                client = genai.Client(api_key=api_key)
                ciclo_u = obtener_ciclo_minedu(grado_u)
                instrucciones_u = "Actúa como un Especialista Curricular experto en Educación Física para Primaria bajo el enfoque del CNEB del MINEDU de Perú. Diseña una Unidad de Aprendizaje completa que incluya estrictamente: 1. Título de la unidad. 2. Situación Significativa (Contexto real, Reto en forma de pregunta y Producto esperado). 3. Propósitos de Aprendizaje basándote en la estructura del CNEB. 4. Secuencia semanal de sesiones (Título y breve descripción)."
                pedido_u = f"Crea una unidad para {grado_u} ({ciclo_u}) con duración de {duracion_u}. Contexto o problema: {problema_u}"
                
                # Usamos gemini-1.5-flash que tiene máxima compatibilidad
                response = client.models.generate_content(model='gemini-1.5-flash', contents=pedido_u, config=types.GenerateContentConfig(system_instruction=instrucciones_u, temperature=0.7))
                resultado_u = response.text
                st.success("¡Unidad Curricular generada con éxito!")
                st.markdown(resultado_u)
                archivo_word_u = crear_archivo_word(resultado_u)
                st.download_button(label="📄 Descargar Unidad en Word (.docx)", data=archivo_word_u, file_name=f"Unidad_MINEDU_{grado_u.replace(' ', '_')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            except Exception as e:
                st.error(f"Error: {e}")

# --- PESTAÑA 2: SESIONES ---
with tab2:
    st.write("Completa los datos oficiales requeridos por el MINEDU para tu clase diaria.")
    with st.form("form_sesion"):
        grado_s = st.selectbox("🏫 Grado de Primaria:", ["1° de Primaria", "2° de Primaria", "3° de Primaria", "4° de Primaria", "5° de Primaria", "6° de Primaria"], key="s1")
        duracion_s = st.number_input("⏱️ Duración (minutos):", value=90, min_value=30, max_value=180, key="s2")
        competencia_s = st.selectbox("🎯 Competencia CNEB:", ["Se desenvuelve de manera autónoma a través de su motricidad", "Asume una vida saludable", "Interactúa a través de sus habilidades sociomotrices"], key="s3")
        tema_s = st.text_input("⚽ Tema / Propósito Motriz:", placeholder="Ej: Coordinación dinámica, Salto de cuerda, Lanzamiento, Juegos tradicionales", key="s4")
        materiales_s = st.text_input("🧱 Materiales Disponibles:", placeholder="Ej: Conos, balones, aros, cuerdas, tiza", key="s5")
        boton_sesion = st.form_submit_button("🚀 Generar Sesión de Aprendizaje CNEB Primaria")

    if boton_sesion and tema_s and materiales_s:
        with st.spinner("Escribiendo la sesión oficial..."):
            try:
                client = genai.Client(api_key=api_key)
                ciclo_s = obtener_ciclo_minedu(grado_s)
                estandar_real = CNEB_PRIMARIA.get(competencia_s, {}).get("estandares", {}).get(ciclo_s, "Estándar general.")
                desempenos_reales = CNEB_PRIMARIA.get(competencia_s, {}).get("desempenos", {}).get(grado_s, ["Desempeños generales."])
                desempenos_texto = " | ".join(desempenos_reales)
                
                instrucciones = f"Actúa como un Asistente Pedagógico experto en Educación Física para el nivel PRIMARIA bajo el enfoque oficial del CNEB del MINEDU de Perú. Incluye obligatoriamente el Estándar: {estandar_real} y los Desempeños: {desempenos_texto}. Estructura la Sesión incluyendo de forma ordenada: 1. Datos Informativos. 2. Propósito del Día. 3. Enfoques Transversales. 4. Momentos Pedagógicos (Inicio, Desarrollo con variantes e hidratación, y Cierre con higiene y metacognición). 5. Criterios de Evaluación."
                pedido = f"Diseña una sesión de {duracion_s} minutes para {grado_s} ({ciclo_s}). Tema: {tema_s}. Materiales: {materiales_s}."
                
                # Usamos gemini-1.5-flash que tiene máxima compatibilidad
                response = client.models.generate_content(model='gemini-1.5-flash', contents=pedido, config=types.GenerateContentConfig(system_instruction=instrucciones, temperature=0.7))
                resultado_s = response.text
                st.success("¡📋 Sesión Generada (MINEDU) con éxito!")
                st.markdown(resultado_s)
                archivo_word = crear_archivo_word(resultado_s)
                st.download_button(label="📄 Descargar Sesión en Word (.docx)", data=archivo_word, file_name=f"Sesion_MINEDU_{grado_s.replace(' ', '_')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            except Exception as e:
                st.error(f"Error técnico o de datos: {e}")

# --- PESTAÑA 3: RÚBRICAS ---
with tab3:
    st.write("Diseña instrumentos de evaluación con criterios claros y descriptores por niveles de logro.")
    with st.form("form_rubrica"):
        grado_r = st.selectbox("🏫 Grado de Primaria:", ["1° de Primaria", "2° de Primaria", "3° de Primaria", "4° de Primaria", "5° de Primaria", "6° de Primaria"], key="r1")
        competencia_r = st.selectbox("🎯 Competencia a Evaluar:", ["Se desenvuelve de manera autónoma a través de su motricidad", "Asume una vida saludable", "Interactúa a través de sus habilidades sociomotrices"], key="r2")
        criterio_r = st.text_input("📊 Desempeño o criterio específico a evaluar:", placeholder="Ej. Lanzamiento de precisión con balones o trabajo en equipo.")
        boton_rubrica = st.form_submit_button("📊 Generar Rúbrica en Word")

    if boton_rubrica and criterio_r:
        with st.spinner("Escribiendo la rúbrica oficial..."):
            try:
                client = genai.Client(api_key=api_key)
                ciclo_r = obtener_ciclo_minedu(grado_r)
                instrucciones_r = "Actúa como un Evaluador Pedagógico experto en Educación Física para Primaria bajo los lineamientos del CNEB del MINEDU. Diseña una rúbrica analítica estructurada para evaluar el desempeño solicitado. Incluye los cuatro niveles de logro oficiales: En Inicio, En Proceso, Logrado y Logro Destacado."
                pedido_r = f"Crea una rúbrica de evaluación para {grado_r} ({ciclo_r}). Competencia: {competencia_r}. Actividad/Desempeño específico a evaluar: {criterio_r}"
                
                # Usamos gemini-1.5-flash que tiene máxima compatibilidad
                response = client.models.generate_content(model='gemini-1.5-flash', contents=pedido_r, config=types.GenerateContentConfig(system_instruction=instrucciones_r, temperature=0.7))
                resultado_r = response.text
                st.success("¡Rúbrica generada con éxito!")
                st.markdown(resultado_r)
                archivo_word_r = crear_archivo_word(resultado_r)
                st.download_button(label="📄 Descargar Rúbrica en Word (.docx)", data=archivo_word_r, file_name=f"Rubrica_MINEDU_{grado_r.replace(' ', '_')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            except Exception as e:
                st.error(f"Error: {e}")
