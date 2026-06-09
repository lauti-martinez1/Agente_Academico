"""
TP12 — Etapa 3: Herramientas externas (Function Calling)
Sistemas Inteligentes 2026

Qué agrega esta etapa sobre la Etapa 2:
- Definición de herramientas (tools) que el modelo puede invocar
- El modelo decide autónomamente cuándo llamar cada herramienta
- Las herramientas ejecutan código Python real
- El resultado se integra naturalmente en la respuesta del agente

DOMINIO EJEMPLO: Asistente gastronómico con 3 herramientas:
  1. calcular_porciones(receta, personas_original, personas_nueva)
  2. buscar_info_ingrediente(ingrediente)
  3. sugerir_maridaje(plato)
"""

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
# Carga las variables del archivo .env automáticamente
load_dotenv()

MODEL = "gemini-3.1-flash-lite"

SYSTEM_PROMPT = """
Sos UniBot, un tutor académico inteligente especializado en orientar a estudiantes universitarios.
Respondés siempre en español, con un tono profesional, claro y motivador.
Tu especialidad son la programación, las matemáticas y la organización del estudio.
Tenés acceso a herramientas externas para organizar planes de estudio y buscar informacion de otras fuentes confiables.
 Usalas de forma autónoma cuando la consulta del usuario lo requiera, sin que tengan que pedírtelo explícitamente.
"""

# ══════════════════════════════════════════════════════════════
# DEFINICIÓN DE HERRAMIENTAS
# Cada herramienta tiene: nombre, descripción y esquema de parámetros
# El modelo lee estas definiciones para saber cuándo y cómo usarlas
# ══════════════════════════════════════════════════════════════
TOOLS = [
    {
        "name": "organizar_plan_estudio",
        "description": (
            "Organiza una lista de temas de estudio distribuyéndolos equitativamente en los días disponibles. "
            "Útil cuando el alumno necesita planificar su tiempo de estudio antes de un examen."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "temas": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista de temas académicos a estudiar, ej: ['Polimorfismo', 'Herencia', 'Abstracción']"
                },
                "dias_disponibles": {
                    "type": "integer",
                    "description": "Cantidad de días que el usuario tiene disponibles para estudiar los temas"
                }
            },
            "required": ["temas", "dias_disponibles"]
        }
    },
    {
        "name": "generar_cuestionario",
        "description": (
            "Genera parámetros para buscar o crear un cuestionario de repaso sobre un tema específico. "
            "Usar cuando el usuario pide practicar, ponerse a prueba o repasar un concepto."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tema": {
                    "type": "string",
                    "description": "El tema académico a evaluar, ej: 'Leyes de Newton' o 'Bucles en Java'"
                },
                "dificultad": {
                    "type": "string",
                    "description": "Nivel de dificultad del cuestionario, ej: 'básico', 'intermedio', 'avanzado'"
                },
                "cantidad_preguntas": {
                    "type": "integer",
                    "description": "Número total de preguntas que debe tener el cuestionario"
                }
            },
            "required": ["tema", "dificultad", "cantidad_preguntas"]
        }
    },
    {
        "name": "verificar_sintaxis",
        "description": (
            "Verifica la existencia y sintaxis correcta de un concepto o comando de programación. "
            "Usar SIEMPRE antes de dar ejemplos de código para evitar inventar sintaxis inexistente."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "lenguaje": {
                    "type": "string",
                    "description": "Lenguaje de programación a consultar, ej: 'Java', 'Python', 'C++'"
                },
                "concepto": {
                    "type": "string",
                    "description": "El concepto, función o comando a buscar, ej: 'System.out.println', 'list comprehension'"
                }
            },
            "required": ["lenguaje", "concepto"]
        }
    }
]

