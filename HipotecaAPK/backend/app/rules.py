"""Reglas de subsidio (Ley 481 de 2025) según los parámetros indicados.
Edita TRAMOS si la normativa o su reglamentación cambia."""
from dataclasses import dataclass
from typing import Optional

LIMITE_SUBSIDIO = 120_000.00

# (tope del tramo, {región: (puntos de subsidio %, años)})
TRAMOS = [
    (50_000.00, {1: (5.0, 8), 2: (5.5, 8)}),
    (80_000.00, {1: (4.5, 7), 2: (5.5, 8)}),
    (120_000.00, {1: (4.0, 7), 2: (4.0, 7)}),
]


@dataclass
class Subsidy:
    points: float
    years: int
    tramo: int


def get_subsidy(value: float, housing_type: str, region: Optional[int]) -> tuple[Optional[Subsidy], str]:
    if housing_type == "usada":
        return None, "Vivienda usada: no aplica interés preferencial; tasa comercial todo el plazo."
    if value > LIMITE_SUBSIDIO:
        return None, "El valor supera $120,000: no aplica el subsidio de la ley."
    for i, (tope, regiones) in enumerate(TRAMOS, start=1):
        if value <= tope:
            pts, yrs = regiones[region]
            return Subsidy(pts, yrs, i), f"Aplica Tramo {i}, Región {region}: subsidio de {pts}% por {yrs} años."
    return None, "No aplica subsidio."
