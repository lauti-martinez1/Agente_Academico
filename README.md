# Agente de IA — TP12 Sistemas Inteligentes 2026

## Integrantes
- Lautaro Martinez
- Juan Sallenave
- Andres Quevedo
- Julian Fermentini

## Dominio
Asistente academico - nombre: UniBot

## Requisitos
- Python 3.10 o superior
- Cuenta en Google AI Studio
- API key de Gemini

## Instalación

```bash
# 1. Clonar o descomprimir el proyecto
# 2. Crear entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

## Configuración de la API key

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY = "TU_API_KEY_DE_GEMINI"
```

**Mac/Linux:**
```bash
export GEMINI_API_KEY="TU_API_KEY_DE_GEMINI"
```

> ⚠️ Nunca escribir la API key directamente en el código.

## Ejecución

```bash
# Etapa 1 — Agente básico
python etapa1_agente_basico.py

# Etapa 2 — Con robustez y comandos
python etapa2_personalidad_robustez.py

# Etapa 3 — Con herramientas
python etapa3_herramientas.py

# Plantilla propia del grupo
python plantilla_agente.py
```

## Comandos del agente
- `/salir` — Termina la conversación
- `/limpiar` — Reinicia el historial
- `/ayuda` — Muestra los comandos disponibles
- `/historial` — Muestra las sesiones guardadas

## Estructura del proyecto
```
tp12_agente/
├── plantilla_agente.py        ← Código principal del grupo
├── etapa1_agente_basico.py    ← Ejemplo Etapa 1
├── etapa2_personalidad_robustez.py  ← Ejemplo Etapa 2
├── etapa3_herramientas.py     ← Ejemplo Etapa 3
├── requirements.txt
└── README.md
```

## Etapas implementadas
- [x] Etapa 1 — Agente conversacional básico
- [x] Etapa 2 — Personalidad y robustez
- [x] Etapa 3 — Herramientas (Function Calling)
- [x] Etapa 4 — Persistencia

## Decisiones de diseño
----Elección de Gemini en lugar de Claude----
El TP sugería la API de Anthropic, pero el grupo optó por la API de Gemini (Google) ya que ofrece una capa gratuita accesible sin tarjeta de crédito, lo que facilitó el desarrollo y las pruebas. Los conceptos aplicados (system prompt, historial de mensajes, function calling) son equivalentes en ambas APIs.

----Historial con types.Content en lugar de diccionarios planos----
La API de Gemini requiere que el historial use objetos types.Content con role y parts, a diferencia del formato {"role": "user", "content": "..."} que usa Claude.

----Tres herramientas coherentes con el dominio académico----
Se implementaron las herramientas organizar_plan_estudio, generar_cuestionario y verificar_sintaxis por considerarlas relevantes para un asistente academico.

----Persistencia en JSON plano----
Para la Etapa 4 (Opcion A) se eligió JSON sobre SQLite por simplicidad: no requiere dependencias adicionales ni conocimiento de SQL. El archivo historial.json acumula sesiones con id, fecha y mensajes, permitiendo retomar cualquier conversación anterior desde el arranque del programa.

## Dificultades encontradas
Adaptar el codigo inicial de claude a gemini, teniendo que modificar algunas secciones.