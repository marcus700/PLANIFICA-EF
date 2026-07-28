import os
import re
from google import genai
from google.genai import types

# ==============================================================================
# BASE DE DATOS EXACTA DEL DOCUMENTO CNEB-EF PRIMARIA (MINEDU - PERÚ)
# ==============================================================================
CNEB_PRIMARIA = {
    "Se desenvuelve de manera autónoma a través de su motricidad": {
        "estandares": {
            "III Ciclo": (
                "Se desenvuelve de manera autónoma a través de su motricidad cuando comprende cómo "
                "usar su cuerpo en las diferentes acciones que realiza utilizando su lado dominante y "
                "realiza movimientos coordinados que le ayudan a sentirse seguro en la práctica de "
                "actividades físicas. Se orienta espacialmente en relación a sí mismo y a otros puntos "
                "de referencia. Se expresa corporalmente con sus pares de diferentes utilizando el ritmo, "
                "gestos y movimientos como recursos para comunicar."
            ),
            "IV Ciclo": (
                "Se desenvuelve de manera autónoma a través de su motricidad cuando comprende cómo "
                "usar su cuerpo explorando la alternancia de sus lados corporales de acuerdo a su utilidad "
                "y ajustando la posición del cuerpo en el espacio y en el tiempo en diferentes etapas "
                "de las acciones motrices, con una actitud positiva y una voluntad de experimentar "
                "situaciones diversas. Experimenta nuevas posibilidades expresivas de su cuerpo y las utiliza "
                "para relacionarse y comunicar ideas, emociones, sentimientos, pensamientos."
            ),
            "V Ciclo": (
                "Se desenvuelve de manera autónoma a través de su motricidad cuando acepta sus "
                "posibilidades y limitaciones según su desarrollo e imagen corporal. Realiza secuencias "
                "de movimientos coordinados aplicando la alternancia de sus lados corporales de acuerdo "
                "a su utilidad. Produce con sus pares secuencias de movimientos corporales, expresivos o "
                "rítmicos en relación a una intención."
            ),
        },
        "desempenos": {
            "1° de Primaria": [
                "1.1.- Es autónomo al explorar las posibilidades de su cuerpo en diferentes acciones para mejorar sus movimientos (saltar, correr, lanzar) al mantener y/o recuperar el equilibrio en el espacio y con los objetos, cuando explora conscientemente distintas bases de sustentación, conociendo en sí mismo su lado dominante.",
                "1.2.- Se orienta a través de sus nociones espacio-temporales (arriba - abajo, dentro - fuera, cerca – lejos) en relación a sí mismo y de acuerdo a sus intereses y necesidades.",
                "1.3.- Descubre nuevos movimientos y gestos para representar objetos, personajes y estados de ánimo y ritmos sencillos de distintos orígenes: de la naturaleza, del propio cuerpo, de la música, etc.",
                "1.4.- Se expresa motrizmente para comunicar sus emociones (miedo, angustia, alegría, placer, torpeza, inhibición, rabia, entre otros) y representa en el juego acciones cotidianas de su familia y de la comunidad."
            ],
            "2° de Primaria": [
                "1.1.- Explora de manera autónoma sus posibilidades de movimiento al realizar con seguridad y confianza habilidades motrices básicas realizando movimientos coordinados según sus intereses, necesidades y posibilidades.",
                "1.2.- Se orienta en el espacio y tiempo en relación a sí mismo y a otros puntos de referencia, reconociendo su lado derecho e izquierdo y sus posibilidades de equilibrio con diferentes bases de sustentación en acciones lúdicas.",
                "1.3.- Resuelve situaciones motrices al utilizar su lenguaje corporal (gesto, contacto visual, actitud corporal, apariencia, etc.), verbal y sonoro que le ayudan a sentirse seguro, confiado y aceptado.",
                "1.4.- Utiliza su cuerpo y el movimiento para expresar ideas y emociones en la práctica de actividades lúdicas con diferentes tipos de ritmos y música para expresarse corporalmente y usando diversos elementos."
            ],
            "3° de Primaria": [
                "1.1.- Reconoce la izquierda y derecha en relación a objetos y en sus pares para mejorar sus posibilidades de movimiento en diferentes acciones lúdicas.",
                "1.2.- Se orienta en un espacio y tiempo determinado, en relación a sí mismo, los objetos y sus compañeros, coordina sus movimientos en situaciones lúdicas y regula su equilibrio al variar la base de sustentación y la altura de la superficie de apoyo, afianzando sus habilidades motrices básicas.",
                "1.3.- Resuelve situaciones motrices al utilizar su lenguaje corporal (gesto, contacto visual, actitud corporal, apariencia, etc.), verbal y sonoro para comunicar actitudes, sensaciones y estados de ánimo, acciones que le posibilitan comunicarse mejor con los otros y disfrutar de las actividades lúdicas.",
                "1.4.- Vivencia el ritmo y se apropia de secuencias rítmicas corporales en situaciones de juego para expresarse corporalmente a través de la música."
            ],
            "4° de Primaria": [
                "1.1.- Regula la posición del cuerpo en situaciones de equilibrio, con modificación del espacio teniendo como referencia la trayectoria de objetos, los otros y sus propios desplazamientos para afianzar sus habilidades motrices básicas.",
                "1.2.- Alterna sus lados corporales de acuerdo a su utilidad y/o necesidad y se orienta en el espacio y en el tiempo, en relación a sí mismo y a otros puntos de referencia en actividades lúdicas y predeportivas.",
                "1.3.- Utiliza su cuerpo (posturas, gestos y mímica) y diferentes movimientos para expresar formas, ideas, emociones, sentimientos y pensamientos en la actividad física.",
                "1.4.- Utiliza su lenguaje corporal para expresar su forma particular de moverse, creando secuencias sencillas de movimientos, relacionados con el ritmo, la música de su cultura y la historia de su región."
            ],
            "5° de Primaria": [
                "1.1.- Anticipa las acciones motrices a realizar en un espacio y tiempo para mejorar las posibilidades de respuesta en la acción, aplicando la alternancia de sus lados corporales de acuerdo a su preferencia, utilidad y/o necesidad en la actividad física.",
                "1.2.- Pone en práctica las habilidades motrices específicas (relacionadas con la carrera, salto y lanzamientos) a través de la exploración y regulación de su cuerpo para dar respuesta a las situaciones motrices (en contextos lúdicos, predeportivos, etc.).",
                "1.3.- Crea movimientos y desplazamientos rítmicos e incorpora las particularidades de su lenguaje corporal teniendo como base la música de su región; al asumir diferentes roles en la práctica de actividad física.",
                "1.4.- Valora en sí mismo y en sus pares nuevas formas de movimiento y gestos corporales; aceptando la existencia de nuevas formas de movimiento y expresión para comunicar ideas y emociones en diferentes situaciones motrices."
            ],
            "6° de Primaria": [
                "1.1.- Anticipa las acciones motrices a realizar en un espacio y tiempo para mejorar las posibilidades de respuesta en la acción, aplicando la alternancia de sus lados corporales de acuerdo a su preferencia, utilidad y/o necesidad en la actividad física.",
                "1.2.- Afianza las habilidades motrices específicas (relacionadas con la carrera, salto y lanzamientos) a través de la regulación de su cuerpo para dar respuesta a las situaciones motrices (en contextos lúdicos, predeportivos, etc.).",
                "1.3.- Aplica su lenguaje corporal para expresar su forma particular de moverse, al asumir y adjudicar diferentes roles en la práctica de actividad física.",
                "1.4.- Crea con sus pares una secuencia de movimientos corporales, expresivos y/o rítmicos, de manera programada y estructurada, expresándose de diferentes maneras y con diversos recursos, a través del cuerpo y el movimiento para comunicar ideas y emociones."
            ]
        }
    },
    "Asume una vida saludable": {
        "estandares": {
            "III Ciclo": (
                "Asume una vida saludable cuando diferencia los alimentos saludables de su dieta familiar, "
                "los momentos adecuados para ingerirlos y las posturas que lo ayudan al buen desempeño en la "
                "práctica de actividad física y de la vida cotidiana, reconociendo la importancia del autocuidado. "
                "Participa regularmente en la práctica de actividades lúdicas identificando su ritmo cardiaco, "
                "respiración y sudoración; utiliza prácticas de activación corporal y psicológica antes de la actividad lúdica."
            ),
            "IV Ciclo": (
                "Asume una vida saludable cuando diferencia los alimentos de su dieta familiar y de su región que son "
                "saludables de los que no lo son. Previene riesgos relacionados con la postura e higiene conociendo aquellas "
                "que favorecen y no favorecen su salud e identifica su fuerza, resistencia y velocidad en la práctica de "
                "actividades lúdicas. Adapta su esfuerzo en la práctica de actividad física de acuerdo a las características "
                "de la actividad y a sus posibilidades, aplicando conocimientos relacionados con el ritmo cardiaco, la "
                "respiración y la sudoración. Realiza prácticas de activación corporal y psicológica, e incorpora el autocuidado "
                "relacionado con los ritmos de actividad y descanso para mejorar el funcionamiento de su organismo."
            ),
            "V Ciclo": (
                "Asume una vida saludable cuando utiliza instrumentos que miden la aptitud física y estado nutricional "
                "e interpreta la información de los resultados obtenidos para mejorar su calidad de vida. Replantea sus "
                "hábitos higiénicos y alimenticios tomando en cuenta los cambios físicos propios de la edad, evita la realización "
                "de ejercicios y posturas contraindicadas para la salud en la práctica de actividad física. Incorpora prácticas "
                "saludables para su organismo consumiendo alimentos adecuados a las características personales y evitando el "
                "consumo de drogas. Propone ejercicios de activación y relajación antes, durante y después de la práctica y "
                "participa en actividad física de distinta intensidad regulando su esfuerzo."
            )
        },
        "desempenos": {
            "1° de Primaria": [
                "2.1.- Reconoce los alimentos de su dieta familiar y las posturas que son beneficiosas para su salud en la vida cotidiana y en la práctica de actividades lúdicas.",
                "2.2.- Identifica en sí mismo y en otros la diferencia entre inspiración y espiración, en reposo y movimiento en las actividades lúdicas, regulando su esfuerzo al participar en actividades lúdicas.",
                "2.3.- Realiza con autonomía prácticas de cuidado personal al asearse, al vestirse, al adoptar posturas adecuadas en la práctica de actividades lúdicas y de la vida cotidiana.",
                "2.4.- Busca satisfacer sus necesidades corporales cuando tiene sed y resuelve las dificultades que le producen el cansancio, la incomodidad y la inactividad, mostrando su bienestar al realizar actividades lúdicas, sintiéndose bien consigo mismo, con los otros y con su entorno."
            ],
            "2° de Primaria": [
                "2.1.- Comprende la importancia de la activación corporal (calentamiento) y psicológica (atención, concentración y motivación) antes de la actividad lúdica identificando los signos y síntomas relacionados con: el ritmo cardiaco, la respiración agitada y la sudoración que aparecen en el organismo al practicar actividades lúdicas.",
                "2.2.- Reflexiona sobre los alimentos saludables de su dieta familiar y de la región, los momentos adecuados para ingerirlos, la importancia de hidratarse, conociendo las posturas adecuadas en la práctica de actividad física y de la vida cotidiana, que le permiten mayor seguridad a la hora de practicar actividades lúdicas y de la vida cotidiana.",
                "2.3.- Incorpora prácticas de cuidado personal al asearse, al vestirse, al adoptar posturas adecuadas en la práctica de actividades lúdicas y de la vida cotidiana que le permitan la participación en el juego sin afectar su desempeño.",
                "2.4.- Reconoce la importancia del autocuidado regulando su esfuerzo en la práctica de actividades lúdicas."
            ],
            "3° de Primaria": [
                "2.1.- Explica la importancia de la activación corporal (calentamiento) y psicológica (atención, concentración y motivación) que le ayuda a estar predispuesto a la actividad.",
                "2.2.- Diferencia los alimentos de su dieta familiar y de su región que son saludables de los que no lo son, para la práctica de actividad física y de la vida cotidiana.",
                "2.3.- Aplica los conocimientos de los beneficios de la práctica de actividad física y salud relacionados con el ritmo cardiaco, la respiración y la sudoración cuando adapta su esfuerzo en la práctica de diferentes actividades lúdicas.",
                "2.4.- Incorpora el autocuidado relacionado con los ritmos de actividad-descanso para mejorar el funcionamiento de su organismo."
            ],
            "4° de Primaria": [
                "2.1.- Selecciona actividades para la activación corporal (calentamiento) y psicológica (atención, concentración y motivación) antes de la actividad e identifica en sí mismo las variaciones en la frecuencia cardiaca y respiratoria en relación a diferentes niveles de esfuerzo en la práctica de actividades lúdicas.",
                "2.2.- Selecciona e incorpora en su dieta los alimentos nutritivos y energéticos existentes en su dieta familiar y región que contribuyen a la práctica de actividad física.",
                "2.3.- Incorpora el autocuidado relacionado con los ritmos de actividad-descanso, hidratación y exposición a los rayos solares, para mejorar el funcionamiento de su organismo.",
                "2.4.- Adopta posturas adecuadas para prevenir problemas musculares y óseos incorporando el autocuidado relacionado con los ritmos de actividad y descanso para mejorar el funcionamiento del organismo."
            ],
            "5° de Primaria": [
                "2.1.- Identifica las condiciones que favorecen la aptitud física (IMC y pruebas físicas) para mejorar la calidad de vida, en relación a sus características personales.",
                "2.2.- Comprende los cambios físicos propios de la edad y su repercusión en la higiene en relación a la práctica de actividad física y actividades de la vida cotidiana y reflexiona sobre las prácticas alimenticias perjudiciales para el organismo analizando la importancia de la alimentación en relación a su IMC.",
                "2.3.- Identifica posturas y ejercicios contraindicados para la salud en la práctica de actividad física.",
                "2.4.- Aplica los beneficios relacionados con la salud al realizar actividades de activación corporal, psicológica y de recuperación antes, durante y después de la práctica de actividad física."
            ],
            "6° de Primaria": [
                "2.1.- Conoce los diferentes métodos de evaluación para determinar la aptitud física y selecciona los que mejor se adecúen a sus posibilidades, y utiliza la información obtenida en beneficio propio de su salud.",
                "2.2.- Comprende la importancia de la actividad física incorporando la práctica en su vida cotidiana e identifica los cambios físicos propios de la edad y su repercusión en la higiene en relación a la práctica de actividad física y actividades de la vida cotidiana.",
                "2.3.- Evita la realización de posturas y ejercicios contraindicados y cualquier práctica de actividad física que perjudique su salud.",
                "2.4.- Previene hábitos perjudiciales para su organismo como el consumo de comida rápida, alcohol, tabaco, drogas, desórdenes alimenticios, entre otros."
            ]
        }
    },
    "Interactúa a través de sus habilidades sociomotrices": {
        "estandares": {
            "III Ciclo": (
                "Interactúa a través de sus habilidades sociomotrices al aceptar al otro como compañero de juego "
                "y busca el consenso sobre la manera de jugar para lograr el bienestar común y muestra una actitud "
                "de respeto evitando juegos violentos y humillantes; expresa su posición ante un conflicto con intención "
                "de resolverlo y escucha la posición de sus compañeros en los diferentes tipos de juegos. Resuelve "
                "situaciones motrices a través de estrategias colectivas y participa en la construcción de reglas de juego "
                "adaptadas a la situación y al entorno, para lograr un objetivo común en la práctica de actividades lúdicas."
            ),
            "IV Ciclo": (
                "Interactúa a través de sus habilidades sociomotrices al tomar acuerdos sobre la manera de jugar "
                "y los posibles cambios o conflictos que se den y propone adaptaciones o modificaciones para favorecer "
                "la inclusión de compañeros en actividades lúdicas, aceptando al oponente como compañero de juego. "
                "Adapta la estrategia de juego anticipando las intenciones de sus compañeros y oponentes para cumplir "
                "con los objetivos planteados. Propone reglas y las modifica de acuerdo a las necesidades del contexto "
                "y los intereses del grupo en la práctica de actividades físicas."
            ),
            "V Ciclo": (
                "Interactúa a través de sus habilidades sociomotrices proactivamente con un sentido de cooperación "
                "teniendo en cuenta las adaptaciones o modificaciones propuestas por el grupo en diferentes actividades físicas. "
                "Hace uso de estrategias de cooperación y oposición seleccionando los diferentes elementos técnicos y tácticos "
                "que se pueden dar en la práctica de actividades lúdicas y predeportivas, para resolver la situación de juego "
                "que le dé un mejor resultado y que responda a las variaciones que se presentan en el entorno."
            )
        },
        "desempenos": {
            "1° de Primaria": [
                "3.1.- Asume roles y funciones de manera individual y dentro de un grupo interactuando de manera espontánea en actividades lúdicas y disfruta de la compañía de sus pares para sentirse parte del grupo.",
                "3.2.- Participa en juegos cooperativos y de oposición en parejas y pequeños grupos, aceptando al oponente como compañero de juego y las formas diferentes de jugar.",
                "3.3.- Propone soluciones a situaciones motrices y lúdicas poniéndose de acuerdo con sus pares, buscando cumplir con los objetivos que surjan y respeta las reglas de juego propuestas (por ellos mismos, por el maestro, por las condiciones del entorno) en diferentes actividades lúdicas."
            ],
            "2° de Primaria": [
                "3.1.- Participa en juegos cooperativos y de oposición en parejas y pequeños grupos, aceptando al oponente como compañero de juego y tomando consensos sobre la manera de jugar.",
                "3.2.- Muestra una actitud de respeto en la práctica de actividades lúdicas evitando juegos bruscos, amenazas, apodos y aceptando la participación de todos sus compañeros.",
                "3.3.- Resuelve de manera compartida situaciones producidas en los diferentes tipos de juegos (tradicionales, autóctonos, etc.) y adecúa las reglas para la inclusión de sus pares y el entorno con el fin de lograr un desarrollo eficaz de la actividad."
            ],
            "3° de Primaria": [
                "3.1.- Propone cambios en las condiciones de juego si fuera necesario para posibilitar la inclusión de sus pares, promoviendo el respeto y la participación y buscando un sentido de pertenencia al grupo en la práctica de diferentes actividades físicas.",
                "3.2.- Participa en juegos cooperativos y de oposición en parejas, pequeños y grandes grupos, aceptando al oponente como compañero de juego y tomando consensos sobre la manera de jugar y los posibles cambios que se den.",
                "3.3.- Asocia el resultado favorable en el juego a la necesidad de generar estrategias colectivas en las actividades lúdicas conociendo el rol de sus compañeros y el suyo propio."
            ],
            "4° de Primaria": [
                "3.1.- Propone normas y reglas en las actividades lúdicas y las modifica de acuerdo a las necesidades, el contexto y los intereses con adaptaciones o modificaciones propuestas por el grupo para favorecer la inclusión, mostrando una actitud responsable y de respeto por el cumplimiento de los acuerdos establecidos.",
                "3.2.- Propone actividades lúdicas como juegos populares y/o tradicionales con adaptaciones o modificaciones propuestas por el grupo aceptando al oponente como compañero de juego y tomando consensos sobre la manera de jugar y los posibles cambios que se den.",
                "3.3.- Propone reglas y las modifica de acuerdo a las necesidades adaptando la estrategia de juego cuando prevé las intenciones de sus compañeros de equipo y oponentes para cumplir con los objetivos planteados."
            ],
            "5° de Primaria": [
                "3.1.- Emplea la resolución reflexiva y el diálogo como herramientas para solucionar problemas o conflictos surgidos con sus pares durante la práctica de actividades lúdicas y predeportivas diversas.",
                "3.2.- Realiza actividades lúdicas interactuando con sus compañeros y oponentes como compañeros de juego respetando las diferencias personales y asumiendo roles y cambio de roles.",
                "3.3.- Propone junto a sus pares soluciones estratégicas oportunas, tomando en cuenta los aportes y las características de cada integrante del grupo al practicar juegos tradicionales, populares, autóctonos, predeportivos y en la naturaleza."
            ],
            "6° de Primaria": [
                "3.1.- Participa en actividades físicas en la naturaleza, eventos predeportivos, juegos populares, entre otros, tomando decisiones en favor del grupo, aunque vaya en contra de sus intereses personales con un sentido solidario y de cooperación.",
                "3.2.- Modifica juegos y actividades para que se adecúen a las necesidades y posibilidades del grupo y a la lógica del juego deportivo.",
                "3.3.- Discrimina y pone en práctica estrategias que se pueden dar al participar en actividades lúdicas y predeportivas y deportivas, adecuando normas de juego y la mejor solución táctica que da respuesta a las variaciones que se presentan en el entorno."
            ]
        }
    }
}


