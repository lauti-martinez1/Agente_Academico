"""
TP12 — Etapa 1: Agente conversacional básico
Sistemas Inteligentes 2026

Qué hace esta etapa:
- Conecta a la API de Gemini
- Define la personalidad del agente con un system prompt
- Mantiene el historial de mensajes para recordar el contexto
- Loop de conversación por consola
"""

import os
from dotenv import load_dotenv 
from google import genai

# Carga las variables del archivo .env automáticamente
load_dotenv()

# ── Configuración ──────────────────────────────────────────────
# La API key se lee desde una variable de entorno
# Windows: $env:GEMINI_API_KEY = "sk-ant-..."
# Mac/Linux: export GEMINI_API_KEY="sk-ant-..."

MODEL = "gemini-3.1-flash-lite"  # Modelo rápido y económico

# ── System prompt: define la personalidad del agente ──────────
# PERSONALIZAR: cambiar según el dominio elegido por el grupo

SYSTEM_PROMPT = """
Sos un tutor académico inteligente llamado 'UniBot', especializado en orientar a estudiantes universitarios.
Respondés siempre en español, tu tono es profesional, motivador y claro.
Tu objetivo es ayudar al usuario a organizar sus temas de estudio, explicar conceptos técnicos complejos de forma sencilla, 
y generar cuestionarios de repaso sobre los temas que el usuario te indique.
FUERA DE DOMINIO:
- Tu objetivo es mantenerte 100% enfocado en el ámbito académico y universitario.
- Si te consultan sobre política, deportes, espectáculos o temas personales, 
  rechazá amablemente la respuesta indicando que tu propósito es exclusivamente 
  ayudar con el estudio.
"""

def crear_cliente():
    """Crea y devuelve el cliente de Gemini.
    La API key se lee desde el archivo .env o desde las variables de entorno.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "No se encontró GEMINI_API_KEY.\n"
            "Creá un archivo .env en esta carpeta con:\n"
            "GEMINI_API_KEY=sk-ant-..."
        )
    return genai.Client(api_key=api_key)


def obtener_respuesta(client, historial: list) -> str:
    """
    Envía el historial a Gemini y devuelve la respuesta como texto.
    El historial incluye todos los mensajes anteriores — así el agente recuerda el contexto.
    """
    response = client.models.generate_content(
            model=MODEL,
            contents=historial,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "max_output_tokens": 1024
            }
        )
    return response.text


def main():
    """Loop principal de conversación."""
    print("=" * 55)
    print("  Asistente Academico — Etapa 1: Conversación básica")
    print("  Escribí 'salir' para terminar.")
    print("=" * 55)

    # Inicializar cliente y historial vacío
    client = crear_cliente()
    historial = []  # Gemini espera que el rol sea 'user' o 'model' (no 'assistant')

    while True:
        # Leer input del usuario
        try:
            mensaje = input("\nVos: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n¡Hasta luego!")
            break

        if not mensaje:
            continue

        if mensaje.lower() == "salir":
            print("\nAgente: ¡Hasta luego! Fue un placer ayudarte.")
            break

        # Agregar mensaje del usuario al historial
        historial.append({
            "role": "user",
            "parts": [{"text": mensaje}]
        })

        # Obtener respuesta del agente
        print("\nAgente: ", end="", flush=True)
        respuesta = obtener_respuesta(client, historial)
        print(respuesta)

        # Agregar respuesta del agente al historial
        # IMPORTANTE: esto es lo que le da "memoria" al agente
        historial.append({
            "role": "assistant",
            "parts": [{"text": respuesta}]
        })


if __name__ == "__main__":
    main()
