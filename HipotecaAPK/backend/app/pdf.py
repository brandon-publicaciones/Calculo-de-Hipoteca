from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from .schemas import CalcResult


def _m(x) -> str:
    return "—" if x is None else f"${x:,.2f}"


def build_pdf(r: CalcResult) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36,
                            title="Tabla de amortización")
    st = getSampleStyleSheet()
    els = [Paragraph("Simulación Hipotecaria – Panamá", st["Title"])]

    resumen = [
        ["Valor propiedad", _m(r.property_value), "Abono inicial", _m(r.down_payment)],
        ["Monto financiado", _m(r.loan_amount), "Plazo", f"{r.years} años"],
        ["Tasa comercial", f"{r.commercial_rate:.2f}%", "Tasa preferencial",
         "—" if r.preferential_rate is None else f"{r.preferential_rate:.2f}% ({r.preferential_months} meses)"],
        ["Letra preferencial", _m(r.preferential_payment), "Letra regular", _m(r.regular_payment)],
        ["Total intereses", _m(r.total_interest), "Total pagado", _m(r.total_paid)],
    ]
    t = Table(resumen, colWidths=[110, 120, 110, 190])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                           ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                           ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                           ("FONTSIZE", (0, 0), (-1, -1), 9)]))
    els += [t, Spacer(1, 6), Paragraph(r.note, st["Italic"]), Spacer(1, 10)]

    data = [["Mes", "Tasa %", "Letra", "Interés", "Capital", "Saldo"]]
    pref_idx = []
    for k, w in enumerate(r.schedule, start=1):
        data.append([w.month, f"{w.rate:.2f}", _m(w.payment), _m(w.interest), _m(w.principal), _m(w.balance)])
        if w.preferential:
            pref_idx.append(k)
    tbl = Table(data, repeatRows=1, colWidths=[40, 50, 95, 95, 95, 105])
    style = [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b3d91")),
             ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
             ("FONTSIZE", (0, 0), (-1, -1), 8), ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
             ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f5fa")])]
    if pref_idx:
        style.append(("BACKGROUND", (0, pref_idx[0]), (-1, pref_idx[-1]), colors.HexColor("#e3f4e8")))
    tbl.setStyle(TableStyle(style))
    els += [tbl, Spacer(1, 8),
            Paragraph("Filas en verde: período con interés preferencial. Simulación referencial; "
                      "confirme condiciones con su banco.", st["Italic"])]
    doc.build(els)
    return buf.getvalue()