# ==============================================================================
# FUNCIONES AUXILIARES Y GENERACIÓN DE SESIÓN
# ==============================================================================

def obtener_ciclo_primaria(grado: str) -> str:
    """Devuelve el ciclo del CNEB según el grado introducido."""
    if "1°" in grado or "2°" in grado:
        return "III Ciclo"
    elif "3°" in grado or "4°" in grado:
        return "IV Ciclo"
    elif "5°" in grado or "6°" in grado:
        return "V Ciclo"
    return "III Ciclo"


def generar_sesion_aprendizaje(
    api_key: str,
    nivel: str,
    duracion: int,
    competencia: str,
    tema: str,
    materiales: str
) -> str:
    """
    Construye la solicitud estructurada y llama a la API de Gemini
    para redactar la sesión de aprendizaje del CNEB.
    """
    ciclo_actual = obtener_ciclo_primaria(nivel)
    estandar_oficial = CNEB_PRIMARIA[competencia]["estandares"][ciclo_actual]
    desempenos_oficiales = "\n".join(CNEB_PRIMARIA[competencia]["desempenos"][nivel])

    prompt_text = f"""
Actúa como un docente experto de Educación Física de nivel Primaria en Perú, especialista en el enfoque por competencias del Currículo Nacional de la Educación Básica (CNEB) de MINEDU.

DATOS OFICIALES EXTRAÍDOS DEL CNEB PRIMARIA PARA ESTA SESIÓN:
- Grado: {nivel} ({ciclo_actual})
- Duración total: {duracion} minutos
- Competencia principal: {competencia}
- Tema / Propósito motriz: {tema}
- Materiales disponibles: {materiales}
- ESTÁNDAR CNEB OFICIAL A TRANSCRIBIR: "{estandar_oficial}"
- DESEMPEÑOS CNEB OFICIALES DISPONIBLES PARA {nivel}:
{desempenos_oficiales}

ESTRUCTURA OBLIGATORIA A GENERAR (en formato Markdown):

# SESIÓN DE APRENDIZAJE N°.......
**Título:** [Crea un título motivador e innovador sobre {tema}]

## 1. DATOS INFORMATIVOS
Genera una tabla con las columnas: | IE | Docente | Grado/Sección | Fecha | Área | Duración |
*(Completa con Grado: {nivel}, Área: Educación Física, Duración: {duracion} minutos)*.

## 2. PROPÓSITOS Y EVIDENCIAS DE APRENDIZAJE
Genera una tabla con exactamente las siguientes 6 columnas:
| Competencia y Capacidades | Estándar CNEB | Desempeños Precisados | Criterios de Evaluación | Evidencia y Producto | Instrumento de Evaluación |

Condiciones para esta tabla:
- **Columna 1:** Transcribe la competencia ({competencia}) y sus capacidades oficiales.
- **Columna 2:** Transcribe EXACTAMENTE el estándar oficial proporcionado arriba ("{estandar_oficial}"), y **resalta en negrita** únicamente la frase o parte del estándar que se aplica directamente en la sesión de hoy sobre {tema}.
- **Columna 3:** Selecciona y redacta el desempeño más idóneo de la lista oficial de {nivel} proporcionada arriba, precisándolo para el tema {tema}.
- **Columna 4:** Redacta criterios de evaluación claros que contengan la estructura: **Acción + Contenido + Condición**.
- **Columna 5:** Define la Evidencia de aprendizaje (producto o actuación medible).
- **Columna 6:** Lista de cotejo.

## 3. ENFOQUE TRANSVERSAL
Genera una tabla con las columnas:
| Enfoque Transversal Priorizado | Valor | Actitud / Comportamiento Observable |

## 4. PREPARACIÓN DE LA SESIÓN
Genera una tabla con las columnas:
| ¿Qué necesitamos hacer antes de la sesión? | Recursos o Materiales a utilizar |
*(En materiales incluye: {materiales})*.

## 5. SECUENCIA DIDÁCTICA (MOMENTOS DE LA SESIÓN)
REGLA FUNDAMENTAL: Redacta todas las acciones de los momentos en **PRIMERA PERSONA** ("Recibo a mis estudiantes...", "Explico el juego...", "Organizo las cuadrillas...") y en **TIEMPO PRESENTE**.

### A) INICIO (Aprox. 20% del tiempo - {round(duracion * 0.20)} min):
- **Motivación inicial:** Una historia corta, imagen o desafío relacionado con {tema}.
- **Recojo de saberes previos:** Preguntas abiertas sobre el tema.
- **Problematización / Conflicto cognitivo:** Reto motriz o pregunta que despierte la curiosidad.
- **Propósito y organización:** Comunicar claramente qué van a aprender hoy en {nivel}.
- **Acuerdos de convivencia:** 2 a 3 acuerdos para el campo o patio.
- **Activación Corporal (Calentamiento dinámico):** Juego motivador relacionado a {tema} y movilidad articular.

### B) DESARROLLO (Aprox. 60% del tiempo - {round(duracion * 0.60)} min) - Gestión y acompañamiento:
- Diseña una secuencia metodológica de lo simple a lo complejo (progresión motriz adecuada para {nivel}).
- Incluye de 3 a 4 actividades prácticas explicadas con claridad para ejecutar en el patio (juegos tradicionales, circuitos, minitorneos o dinámicas de exploración).
- Asegúrate de que las actividades promuevan la autonomía, el pensamiento estratégico y la interacción saludable.
- Describe la estrategia de retroalimentación (feedback) que brindo como docente durante la práctica.

### C) CIERRE (Aprox. 20% del tiempo - {round(duracion * 0.20)} min):
- **Actividad de Vuelta a la Calma:** Juegos de baja intensidad, estiramientos, ejercicios de respiración o relajación.
- **Metacognición:** Preguntas de reflexión (¿Qué aprendimos hoy? ¿Cómo lo logramos? ¿En qué tuvimos dificultad? ¿Para qué nos sirve?).
- **Cuidado e Higiene Personal:** Hábitos de lavado de manos, hidratación y orden del material recolectado.

## 6. ANEXO: INSTRUMENTO DE EVALUACIÓN
Diseña una tabla de **Lista de Cotejo** con los criterios de evaluación planteados al inicio y filas con espacio para los nombres de los estudiantes.
"""

    # Inicializar cliente de Gemini con la librería google-genai
    client = genai.Client(api_key=api_key)

    # Modelos recomendados según disponibilidad
    modelos = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    
    response_text = None
    ultimo_error = None

    for model in modelos:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt_text
            )
            if response and response.text:
                response_text = response.text
                break
        except Exception as e:
            ultimo_error = str(e)

    if not response_text:
        raise RuntimeError(f"Error al conectar con la API de Gemini: {ultimo_error}")

    return response_text


