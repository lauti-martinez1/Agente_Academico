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
from google import genai

# Carga las variables del archivo .env automáticamente
load_dotenv()

MODEL = "gemini-3.1-flash-lite"

SYSTEM_PROMPT = """
Sos Olivia, una asistente gastronómica especializada en cocina mediterránea.
Respondés siempre en español, con tono cálido y profesional.
Tu especialidad son las recetas mediterráneas, ingredientes y maridajes.
Tenés acceso a herramientas para calcular porciones, obtener información
sobre ingredientes y sugerir maridajes de vinos. Usalas cuando el usuario
lo necesite sin que tengan que pedirlo explícitamente.
"""

# ══════════════════════════════════════════════════════════════
# DEFINICIÓN DE HERRAMIENTAS
# Cada herramienta tiene: nombre, descripción y esquema de parámetros
# El modelo lee estas definiciones para saber cuándo y cómo usarlas
# ══════════════════════════════════════════════════════════════

TOOLS = [
    {
        "name": "calcular_porciones",
        "description": (
            "Ajusta las cantidades de una receta para una cantidad diferente de personas. "
            "Útil cuando el usuario quiere adaptar una receta para más o menos comensales."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ingredientes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista de ingredientes con cantidades, ej: ['200g harina', '2 huevos']"
                },
                "porciones_original": {
                    "type": "integer",
                    "description": "Cantidad de personas para las que estaba pensada la receta original"
                },
                "porciones_nueva": {
                    "type": "integer",
                    "description": "Cantidad de personas para las que se quiere adaptar"
                }
            },
            "required": ["ingredientes", "porciones_original", "porciones_nueva"]
        }
    },
    {
        "name": "buscar_info_ingrediente",
        "description": (
            "Devuelve información nutricional y culinaria básica sobre un ingrediente. "
            "Usar cuando el usuario pregunta sobre propiedades, usos o sustitutos de un ingrediente."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ingrediente": {
                    "type": "string",
                    "description": "Nombre del ingrediente a consultar, ej: 'aceite de oliva'"
                }
            },
            "required": ["ingrediente"]
        }
    },
    {
        "name": "sugerir_maridaje",
        "description": (
            "Sugiere vinos o bebidas que maridan bien con un plato específico. "
            "Usar cuando el usuario pregunta qué vino tomar con una comida."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "plato": {
                    "type": "string",
                    "description": "Nombre del plato para el que se busca maridaje, ej: 'paella de mariscos'"
                }
            },
            "required": ["plato"]
        }
    }
]


# ══════════════════════════════════════════════════════════════
# IMPLEMENTACIÓN DE LAS HERRAMIENTAS
# Estas son las funciones Python que se ejecutan cuando el modelo
# decide invocar una herramienta. Pueden hacer cálculos, llamar
# APIs externas, consultar bases de datos, etc.
# ══════════════════════════════════════════════════════════════

def calcular_porciones(ingredientes: list, porciones_original: int, porciones_nueva: int) -> dict:
    """
    Ajusta proporciones de una receta.
    En un caso real, esto podría parsear unidades de medida más sofisticadas.
    """
    factor = porciones_nueva / porciones_original
    ingredientes_ajustados = []

    for ing in ingredientes:
        # Intentar multiplicar números en el ingrediente
        partes = ing.split()
        nueva_linea = []
        for parte in partes:
            try:
                numero = float(parte.replace(',', '.'))
                nueva_linea.append(str(round(numero * factor, 1)))
            except ValueError:
                nueva_linea.append(parte)
        ingredientes_ajustados.append(" ".join(nueva_linea))

    return {
        "porciones_original": porciones_original,
        "porciones_nueva": porciones_nueva,
        "factor": round(factor, 2),
        "ingredientes_ajustados": ingredientes_ajustados
    }


