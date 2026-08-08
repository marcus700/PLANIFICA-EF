import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import io
import time
import re

# Importamos la base de datos oficial CNEB completa y el helper de ciclo
from cneb_datos import CNEB_PRIMARIA, obtener_ciclo_primaria

# --- LISTAS DE OPCIONES ---
GRADOS = [
    "1° de Primaria",
    "2° de Primaria",
    "3° de Primaria",
    "4° de Primaria",
    "5° de Primaria",
    "6° de Primaria"
]

DURACIONES_UNIDAD = [
    "4 Semanas (4 sesiones)",
    "5 Semanas (5 sesiones)",
    "6 Semanas (6 sesiones)",
    "8 Semanas (8 sesiones)"
]

COMPETENCIAS_EF = [
    "Se desenvuelve de manera autónoma a través de su motricidad",
    "Asume una vida saludable",
    "Interactúa a través de sus habilidades sociomotrices"
]

# 1. Configuración de la Plataforma
st.set_page_config(page_title="Generador CNEB Primaria", page_icon="🏃‍♂️", layout="centered")

st.title("🏃 Generador CNEB - Educación Física (Primaria)")
st.subheader("Con Estándares y Desempeños oficiales del MINEDU (1° a 6° de Primaria)")
st.write("Herramienta inteligente para diseñar tus documentos curriculares al instante utilizando la base de datos CNEB oficial.")

# Configuramos la clave API
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("🔑 No se encontró la variable GEMINI_API_KEY en los Secrets de Streamlit.")

# FUNCIÓN DE GENERACIÓN CON GEMINI
def generar_con_gemini(prompt, instrucciones_sistema=""):
    modelos_a_probar = [
        "gemini-1.5-flash",
        "models/gemini-1.5-flash",
        "gemini-1.5-pro",
        "models/gemini-1.5-pro"
    ]
    
    ultimo_error = None
    
    for nombre_modelo in modelos_a_probar:
        try:
            model = genai.GenerativeModel(model_name=nombre_modelo, system_instruction=instrucciones_sistema)
            return model.generate_content(prompt)
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                time.sleep(5)
                try:
                    return model.generate_content(prompt)
                except Exception as ex:
                    ultimo_error = ex
                    continue
            else:
                ultimo_error = e
                continue
                
    raise ultimo_error

