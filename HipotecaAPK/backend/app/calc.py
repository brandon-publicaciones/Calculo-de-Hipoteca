"""Amortización francesa con tasa preferencial (ley o manual) y recálculo al terminar la promoción."""
from .rules import get_subsidy
from .schemas import CalcRequest, CalcResult, Row


def _pmt(principal: float, i: float, n: int) -> float:
    if n <= 0:
        return 0.0
    return principal / n if i == 0 else principal * i / (1 - (1 + i) ** -n)


def _tea(nominal: float) -> float:
    return round(((1 + nominal / 1200) ** 12 - 1) * 100, 2)


def calculate(req: CalcRequest) -> CalcResult:
    value = req.property_value
    down = value * req.down_payment / 100 if req.down_payment_mode == "percent" else req.down_payment
    loan = value - down
    n = req.years * 12

    manual = req.promo_rate is not None
    if manual:
        pref_rate = req.promo_rate
        promo_years = req.promo_years
        points = round(req.commercial_rate - pref_rate, 2)
        tramo = None
        note = f"Tasa promocional manual: {pref_rate:.2f}% nominal por {promo_years} años."
    else:
        sub, note = get_subsidy(value, req.housing_type, req.region)
        pref_rate = max(req.commercial_rate - sub.points, 0.0) if sub else None
        promo_years = sub.years if sub else 0
        points = sub.points if sub else 0
        tramo = sub.tramo if sub else None

    sub_months = min(promo_years * 12, n) if pref_rate is not None else 0

    rows: list[Row] = []
    bal = loan
    pay_pref = pay_reg = None

    def run(start: int, end: int, rate: float, pay: float, preferential: bool):
        nonlocal bal
        i = rate / 1200
        for m in range(start, end + 1):
            interest = bal * i
            p = pay if m < n else bal + interest  # último mes cierra en 0
            princ = p - interest
            bal = max(bal - princ, 0.0)
            rows.append(Row(month=m, rate=rate, payment=round(p, 2), interest=round(interest, 2),
                            principal=round(princ, 2), balance=round(bal, 2), preferential=preferential))

    if sub_months:
        pay_pref = _pmt(bal, pref_rate / 1200, n)
        run(1, sub_months, pref_rate, pay_pref, True)
    if sub_months < n:
        pay_reg = _pmt(bal, req.commercial_rate / 1200, n - sub_months)
        run(sub_months + 1, n, req.commercial_rate, pay_reg, False)

    total_paid = sum(r.payment for r in rows)
    return CalcResult(
        property_value=value, down_payment=round(down, 2), loan_amount=round(loan, 2),
        years=req.years, commercial_rate=req.commercial_rate,
        subsidy_applies=pref_rate is not None, subsidy_points=points,
        subsidy_years=promo_years, tramo=tramo,
        preferential_rate=pref_rate, preferential_months=sub_months,
        preferential_payment=round(pay_pref, 2) if pay_pref is not None else None,
        regular_payment=round(pay_reg, 2) if pay_reg is not None else None,
        regular_months=n - sub_months,
        total_interest=round(total_paid - loan, 2), total_paid=round(total_paid, 2),
        effective_commercial_rate=_tea(req.commercial_rate),
        effective_preferential_rate=_tea(pref_rate) if pref_rate is not None else None,
        manual_promo=manual,
        note=note, schedule=rows,
    )