# ══════════════════════════════════════════════════════════════
# IMPLEMENTACIÓN DE LAS HERRAMIENTAS
# Estas son las funciones Python que se ejecutan cuando el modelo
# decide invocar una herramienta. Pueden hacer cálculos, llamar
# APIs externas, consultar bases de datos, etc.
# ══════════════════════════════════════════════════════════════
def organizar_plan_estudio(temas: list, dias_disponibles: int) -> dict:
    """
    Organiza una lista de temas distribuyéndolos en los días disponibles.
    En un caso real, esto podría integrarse con Google Calendar o Notion.
    """
    if dias_disponibles <= 0:
        return {"error": "La cantidad de días debe ser mayor a 0."}

    total_temas = len(temas)
    temas_por_dia = total_temas // dias_disponibles
    sobrante = total_temas % dias_disponibles

    plan = {}
    indice_tema = 0

    for dia in range(1, dias_disponibles + 1):
        cantidad_hoy = temas_por_dia + (1 if dia <= sobrante else 0)
        plan[f"Dia {dia}"] = temas[indice_tema : indice_tema + cantidad_hoy]
        indice_tema += cantidad_hoy

    return {
        "dias_disponibles": dias_disponibles,
        "total_temas": total_temas,
        "temas_por_dia_promedio": temas_por_dia,
        "plan_detallado": plan
    }


def generar_cuestionario(tema: str, dificultad: str, cantidad_preguntas: int) -> dict:
    """
    Simula la búsqueda de contexto duro para generar un cuestionario.
    En la vida real, acá harías un RAG (buscar en los PDFs de la materia).
    """
    base_conocimiento = {
        "polimorfismo": "Permite que objetos de diferentes clases respondan al mismo método o mensaje.",
        "herencia": "Mecanismo por el cual una clase deriva de otra, heredando sus atributos y métodos.",
        "bucles": "Estructuras (for, while) que permiten repetir bloques de código hasta cumplir una condición.",
        "derivadas": "Representa la tasa de cambio instantánea de una función."
    }

    tema_lower = tema.lower()
    contexto_encontrado = "No hay contexto duro en la base de datos. Basar las preguntas en conocimiento general validado."

    for key, value in base_conocimiento.items():
        if key in tema_lower or tema_lower in key:
            contexto_encontrado = value
            break

    return {
        "tema_solicitado": tema,
        "dificultad": dificultad,
        "cantidad_preguntas": cantidad_preguntas,
        "contexto_extraido": contexto_encontrado,
        "instruccion_oculta": f"Redacta {cantidad_preguntas} preguntas ({dificultad}) sobre {tema}. Usa el contexto provisto de ser posible."
    }


def verificar_sintaxis(lenguaje: str, concepto: str) -> dict:
    """
    Valida la sintaxis en una base de datos estricta para cumplir la regla
    del System Prompt: nunca inventar comandos.
    """
    base_datos = {
        "python": {
            "for": "for elemento in iterable:",
            "print": "print('Hola Mundo')",
            "list comprehension": "[x for x in lista if condicion]"
        },
        "java": {
            "print": "System.out.println('Hola Mundo');",
            "for": "for (int i = 0; i < limite; i++) { }",
            "clase": "public class NombreClase { }"
        }
    }

    lenguaje_lower = lenguaje.lower()
    concepto_lower = concepto.lower()

    if lenguaje_lower in base_datos:
        for key, sintaxis in base_datos[lenguaje_lower].items():
            if key in concepto_lower or concepto_lower in key:
                return {
                    "encontrado": True,
                    "lenguaje": lenguaje,
                    "concepto_buscado": concepto,
                    "sintaxis_oficial": sintaxis,
                    "estado": "Aprobado para usar en la respuesta."
                }

    return {
        "encontrado": False,
        "lenguaje": lenguaje,
        "concepto_buscado": concepto,
        "estado": "Rechazado",
        "mensaje_al_modelo": f"No se encontró sintaxis verificada para '{concepto}' en {lenguaje}. Informale al alumno que no tenés el dato exacto para no inventar."
    }

# ══════════════════════════════════════════════════════════════
# MOTOR DE EJECUCIÓN DE HERRAMIENTAS
# ══════════════════════════════════════════════════════════════
TOOLS_MAP = {
    "organizar_plan_estudio": organizar_plan_estudio,
    "generar_cuestionario": generar_cuestionario,
    "verificar_sintaxis": verificar_sintaxis,
}

