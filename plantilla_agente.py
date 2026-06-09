"""
TP12 — Plantilla base para el agente de IA
Sistemas Inteligentes 2026

Integrantes del grupo:
- Lautaro Martinez
- Juan Sallenave
- Andres Quevedo
- Julian Fermentini

Dominio elegido: Asistente académico
Nombre del agente: UniBot

Instrucciones:
  1. Completar todas las secciones marcadas con [COMPLETAR]
  2. No eliminar los comentarios — son parte de la documentación
  3. Para ejecutar: python plantilla_agente.py
  4. La API key debe estar en la variable de entorno GEMINI_API_KEY
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.api_core import exceptions

# Carga las variables del archivo .env automáticamente
load_dotenv()

# ── Configuración ──────────────────────────────────────────────
MODEL = "gemini-3.1-flash-lite"  # No cambiar sin justificación

# ── [COMPLETAR] System prompt del agente ─────────────────────
# Definir:
#   - Nombre y rol del agente
#   - Tono y estilo de comunicación
#   - Dominio de especialización
#   - Comportamiento ante preguntas fuera del dominio
#   - Restricciones y reglas de comportamiento
SYSTEM_PROMPT = """
Sos UniBot, un tutor académico inteligente especializado en orientar a estudiantes universitarios.

TONO Y ESTILO:
- Respondés siempre en español.
- Tu tono es profesional, motivador, claro y paciente.
- Explicás conceptos técnicos complejos de forma sencilla, usando analogías si es necesario.
- Presentás la información organizada (listas, pasos numerados, etc.).

DOMINIO DE ESPECIALIZACIÓN:
- Organización de temas de estudio y cronogramas.
- Explicación de conceptos técnicos, científicos o académicos.
- Generación de cuestionarios de repaso sobre temas indicados.
- Técnicas de estudio y gestión de tiempo universitario.

COMPORTAMIENTO ANTE CONSULTAS FUERA DE DOMINIO:
- Tu objetivo es mantenerte 100% enfocado en el ámbito académico y universitario.
- Si te consultan sobre política, deportes, espectáculos, vida personal u otros temas ajenos al estudio, rechaza la consulta firmemente.
- Ejemplo de respuesta: "Disculpame, pero como tutor académico mi foco está puesto en ayudarte con tus estudios. Prefiero no desviarme con otros temas para ser más eficiente en nuestra sesión. ¿En qué materia o concepto técnico puedo ayudarte hoy?"

RESTRICCIONES Y SEGURIDAD:
- Nunca inventés comandos o sintaxis inexistente en programación, tampoco operaciones inexistentes en matemáticas.
- No proporciones consejos médicos, legales o financieros.
- Si el usuario te pide ayuda para realizar actividades deshonestas (como hacer trampa en un examen), rechazá la solicitud firmemente pero con educación, explicando que tu propósito es fomentar el aprendizaje auténtico.
- Mantené siempre un ambiente de respeto académico.
"""

# ══════════════════════════════════════════════════════════════
# ETAPA 1 — Funciones básicas (OBLIGATORIO)
# ══════════════════════════════════════════════════════════════

def crear_cliente():  # -> anthropic.Anthropic:
    """
    Crea el cliente de Gemini.
    [COMPLETAR Etapa 2]: agregar manejo de error si la API key no existe.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    # [COMPLETAR]: validar que api_key no sea None
    if not api_key:
        raise ValueError(
            "No se encontró GEMINI_API_KEY.\n"
            "Creá un archivo .env en esta carpeta con:\n"
            "GEMINI_API_KEY=TU_API_KEY_DE_GEMINI"
        )
    return genai.Client(api_key=api_key)



