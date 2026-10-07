import type { CalcRequest, CalcResult } from "./types";

async function post(path: string, body: CalcRequest): Promise<Response> {
  const res = await fetch(path, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    const detail = err?.detail;
    throw new Error(Array.isArray(detail) ? detail.map((d: any) => d.msg).join("; ") : "Error al calcular.");
  }
  return res;
}

export const calculate = async (b: CalcRequest): Promise<CalcResult> => (await post("/api/calculate", b)).json();

export async function downloadPdf(b: CalcRequest) {
  const blob = await (await post("/api/pdf", b)).blob();
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "amortizacion.pdf";
  a.click();
  URL.revokeObjectURL(a.href);
}
