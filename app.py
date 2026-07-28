import streamlit as st
from google import genai
from google.genai import types
from docx import Document
import io

# Configuración visual de la plataforma con su nuevo nombre
st.set_page_config(page_title="PlanificaEF", page_icon="🏃‍♂️", layout="centered")

st.title("🏃‍♂️ PlanificaEF")
st.subheader("Asistente Pedagógico de Educación Física (Primaria - CNEB)")
st.write("Herramienta inteligente para diseñar tus documentos curriculares al instante.")

# Enlace automático a la clave secreta guardada de forma segura
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

# Creación de las 3 Pestañas de Trabajo
tab1, tab2, tab3 = st.tabs([
    "📂 Crear Unidad de Aprendizaje", 
    "📝 Crear Sesión de Aprendizaje", 
    "📊 Crear Rúbrica de Evaluación"
])

# --- PESTAÑA 1: UNIDADES ---
with tab1:
    st.write("Estructura una unidad didáctica completa para varias semanas.")
    with st.form("form_unidad"):
        grado_u = st.selectbox("Grado de Primaria:", ["1° Grado", "2° Grado", "3° Grado", "4° Grado", "5° Grado", "6° Grado"], key="u1")
        duracion_u = st.selectbox("Duración de la Unidad:", ["4 Semanas (4 sesiones)", "6 Semanas (6 sesiones)", "8 Semanas (8 sesiones)"], key="u2")
        problema_u = st.text_area("Describe el problema del contexto o interés de los niños:", placeholder="Ej. Los estudiantes muestran dificultades para trabajar en equipo y respetar reglas en los juegos del recreo.", key="u3")
        boton_unidad = st.form_submit_button("📂 Generar Unidad en Word")

    if boton_unidad and problema_u:
        with st.spinner("Diseñando la Unidad de Aprendizaje..."):
            try:
                client = genai.Client(api_key=api_key)
                instrucciones_u = (
                    "Actúa como un Especialista Curricular experto en Educación Física para Primaria bajo el enfoque del CNEB de Perú. "
                    "Diseña una Unidad de Aprendizaje completa que incluya estrictamente:\n"
                    "1. Título de la unidad (significativo).\n"
                    "2. Situación Significativa (Contexto, Reto en forma de pregunta y Producto esperado).\n"
                    "3. Propósitos de Aprendizaje articulados con las competencias del área.\n"
                    "4. Secuencia semanal de sesiones (Título y una breve descripción pedagógica de cada clase)."
                )
                pedido_u = f"Crea una unidad para {grado_u} con duración de {duracion_u}. Contexto: {problema_u}"
                response = client.models.generate_content(model='gemini-2.5-flash', contents=pedido_u, config=types.GenerateContentConfig(system_instruction=instrucciones_u, temperature=0.7))
                resultado_u = response.text
                st.success("¡Unidad Curricular generada con éxito!")
                st.markdown(resultado_u)
                
                archivo_word_u = crear_archivo_word(resultado_u)
                st.download_button(label="📥 Descargar Unidad en Word (.docx)", data=archivo_word_u, file_name=f"Unidad_PlanificaEF_{grado_u.replace(' ', '_')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            except Exception as e: st.error(f"Error: {e}")

# --- PESTAÑA 2: SESIONES ---
with tab2:
    st.write("Genera el desarrollo de una sesión diaria paso a paso.")
    with st.form("form_sesion"):
        grado_s = st.selectbox("Grado de Primaria:", ["1° Grado", "2° Grado", "3° Grado", "4° Grado", "5° Grado", "6° Grado"], key="s1")
        competencia_s = st.selectbox("Competencia Principal:", ["Se desenvuelve de manera autónoma a través de su motricidad", "Asume una vida saludable", "Interactúa a través de sus habilidades sociomotrices"], key="s2")
        detalles_s = st.text_area("Tema de la clase o materiales disponibles:", placeholder="Ej. Coordinación óculo-manual lanzando y recibiendo pelotas de plástico.", key="s3")
        boton_sesion = st.form_submit_button("⚡ Generar Sesión en Word")

    if boton_sesion and detalles_s:
        with st.spinner("Diseñando la sesión de aprendizaje..."):
            try:
                client = genai.Client(api_key=api_key)
                instrucciones = (
                    "Actúa como un Asistente Pedagógico experto en Educación Física para Primaria (CNEB Perú). "
                    "Diseña una Sesión de Aprendizaje que incluya: Datos informativos, Propósito, Momentos de la sesión "
                    "(Inicio con saberes previos y motivación; Desarrollo con actividades físicas lúdicas, variantes de dificultad e hidratación; "
                    "Cierre con vuelta a la calma, higiene corporal y preguntas de metacognición) y Materiales."
                )
                pedido = f"Diseña una sesión para {grado_s}. Competencia: {competencia_s}. Detalles: {detalles_s}"
                response = client.models.generate_content(model='gemini-2.5-flash', contents=pedido, config=types.GenerateContentConfig(system_instruction=instrucciones, temperature=0.7))
                resultado_s = response.text
                st.success("¡Sesión generada con éxito!")
                st.markdown(resultado_s)
                
                archivo_word = crear_archivo_word(resultado_s)
                st.download_button(label="📥 Descargar Sesión en Word (.docx)", data=archivo_word, file_name=f"Sesion_PlanificaEF_{grado_s.replace(' ', '_')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            except Exception as e: st.error(f"Error: {e}")

# --- PESTAÑA 3: RÚBRICAS ---
with tab3:
    st.write("Diseña instrumentos de evaluación con criterios claros.")
    with st.form("form_rubrica"):
        grado_r = st.selectbox("Grado de Primaria:", ["1° Grado", "2° Grado", "3° Grado", "4° Grado", "5° Grado", "6° Grado"], key="r1")
        competencia_r = st.selectbox("Competencia a Evaluar:", ["Se desenvuelve de manera autónoma a través de su motricidad", "Asume una vida saludable", "Interactúa a través de sus habilidades sociomotrices"], key="r2")
        criterio_r = st.text_input("Desempeño específico a evaluar:", placeholder="Ej. Control de la postura al saltar con un pie.")
        boton_rubrica = st.form_submit_button("📊 Generar Rúbrica en Word")

    if boton_rubrica and criterio_r:
        with st.spinner("Estructurando la rúbrica..."):
            try:
                client = genai.Client(api_key=api_key)
                instrucciones_r = (
                    "Actúa como un Evaluador Pedagógico experto en Educación Física para Primaria. "
                    "Diseña una rúbrica analítica estructurada con los niveles: En Inicio, En Proceso, Logrado y Logro Destacado "
                    "para el desempeño solicitado, utilizando criterios claros y observables alineados al CNEB."
                )
                pedido_r = f"Crea una rúbrica para {grado_r}. Competencia: {competencia_r}. Desempeño: {criterio_r}"
                response = client.models.generate_content(model='gemini-2.5-flash', contents=pedido_r, config=types.GenerateContentConfig(system_instruction=instrucciones_r, temperature=0.7))
                resultado_r = response.text
                st.success("¡Rúbrica generada con éxito!")
                st.markdown(resultado_r)
                
                archivo_word_r = crear_archivo_word(resultado_r)
                st.download_button(label="📥 Descargar Rúbrica en Word (.docx)", data=archivo_word_r, file_name=f"Rubrica_PlanificaEF_{grado_r.replace(' ', '_')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            except Exception as e: st.error(f"Error: {e}")