def obtener_respuesta(client, historial: list) -> str:
    """
    Envía el historial a Gemini y devuelve la respuesta.
    
    El historial es una lista de dicts con formato:
    [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
    
    [COMPLETAR Etapa 3]: agregar el parámetro tools=TOOLS si implementan herramientas.
    [COMPLETAR Etapa 2]: agregar try/except para manejar errores de API.
    """
    try:
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=1024,
            # [COMPLETAR Etapa 3]: tools=TOOLS
                  tools=[types.Tool(function_declarations=[
                types.FunctionDeclaration(
                    name=t["name"],
                    description=t["description"],
                    parameters=t["input_schema"]
                )
                for t in TOOLS
            ])]
        )
        
        response = client.models.generate_content(
            model=MODEL,
            contents=historial,
            config=config
        )

        # Lógica de Function Calling (Etapa 3) integrada aquí sin romper la firma de la función
        if response.candidates and response.candidates[0].content.parts:
            partes = response.candidates[0].content.parts
            llamadas = [p.function_call for p in partes if p.function_call]
            
            if llamadas:
                partes_respuesta = []
                for fc in llamadas:
                    nombre = fc.name
                    parametros = dict(fc.args)
                    print(f"\n[⚙️ UniBot ejecutando: {nombre}]")
                    
                    resultado_str = ejecutar_herramienta(nombre, parametros)
                    
                    partes_respuesta.append(
                        types.Part.from_function_response(
                            name=nombre,
                            response={"resultado": resultado_str}
                        )
                    )
                
                # Agregamos la llamada al historial temporal y devolvemos el resultado a Gemini
                historial.append(response.candidates[0].content)
                historial.append(types.Content(role="user", parts=partes_respuesta))
                
                respuesta_final = client.models.generate_content(
                    model=MODEL,
                    contents=historial,
                    config=config
                )
                return respuesta_final.text

        return response.text

    # Manejo de errores específicos (Etapa 2)
    except exceptions.ServiceUnavailable:
        return "[Error de conexión] No pude conectarme al servidor. Verificá tu conexión a internet e intentá de nuevo."

    except exceptions.ResourceExhausted:
        return "[Límite de uso] Se alcanzó el límite de solicitudes. Esperá unos segundos e intentá de nuevo."

    except exceptions.GoogleAPICallError as e:
        return f"[Error de API {e.status_code}] Ocurrió un problema con el servicio. Intentá de nuevo en unos momentos."

    except Exception as e:
        return f"[Error inesperado] {str(e)}"
    


# ══════════════════════════════════════════════════════════════
# ETAPA 2 — Comandos y robustez (agregar sobre Etapa 1)
# ══════════════════════════════════════════════════════════════

def mostrar_ayuda():
    """
    [COMPLETAR Etapa 2]: mostrar los comandos disponibles del agente.
    """
    #print("\n[COMPLETAR: lista de comandos]")
    # Ejemplo:
    # print("  /salir   → Termina la conversación")
    # print("  /limpiar → Reinicia el historial")
    print("\nComandos disponibles:")
    print("  /salir   → Termina la conversación")
    print("  /limpiar → Reinicia el historial")
    print("  /ayuda   → Muestra esta lista de comandos")

# ══════════════════════════════════════════════════════════════
# ETAPA 3 — Herramientas / Function Calling (agregar sobre Etapa 2)
# ══════════════════════════════════════════════════════════════

# [COMPLETAR Etapa 3]: definir las herramientas del agente
# Cada herramienta tiene: name, description, input_schema
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

# [COMPLETAR Etapa 3]: implementar las funciones de cada herramienta
# def mi_herramienta_1(param1, param2):
#     """Implementación de la herramienta 1."""
#     pass

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


TOOLS_MAP = {
    "organizar_plan_estudio": organizar_plan_estudio,
    "generar_cuestionario": generar_cuestionario,
    "verificar_sintaxis": verificar_sintaxis,
}

def ejecutar_herramienta(nombre: str, parametros: dict) -> str:
    """
    [COMPLETAR Etapa 3]: ejecutar la herramienta correspondiente y devolver resultado como string.
    
    Ejemplo:
    if nombre == "nombre_herramienta":
        resultado = mi_funcion(**parametros)
        return json.dumps(resultado)
    """
        # Gemini devuelve enteros como float (2.0 → 2)
    parametros = {
        k: int(v) if isinstance(v, float) and v.is_integer() else v
        for k, v in parametros.items()
    }
    # Gemini devuelve listas como MapComposite/RepeatedComposite, hay que convertirlas
    parametros = {
        k: list(v) if hasattr(v, '__iter__') and not isinstance(v, str) and not isinstance(v, dict) 
        else v
            for k, v in parametros.items()
    }
 
    if nombre in TOOLS_MAP:
        return TOOLS_MAP[nombre](**parametros)
    return {"error": f"Herramienta '{nombre}' no reconocida"}