def exportar_a_word_doc(contenido_markdown: str, nombre_archivo: str = "Sesion_de_Aprendizaje.doc"):
    """
    Exporta el contenido Markdown formateado en un archivo .doc (HTML estructurado con XML de MS Word)
    compatible con Microsoft Word, manteniendo tablas y formatos de texto.
    """
    # Limpieza simple de Markdown para convertir encabezados y tablas básicas a HTML
    html_body = contenido_markdown

    # Convertir títulos Markdown a HTML
    html_body = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'^### (.*?)$', r'3>\1</h3>', html_body, flags=re.MULTILINE)
    
    # Convertir negritas
    html_body = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_body)
    
    # Reemplazar saltos de línea por párrafos
    lineas = html_body.split('\n')
    html_procesado = ""
    for linea in lineas:
        if linea.strip().startswith('<h') or linea.strip().startswith('|'):
            html_procesado += linea + "\n"
        elif linea.strip():
            html_procesado += f"<p>{linea}</p>\n"

    html_header = f"""<html xmlns:o='urn:schemas-microsoft-com:office:office' 
                              xmlns:w='urn:schemas-microsoft-com:office:word' 
                              xmlns='http://www.w3.org/TR/REC-html40'>
    <head>
        <meta charset='utf-8'>
        <title>Sesión de Aprendizaje CNEB</title>
        <!--[if gte mso 9]>
        <xml>
            <w:WordDocument>
                <w:View>Print</w:View>
                <w:Zoom>100</w:Zoom>
            </w:WordDocument>
        </xml>
        <![endif]-->
        <style>
            body {{ font-family: 'Calibri', 'Segoe UI', Arial, sans-serif; font-size: 11pt; color: #333333; line-height: 1.35; }}
            h1 {{ color: #1b5e20; font-size: 16pt; text-align: center; margin-bottom: 12pt; font-weight: bold; }}
            h2 {{ color: #2e7d32; font-size: 13pt; border-bottom: 2pt solid #2e7d32; padding-bottom: 3pt; margin-top: 14pt; margin-bottom: 8pt; font-weight: bold; }}
            h3 {{ color: #1b5e20; font-size: 11pt; margin-top: 10pt; margin-bottom: 4pt; font-weight: bold; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10pt 0; }}
            table, th, td {{ border: 1px solid #777777; }}
            th {{ background-color: #2e7d32; color: #ffffff; padding: 6pt; text-align: left; font-weight: bold; font-size: 10.5pt; }}
            td {{ padding: 6pt; background-color: #ffffff; vertical-align: top; font-size: 10pt; }}
            p {{ margin-bottom: 6pt; }}
        </style>
    </head>
    <body>
        <div class="WordSection1">
            {html_procesado}
        </div>
    </body>
    </html>"""

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("\ufeff" + html_header)

    print(f"\n✅ Archivo guardado correctamente en: {nombre_archivo}")


