"""CLI interactiva: escribís un texto técnico y el pipeline devuelve el JSON validado.

Uso:
    python main.py                      # modo interactivo (línea vacía o 'salir' para terminar)
    python main.py "texto a analizar"   # una sola consulta
"""

import asyncio
import logging
import sys

from pydantic import ValidationError

from chain import FueraDeTemaError, process_text

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
logging.getLogger("pipeline").setLevel(logging.INFO)


async def analizar(texto: str) -> None:
    try:
        resultado = await process_text(texto)
        print(resultado.model_dump_json(indent=2, ensure_ascii=False))
    except FueraDeTemaError as exc:
        print(f"Rechazado por el guardrail: {exc}")
    except ValidationError as exc:
        print(f"La salida del modelo no pasó la validación tras los reintentos:\n{exc}")
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {type(exc).__name__}: {exc}")


async def main() -> None:
    if len(sys.argv) > 1:
        await analizar(" ".join(sys.argv[1:]))
        return
    print("Pegá un texto técnico (descripción de arquitectura, log de error...). Línea vacía para salir.")
    while True:
        texto = await asyncio.to_thread(input, "\n> ")
        if not texto.strip() or texto.strip().lower() == "salir":
            break
        await analizar(texto)


if __name__ == "__main__":
    asyncio.run(main())
