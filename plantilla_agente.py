"""
TP12 — Plantilla base para el agente de IA
Sistemas Inteligentes 2026

Integrantes del grupo:
- Lautaro Martinez
- Juan Sallenave
- Andres Quevedo
- Julian Fermentini

Dominio elegido: [COMPLETAR — ej: asistente académico, gastronómico, etc.]
Nombre del agente: [COMPLETAR]

Instrucciones:
  1. Completar todas las secciones marcadas con [COMPLETAR]
  2. No eliminar los comentarios — son parte de la documentación
  3. Para ejecutar: python plantilla_agente.py
  4. La API key debe estar en la variable de entorno GEMINI_API_KEY
"""

import os
from dotenv import load_dotenv
from google import genai

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
Sos un tutor académico inteligente llamado 'UniBot', especializado en orientar a estudiantes universitarios.
Respondés siempre en español, tu tono es profesional, motivador y claro.
Tu objetivo es ayudar al usuario a organizar sus temas de estudio, explicar conceptos técnicos complejos de forma sencilla, 
y generar cuestionarios de repaso sobre los temas que el usuario te indique.
"""

# ══════════════════════════════════════════════════════════════
# ETAPA 1 — Funciones básicas (OBLIGATORIO)
# ══════════════════════════════════════════════════════════════

def crear_cliente():  # -> anthropic.Anthropic:
    """
    Crea el cliente de Anthropic.
    [COMPLETAR Etapa 2]: agregar manejo de error si la API key no existe.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    # [COMPLETAR]: validar que api_key no sea None
    if not api_key:
        raise ValueError(
            "No se encontró GEMINI_API_KEY.\n"
            "Creá un archivo .env en esta carpeta con:\n"
            "GEMINI_API_KEY=sk-ant-..."
        )
    return genai.Client(api_key=api_key)


def obtener_respuesta(client, historial: list) -> str:
    """
    Envía el historial a Claude y devuelve la respuesta.
    
    El historial es una lista de dicts con formato:
    [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
    
    [COMPLETAR Etapa 3]: agregar el parámetro tools=TOOLS si implementan herramientas.
    [COMPLETAR Etapa 2]: agregar try/except para manejar errores de API.
    """
    response = client.models.generate_content(
        model=MODEL,
        contents=historial,
        config={
            "system_instruction": SYSTEM_PROMPT,
            "max_output_tokens": 1024
        }
        # [COMPLETAR Etapa 3]: tools=TOOLS
    )
    return response.text


# ══════════════════════════════════════════════════════════════
# ETAPA 2 — Comandos y robustez (agregar sobre Etapa 1)
# ══════════════════════════════════════════════════════════════

def mostrar_ayuda():
    """
    [COMPLETAR Etapa 2]: mostrar los comandos disponibles del agente.
    """
    print("\n[COMPLETAR: lista de comandos]")
    # Ejemplo:
    # print("  /salir   → Termina la conversación")
    # print("  /limpiar → Reinicia el historial")


# ══════════════════════════════════════════════════════════════
# ETAPA 3 — Herramientas / Function Calling (agregar sobre Etapa 2)
# ══════════════════════════════════════════════════════════════

# [COMPLETAR Etapa 3]: definir las herramientas del agente
# Cada herramienta tiene: name, description, input_schema
TOOLS = [
    # {
    #     "name": "nombre_herramienta",
    #     "description": "Descripción de para qué sirve y cuándo usarla",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "parametro1": {"type": "string", "description": "..."},
    #             "parametro2": {"type": "number", "description": "..."},
    #         },
    #         "required": ["parametro1"]
    #     }
    # },
]


def ejecutar_herramienta(nombre: str, parametros: dict) -> str:
    """
    [COMPLETAR Etapa 3]: ejecutar la herramienta correspondiente y devolver resultado como string.
    
    Ejemplo:
    if nombre == "nombre_herramienta":
        resultado = mi_funcion(**parametros)
        return json.dumps(resultado)
    """
    return f"[COMPLETAR: implementar ejecución de herramienta '{nombre}']"


# [COMPLETAR Etapa 3]: implementar las funciones de cada herramienta
# def mi_herramienta_1(param1, param2):
#     """Implementación de la herramienta 1."""
#     pass


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
    print(f"  Agente IA — [COMPLETAR: nombre del agente]")
    print(f"  Dominio: [COMPLETAR: dominio]")
    print("  Escribí /ayuda para ver los comandos.")
    print("=" * 55)

    client = crear_cliente()
    historial = []

    # [COMPLETAR]: saludo inicial del agente
    print("\n[COMPLETAR: saludo inicial del agente]")

    while True:
        try:
            mensaje = input("\nVos: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[COMPLETAR: mensaje de despedida]")
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

        # Agregar mensaje al historial
        historial.append({"role": "user", "content": mensaje})

        # Obtener y mostrar respuesta
        print(f"\n[COMPLETAR: nombre del agente]: ", end="", flush=True)
        respuesta = obtener_respuesta(client, historial)
        print(respuesta)

        # Agregar respuesta al historial
        historial.append({"role": "assistant", "content": respuesta})

        # [COMPLETAR Etapa 4]: guardar_historial(historial)


if __name__ == "__main__":
    main()