# ==============================================================================
# EJECUCIÓN DEL PROGRAMA
# ==============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print(" GENERADOR DE SESIONES DE EDUCACIÓN FÍSICA - CNEB PRIMARIA")
    print("=" * 60)

    # 1. Parámetros de entrada (puedes cambiarlos o leerlos por teclado)
    api_key = os.getenv("GEMINI_API_KEY") or input("Ingresa tu API Key de Gemini: ").strip()
    nivel_seleccionado = "3° de Primaria"  # Opciones: 1° de Primaria ... 6° de Primaria
    duracion_minutos = 90
    competencia_seleccionada = "Se desenvuelve de manera autónoma a través de su motricidad"
    tema_sesion = "Coordinación dinámica general y equilibrio en desplazamientos"
    materiales_disp = "Conos, aros, pelotas de trapo, tizas"

    print(f"\nGenerando sesión para {nivel_seleccionado}...")
    print(f"Competencia: {competencia_seleccionada}")
    print(f"Tema: {tema_sesion}\n")

    try:
        # 2. Generar el contenido mediante la API
        resultado_markdown = generar_sesion_aprendizaje(
            api_key=api_key,
            nivel=nivel_seleccionado,
            duracion=duracion_minutos,
            competencia=competencia_seleccionada,
            tema=tema_sesion,
            materiales=materiales_disp
        )

        # 3. Mostrar el resultado en consola
        print("=" * 60)
        print("RESULTADO GENERADO (MARKDOWN):")
        print("=" * 60)
        print(resultado_markdown)

        # 4. Exportar a archivo Word (.doc)
        exportar_a_word_doc(resultado_markdown, "Sesion_Educacion_Fisica_CNEB.doc")

    except Exception as error:
        print(f"\n❌ Ocurrió un error: {error}")