def buscar_info_ingrediente(ingrediente: str) -> dict:
    """
    Base de datos de ingredientes (simulada).
    En un caso real, esto podría llamar a una API de nutrición.
    """
    base_datos = {
        "aceite de oliva": {
            "tipo": "grasa vegetal",
            "origen": "Mediterráneo",
            "usos": "Cocinar, aliñar, conservar",
            "temperatura_coccion": "Hasta 180°C (virgen extra), 210°C (refinado)",
            "beneficios": "Rico en grasas monoinsaturadas y antioxidantes",
            "sustituto": "Aceite de girasol o manteca para cocinar"
        },
        "tomate": {
            "tipo": "fruta/hortaliza",
            "origen": "América del Sur",
            "usos": "Salsas, ensaladas, sopas",
            "temporada": "Verano (mejor sabor)",
            "beneficios": "Licopeno, vitamina C",
            "sustituto": "Tomates enlatados fuera de temporada"
        },
        "ajo": {
            "tipo": "bulbo",
            "origen": "Asia Central",
            "usos": "Aromatizar, base de salsas",
            "intensidad": "Crudo es más fuerte, cocido más suave",
            "beneficios": "Propiedades antimicrobianas, alicina",
            "sustituto": "Ajo en polvo (1/4 cucharadita por diente)"
        },
    }

    ing_lower = ingrediente.lower()
    for key in base_datos:
        if key in ing_lower or ing_lower in key:
            return {"encontrado": True, "ingrediente": key, "info": base_datos[key]}

    return {
        "encontrado": False,
        "ingrediente": ingrediente,
        "mensaje": f"No tengo información específica sobre '{ingrediente}' en mi base de datos, pero puedo ayudarte con otros ingredientes mediterráneos."
    }


def sugerir_maridaje(plato: str) -> dict:
    """
    Sugerencias de maridaje según el tipo de plato.
    En un caso real, podría integrarse con una API de vinos.
    """
    plato_lower = plato.lower()

    if any(p in plato_lower for p in ["mariscos", "pescado", "pulpo", "calamar"]):
        return {
            "plato": plato,
            "vinos_blancos": ["Albariño", "Verdejo", "Chardonnay sin roble"],
            "vinos_rosados": ["Rosado de Provence"],
            "temperatura": "8-10°C",
            "nota": "Los vinos blancos secos y frescos equilibran la salinidad del mar"
        }
    elif any(p in plato_lower for p in ["carne", "cordero", "ternera", "pollo"]):
        return {
            "plato": plato,
            "vinos_tintos": ["Malbec", "Tempranillo", "Sangiovese"],
            "vinos_blancos": ["Chardonnay con roble (para pollo)"],
            "temperatura": "16-18°C",
            "nota": "Tintos con cuerpo para carnes rojas, blancos para aves"
        }
    elif any(p in plato_lower for p in ["pasta", "risotto", "pizza"]):
        return {
            "plato": plato,
            "vinos_tintos": ["Chianti", "Barbera", "Montepulciano"],
            "vinos_blancos": ["Pinot Grigio", "Soave"],
            "temperatura": "Tintos 16°C, blancos 10°C",
            "nota": "Los vinos italianos son los compañeros naturales de la pasta"
        }
    else:
        return {
            "plato": plato,
            "recomendacion_general": "Rosado versátil o blanco seco",
            "vinos": ["Rosado Malbec", "Sauvignon Blanc", "Torrontés"],
            "nota": "Para platos mediterráneos en general, un blanco fresco o rosado seco es una buena elección segura"
        }


# ══════════════════════════════════════════════════════════════
# MOTOR DE EJECUCIÓN DE HERRAMIENTAS
# ══════════════════════════════════════════════════════════════

def ejecutar_herramienta(nombre: str, parametros: dict) -> str:
    """
    Despacha la llamada a la función correcta y devuelve el resultado como JSON.
    Este es el 'router' de herramientas.
    """
    if nombre == "calcular_porciones":
        resultado = calcular_porciones(**parametros)
    elif nombre == "buscar_info_ingrediente":
        resultado = buscar_info_ingrediente(**parametros)
    elif nombre == "sugerir_maridaje":
        resultado = sugerir_maridaje(**parametros)
    else:
        resultado = {"error": f"Herramienta '{nombre}' no reconocida"}

    return json.dumps(resultado, ensure_ascii=False, indent=2)