# ══════════════════════════════════════════════════════════════
# ETAPA 4 — Persistencia (agregar sobre Etapa 3)
# ══════════════════════════════════════════════════════════════

def guardar_historial(historial: list, archivo: str = "historial.json"):
    """
    [COMPLETAR Etapa 4 - Opción A]: guardar el historial en un archivo JSON.
    """
    # import json
    # from datetime import datetime
    # [COMPLETAR]: guardar historial con fecha/hora
    pass


def cargar_historial(archivo: str = "historial.json") -> list:
    """
    [COMPLETAR Etapa 4 - Opción A]: cargar el historial desde un archivo JSON.
    Devuelve lista vacía si el archivo no existe.
    """
    # [COMPLETAR]: cargar y devolver historial
    return []


# ══════════════════════════════════════════════════════════════
# LOOP PRINCIPAL
# ══════════════════════════════════════════════════════════════

def main():
    print("=" * 55)
    print(f"  Agente IA — UniBot")
    print(f"  Dominio: Asistente académico")
    print("  Escribí /ayuda para ver los comandos.")
    print("=" * 55)

    client = crear_cliente()
    historial = []

    # [COMPLETAR]: saludo inicial del agente
    print("\nUniBot: ¡Hola! Soy UniBot, tu tutor académico. Puedo ayudarte a organizar")
    print("        tus temas de estudio, armar cuestionarios de repaso y validar")
    print("        sintaxis de programación. ¿Por dónde empezamos hoy?")

    while True:
        try:
            mensaje = input("\nVos: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nUniBot: ¡Hasta luego! Fue un placer ayudarte.")
            break

        if not mensaje:
            continue

        # [COMPLETAR Etapa 2]: manejo de comandos especiales
        # if mensaje.lower() == "/salir":
        #     print("[COMPLETAR: despedida]")
        #     break
        # if mensaje.lower() == "/limpiar":
        #     historial = []
        #     continue
        # if mensaje.lower() == "/ayuda":
        #     mostrar_ayuda()
        #     continue


        if mensaje.lower() == "/salir":
            print("\nUniBot: ¡Hasta pronto! Segui aprendiendo. 📚")
            break
 
        if mensaje.lower() == "/limpiar":
            # Para limpiar el historial en Gemini, simplemente creamos un chat nuevo
            historial = []
            print("\n[Sistema] Historial limpiado. Comenzamos de nuevo.")
            print("\nUniBot: ¡Claro! Empecemos de cero. ¿Qué te interesa aprender hoy?")
            continue
 
        if mensaje.lower() == "/ayuda":
            mostrar_ayuda()
            print("\n📋 Herramientas disponibles (se activan solas según tu consulta):")
            print("  • Organizar estudio: 'Tengo 4 días para estudiar herencia y polimorfismo'")
            print("  • Cuestionarios: 'Armame 5 preguntas difíciles sobre bucles en Java'")
            print("  • Validar código: '¿Cómo se hace un for en Python?'")
            continue


        # Agregar mensaje al historial (Formato Gemini)
        historial.append(
            types.Content(
                role="user",
                parts=[types.Part(text=mensaje)]
            )
        )

        # Obtener y mostrar respuesta
        print(f"\nUniBot: ", end="", flush=True)
        respuesta = obtener_respuesta(client, historial)
        print(respuesta)

        # Agregar mensaje al historial (Formato Gemini)
        if not respuesta.startswith("[Error"):
            historial.append(
                types.Content(
                    role="model",
                    parts=[types.Part(text=respuesta)]
                )
            )
        # [COMPLETAR Etapa 4]: guardar_historial(historial)


if __name__ == "__main__":
    main()