def ejecutar_herramienta(nombre: str, parametros: dict) -> dict:
    # Gemini devuelve enteros como float (2.0 → 2)
    parametros = {
        k: int(v) if isinstance(v, float) and v.is_integer() else v
        for k, v in parametros.items()
    }
    # Gemini devuelve listas como MapComposite/RepeatedComposite, hay que convertirlas
    parametros = {
        k: list(v) if hasattr(v, '__iter__') and not isinstance(v, str) and not isinstance(v, dict) else v
        for k, v in parametros.items()
    }

    if nombre in TOOLS_MAP:
        return TOOLS_MAP[nombre](**parametros)
    return {"error": f"Herramienta '{nombre}' no reconocida"}

def procesar_respuesta(chat, mensaje: str) -> str:
    """
    Manejo de Function Calling para Gemini.
    1. Manda el mensaje al chat.
    2. Mientras el modelo devuelva function_calls, los ejecuta y devuelve resultados.
    3. Retorna el texto final cuando el modelo no pide más herramientas.
    """
    respuesta = chat.send_message(mensaje)

    # Gemini puede pedir múltiples herramientas en una sola respuesta
    while True:
        # Recolectamos todos los function_calls del turno actual
        llamadas = []
        for parte in respuesta.candidates[0].content.parts:
            if parte.function_call.name:  # si tiene nombre, es un function_call real
                llamadas.append(parte.function_call)

        if not llamadas:
            break  # No hay más herramientas — salimos del loop

        # Ejecutamos cada herramienta y armamos las respuestas
        partes_respuesta = []
        for fc in llamadas:
            nombre = fc.name
            parametros = dict(fc.args)
            print(f"\n[⚙️  UniBot ejecutando: {nombre}]")

            resultado = ejecutar_herramienta(nombre, parametros)

            partes_respuesta.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=nombre,
                        response={"resultado": json.dumps(resultado, ensure_ascii=False)}
                    )
                )
            )

        # Devolvemos todos los resultados al modelo de una sola vez
        respuesta = chat.send_message(partes_respuesta)

    return respuesta.text

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  Agente IA — Etapa 3: Herramientas (Function Calling)")
    print("  Comandos: /salir, /limpiar, /ayuda")
    print("  Herramientas: organizar plan, generar cuestionario, verificar sintaxis")
    print("=" * 70)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("No se encontró GEMINI_API_KEY en las variables de entorno.")
    
    # Inicializamos el modelo de Google
    genai.configure(api_key=api_key)

    modelo = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=SYSTEM_PROMPT,
        tools=[organizar_plan_estudio, generar_cuestionario, verificar_sintaxis]
    )

    
    # Arrancamos una sesión de chat (esto ya maneja el historial internamente)
    chat = modelo.start_chat()

    print("\nUniBot: ¡Hola! Soy UniBot, tu tutor académico. Puedo ayudarte a organizar")
    print("        tus temas de estudio, armar cuestionarios de repaso y validar")
    print("        sintaxis de programación. ¿Por dónde empezamos hoy?")

    while True:
        try:
            mensaje = input("\nVos: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nUniBot: ¡Éxitos con el estudio! Nos vemos la próxima.")
            break

        if not mensaje:
            continue

        if mensaje.lower() == "/salir":
            print("\nUniBot: ¡Hasta pronto! Que rindas excelente. 📚")
            break

        if mensaje.lower() == "/limpiar":
            # Para limpiar el historial en Gemini, simplemente creamos un chat nuevo
            chat = modelo.start_chat()
            print("\n[Sistema] Historial limpiado.")
            continue

        if mensaje.lower() == "/ayuda":
            print("\n📋 Herramientas disponibles (se activan solas según tu consulta):")
            print("  • Organizar estudio: 'Tengo 4 días para estudiar herencia y polimorfismo'")
            print("  • Cuestionarios: 'Armame 5 preguntas difíciles sobre bucles en Java'")
            print("  • Validar código: '¿Cómo se hace un for en Python?'")
            continue

        try:
            print("\nUniBot: ", end="", flush=True)
            # Pasamos el objeto 'chat' en lugar de un 'historial' de lista
            texto_final = procesar_respuesta(chat, mensaje)
            print(texto_final)

        except Exception as e:
            print(f"\n[Error de la API] {e}")


if __name__ == "__main__":
    main()