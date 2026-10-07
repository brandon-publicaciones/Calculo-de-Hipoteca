from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from .calc import calculate
from .pdf import build_pdf
from .schemas import CalcRequest, CalcResult

app = FastAPI(title="Hipoteca Panamá 2026")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_methods=["*"], allow_headers=["*"])


@app.post("/api/calculate", response_model=CalcResult)
def api_calculate(req: CalcRequest):
    return calculate(req)


@app.post("/api/pdf")
def api_pdf(req: CalcRequest):
    pdf = build_pdf(calculate(req))
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": 'attachment; filename="amortizacion.pdf"'})
