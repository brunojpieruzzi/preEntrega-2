"""Mini-script de prueba asíncrono: ejecuta el pipeline con un caso claro y uno ambiguo."""

import asyncio
import logging

from pydantic import ValidationError

from chain import process_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

TEXTO_CLARO = (
    "Nuestra API en FastAPI usa Redis como caché y PostgreSQL para persistencia. "
    "En producción vemos timeouts: el pool de conexiones a PostgreSQL se agota "
    "bajo carga concurrente y los usuarios no pueden operar."
)

# Prueba de estrés: texto ambiguo, sin tecnologías explícitas.
TEXTO_AMBIGUO = "Algo anda lento desde ayer, creo que es la base o quizás el servidor. Revisen."


async def main() -> None:
    for nombre, texto in [("CLARO", TEXTO_CLARO), ("AMBIGUO", TEXTO_AMBIGUO)]:
        print(f"\n=== Caso {nombre} ===")
        try:
            resultado = await process_text(texto)
            print(resultado.model_dump_json(indent=2))
        except ValidationError as exc:
            print(f"El validador rechazó la salida tras los reintentos:\n{exc}")
        except Exception as exc:  # noqa: BLE001
            print(f"Fallo tras agotar reintentos: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
