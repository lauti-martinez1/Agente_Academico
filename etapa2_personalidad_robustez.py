"""
TP12 — Etapa 2: Personalidad, contexto y robustez
Sistemas Inteligentes 2026

Qué agrega esta etapa sobre la Etapa 1:
- System prompt más elaborado con restricciones de dominio
- El agente rechaza educadamente consultas fuera del dominio
- Manejo de errores de la API (no se cierra abruptamente)
- Comandos especiales: /salir y /limpiar
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.api_core import exceptions

# Carga las variables del archivo .env automáticamente
load_dotenv()

MODEL = "gemini-3.1-flash-lite"

# ── System prompt elaborado ────────────────────────────────────
# PERSONALIZAR: adaptar al dominio del grupo
# Notar los elementos clave:
#   1. Nombre y rol específico
#   2. Tono y estilo de comunicación
#   3. Restricción de dominio explícita
#   4. Comportamiento ante preguntas fuera del dominio
#   5. Restricciones de seguridad/ética

SYSTEM_PROMPT = """
Sos UniBot, un tutor académico inteligente especializado en orientar a estudiantes universitarios.

PERSONALIDAD:
- Respondés siempre en español. Tu tono es profesional, motivador, claro y paciente.
- Usás lenguaje accesible acorde al nivel del usuario, sin usar tecnicismos innecesarios
- Cuando das una respuesta, la presentás de forma ordenada

DOMINIO:
- Tu especialidad son la programacion, las matematicas y tecnologia en general
- También podés ayudar con temas relacionados a otras areas de la ciencia como fisica y quimica
- Generación de cuestionarios de repaso sobre temas indicados.
- Organización de temas de estudio

FUERA DE DOMINIO:
- Tu objetivo es mantenerte 100% enfocado en el ámbito académico y universitario.
- Si te preguntan algo que no tenga relación con lo academico,
  respondés amablemente que tu especialidad es la educacion academica orientada a las ciencias y ofrecés
  redirigir la conversación a ese tema.
- Ejemplo: si preguntan sobre política, recetas o arte, decís algo como:
  "Eso está fuera de mi área, pero si querés te cuento sobre los ultimos avances en inteligencia artificial..."

RESTRICCIONES:
- Nunca inventés comandos o sintaxis inexistente en programacion, tampoco operaciones inexistentes en matemicas
- Si una persona menciona dificultades para entender, das ejemplos ilustrativos
- Si el usuario te pide ayuda para realizar actividades deshonestas, rechazá la solicitud firmemente pero con educación, explicando que tu propósito es fomentar el aprendizaje
"""


# ── Comandos disponibles ───────────────────────────────────────
COMANDOS = {
    "/salir":   "Termina la conversación",
    "/limpiar": "Reinicia el historial — el agente olvida la conversación actual",
    "/ayuda":   "Muestra esta lista de comandos",
}


def crear_cliente():
    """Crea el cliente de Gemini con validación de API key.
    La API key se lee desde el archivo .env o desde las variables de entorno.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "No se encontró GEMINI_API_KEY.\n"
            "Creá un archivo .env en esta carpeta con:\n"
            "GEMINI_API_KEY=TU_API_KEY_DE_GEMINI"
        )
    return genai.Client(api_key=api_key)


def obtener_respuesta(client, historial: list) -> str:
    """
    Llama a la API con manejo de errores.
    Si la API falla, devuelve un mensaje de error amigable en lugar de cerrarse.
    """
    try:
        respuesta = client.models.generate_content(
            model=MODEL,
            contents=historial,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=1024
            )
        )
        return respuesta.text

    except exceptions.ServiceUnavailable:
        return "[Error de conexión] No pude conectarme al servidor. Verificá tu conexión a internet e intentá de nuevo."

    except exceptions.ResourceExhausted:
        return "[Límite de uso] Se alcanzó el límite de solicitudes. Esperá unos segundos e intentá de nuevo."

    except exceptions.GoogleAPICallError as e:
        return f"[Error de API {e.status_code}] Ocurrió un problema con el servicio. Intentá de nuevo en unos momentos."

    except Exception as e:
        return f"[Error inesperado] {str(e)}"


def mostrar_ayuda():
    """Muestra los comandos disponibles."""
    print("\n📋 Comandos disponibles:")
    for cmd, desc in COMANDOS.items():
        print(f"  {cmd:<12} → {desc}")


def main():
    print("=" * 60)
    print("  Agente IA — Etapa 2: Personalidad y robustez")
    print("  Escribí /ayuda para ver los comandos disponibles.")
    print("=" * 60)

    client = crear_cliente()
    historial = []

    # Saludo inicial del agente
    print("\nUniBot: ¡Hola! Soy Unibot, tu asistente academico especializado")
    print("        en programacion y matematicas. ¿En qué puedo ayudarte hoy?")

    while True:
        try:
            mensaje = input("\nVos: ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\nUniBot: ¡Hasta luego! Fue un placer ayudarte.")
            break

        if not mensaje:
            continue

        # ── Manejo de comandos especiales ─────────────────────
        if mensaje.lower() == "/salir":
            print("\nUniBot: ¡Hasta pronto! Segui aprendiendo.")
            break

        if mensaje.lower() == "/limpiar":
            historial = []
            print("\n[Sistema] Historial limpiado. Comenzamos de nuevo.")
            print("nUniBot: ¡Claro! Empecemos de cero. ¿Qué te interesa aprender hoy?")
            continue

        if mensaje.lower() == "/ayuda":
            mostrar_ayuda()
            continue

        # ── Conversación normal ────────────────────────────────
        
        historial.append(
            types.Content(
                role="user",
                parts=[types.Part(text=mensaje)],
            )
        )

        print("\nUniBot: ", end="", flush=True)
        
        respuesta = obtener_respuesta(client, historial)

        print(respuesta)

        # Solo agregamos al historial si fue una respuesta real (no error de API)
        if not respuesta.startswith("[Error"):
            historial.append(
                types.Content(
                    role="model",
                    parts=[types.Part(text=respuesta)],
                )
            )

if __name__ == "__main__":
    main()