# FUNCIONES AUXILIARES PARA FORMATEO DE WORD (.docx)
def add_formatted_text(paragraph, text):
    """Procesa negritas **texto** dentro de un párrafo de python-docx"""
    parts = re.split(r'(\*\*.*?\*\*)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        else:
            paragraph.add_run(part)

def render_markdown_table(doc, lines):
    """Convierte líneas de tabla Markdown a tabla nativa de MS Word"""
    rows = []
    for line in lines:
        if '---' in line:
            continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if cells:
            rows.append(cells)

    if not rows:
        return

    num_cols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'

    for i, row_data in enumerate(rows):
        row = table.rows[i]
        for j, cell_value in enumerate(row_data):
            if j < len(row.cells):
                cell = row.cells[j]
                cell.text = ""
                p = cell.paragraphs[0]
                add_formatted_text(p, cell_value)
                if i == 0:
                    for run in p.runs:
                        run.bold = True

def crear_archivo_word(texto_contenido):
    """Genera un archivo Word (.docx) procesando títulos, listas, negritas y tablas Markdown"""
    doc = Document()
    
    # Configuración de márgenes estándar de 1 pulgada
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    lines = texto_contenido.split('\n')
    in_table = False
    table_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith('|') and stripped.endswith('|'):
            in_table = True
            table_lines.append(stripped)
            continue
        elif in_table:
            render_markdown_table(doc, table_lines)
            in_table = False
            table_lines = []

        if not stripped:
            continue

        if stripped.startswith('# '):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(stripped[2:])
            run.bold = True
            run.font.size = Pt(16)
            run.font.color.rgb = RGBColor(27, 94, 32)
        elif stripped.startswith('## '):
            p = doc.add_paragraph()
            run = p.add_run(stripped[3:])
            run.bold = True
            run.font.size = Pt(13)
            run.font.color.rgb = RGBColor(46, 125, 50)
        elif stripped.startswith('### '):
            p = doc.add_paragraph()
            run = p.add_run(stripped[4:])
            run.bold = True
            run.font.size = Pt(11)
            run.font.color.rgb = RGBColor(27, 94, 32)
        elif stripped.startswith('- ') or stripped.startswith('* '):
            p = doc.add_paragraph(style='List Bullet')
            add_formatted_text(p, stripped[2:])
        else:
            p = doc.add_paragraph()
            add_formatted_text(p, stripped)

    if in_table:
        render_markdown_table(doc, table_lines)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Creación de las 3 Pestañas de Navegación
tab1, tab2, tab3 = st.tabs([
    "📂 Crear Unidad de Aprendizaje", 
    "📝 Crear Sesión de Aprendizaje", 
    "📊 Crear Rúbrica de Evaluación"
])

# ==============================================================================
# PESTAÑA 1: UNIDADES DE APRENDIZAJE
# ==============================================================================
with tab1:
    st.write("Estructura una unidad didáctica completa alineada al CNEB con su matriz de planificación y secuencia de sesiones.")
    with st.form("form_unidad"):
        col1, col2 = st.columns(2)
        with col1:
            grado_u = st.selectbox("🏫 Grado de Primaria:", GRADOS, key="u1")
            duracion_u = st.selectbox("⏱️ Duración de la Unidad:", DURACIONES_UNIDAD, key="u2")
            ie_u = st.text_input("🏢 Nombre de la I.E.:", value='N.° 22314 "Vicenta Aquije de Huamán"', key="u_ie")
            directora_u = st.text_input("👤 Directora:", value="Prof. Luisa Ruth Aronés Herrera", key="u_dir")
        with col2:
            docente_u = st.text_input("👨‍🏫 Docente de Ed. Física:", value="Mario A. García Torres", key="u_doc")
            fechas_u = st.text_input("📅 Fechas / Periodo:", value="25 de mayo al 19 de junio del 2026", key="u_fechas")
            producto_u = st.text_input("🏆 Producto de la Unidad:", value="Festival Lúdico-Motor Peruanito", key="u_prod")

        problema_u = st.text_area(
            "📋 Describe el problema del contexto o necesidad de los estudiantes:",
            placeholder="Ej. Los estudiantes muestran dificultades en la orientación espacial y coordinación motriz en juegos grupales, y se requiere promover hábitos de higiene y normas consensuadas.",
            value="Muchos amiguitos tienen dificultades para orientarse en el patio al desplazarse en grupo y poca comprensión de señales espaciales. Además, se requiere consolidar el hábito de lavado de manos e higiene al finalizar la actividad física.",
            key="u3"
        )
        boton_unidad = st.form_submit_button("📂 Generar Unidad de Aprendizaje en Word")

    if boton_unidad and problema_u:
        with st.spinner("Escribiendo la unidad didáctica oficial CNEB..."):
            try:
                ciclo_u = obtener_ciclo_primaria(grado_u)
                
                # Extraemos la base de datos oficial del CNEB para el ciclo y grado
                cneb_contexto = ""
                for comp_nombre, comp_data in CNEB_PRIMARIA.items():
                    est_texto = comp_data["estandares"].get(ciclo_u, "")
                    des_lista = comp_data["desempenos"].get(grado_u, [])
                    cneb_contexto += f"\n\nCOMPETENCIA: {comp_nombre}\nESTÁNDAR OFICIAL ({ciclo_u}):\n{est_texto}\nDESEMPEÑOS OFICIALES ({grado_u}):\n" + "\n".join(des_lista)

                instrucciones_u = f"""
Actúa como un Especialista Curricular experto en Educación Física para Primaria bajo el enfoque oficial del CNEB del MINEDU de Perú.
Tu tarea es diseñar una UNIDAD DE APRENDIZAJE completa, rigurosa y estructurada en exactamente 10 secciones obligatorias.

BASE DE DATOS OFICIAL CNEB A UTILIZAR PARA {grado_u} ({ciclo_u}):
{cneb_contexto}

ESTRUCTURA OBLIGATORIA A GENERAR (en Markdown):

# UNIDAD DE APRENDIZAJE N°.......
### "[TÍTULO MOTIVADOR Y COMPLETO ENTRE COMILLAS]"

## II. DATOS INFORMATIVOS
- **IE:** {ie_u}
- **Directora:** {directora_u}
- **Profesor:** {docente_u}
- **Ciclo:** {ciclo_u}
- **Grado y sección:** {grado_u}
- **Duración:** {duracion_u} ({fechas_u})

## III. SITUACIÓN SIGNIFICATIVA
- Contextualizar la realidad: {problema_u}.
- Incluir un dato cuantitativo o cualitativo sobre la problemática (ej. "solo el 35% logra...").
- Formular 3 preguntas retadoras y desafiantes asociadas al desarrollo motriz y social.
- Proponer la estrategia pedagógica para resolver los retos.

## IV. PRODUCTO DE LA UNIDAD
- Describir el desempeño práctico o producto tangible: {producto_u}.

## V. ENFOQUES TRANSVERSALES
Genera una tabla con 2 enfoques transversales del CNEB:
| Enfoque Transversal | Valor(es) | Acciones o Actitudes Observables |

## VI. COMPETENCIAS TRANSVERSALES
Genera una tabla con "Gestiona su aprendizaje de manera autónoma" y "Se desenvuelve en entornos virtuales generados por las TIC" con sus Capacidades y Desempeños adaptados a Educación Física.

## VII. ESTÁNDARES, COMPETENCIAS Y CAPACIDADES DEL ÁREA DE EDUCACIÓN FÍSICA
Transcribe las 3 competencias oficiales de Educación Física con sus capacidades y el ESTÁNDAR COMPLETO del {ciclo_u} provisto en la base de datos sin alterarlo.

## VIII. MATRIZ DE PLANIFICACIÓN (Formato Tabla detallado por sesión)
REGLAS OBLIGATORIAS PARA CADA ACTIVIDAD DE LA MATRIZ:
1. En la parte superior de cada actividad/sesión, coloca un bloque o fila con el ESTÁNDAR COMPLETO del CNEB correspondiente al {ciclo_u} (transcrito íntegramente de la base de datos oficial provista, sin modificar ni alterar el texto original), pero RESALTANDO EN NEGRITA únicamente la parte específica del estándar que se evalúa o trabaja en esa sesión.
2. Columnas obligatorias de la tabla:
   | Sesión N.° y Título de la sesión | Competencia / Capacidad | Desempeño | Criterios de Evaluación | Evidencia y Producto | Instrumento de Evaluación |
3. REGLA DEL DESEMPEÑO: En la columna Desempeño, transcribe el desempeño COMPLETO del CNEB correspondiente a {grado_u}, RESALTANDO EN NEGRITA tanto la parte del desempeño utilizada como las palabras/términos precisados agregados para contextualizar la sesión.
4. REGLA IMPORTANTE: NO incluyas la columna "Propósito" en esta tabla de matriz.

## IX. SECUENCIA DE SESIONES
Genera una tabla con las columnas:
| N° | Título de la actividad | Propósito de la actividad | Representación gráfica |
- El propósito debe incluir la secuencia metodológica (calentamiento, desarrollo motriz/juego, higiene personal y reflexión).
- La representación gráfica describe brevemente el esquema visual o distribución de materiales en el patio.

## X. RECURSOS
- Recursos para el Docente (Normativa CNEB, RM N° 501-2025, Oficio Múltiple N° 00052-2026, etc.).
- Recursos para el Estudiante (Kit de aseo, ropa deportiva, materiales específicos).
- Fecha y espacio para firmas (Directora y Docente de Educación Física).
"""

                pedido_u = f"Genera la unidad completa para {grado_u} ({ciclo_u}), duración {duracion_u}. Problema: {problema_u}. Producto: {producto_u}"

                response = generar_con_gemini(pedido_u, instrucciones_sistema=instrucciones_u)
                
                resultado_u = response.text
                st.success("¡Unidad Curricular CNEB generada con éxito!")
                st.markdown(resultado_u)
                archivo_word_u = crear_archivo_word(resultado_u)
                st.download_button(
                    label="📄 Descargar Unidad de Aprendizaje en Word (.docx)", 
                    data=archivo_word_u, 
                    file_name=f"Unidad_Aprendizaje_EF_{grado_u.replace(' ', '_')}.docx", 
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error(f"❌ Error al generar la unidad: {str(e)}")

# ==============================================================================
# PESTAÑA 2: SESIONES DE APRENDIZAJE
# ==============================================================================
with tab2:
    st.write("Completa los datos oficiales requeridos por el MINEDU para tu clase diaria.")
    with st.form("form_sesion"):
        grado_s = st.selectbox("🏫 Grado de Primaria:", GRADOS, key="s1")
        duracion_s = st.number_input("⏱️ Duración (minutos):", value=90, min_value=30, max_value=180, key="s2")
        competencia_s = st.selectbox("🎯 Competencia CNEB:", COMPETENCIAS_EF, key="s3")
        tema_s = st.text_input("⚽ Tema / Propósito Motriz:", value="Coordinación dinámica general y equilibrio en desplazamientos", key="s4")
        materiales_s = st.text_input("🧱 Materiales Disponibles:", value="Conos, aros, pelotas, tizas, kit de aseo", key="s5")
        boton_sesion = st.form_submit_button("🚀 Generar Sesión de Aprendizaje CNEB Primaria")

    if boton_sesion and tema_s and materiales_s:
        with st.spinner("Escribiendo la sesión oficial CNEB..."):
            try:
                ciclo_s = obtener_ciclo_primaria(grado_s)
                estandar_real = CNEB_PRIMARIA.get(competencia_s, {}).get("estandares", {}).get(ciclo_s, "Estándar general.")
                desempenos_reales = CNEB_PRIMARIA.get(competencia_s, {}).get("desempenos", {}).get(grado_s, ["Desempeños generales."])
                desempenos_texto = "\n".join(desempenos_reales)
                
                instrucciones = f"""Actúa como un Asistente Pedagógico experto en Educación Física para Primaria bajo el enfoque oficial del CNEB del MINEDU de Perú.
Estás redactando para {grado_s} ({ciclo_s}).

DATOS OFICIALES CNEB:
- Estándar: "{estandar_real}"
- Desempeños disponibles:
{desempenos_texto}

Estructura la Sesión incluyendo de forma ordenada:
1. Datos Informativos (IE, Docente, Grado, Fecha, Área: Educación Física, Duración: {duracion_s} min).
2. Propósitos y Evidencias de Aprendizaje (Tabla con: Competencia y Capacidades, Estándar CNEB con **negrita** en la parte aplicada, Desempeño precisado completo con **negrita**, Criterios de Evaluación, Evidencia y Producto, Instrumento: Lista de Cotejo).
3. Enfoques Transversales.
4. Preparación de la Sesión.
5. Secuencia Didáctica (Inicio {round(duracion_s * 0.2)} min, Desarrollo {round(duracion_s * 0.6)} min con progresiones y variaciones, Cierre {round(duracion_s * 0.2)} min con vuelta a la calma, metacognición e higiene personal) redactada en PRIMERA PERSONA y TIEMPO PRESENTE.
6. Anexo: Lista de Cotejo."""

                pedido = f"Diseña una sesión de {duracion_s} minutos para {grado_s} ({ciclo_s}). Tema: {tema_s}. Materiales: {materiales_s}."
                
                response = generar_con_gemini(pedido, instrucciones_sistema=instrucciones)
                
                resultado_s = response.text
                st.success("¡📋 Sesión Generada (MINEDU) con éxito!")
                st.markdown(resultado_s)
                archivo_word = crear_archivo_word(resultado_s)
                st.download_button(
                    label="📄 Descargar Sesión en Word (.docx)", 
                    data=archivo_word, 
                    file_name=f"Sesion_EF_{grado_s.replace(' ', '_')}.docx", 
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error(f"❌ Error al generar la sesión: {str(e)}")

# ==============================================================================
# PESTAÑA 3: RÚBRICAS DE EVALUACIÓN
# ==============================================================================
with tab3:
    st.write("Diseña instrumentos de evaluación con criterios claros y descriptores por niveles de logro CNEB.")
    with st.form("form_rubrica"):
        grado_r = st.selectbox("🏫 Grado de Primaria:", GRADOS, key="r1")
        competencia_r = st.selectbox("🎯 Competencia a Evaluar:", COMPETENCIAS_EF, key="r2")
        criterio_r = st.text_input("📊 Desempeño o criterio específico a evaluar:", value="Orientación espacial y equilibrio postural en actividades lúdicas")
        boton_rubrica = st.form_submit_button("📊 Generar Rúbrica en Word")

    if boton_rubrica and criterio_r:
        with st.spinner("Escribiendo la rúbrica oficial CNEB..."):
            try:
                ciclo_r = obtener_ciclo_primaria(grado_r)
                instrucciones_r = f"""Actúa como un Evaluador Pedagógico experto en Educación Física para Primaria bajo los lineamientos del CNEB del MINEDU. 
Diseña una rúbrica analítica en formato tabla estructurada para evaluar a estudiantes de {grado_r} ({ciclo_r}). 
Competencia: {competencia_r}. 
Actividad/Criterio a evaluar: {criterio_r}.
Incluye los cuatro niveles de logro oficiales del CNEB: En Inicio, En Proceso, Logrado y Logro Destacado."""

                pedido_r = f"Crea una rúbrica analítica de evaluación para {grado_r} ({ciclo_r}). Criterio: {criterio_r}"
                
                response = generar_con_gemini(pedido_r, instrucciones_sistema=instrucciones_r)
                
                resultado_r = response.text
                st.success("¡Rúbrica CNEB generada con éxito!")
                st.markdown(resultado_r)
                archivo_word_r = crear_archivo_word(resultado_r)
                st.download_button(
                    label="📄 Descargar Rúbrica en Word (.docx)", 
                    data=archivo_word_r, 
                    file_name=f"Rubrica_EF_{grado_r.replace(' ', '_')}.docx", 
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error(f"❌ Error al generar la rúbrica: {str(e)}")
