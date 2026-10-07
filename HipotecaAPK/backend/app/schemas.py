from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator


class CalcRequest(BaseModel):
    property_value: float = Field(gt=0, description="Valor total de la propiedad (USD)")
    housing_type: Literal["nueva", "usada"]
    region: Optional[Literal[1, 2]] = None  # solo vivienda nueva
    down_payment_mode: Literal["percent", "amount"] = "percent"
    down_payment: float = Field(ge=0)
    years: int = Field(ge=1, le=40)
    commercial_rate: float = Field(gt=0, le=40, description="Tasa anual comercial (%)")
    promo_rate: Optional[float] = Field(default=None, ge=0, le=40)
    promo_years: Optional[int] = Field(default=None, ge=1, le=40)

    @model_validator(mode="after")
    def _check(self):
        if self.housing_type == "nueva" and self.region is None:
            raise ValueError("La región es obligatoria para vivienda nueva.")
        if self.down_payment_mode == "percent" and self.down_payment >= 100:
            raise ValueError("El abono inicial debe ser menor al 100%.")
        if self.down_payment_mode == "amount" and self.down_payment >= self.property_value:
            raise ValueError("El abono inicial debe ser menor al valor de la propiedad.")
        if (self.promo_rate is None) != (self.promo_years is None):
            raise ValueError("Indica la tasa y los años promocionales juntos.")
        return self


class Row(BaseModel):
    month: int
    rate: float
    payment: float
    interest: float
    principal: float
    balance: float
    preferential: bool


class CalcResult(BaseModel):
    property_value: float
    down_payment: float
    loan_amount: float
    years: int
    commercial_rate: float
    subsidy_applies: bool
    subsidy_points: float
    subsidy_years: int
    tramo: Optional[int]
    preferential_rate: Optional[float]
    preferential_months: int
    preferential_payment: Optional[float]
    regular_payment: Optional[float]
    regular_months: int
    total_interest: float
    total_paid: float
    note: str
    schedule: list[Row]
    effective_commercial_rate: float
    effective_preferential_rate: Optional[float]
    manual_promo: bool
