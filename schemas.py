"""Contrato de salida del pipeline de extracción de entidades técnicas."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class NivelCriticidad(str, Enum):
    baja = "baja"
    media = "media"
    alta = "alta"


class EntidadesTecnicas(BaseModel):
    """Información técnica extraída de un texto (arquitectura, log de error, etc.)."""

    tecnologias: list[str] = Field(
        ...,
        min_length=1,
        description="Tecnologías, frameworks, lenguajes o servicios mencionados. No puede estar vacía.",
    )
    nivel_de_criticidad: NivelCriticidad = Field(
        ...,
        description="Criticidad del problema o sistema descrito: baja, media o alta.",
    )
    resumen_tecnico: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Resumen técnico conciso (1-2 oraciones) del texto.",
    )

    @field_validator("tecnologias")
    @classmethod
    def limpiar_tecnologias(cls, valores: list[str]) -> list[str]:
        """Quita espacios, descarta vacíos y elimina duplicados conservando el orden."""
        limpias = list(dict.fromkeys(v.strip() for v in valores if v and v.strip()))
        if not limpias:
            raise ValueError("La lista de tecnologías no puede estar vacía")
        return limpias


class ClasificacionTema(BaseModel):
    """Resultado del guardrail: ¿el texto es de contenido técnico de software/infraestructura?"""

    es_tecnico: bool = Field(
        ...,
        description="True solo si el texto describe arquitectura, código, infraestructura, logs o errores técnicos.",
    )
    motivo: str = Field(..., description="Justificación breve (una oración) de la decisión.")