def procesar_respuesta(client, historial: list) -> str:
    """
    Ciclo completo de procesamiento:
    1. Llama a la API con las herramientas disponibles
    2. Si el modelo quiere usar una herramienta, la ejecuta
    3. Devuelve el resultado al modelo para que genere la respuesta final
    4. Repite hasta que el modelo devuelve texto normal (stop_reason == "end_turn")
    """
    while True:
        respuesta = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=historial
        )

        # Si el modelo terminó normalmente, devolver el texto
        if respuesta.stop_reason == "end_turn":
            for bloque in respuesta.content:
                if hasattr(bloque, 'text'):
                    return bloque.text
            return "[Sin respuesta]"

        # Si el modelo quiere usar herramientas
        if respuesta.stop_reason == "tool_use":
            # Agregar la respuesta del asistente al historial
            historial.append({
                "role": "assistant",
                "content": respuesta.content
            })

            # Ejecutar todas las herramientas solicitadas
            resultados_tools = []
            for bloque in respuesta.content:
                if bloque.type == "tool_use":
                    print(f"\n[🔧 Usando herramienta: {bloque.name}]")
                    resultado = ejecutar_herramienta(bloque.name, bloque.input)
                    resultados_tools.append({
                        "type": "tool_result",
                        "tool_use_id": bloque.id,
                        "content": resultado
                    })

            # Agregar los resultados al historial y hacer otra llamada
            historial.append({
                "role": "user",
                "content": resultados_tools
            })
            # El while continúa — el modelo procesa los resultados y genera respuesta final

        else:
            # stop_reason inesperado
            return f"[Respuesta inesperada del modelo: {respuesta.stop_reason}]"


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def crear_cliente():
    """La API key se lee desde el archivo .env o desde las variables de entorno."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "No se encontró GEMINI_API_KEY.\n"
            "Creá un archivo .env en esta carpeta con:\n"
            "GEMINI_API_KEY=sk-ant-..."
        )
    return anthropic.Anthropic(api_key=api_key)


def main():
    print("=" * 60)
    print("  Agente IA — Etapa 3: Herramientas (Function Calling)")
    print("  Comandos: /salir, /limpiar, /ayuda")
    print("  Herramientas: calcular porciones, info ingrediente, maridaje")
    print("=" * 60)

    client = crear_cliente()
    historial = []

    print("\nOlivia: ¡Hola! Soy Olivia. Puedo ayudarte con recetas, calcular")
    print("        porciones, darte info de ingredientes y sugerir maridajes.")
    print("        ¿Por dónde empezamos?")

    while True:
        try:
            mensaje = input("\nVos: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nOlivia: ¡Hasta luego!")
            break

        if not mensaje:
            continue

        if mensaje.lower() == "/salir":
            print("\nOlivia: ¡Hasta pronto! Que disfrutes cocinando. 🍋")
            break

        if mensaje.lower() == "/limpiar":
            historial = []
            print("\n[Sistema] Historial limpiado.")
            continue

        if mensaje.lower() == "/ayuda":
            print("\n📋 Herramientas disponibles:")
            print("  • Calculá porciones: 'adaptá esta receta para 8 personas'")
            print("  • Info de ingrediente: '¿qué es el za'atar?'")
            print("  • Maridaje: '¿qué vino va bien con paella?'")
            continue

        historial.append({"role": "user", "content": mensaje})

        try:
            print("\nOlivia: ", end="", flush=True)
            respuesta = procesar_respuesta(client, historial)
            print(respuesta)
            historial.append({"role": "assistant", "content": respuesta})

        except anthropic.APIError as e:
            print(f"\n[Error de API] {e}")
        except Exception as e:
            print(f"\n[Error] {e}")


if __name__ == "__main__":
    main()
