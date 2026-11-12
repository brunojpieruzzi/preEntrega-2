# Pipeline de Extracción de Entidades Técnicas (LangChain + Pydantic)

Recibe un texto sin procesar (descripción de arquitectura, log de error) y devuelve un objeto **validado** con tecnologías, nivel de criticidad y resumen técnico.

## Estructura

| Archivo | Contenido |
|---|---|
| `schemas.py` | Modelo Pydantic `EntidadesTecnicas` (+ enum `NivelCriticidad`) |
| `chain.py` | Cliente LLM, `ChatPromptTemplate`, cadena LCEL, reintentos y `process_text()` async |
| `test_pipeline.py` | Mini-script asíncrono (caso claro + caso ambiguo) |

## Diseño

- **Contrato**: `tecnologias` (lista no vacía, sin duplicados ni vacíos), `nivel_de_criticidad` (enum `baja|media|alta`), `resumen_tecnico` (10–500 caracteres).
- **Prompt**: `ChatPromptTemplate` con variables (`{texto}`, `{niveles}`), sin f-strings.
- **Cadena LCEL**: `prompt | model.with_structured_output(EntidadesTecnicas, include_raw=True) | validación`.
- **Resiliencia**: `.with_retry()` (hasta 3 intentos, backoff exponencial con jitter) ante `ValidationError`, `OutputParserException` o `RespuestaIncompletaError`.
- **`finish_reason`**: el paso de validación inspecciona `finish_reason` / `stop_reason`; si es `length` / `max_tokens` la respuesta se considera incompleta y se reintenta antes de usarla.
- **Logs**: módulo `logging` (logger `pipeline`) registra inicio, truncamientos, errores de validación y resultado final.

## Instalación y uso

```bash
python -m venv .venv
.venv\Scripts\activate        # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # y completar la API key
python test_pipeline.py
```

Para usar Anthropic: `LLM_PROVIDER=anthropic` y `ANTHROPIC_API_KEY` en `.env`.

Uso desde código:

```python
import asyncio
from chain import process_text

print(asyncio.run(process_text("API FastAPI con Redis y PostgreSQL, se agotan las conexiones")))
```

## Ejemplo de salida

```json
{
  "tecnologias": ["FastAPI", "Redis", "PostgreSQL"],
  "nivel_de_criticidad": "alta",
  "resumen_tecnico": "API con caché en Redis y persistencia en PostgreSQL; cuello de botella en conexiones concurrentes."
}
```

## Prueba de estrés (texto ambiguo)

`test_pipeline.py` incluye un texto sin tecnologías explícitas. Si el modelo devuelve una lista vacía, el validador de Pydantic lanza `ValidationError`, se reintenta y, si se agotan los intentos, el error se muestra de forma controlada en lugar de propagar datos inválidos.
