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
Sos Olivia, una asistente gastronómica virtual especializada en cocina mediterránea.
Trabajás para un restaurante llamado "Mar Nostrum" en Mendoza, Argentina.

PERSONALIDAD:
- Respondés siempre en español, con un tono cálido, amigable y entusiasta
- Usás lenguaje accesible, sin tecnicismos innecesarios
- Cuando das una receta, la presentás de forma ordenada con ingredientes y pasos numerados

DOMINIO:
- Tu especialidad son las recetas mediterráneas, los ingredientes, las técnicas culinarias
- También podés ayudar con maridajes de vinos y platos

FUERA DE DOMINIO:
- Si te preguntan algo que no tenga relación con gastronomía, cocina o alimentación,
  respondés amablemente que tu especialidad es la cocina mediterránea y ofrecés
  redirigir la conversación a ese tema.
- Ejemplo: si preguntan sobre política, matemáticas o tecnología, decís algo como:
  "Eso está fuera de mi área, pero si querés te cuento sobre gastronomía mediterránea..."

RESTRICCIONES:
- Nunca inventés ingredientes que puedan ser peligrosos para la salud
- Si una persona menciona alergias, siempre advertís sobre los ingredientes relevantes
- No dás consejos médicos aunque estén relacionados con la alimentación
"""

# ── Comandos disponibles ───────────────────────────────────────
COMANDOS = {
    "/salir":   "Termina la conversación",
    "/limpiar": "Reinicia el historial — el agente olvida la conversación actual",
    "/ayuda":   "Muestra esta lista de comandos",
}


def crear_cliente():
    """Crea el cliente de Anthropic con validación de API key.
    La API key se lee desde el archivo .env o desde las variables de entorno.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "No se encontró GEMINI_API_KEY.\n"
            "Creá un archivo .env en esta carpeta con:\n"
            "GEMINI_API_KEY=sk-ant-..."
        )
    return anthropic.Anthropic(api_key=api_key)


def obtener_respuesta(client, historial: list) -> str:
    """
    Llama a la API con manejo de errores.
    Si la API falla, devuelve un mensaje de error amigable en lugar de cerrarse.
    """
    try:
        respuesta = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=historial
        )
        return respuesta.content[0].text

    except anthropic.APIConnectionError:
        return "[Error de conexión] No pude conectarme al servidor. Verificá tu conexión a internet e intentá de nuevo."

    except anthropic.RateLimitError:
        return "[Límite de uso] Se alcanzó el límite de solicitudes. Esperá unos segundos e intentá de nuevo."

    except anthropic.APIStatusError as e:
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
    print("\nOlivia: ¡Hola! Soy Olivia, tu asistente gastronómica especializada")
    print("        en cocina mediterránea. ¿En qué puedo ayudarte hoy?")

    while True:
        try:
            mensaje = input("\nVos: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nOlivia: ¡Hasta luego! Fue un placer ayudarte.")
            break

        if not mensaje:
            continue

        # ── Manejo de comandos especiales ─────────────────────
        if mensaje.lower() == "/salir":
            print("\nOlivia: ¡Hasta pronto! Que disfrutes cocinando. 🍋")
            break

        if mensaje.lower() == "/limpiar":
            historial = []
            print("\n[Sistema] Historial limpiado. Comenzamos de nuevo.")
            print("Olivia: ¡Claro! Empecemos de cero. ¿Qué receta te interesa hoy?")
            continue

        if mensaje.lower() == "/ayuda":
            mostrar_ayuda()
            continue

        # ── Conversación normal ────────────────────────────────
        historial.append({"role": "user", "content": mensaje})

        print("\nOlivia: ", end="", flush=True)
        respuesta = obtener_respuesta(client, historial)
        print(respuesta)

        # Solo agregamos al historial si fue una respuesta real (no error de API)
        if not respuesta.startswith("[Error"):
            historial.append({"role": "assistant", "content": respuesta})


if __name__ == "__main__":
    main()
