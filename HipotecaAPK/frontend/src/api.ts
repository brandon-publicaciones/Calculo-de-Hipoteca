import type { CalcRequest, CalcResult } from "./types";

const API = (
  (import.meta as unknown as { env: { VITE_API_URL?: string } }).env.VITE_API_URL ?? ""
).replace(/\/$/, "");

async function post(path: string, body: CalcRequest): Promise<Response> {
  const url = API + path;
  let res: Response;
  try {
    res = await fetch(url, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
    });
  } catch {
    throw new Error(
      `No se pudo conectar con ${url}. Si el servidor estaba dormido, espera 1 minuto y reintenta.`
    );
  }
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    const detail = err?.detail;
    throw new Error(
      Array.isArray(detail) ? detail.map((d: any) => d.msg).join("; ") : `Error ${res.status} al llamar ${url}`
    );
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