# Agente de IA — TP12 Sistemas Inteligentes 2026

## Integrantes
- Lautaro Martinez
- Juan Sallenave
- Andres Quevedo
- Julian Fermentini

## Dominio
[COMPLETAR: describir el dominio y el nombre del agente]

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
$env:GEMINI_API_KEY = "sk-ant-..."
```

**Mac/Linux:**
```bash
export GEMINI_API_KEY="sk-ant-..."
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
- [ ] Etapa 2 — Personalidad y robustez
- [ ] Etapa 3 — Herramientas (Function Calling)
- [ ] Etapa 4 — Persistencia

## Decisiones de diseño
[COMPLETAR: describir las decisiones más importantes que tomaron]

## Dificultades encontradas
[COMPLETAR: qué salió mal y cómo lo resolvieron]
